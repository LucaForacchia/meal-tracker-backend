## [0.3.0] - 2026-10-02
### Added
- `date` query parameter on `GET /meal/week`: returns the week containing the given date (YYYY-MM-DD), 404 "Data fuori periodo tracciato" when the date is before the first week or more than 14 days after the start of the last one
- Repository, service and acceptance tests for the week lookup by date

### Changed
- Software version aligned to 0.3.0
- Test fixtures moved to `conftest.py` files (auto-discovered, no more explicit imports): each test gets its own sqlite database in the pytest `tmp_path`, and `meal_db_path` is set through `monkeypatch` so the app under test uses it
- _acceptance-test.sh_ no longer sets `meal_db_path`
- Test documentation in _docs/tests.md_

### Fixed
- `GET /meal/week` with a non-integer `week-number` now returns 400 (was 500)
- Acceptance tests used the app default database (`./db/meals.db`) instead of the test database: they now share the database of the test fixture

## [0.2.2] - 2026-08-06
### Added
- Tests reproducing the deletion of a meal with an empty `Meal` field (service and acceptance level)

### Changed
- Standardized the environment: Python 3.11.7 in Docker (`python:3.11.7-slim`), local (_.python-version_) and tests
- Locked all dependencies in _requirements.txt_ (generated from a clean Python 3.11.7 virtualenv)
- Local development uses a minimal `.venv` matching the Docker image (instead of a shared environment)
- Software version aligned to 0.2.2

### Fixed
- Deleting a meal could fail with 500 when the stored timestamp was computed in a different timezone than the request (e.g. production container in UTC vs local runs): the meal is now looked up by its natural key (date, meal type, participants)
- Deleting a meal with an empty `Meal` field (only notes) failed with 500: the meal counter was downscaled even for meals never tracked in `meal_counter`
- `delete_meal` used the request meal id instead of the stored one when applying id replacements
- `DELETE /meal/single` now returns the documented 204 (was returning 200 with the status code as body), and 404 when the meal does not exist
- Default sqlite database path now creates the `db/` directory when missing

## [0.2.1] - 2025-10-06
### Added
- Per-person meal counts via `who` query parameter on `GET /meal/counts`
- Tests for the `who` filter

### Changed
- Software version aligned to 0.2.1 across service, tests and documentation
- API version in Swagger UI bumped to 0.2.1

### Fixed
- Security: meal count query now only accepts a whitelist of count columns (was open to SQL injection via the `who` parameter)
- Welcome acceptance test expected version (was stale at 1.1.0)
- Crash in `delete_meal` DEBUG logging (malformed log call with unformatted arguments)

### Removed
- Unused `weekday` field and related database column (never used in production)

## [0.2.0] - 2023-09-18
### Added
- Delete meal functionality
- Tests extended

### Changed
- Cleaned update meal counter flow.

## [0.1.0] - 2022-12-16
### Added
- Dessert handling
- First acceptance test

### Removed
- Get last meal

## [0.0.3] - 2022-11-10
### Added
- Get replacement list 
- Extended meal service tests
- _pytest.ini_ file

### Fixed
- Returning current week also when requested with week number parameter

## [0.0.2] - 2022-10-07
### Added
- New db table meal_counter to store meal occurrences
- Domain object Meal Occurrences
- Db table aka to store id replacement
- Logging on file

### Changed
- Meal implemented as dataclass
- Meal_id built inside Meal classes, as well as meal timestamp.
- Meal_repository accepting and returning Meal objects
- Simplified validation of meal form in controller
- Retrieving count from meal_counter_table

### Fixed
- Bug in retrieving last_week number from meal_service
