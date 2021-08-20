"""Global distributed locking via Google Cloud Storage.

CAVEAT: The DeployLock abstraction stores git commit info in the GCS lock file,
which it uses to detect if an existing deploy is for newer code and quit if so.
However, the `gsutil cp` and `gsutil cat` steps have a race condition, so this
isn't really bulletproof - this locking mechanism ultimately can only guarantee
mutual exclusion, and not ordering.

Requires the `gsutil` command (raises FileNotFoundError otherwise).

Inspiration:
- https://github.com/thinkingmachines/gcs-mutex-lock
- https://github.com/mco-gh/gcslock
"""

from __future__ import annotations

from datetime import datetime, timedelta
from enum import Enum, auto
import os
import subprocess
import json
from typing import NamedTuple, Optional
import socket

# for retries
import tenacity
from tenacity.retry import retry_if_result
from tenacity.stop import stop_after_delay
from tenacity.wait import wait_random_exponential


##### low-level operations


class LockResult(NamedTuple):
    # Whether the lock was acquired successfully.
    acquired: bool
    # If we failed to acquire the lock, contains existing lock state.
    # Note: if acquired==False and existing_state==None, then the lock
    # state disappeared in between when we first tried to acquire the lock
    # and when we tried to get the lock state.
    existing_state: Optional[str]


def acquire_lock(gcs_path: str, data: str) -> LockResult:
    """Attempts to acquire lock file `gcs_path`, populated with `data`."""
    print(f"Attempting to lock {gcs_path}...")
    lock_result = subprocess.run(
        ["gsutil", "-h", "x-goog-if-generation-match:0", "cp", "-", gcs_path],
        text=True,
        input=data,
    )
    if lock_result.returncode == 0:
        print("Lock acquired!")
        return LockResult(True, None)

    print("Lock acquisition failed. Attempting to get current lock data...")
    cat_result = subprocess.run(
        ["gsutil", "cat", gcs_path], text=True, stdout=subprocess.PIPE
    )
    if cat_result.returncode == 0:
        print("Got existing lock state.")
        return LockResult(False, cat_result.stdout)

    # Lock failed, and there wasn't existing deploy info. This should only
    # happen in rare race conditions.
    print(
        "Failed to get current lock data - disappeared between `gsutil cp` and `gsutil cat`?"
    )
    return LockResult(False, None)


def release_lock(gcs_path: str):
    """Release the lock. Raises exception if the lockfile isn't present."""
    print(f"Releasing lock {gcs_path}...")
    subprocess.run(["gsutil", "rm", gcs_path], check=True)
    print("Lock released.")


##### DeployLock helpers

# lock bucket setup:
# gsutil mb gs://BUCKET_NAME && gsutil versioning set on gs://BUCKET_NAME
GCS_DEPLOY_LOCK_BASE = "gs://your-gcs-deploy-lock-bucket-name-here"


class DeployState(NamedTuple):
    """Data stored in GCS lockfile"""

    # the git commit being deployed
    git_sha: str
    git_timestamp: int  # epoch seconds
    # metadata fields for debugging
    deploy_datetime: str
    deploy_hostname: str

    @staticmethod
    def latest_commit() -> DeployState:
        # Get short hash, newline, and UNIX timestamp of commit.
        # See format placeholders docs: https://git-scm.com/docs/git-log
        git_result = subprocess.run(
            ["git", "log", "-1", "--format=%h%n%ct"],
            text=True,
            stdout=subprocess.PIPE,
            check=True,
        )
        git_lines = git_result.stdout.rstrip().split("\n")
        assert len(git_lines) == 2, f"Expecting 2 lines, got: {git_lines}"
        now = datetime.now()
        return DeployState(
            git_sha=git_lines[0],
            git_timestamp=int(git_lines[1]),
            deploy_datetime=f"{now.timestamp()} {now.isoformat()}",
            deploy_hostname=socket.gethostname(),
        )

    @staticmethod
    def from_json(data: str) -> DeployState:
        return DeployState(**json.loads(data))

    def to_json(self) -> str:
        return json.dumps(self._asdict(), indent=2)

    def has_newer_commit(self, other: DeployState) -> bool:
        return self.git_timestamp > other.git_timestamp


class DeployLockResult(Enum):
    """Outcomes of trying to acquire the deploy lock."""

    got_lock = auto()
    this_deploy_is_newer = auto()
    existing_deploy_is_newer = auto()
    failed_to_get_lock_and_lock_state = auto()
    timed_out = auto()


