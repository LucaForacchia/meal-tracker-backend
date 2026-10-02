import pytest
from json import loads


@pytest.mark.acceptance
def test_welcome(client):
    # given: the server is running

    # when: calling the server welcome
    response = client.get("/welcome/")

    # then: it returns 200
    # then: the returned welcome message is as expected
    assert response.status_code == 200
    message = loads(response.data)
    assert message["name"] == "Meal Tracker"
    assert message["description"] == "This service stores the meals for the Foracchia-Manini family"
    assert message["version"] == "0.3.0"
    assert message["status"] == "Towards a production-ready version, but still in development"