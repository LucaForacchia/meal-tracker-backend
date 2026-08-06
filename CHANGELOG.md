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
