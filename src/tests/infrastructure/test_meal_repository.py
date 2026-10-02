from datetime import datetime, date
import pytest

from domain.meal import Meal

from infrastructure.persistence.meal_repository import MealRepository, WeekNotFound

from tests.utils import database, clean_db, get_meal

@pytest.fixture
def repository(database):
    (db, db_type) = database
    for table in ["meals"]:
        clean_db(db, table)
    return MealRepository(db, db_type)

@pytest.mark.repository
def test_init_db(database):
    # given: a valid db connection
    (db, db_type) = database

    # when: init the repo
    repo = MealRepository(db, db_type)

    # then: the db tables are created
    c = db.cursor()
    c.execute("SELECT * FROM meals")
    # no error has being thrown, careful there are differences with mysql

@pytest.mark.repository
def test_save_meal(repository, database):
    # given: a correctly initialized repository and a valid meal:
    meal_obj = get_meal()

    # when: inserting a new meal in db
    repository.insert_meal(meal_obj)

    # then: the meal is correctly stored into the db
    (db, db_type) = database

    c = db.cursor()
    c.execute("SELECT * FROM meals")
    meals = c.fetchall()
    assert len(meals) == 1
    assert meals[0] == ('2022-01-01', 1641034800, 0, 'Pranzo', 'Entrambi', 'Test meal', 'TESTMEAL', None, 'Nota')

@pytest.mark.repository
def test_delete_meal(repository, database):
    # given: a correctly initialized repository and a valid meal inserted into db:
    meal_obj = get_meal()
    repository.insert_meal(meal_obj)

    # when: deleting the new meal from db
    repository.delete_meal(meal_obj.timestamp, "Entrambi")

    # then: the meal is no more stored into the db
    (db, db_type) = database

    c = db.cursor()
    c.execute("SELECT * FROM meals")
    meals = c.fetchall()
    assert len(meals) == 0

@pytest.mark.repository
def test_save_meal_with_dessert(repository, database):
    # given: a correctly initialized repository and a valid meal, including dessert:
    meal_obj = get_meal(dessert="Test dessert")

    # when: inserting a new meal in db
    repository.insert_meal(meal_obj)

    # then: the meal is correctly stored into the db
    (db, db_type) = database

    c = db.cursor()
    c.execute("SELECT * FROM meals")
    meals = c.fetchall()
    assert len(meals) == 1
    print(meals[0])
    assert meals[0] == ('2022-01-01', 1641034800, 0, 'Pranzo', 'Entrambi', 'Test meal', 'TESTMEAL', 'Test dessert', 'Nota')

@pytest.mark.repository
def test_save_meal_new_week(repository, database):
    # given: a correctly initialized repository and a valid meal:
    meal_obj = get_meal()
    meal_obj.start_week = True
    meal_obj.week_number = 120

    # when: inserting a new meal in db
    repository.insert_meal(meal_obj)

    # then: the meal is correctly stored into the db
    (db, db_type) = database

    c = db.cursor()
    c.execute("SELECT * FROM meals")
    meals = c.fetchall()
    assert len(meals) == 1
    assert meals[0] == ('2022-01-01', 1641034800, 120, 'Pranzo', 'Entrambi', 'Test meal', 'TESTMEAL', None, 'Nota')

@pytest.mark.repository
def test_meal_counts(repository):
    # given: 4 meal inserted into both dbs, 2 of them having same meal_id
    repository.insert_meal(get_meal())
    repository.update_meal_counter(get_meal())

    repository.insert_meal(get_meal(date_meal=datetime(2022,1,2)))
    repository.update_meal_counter(get_meal(date_meal=datetime(2022,1,2)))

    repository.insert_meal(get_meal(date_meal=datetime(2022,1,3), meal="Another meal"))
    repository.update_meal_counter(get_meal(date_meal=datetime(2022,1,3), meal="Another meal"))

    repository.insert_meal(get_meal(date_meal=datetime(2022,1,4), meal="Third meal"))
    repository.update_meal_counter(get_meal(date_meal=datetime(2022,1,4), meal="Third meal"))

    # when: requiring the count of meals:
    meal_counts = repository.get_meals_count()

    # then: meal_counts is as expected
    print(meal_counts)
    assert type(meal_counts) == dict
    assert len(meal_counts) == 3
    assert 'ANOTHERMEAL' in meal_counts
    assert meal_counts['ANOTHERMEAL']["name"] == "Another meal"
    assert meal_counts['ANOTHERMEAL']["count"] == 1
    assert 'TESTMEAL' in meal_counts
    assert meal_counts['TESTMEAL'] == {"name": 'Test meal', "count": 2}

