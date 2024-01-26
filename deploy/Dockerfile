FROM python:3.10-buster

# use root as workdir and set as python path
WORKDIR /code

# install poetry
RUN pip install poetry

# install requirements
COPY poetry.lock /code/poetry.lock
COPY pyproject.toml /code/pyproject.toml

RUN poetry config virtualenvs.create false
RUN poetry install --no-root

# copy code and resources
COPY src /code/src

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]
