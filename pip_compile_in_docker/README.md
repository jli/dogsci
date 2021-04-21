# pip-compile-in-docker

Just a small example of running pip-compile in the same Docker environment as
the application to ensure the same Python version is used, per this:

> **Important**: `pip-compile` has no proper resolver. Thus it *has* to run
> under the *same* Python version as the project it’s locking and in the *same*
> environment, or else conditional dependencies will not work correctly.

(<https://hynek.me/articles/python-app-deps-2018/>)

Also see <https://pythonspeed.com/articles/pipenv-docker/> for discussion on
why pinning dependencies is good (tl;dr reproducible and faster builds).

