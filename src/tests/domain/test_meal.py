from datetime import datetime, date
import pytest

from datetime import datetime
from domain.meal import Meal

@pytest.mark.domain
def test_meal_creation():
    # given: a set of valid values for a meal:

    # when: creating the Meal object
    meal_object = Meal(datetime(2022,1,1), "Pranzo", "Entrambi", "Test meal", "Nota")

    # then: meal object is as expected
    assert meal_object is not None
    print(meal_object)
    assert meal_object.date == "2022-01-01"
    assert meal_object.timestamp == 1641034800
    assert meal_object.meal_type == "Pranzo"
    assert meal_object.participants == "Entrambi"
    assert meal_object.meal == "Test meal"
    assert meal_object.notes == "Nota"
    assert not meal_object.start_week
    assert meal_object.week_number is None
    assert meal_object.meal_id == "TESTMEAL"
    assert meal_object.dessert is None
    assert len(meal_object.__dict__) == 10

@pytest.mark.domain
def test_creation_dict():
    # given: a dict containing valid values for a Meal, including dessert
    meal = {
            "date": datetime.fromisoformat("2022-02-28"),
            "start_week": bool("True"),
            "meal_type": "Pranzo",
            "participants": "Entrambi",
            "meal": "DictMeal",
            "notes": "Notes",
            "dessert": "Test dessert"
        }

    # when: using it to create the Meal object
    meal_object = Meal(**meal)

    # then: meal object is as expected
    assert meal_object is not None
    print(meal_object)
    assert meal_object.date == "2022-02-28"
    assert meal_object.timestamp == 1646046000
    assert meal_object.meal_type == "Pranzo"
    assert meal_object.participants == "Entrambi"
    assert meal_object.meal == "DictMeal"
    assert meal_object.notes == "Notes"
    assert meal_object.start_week
    assert meal_object.week_number is None
    assert meal_object.meal_id == "DICTMEAL"
    assert meal_object.dessert == "Test dessert"
    assert len(meal_object.__dict__) == 10
