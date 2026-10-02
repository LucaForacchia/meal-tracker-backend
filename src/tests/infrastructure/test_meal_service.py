from datetime import datetime, date
import pytest

from domain.meal import Meal

from infrastructure.services.meal_service import MealService
from infrastructure.persistence.meal_repository import MealRepository

from tests.utils import clean_db, get_meal

@pytest.fixture
def service(database):
    (db, db_type) = database
    for table in ["meals"]:
        clean_db(db, table)
    return MealService(db, {"db_type": db_type})

@pytest.mark.service
def test_store_meal(service, database):
    # given: a meal service and a valid meal:
    meal_obj = get_meal()

    # when: inserting a new meal in db
    service.store_meal(meal_obj)

    # then: the meal is correctly stored into the db
    (db, db_type) = database

    c = db.cursor()
    c.execute("SELECT * FROM meals")
    meals = c.fetchall()
    assert len(meals) == 1
    assert meals[0] == ('2022-01-01', 1641034800, 0, 'Pranzo', 'Entrambi', 'Test meal', 'TESTMEAL', None, 'Nota')

@pytest.mark.service
def test_store_meal_new_week(service, database):
    # given: a meal service and a valid meal, with a week previously insertd into db:
    meal_obj = get_meal()
    meal_obj.start_week = True
    meal_obj.week_number = 120

    # when: inserting a new meal in db
    service.repository.insert_meal(meal_obj)

    new_meal = get_meal(date_meal=datetime(2022,2,15), start_week=True)

    # when: inserting a new meal in db
    service.store_meal(new_meal)

    # then: the meal is correctly stored into the db
    (db, db_type) = database

    c = db.cursor()
    c.execute("SELECT * FROM meals")
    meals = c.fetchall()
    print(meals)
    assert len(meals) == 2
    assert meals[0] == ('2022-01-01', 1641034800, 120, 'Pranzo', 'Entrambi', 'Test meal', 'TESTMEAL', None, 'Nota')
    assert meals[1] == ('2022-02-15', 1644922800, 121, 'Pranzo', 'Entrambi', 'Test meal', 'TESTMEAL', None, 'Nota')

@pytest.mark.service
def test_get_weekly_meals(service, database):
    # given: a meal service and valid meals, with week previously insertd into db:
    meal_obj = get_meal()
    meal_obj.start_week = True
    meal_obj.week_number = 120
    service.repository.insert_meal(meal_obj)
    new_meal = get_meal(date_meal=datetime(2022,2,15), start_week=True)
    service.store_meal(new_meal)
    new_meal = get_meal(date_meal=datetime(2022,2,16), start_week=True)
    service.store_meal(new_meal)

    # when: requiring last week meals (week number is None)
    weekly_meals = service.get_weekly_meals(None)

    # then: last week is retrieved correctly
    print(weekly_meals)
    assert weekly_meals[0] == 122
    assert len(weekly_meals[1]) == 1
    first_meal = weekly_meals[1][0] 
    assert type(first_meal) == Meal
    assert first_meal.date == "2022-02-16"
    assert first_meal.start_week == True
    assert first_meal.week_number is None

    # when: requiring previous week meals specifying week number
    weekly_meals = service.get_weekly_meals(121)

    # then: week meals are retrieved correctly
    print(weekly_meals)
    assert weekly_meals[0] == 121
    assert len(weekly_meals[1]) == 1
    first_meal = weekly_meals[1][0] 
    assert type(first_meal) == Meal
    assert first_meal.date == "2022-02-15"
    assert first_meal.start_week == True
    assert first_meal.week_number is None

    # when: requiring last week meals specifying week number
    weekly_meals = service.get_weekly_meals(122)

    # then: last week is retrieved correctly
    print(weekly_meals)
    assert weekly_meals[0] == 122
    assert len(weekly_meals[1]) == 1
    first_meal = weekly_meals[1][0] 
    assert type(first_meal) == Meal
    assert first_meal.date == "2022-02-16"
    assert first_meal.start_week == True
    assert first_meal.week_number is None

