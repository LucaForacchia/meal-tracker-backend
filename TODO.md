# Future!

## Replacement
- Expose replacement table
- Carefully test meal_counter, before allowing replacement exposure
- Implement "DELETE" replacement, restoring counting on meal_counter table

## Weeks
 - `store_meal` computes the new week number with `get_last_week_timestamp`, which ignores week 1 (`start_week > 1`): on an empty db the second week gets number 1 again. Not an issue in production (weeks are already > 1), but to be fixed with a test

## Tests
 - ? Acceptance test ?
 - Ensure current implementation with unit test

## Environment
 - "Rejuvenate" the whole environment to a newer Python (at least 3.12): Dockerfile base image (now python:3.11.7-slim), _.python-version_, local _.venv_, re-lock _requirements.txt_, run the full test suite, build and deploy the new image
 - Keep Python version aligned with the webapp (now 3.10)

## Server
 - Automate start at boot
 - CI/CD?
 - Run on a server!

## DB
 - Move to MySql

### Allow frequencies count for date?