import pytest
from json import loads
from datetime import datetime

from .fixtures import client, app, database

@pytest.mark.acceptance
def test_meal_insertion(client):
    # given: a valid meal form
    meal = {
        "date": "2022-02-28",
        "start_week": "True",
        "meal_type": "Pranzo",
        "participants": "Entrambi",
        "meal": "DictMeal",
        "notes": "Notes",
        "dessert": "Test dessert"
    }

    # when: requesting to insert the meal
    response = client.post("/meal/", json=meal)

    # then: it returns 201
    # then: the meal is correctly stored
    assert response.status_code == 201
    assert loads(response.data) == "Meal stored"

    # when: requiring last week meals
    response = client.get("/meal/week")

    # then: the meal is correctly represented:
    assert response.status_code == 200
    message = loads(response.data)
    print(message)
    assert message["total"] == 1
    assert message["week_number"] == 0
    meal_view = message["meals"][0]
    assert meal_view["meal"] == "DictMeal"
    assert meal_view["dessert"] == "Test dessert"

    # when: requiring the count of meals
    response = client.get("/meal/counts")

    #then: only the meal is counted, not the dessert
    assert response.status_code == 200
    meal_count = loads(response.data)
    print(meal_count)
    assert len(meal_count) == 1
    assert meal_count[0][0] == 1
    assert meal_count[0][1] == "DictMeal"

@pytest.mark.acceptance
def test_meal_counts_who(client):
    # given: a valid meal form with a specific participant
    meal = {
        "date": "2022-02-28",
        "start_week": "True",
        "meal_type": "Pranzo",
        "participants": "Luca",
        "meal": "DictMeal",
        "notes": "Notes",
        "dessert": "Test dessert"
    }
    client.post("/meal/", json=meal)

    # when: requiring the count filtered by who
    response = client.get("/meal/counts?who=L")

    # then: only the meals for Luca are counted
    assert response.status_code == 200
    meal_count = loads(response.data)
    assert meal_count == [[1, "DictMeal"]]

    # when: requiring the count with an invalid who
    response = client.get("/meal/counts?who=OR%201%3D1--")

    # then: a 400 is returned
    assert response.status_code == 400