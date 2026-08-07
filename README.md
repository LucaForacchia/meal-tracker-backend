# MealTracker Backend

version 0.2.2

# How to use

## Environment

The whole project runs on a single locked environment, identical in every context:

- **Python 3.11.7** everywhere:
  - Docker image: `python:3.11.7-slim` (see _Dockerfile_)
  - Local development: `.venv` created from Python 3.11.7 (_.python-version_ pins the interpreter for pyenv)
  - Tests: run with the same interpreter (see below)
- **Dependencies**: fully pinned in _requirements.txt_ (locked from a clean Python 3.11.7 virtualenv). Docker, local and tests install exactly the same versions.

## Setup

Create the local virtual environment with the same interpreter and the same dependencies used by Docker:

    > python -m venv .venv                # uses Python 3.11.7 (see .python-version)
    > .venv/bin/pip install -r requirements.txt

## Launch the server

Start the server from command line with:

    > .venv/bin/python src/main.py

## Run the tests

Run the full test suite with the same environment:

    > .venv/bin/python -m pytest

The acceptance tests can also be run through _acceptance-test.sh_ (it sets a temporary sqlite database):

    > PYTEST_COMMAND=".venv/bin/python -m pytest" bash acceptance-test.sh

## Configuration

Software configuration is driven by env variables:

| Variable | Meaning | Default/Allowed values |
|----------|---------|----------------|
| db_type | Db type to be used | sqlite (default); mysql |
| meal_db_path | Configure sqlite db path | ./db/meals.db |
| db_host | Db host for mysql | - |
| db_name | Db name for mysql | - |
| db_user | Db user for mysql | - |
| db_pass | Db pass for mysql | - |

## API

### Meal counts by person

`GET /meal/counts` returns the total count of meals. Add the `who` query parameter to filter by person:

- `who=count_total` (default): total occurrences
- `who=both`: meals for both Luca and Gioi
- `who=L`: meals for Luca
- `who=G`: meals for Gioi

Any other value returns a 400 Bad Request.

## Development

### Docker image

Build the image with the version tag (0.2.2):

    > bash script_docker_build.sh

### Local debug with the frontend

`deployment/` contains a local setup to test the interaction with the frontend webapp:

    > bash deployment/run_for_testing.sh

It starts the frontend container (docker-compose) and runs the backend (with the project `.venv`) on port 15001.
