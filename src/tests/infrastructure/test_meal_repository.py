from datetime import datetime, date
import pytest

from domain.meal import Meal

from infrastructure.persistence.meal_repository import MealRepository

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
