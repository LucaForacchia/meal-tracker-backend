import pytest
import os
import logging
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from tests.utils import clean_db

from infrastructure.web_controller import api

@pytest.fixture
def app(database):
    (db, db_type) = database

    for table in ["meals", "meal_counter", "aka"]:
        clean_db(db, table)

    logging.getLogger().setLevel(logging.DEBUG)

    app = Flask(__name__)

    app.wsgi_app = ProxyFix(app.wsgi_app)

    api.init_app(app)
    return app

@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client