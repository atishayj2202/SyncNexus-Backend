# SyncNexus-Backend

## environment setup

need a locally installed python version 3.10.12. recommended to use pyenv to install that.

```shell
poetry env use ~/.pyenv/versions/3.10.12/bin/python
poetry install
```

## testing app

1. Run a local instance of cockraoch db For Testing using:

```shell
sh deploy/local_test.sh pull  # required only first time
sh deploy/local_test.sh local-start
sh deploy/local_test.sh stop  # when testing is over
```

Now the tests which require this local instance will run. They can be run individually in pycharm or using the command:
```shell
poetry run pytest
```

## linting/formatting
The following commands can be used:

```shell
poetry run sh deploy/local_test.sh check-format
poetry run sh deploy/local_test.sh format
```

```shell
poetry run bumpversion --config-file=./deploy/.bumpversion.cfg <option>
```
The option can be:
- patch: to update the patch version
- minor: to update the minor version
- major: to update the major version
- release: to update the release version
  - also add `--tag` to create a git tag when releasing