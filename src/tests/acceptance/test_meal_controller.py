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

@pytest.mark.acceptance
def test_delete_meal_with_empty_meal_field(client, database):
    # given: a meal with an empty meal field (only notes) stored
    meal = {
        "date": "2022-02-28",
        "start_week": "True",
        "meal_type": "Cena",
        "participants": "Luca",
        "meal": "",
        "notes": "Solo appunti",
        "dessert": None
    }
    response = client.post("/meal/", json=meal)
    assert response.status_code == 201

    # when: deleting the meal from the UI
    response = client.delete("/meal/single", json={
        "date": "2022-02-28",
        "meal_type": "Cena",
        "participants": "Luca"
    })

    # then: the meal is deleted
    assert response.status_code == 204

    # then: no meal remains in the db
    (db, db_type) = database
    c = db.cursor()
    c.execute("SELECT * FROM meals")
    assert len(c.fetchall()) == 0

@pytest.mark.acceptance
def test_delete_meal_stored_in_different_timezone(client, database):
    # given: the service is up (this creates the tables)
    client.get("/meal/counts")

    # given: a meal stored with a timestamp computed in a different timezone
    # (e.g. the production container runs in UTC, while local runs are UTC+2)
    (db, db_type) = database
    c = db.cursor()
    c.execute('''INSERT INTO meals (date, timestamp, start_week, type, participants, meal, meal_id, dessert, notes)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              ("2022-02-28", 1646046000 + 2 * 60 * 60, 0, "Pranzo", "Entrambi", "", "", None, "Solo appunti"))
    db.commit()

    # when: deleting it from the UI (date, meal_type and participants are sent)
    response = client.delete("/meal/single", json={
        "date": "2022-02-28",
        "meal_type": "Pranzo",
        "participants": "Entrambi"
    })

    # then: the meal is deleted
    assert response.status_code == 204

    c = db.cursor()
    c.execute("SELECT * FROM meals")
    assert len(c.fetchall()) == 0

@pytest.mark.acceptance
def test_delete_meal_not_found(client):
    # when: deleting a meal that does not exist
    response = client.delete("/meal/single", json={
        "date": "2022-02-28",
        "meal_type": "Pranzo",
        "participants": "Luca"
    })

    # then: a 404 is returned
    assert response.status_code == 404
def insert_week_start(client, date_meal):
    response = client.post("/meal/", json={
        "date": date_meal,
        "start_week": "True",
        "meal_type": "Pranzo",
        "participants": "Entrambi",
        "meal": "Start " + date_meal,
        "notes": ""
    })
    assert response.status_code == 201

@pytest.mark.acceptance
def test_week_by_date(client, database):
    # given: the service is up (this creates the tables)
    client.get("/meal/counts")

    # given: two tracked weeks
    (db, db_type) = database
    c = db.cursor()
    c.execute('''INSERT INTO meals (date, timestamp, start_week, type, participants, meal, meal_id, dessert, notes)
        VALUES ('2022-02-21', 1645441200, 1, 'Pranzo', 'Entrambi', 'First', 'FIRST', NULL, ''),
               ('2022-02-28', 1646046000, 2, 'Pranzo', 'Entrambi', 'Second', 'SECOND', NULL, '')''')
    db.commit()

    # when: requesting the week containing a date
    response = client.get("/meal/week?date=2022-02-23")

    # then: that week is returned
    assert response.status_code == 200
    message = loads(response.data)
    assert message["week_number"] == 1
    assert message["meals"][0]["meal"] == "First"

    # when: requesting the start day of the last week
    response = client.get("/meal/week?date=2022-02-28")

    # then: the last week is returned
    assert response.status_code == 200
    assert loads(response.data)["week_number"] == 2

@pytest.mark.acceptance
@pytest.mark.parametrize("query", ["date=2022-02-20", "date=2022-03-14"])
def test_week_by_date_out_of_period(client, query):
    # given: a tracked week
    insert_week_start(client, "2022-02-28")

    # when: requesting a date before the first week or too far after the last one
    response = client.get("/meal/week?" + query)

    # then: 404 with a user message
    assert response.status_code == 404
    assert loads(response.data)["error_message"] == "Data fuori periodo tracciato"

@pytest.mark.acceptance
@pytest.mark.parametrize("query", ["date=2022-02-28&week-number=1", "date=2022-13-01", "date=yesterday", "week-number=abc"])
def test_week_bad_request(client, query):
    # when: requesting a week with invalid parameters
    response = client.get("/meal/week?" + query)

    # then: 400
    assert response.status_code == 400
    assert "error_message" in loads(response.data)