def _lockresult_to_deploylockresult(
    lock_result: LockResult, this_deploy: DeployState
) -> DeployLockResult:
    """Converts from LockResult to DeployLockResult."""
    if lock_result.acquired:
        return DeployLockResult.got_lock
    if lock_result.existing_state:
        existing_deploy = DeployState.from_json(lock_result.existing_state)
        if this_deploy.has_newer_commit(existing_deploy):
            return DeployLockResult.this_deploy_is_newer
        else:
            print(
                "There's an existing deployment with a newer commit.\n"
                f"    this deploy: {this_deploy}\n"
                f"existing deploy: {existing_deploy}"
            )
            return DeployLockResult.existing_deploy_is_newer
    return DeployLockResult.failed_to_get_lock_and_lock_state


# split apart so it's easier to test without mocking acquire_lock
def _acquire_deploy_lock_once(
    gcs_path: str, deploy_state: DeployState
) -> DeployLockResult:
    lock_result = acquire_lock(gcs_path, deploy_state.to_json())
    return _lockresult_to_deploylockresult(lock_result, deploy_state)


def _wait_for_deploy_lock(
    gcs_path: str, deploy_state: DeployState, timeout: timedelta
) -> DeployLockResult:
    """Tries to continually acquire the lock until the timeout."""

    def should_retry(result: DeployLockResult) -> bool:
        # We retry in the failed_to_get_lock_and_lock_state case. That's
        # assuming that the previous deploy finished and released the lock in
        # between when we first tried to check it.
        should_retry = result in (
            DeployLockResult.this_deploy_is_newer,
            DeployLockResult.failed_to_get_lock_and_lock_state,
        )
        print(f"should retry? condition: {result}, {should_retry=}")
        return should_retry

    # deploys take a while, so we don't retry that aggressively
    @tenacity.retry(
        retry=retry_if_result(should_retry),
        wait=wait_random_exponential(min=5, max=15),
        stop=stop_after_delay(timeout.total_seconds()),
    )
    def _wait_for_deploy_lock() -> DeployLockResult:
        return _acquire_deploy_lock_once(gcs_path, deploy_state)

    try:
        return _wait_for_deploy_lock()
    except tenacity.RetryError as e:
        print(f"Timed out after {timeout} waiting for deploy lock ({e}).")
        return DeployLockResult.timed_out


##### DeployLock implementation


class ExistingDeployWithNewerCommit(Exception):
    pass


class TimedOutAcquiringLock(Exception):
    pass


class DeployLock:
    """Context manager for acquiring a deploy lock file.

    Raises:
    - ExistingDeployWithNewerCommit: when an existing lock is for a newer deploy
    - TimedOutAcquiringLock: when specified timeout is exceeded.
    - GcsRaceCondition: this should rarely happen...?
    """

    def __init__(
        self,
        lockfile_name: str,
        timeout: timedelta,
        deploy_state: Optional[DeployState] = None,
    ):
        self.gcs_path = os.path.join(GCS_DEPLOY_LOCK_BASE, lockfile_name)
        del lockfile_name
        # Note: `latest_commit` requires git and .git state (so won't work in
        # slimmed Docker containers)
        deploy_state = deploy_state or DeployState.latest_commit()

        lock_result = _wait_for_deploy_lock(self.gcs_path, deploy_state, timeout)
        if lock_result in (
            DeployLockResult.this_deploy_is_newer,
            DeployLockResult.failed_to_get_lock_and_lock_state,
        ):
            assert False, f"Bug: should have auto-retried on {lock_result}"
        elif lock_result == DeployLockResult.existing_deploy_is_newer:
            raise ExistingDeployWithNewerCommit
        elif lock_result == DeployLockResult.timed_out:
            raise TimedOutAcquiringLock
        assert lock_result == DeployLockResult.got_lock, "Bug: failed to handle a case?"

    def __enter__(self) -> None:
        pass

    def __exit__(self, _type, _value, _traceback):
        release_lock(self.gcs_path)


if __name__ == "__main__":
    import argparse
    import time

    p = argparse.ArgumentParser()
    p.add_argument("-t", type=int, required=False, help="simulated timestamp")
    args = p.parse_args()

    if args.t is not None:
        deploy_state = DeployState("sha", args.t, datetime.now().isoformat(), "host")
    else:
        deploy_state = DeployState.latest_commit()
    print(f"using {deploy_state=}")

    lockfile = "gcs_lock_test.json"
    try:
        with DeployLock(
            lockfile, deploy_state=deploy_state, timeout=timedelta(minutes=10)
        ):
            print("\nwe got the lock, yay! doing stuff with lock...")
            time.sleep(20)
    except ExistingDeployWithNewerCommit:
        print("\nexisting deploy wins")
