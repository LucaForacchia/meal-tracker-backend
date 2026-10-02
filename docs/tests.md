# Tests

## Run

From the repository root, with the project `.venv` (Python 3.11.7, see README):

    > .venv/bin/python -m pytest              # full suite
    > .venv/bin/python -m pytest -m acceptance # one level only (markers below)
    > .venv/bin/python -m pytest -q src/tests/acceptance/test_meal_controller.py::test_week_by_date

The suite can be launched from any folder and never touches a real database: no environment variable is needed.
_acceptance-test.sh_ runs only the acceptance tests (`PYTEST_COMMAND=".venv/bin/python -m pytest" bash acceptance-test.sh`).

## Levels and markers

Markers are declared in _pytest.ini_. Every test carries the marker of its level:

| Marker | Folder | What it tests | Entry point |
|--------|--------|---------------|-------------|
| `domain` | _src/tests/domain/_ | dataclasses in _src/domain/_ (e.g. `Meal` building `meal_id`, `date`, `timestamp`) | domain objects, no db |
| `repository` | _src/tests/infrastructure/test_meal_repository.py_ | SQL queries | `MealRepository` on the test db |
| `service` | _src/tests/infrastructure/test_meal_service.py_ | business logic (week numbering, counters, replacements) | `MealService` on the test db |
| `acceptance` | _src/tests/acceptance/_ | HTTP API: status codes, payloads, error messages | Flask test `client` |

Tests follow the _given / when / then_ comment style.

## Fixtures

Fixtures live in `conftest.py` files and pytest discovers them automatically: **do not import them** in test modules (an explicit import would shadow the conftest one).

- _src/tests/conftest.py_
  - `database`: a fresh database for each test, returned as `(db, db_type)`.
    - sqlite (default): a new file in the pytest `tmp_path` folder (deleted by pytest, old runs are pruned automatically). The fixture also sets `meal_db_path` to that file through `monkeypatch`, so the app under test (acceptance) opens **the same** database; the variable is restored after each test.
    - mysql (`db_type=mysql`, with `db_host`, `db_name`, `db_user`, `db_pass`): connects to the given server, retrying `db_max_retry` times every `db_sleep_time` seconds. Tables are not dropped automatically: tests call `clean_db` for this.
- _src/tests/acceptance/conftest.py_
  - `app`: Flask app with the API namespaces, on top of `database`.
  - `client`: Flask test client of `app`.
- _src/tests/infrastructure/test_meal_*.py_: local `repository` / `service` fixtures, built on `database`.

Helpers (plain functions, imported explicitly) are in _src/tests/utils.py_: `get_meal(...)` builds a `Meal` with sensible defaults, `clean_db(db, table)` drops a table, `get_environ`, `mysql_query_adapter`.

## Writing tests

- Tables are created when a `MealRepository` is built. In acceptance tests that write directly to the db, first call any endpoint (e.g. `client.get("/meal/counts")`) so the service creates the tables.
- To set up specific weeks, insert meals with an explicit week number (`meal.week_number = N` and `repository.insert_meal(meal)`, or a direct `INSERT`): `store_meal` computes the week number on its own (see TODO for its week 1 issue).
- Every fix comes with a test reproducing it, at the lowest level where it shows up and, when it changes the API, at acceptance level too.

## Why the test database is isolated

The app reads its sqlite path from `meal_db_path` and falls back to `./db/meals.db`, relative to the working directory (creating the folder if missing). Before 0.3.0 the tests did not set it: the acceptance tests wrote into a `db/meals.db` inside the repository, which persisted across runs and was not the db seen by the other fixtures. The `database` fixture now always points the app to its own temporary file.
