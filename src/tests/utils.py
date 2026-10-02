from datetime import date
import os

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
