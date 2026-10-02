from datetime import date
import os
import shutil
import pytest
import sqlite3
import mysql.connector as mysql_conn

from time import sleep
from datetime import datetime

from domain.meal import Meal

def get_environ(key, default=None):
    try:
        return os.environ[key]
    except:
        return default

def clean_db(db, table_name):
    c = db.cursor()
    c.execute("DROP TABLE IF EXISTS %s" % (table_name))
    db.commit()

def mysql_query_adapter(db_type, query):
    if db_type=="mysql":
        return query.replace("?", "%s")
    return query

def get_meal(date_meal=datetime(2022,1,1), meal_type = "Pranzo", participants = "Entrambi", meal = "Test meal", notes = "Nota", start_week = False, dessert=None):
    return Meal(date_meal, meal_type, participants, meal, notes, start_week, dessert = dessert)

@pytest.fixture
def database():
    db_type = get_environ("db_type", default="sqlite")

    if db_type=="sqlite":
        path = get_environ("meal_db_path", default="/tmp/pytest.db")
        # the app under test (acceptance) must use the same db, not its default ./db/meals.db
        os.environ["meal_db_path"] = path
        if os.path.exists(path):
            os.remove(path)

        return (sqlite3.connect(path), "sqlite")

    elif db_type=="mysql":
        db_max_retry = int(get_environ("db_max_retry", default = 10))
        db_sleep_time = int(get_environ("db_sleep_time", default = 10))
        for i in range(0, db_max_retry):
            try:
                db = mysql_conn.connect(host=get_environ("db_host"),
                                                 database=get_environ("db_name"),
                                                 user=get_environ("db_user"),
                                                 password=get_environ("db_pass"))
                return (db, "mysql")
            except Exception as e:
                print ("Cannot connect to mysql", e)
                sleep(db_sleep_time)

        os.environ["db_max_retry"]=0

        raise Exception("Couldn't connect to mysql")        

    else:
        raise Exception("Unknown db_type!")