@pytest.mark.service
def test_delete_meal(service, database):
    # given: a meal service and two valid meals stored in db:
    meal_obj = get_meal(meal="TestDelete")
    service.store_meal(meal_obj)

    meal_obj = get_meal(date_meal = datetime(2023,1,1), meal="Test Delete", participants="Luca")
    service.store_meal(meal_obj)


    # when: requiring to delete the meal (only timestamp and participants fields are required)
    service.delete_meal(get_meal())

    # then: the meal is correctly deleted from db
    (db, db_type) = database

    c = db.cursor()
    c.execute("SELECT * FROM meals")
    meals = c.fetchall()
    assert len(meals) == 1
    assert meals[0] == ('2023-01-01', 1672570800, 0, 'Pranzo', 'Luca', 'Test Delete', 'TESTDELETE', None, 'Nota')

    # then: the meal counter is correctly updated
    c.execute('''SELECT 
        meal_id,
        meal,
        count_total,
        both,
        L,
        G
        FROM meal_counter''')
    meals = c.fetchall()
    assert len(meals) == 1
    assert meals[0] == ('TESTDELETE', 'TestDelete', 1, 0, 1, 0)

@pytest.mark.service
def test_delete_meal_with_empty_meal_field(service, database):
    # given: a meal with an empty meal field (only notes) stored:
    meal_obj = get_meal(meal="", notes="Solo appunti")
    service.store_meal(meal_obj)

    # when: requiring to delete the meal
    service.delete_meal(meal_obj)

    # then: the meal is correctly deleted from db
    (db, db_type) = database

    c = db.cursor()
    c.execute("SELECT * FROM meals")
    meals = c.fetchall()
    assert len(meals) == 0

    # then: the meal counter is not touched
    c.execute("SELECT * FROM meal_counter")
    meals = c.fetchall()
    assert len(meals) == 0

@pytest.mark.service
def test_delete_meal_stored_in_different_timezone(service, database):
    # given: a meal stored with a timestamp computed in a different timezone
    # (e.g. the production container runs in UTC, while local runs are UTC+2)
    meal_obj = get_meal()
    meal_obj.timestamp += 2 * 60 * 60
    service.store_meal(meal_obj)

    # when: deleting it with a meal whose timestamp is computed in local time
    service.delete_meal(get_meal())

    # then: the meal is correctly deleted from db
    (db, db_type) = database

    c = db.cursor()
    c.execute("SELECT * FROM meals")
    meals = c.fetchall()
    assert len(meals) == 0

    # then: the meal counter is decremented accordingly
    c.execute("SELECT * FROM meal_counter")
    meals = c.fetchall()
    assert meals == [('TESTMEAL', 'Test meal', 0, 0, 0, 0)]
@pytest.mark.service
def test_get_weekly_meals_by_date(service):
    # given: two tracked weeks, the second starting with a Cena
    for week_number, date_meal, meal_type in [(1, datetime(2022,1,1), "Pranzo"), (2, datetime(2022,1,8), "Cena")]:
        meal_obj = get_meal(date_meal=date_meal, meal_type=meal_type, start_week=True)
        meal_obj.week_number = week_number
        service.repository.insert_meal(meal_obj)
    service.store_meal(get_meal(date_meal=datetime(2022,1,3), meal="Week one"))
    service.store_meal(get_meal(date_meal=datetime(2022,1,8), meal="Week one boundary"))
    service.store_meal(get_meal(date_meal=datetime(2022,1,10), meal="Week two"))

    # when: requesting the week containing a date
    week_number, meals = service.get_weekly_meals_by_date(date(2022,1,5))

    # then: the meals of that week are returned
    assert week_number == 1
    assert [m.meal for m in meals] == ["Test meal", "Week one", "Week one boundary"]

    # when: requesting the boundary day
    week_number, meals = service.get_weekly_meals_by_date(date(2022,1,8))

    # then: the new week is returned
    assert week_number == 2
    assert [m.meal for m in meals] == ["Test meal", "Week two"]
