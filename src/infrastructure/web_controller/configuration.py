from flask import g
import os

from infrastructure.persistence.meal_repository import MealRepository
from infrastructure.services.meal_service import MealService

import mysql.connector as mysql_conn
import sqlite3


def load_config():
    config = {}

    config["db_type"] = os.environ.get("db_type")
    if config["db_type"] is None:
        config["db_type"] = "sqlite"

    config["meal_db_path"] = os.environ.get("meal_db_path")
    if config["meal_db_path"] is None:
        config["meal_db_path"] = "./db/meals.db"
    
    config["db_host"] = os.environ.get("db_host")
    config["db_name"] = os.environ.get("db_name")
    config["db_user"] = os.environ.get("db_user")
    config["db_pass"] = os.environ.get("db_pass")

    return config

def get_config():
    config = getattr(g, "_config", None)

    if config is None:

        config = load_config()

        g._config = config

    return config


def db_connect(config, db_type="sqlite", path="/tmp/database.sqlite"):
    if db_type=="mysql":
        db = mysql_conn.connect(host=config["db_host"],
                                         database=config["db_name"],
                                         user=config["db_user"],
                                         password=config["db_pass"])

    elif db_type=="sqlite":
        db_dir = os.path.dirname(path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        db = sqlite3.connect(path)

    else:
        raise ValueError("Unknown db_type %s, unable to connect to db" % (db_type))

    return db

# def get_meal_repository():
#     repository = getattr(g, "_meal_repository", None)

#     if repository is None:
#         config = get_config()
#         db_type = config["db_type"]
#         db = db_connect(config, db_type=db_type, path=config["meal_db_path"])
#         repository = MealRepository(db, db_type)
#         g._meal_repository = repository

#     return repository

def get_meal_service():
    service = getattr(g, "_meal_service", None)

    if service is None:
        config = get_config()

        print("Creating meal service with config", config)
        
        db = db_connect(config, config["db_type"], path=config["meal_db_path"])

        service = MealService(db, config)

        g._meal_service = service
    
    return service