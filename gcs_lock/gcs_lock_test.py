from gcs_lock.gcs_lock import (
    DeployState,
    DeployLockResult,
    LockResult,
    _lockresult_to_deploylockresult,
)


def test_lockresult_to_deploylockresult__no_existing_lock() -> None:
    lr = LockResult(acquired=True, existing_state=None)
    this_deploy = DeployState('abc', 1, '2021-01-01', 'host')
    dlr = _lockresult_to_deploylockresult(lr, this_deploy)
    assert dlr == DeployLockResult.got_lock


def test_lockresult_to_deploylockresult__existing_deploy_is_newer() -> None:
    lr = LockResult(
        acquired=False,
        existing_state=DeployState('abc', 100, '2021-01-02', 'host').to_json(),
    )
    this_deploy = DeployState('abc', 99, '2021-01-01', 'host')
    dlr = _lockresult_to_deploylockresult(lr, this_deploy)
    assert dlr == DeployLockResult.existing_deploy_is_newer


def test_lockresult_to_deploylockresult__this_deploy_is_newer() -> None:
    lr = LockResult(
        acquired=False,
        existing_state=DeployState('abc', 100, '2021-01-02', 'host').to_json(),
    )
    this_deploy = DeployState('abc', 101, '2021-01-03', 'host')
    dlr = _lockresult_to_deploylockresult(lr, this_deploy)
    assert dlr == DeployLockResult.this_deploy_is_newer


def test_lockresult_to_deploylockresult__failed_to_read_state() -> None:
    # race condition case: failed to get lock *and* failed to read lock state
    lr = LockResult(acquired=False, existing_state=None)
    this_deploy = DeployState('abc', 1, '2021-01-01', 'host')
    dlr = _lockresult_to_deploylockresult(lr, this_deploy)
    assert dlr == DeployLockResult.failed_to_get_lock_and_lock_state


# TODO: do deeper tests by mocking out acquire_lock and release_lock...
# - _wait_for_deploy_lock returns immediately if no existing lock
# - _wait_for_deploy_lock retries if existing lock, and then returns successful acquisition after lock goes away
# - _wait_for_deploy_lock retries if existing lock and return timeout after time expires
# - BlueroseDeployLock succeeds / raises the right exceptions
