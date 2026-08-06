# MealTracker Backend

version 0.2.1

# How to use

## Setup

Please use python 3.10+ (see the _Dockerfile_) and install dependencies using pip3

    > pip3 install -r requirements.txt

## Launch the server

Start the server from command line with:

    > python src/main.py

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

Build the image with the version tag (0.2.1):

    > bash script_docker_build.sh

### Local debug with the frontend

`deployment/` contains a local setup to test the interaction with the frontend webapp:

    > bash deployment/run_for_testing.sh

It starts the frontend container (docker-compose) and runs the backend on port 15001.
