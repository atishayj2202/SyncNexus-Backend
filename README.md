# Google-Solution-Challenge

## environment setup

need a locally installed python version 3.10.12. recommended to use pyenv to install that.

```shell
poetry env use ~/.pyenv/versions/3.10.12/bin/python
poetry install
```

## testing app

1. Run a local instance of cockraoch db For Testing using:

```shell
sh deploy/local_test.sh cr-pull  # required only first time
sh deploy/local_test.sh cr-local-start
sh deploy/local_test.sh cr-stop  # when testing is over
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