@pytest.mark.repository
def test_meal_counts_who_filter(repository):
    # given: meals with different participants stored and counted
    repository.insert_meal(get_meal(participants="Luca"))
    repository.update_meal_counter(get_meal(participants="Luca"))

    repository.insert_meal(get_meal(date_meal=datetime(2022,1,2), participants="Gioi"))
    repository.update_meal_counter(get_meal(date_meal=datetime(2022,1,2), participants="Gioi"))

    repository.insert_meal(get_meal(date_meal=datetime(2022,1,3)))
    repository.update_meal_counter(get_meal(date_meal=datetime(2022,1,3)))

    # when: requiring the total count
    meal_counts = repository.get_meals_count()
    assert meal_counts['TESTMEAL']["count"] == 3

    # when: requiring the count for a specific person
    meal_counts = repository.get_meals_count("L")
    assert meal_counts['TESTMEAL']["count"] == 1

    meal_counts = repository.get_meals_count("G")
    assert meal_counts['TESTMEAL']["count"] == 1

    meal_counts = repository.get_meals_count("both")
    assert meal_counts['TESTMEAL']["count"] == 1

    # then: an invalid who value is rejected
    with pytest.raises(ValueError):
        repository.get_meals_count("OR 1=1--")

@pytest.mark.repository
def test_meal_names(repository):
    # given: 4 meal inserted into both dbs, 2 of them having same meal_id
    repository.insert_meal(get_meal())
    repository.update_meal_counter(get_meal())

    repository.insert_meal(get_meal(date_meal=datetime(2022,1,2)))
    repository.update_meal_counter(get_meal(date_meal=datetime(2022,1,2)))

    repository.insert_meal(get_meal(date_meal=datetime(2022,1,3), meal="Another meal"))
    repository.update_meal_counter(get_meal(date_meal=datetime(2022,1,3), meal="Another meal"))

    repository.insert_meal(get_meal(date_meal=datetime(2022,1,4), meal="Third meal"))
    repository.update_meal_counter(get_meal(date_meal=datetime(2022,1,4), meal="Third meal"))

    # when: requiring the meals names:
    meal_names = repository.get_meals_names()

    # then: meal_counts is as expected
    print(meal_names)
    assert type(meal_names) == list
    assert len(meal_names) == 3
    assert 'Another meal' in meal_names
    assert 'Test meal' in meal_names

@pytest.mark.repository
def test_meal_counter_table(repository, database):
    # given: a valid meal form
    meal_obj = get_meal()

    # when: inserting it to meal_counter table
    repository.update_meal_counter(meal_obj)

    # then: an entry is correctly created into the meal_counter table
    (db, db_type) = database

    c = db.cursor()
    c.execute("SELECT * FROM meal_counter")
    meals = c.fetchall()
    assert len(meals) == 1
    assert meals[0] == ('TESTMEAL', 'Test meal', 1, 1, 0, 0)

    # when: updating the table with the same meal
    meal_obj.participants = "Luca"
    repository.update_meal_counter(meal_obj)

    # then: meal_counter table is correctly updated
    c = db.cursor()
    c.execute("SELECT * FROM meal_counter")
    meals = c.fetchall()
    assert len(meals) == 1
    assert meals[0] == ('TESTMEAL', 'Test meal', 2, 1, 1, 0)

def insert_weeks(repository, week_starts):
    # week_starts: list of (week_number, date, meal_type) of the meals starting a week
    for week_number, date_meal, meal_type in week_starts:
        meal_obj = get_meal(date_meal=date_meal, meal_type=meal_type, start_week=True)
        meal_obj.week_number = week_number
        repository.insert_meal(meal_obj)

WEEKS = [(1, datetime(2022,1,1), "Pranzo"), (2, datetime(2022,1,8), "Cena"), (3, datetime(2022,1,15), "Pranzo")]

@pytest.mark.repository
@pytest.mark.parametrize("date_iso,expected_week", [
    ("2022-01-01", 1),  # first day tracked, week 1 included
    ("2022-01-05", 1),
    ("2022-01-07", 1),
    ("2022-01-08", 2),  # boundary day (week starting with a Cena) goes to the new week
    ("2022-01-14", 2),
    ("2022-01-15", 3),
    ("2022-01-28", 3),  # last week, 13 days from its start
])
def test_get_week_number_by_date(repository, date_iso, expected_week):
    # given: three tracked weeks
    insert_weeks(repository, WEEKS)
    repository.insert_meal(get_meal(date_meal=datetime(2022,1,5), meal_type="Cena"))

    # when: resolving the week of a date
    # then: the week started last on or before the date is returned
    assert repository.get_week_number_by_date(date_iso) == expected_week

@pytest.mark.repository
@pytest.mark.parametrize("date_iso", [
    "2021-12-31",  # before the first week
    "2022-01-29",  # last week, 14 days from its start
    "2023-01-01",
])
def test_get_week_number_by_date_out_of_period(repository, date_iso):
    # given: three tracked weeks
    insert_weeks(repository, WEEKS)

    # when: resolving a date outside the tracked period
    # then: WeekNotFound is raised with the user message
    with pytest.raises(WeekNotFound) as err:
        repository.get_week_number_by_date(date_iso)
    assert str(err.value) == "Data fuori periodo tracciato"

@pytest.mark.repository
def test_get_week_number_by_date_empty_db(repository):
    # given: no meals stored
    # when: resolving a date
    # then: WeekNotFound is raised
    with pytest.raises(WeekNotFound):
        repository.get_week_number_by_date("2022-01-01")
