import pytest
import sqlite3
import mysql.connector as mysql_conn

from time import sleep

from tests.utils import get_environ

@pytest.fixture
def database(tmp_path, monkeypatch):
    db_type = get_environ("db_type", default="sqlite")

    if db_type=="sqlite":
        # one fresh db per test, in a pytest-managed temporary folder (removed automatically)
        path = str(tmp_path / "meals.db")
        # the app under test (acceptance) reads its db path from env: point it to the same db,
        # never to its default ./db/meals.db. monkeypatch restores env after each test
        monkeypatch.setenv("meal_db_path", path)

        db = sqlite3.connect(path)
        yield (db, "sqlite")
        db.close()

    elif db_type=="mysql":
        db_max_retry = int(get_environ("db_max_retry", default = 10))
        db_sleep_time = int(get_environ("db_sleep_time", default = 10))
        for i in range(0, db_max_retry):
            try:
                db = mysql_conn.connect(host=get_environ("db_host"),
                                                 database=get_environ("db_name"),
                                                 user=get_environ("db_user"),
                                                 password=get_environ("db_pass"))
                break
            except Exception as e:
                print ("Cannot connect to mysql", e)
                sleep(db_sleep_time)
        else:
            raise Exception("Couldn't connect to mysql")

        yield (db, "mysql")
        db.close()

    else:
        raise Exception("Unknown db_type!")
