from json import loads, dumps
import sqlite3
from mysql.connector.errors import IntegrityError as MySqlIntegrityError
import logging
from uuid import uuid4
from datetime import datetime
from collections import Counter

from domain.meal import Meal
from domain.meal_occurrences import MealOccurrences

class MealRepository:
    def __init__(self, db, db_type="sqlite"):
        self.db = db
        self.db_type = db_type

        self.__create_tables__()

    def __mysql_query_adapter__(self, query):
        if self.db_type=="mysql":
            return query.replace("?", "%s")
        return query

    def __create_tables__ (self):
        c = self.db.cursor()

        c.execute(self.__mysql_query_adapter__('''
            CREATE TABLE IF NOT EXISTS meals (
                date VARCHAR(255) NOT NULL,
                timestamp INT NOT NULL,
                start_week INT NOT NULL,
                type VARCHAR(50) NOT NULL,
                participants VARCHAR(50) NOT NULL,
                meal TEXT,
                meal_id TEXT NOT NULL,
                dessert TEXT,
                notes TEXT,
                PRIMARY KEY(timestamp, participants)
            )
        '''))

        c.execute(self.__mysql_query_adapter__('''
            CREATE TABLE IF NOT EXISTS meal_counter (
                meal_id VARCHAR(50) NOT NULL,
                meal TEXT NOT NULL,
                count_total INT NOT NULL DEFAULT 0,
                both INT NOT NULL DEFAULT 0,
                L INT NOT NULL DEFAULT 0,
                G INT NOT NULL DEFAULT 0,
                PRIMARY KEY(meal_id)
            )
        '''))

        self.db.commit()

    def __del__ (self):
        try:
            self.db.close()
        except Exception as err:
            print("error while closing the connection:", err)
            pass

    def __serialize_row__(self, row):
        return Meal(datetime.fromisoformat(row[0]), row[1], row[2], row[3], row[4], start_week = bool(row[5]), meal_id=row[6], dessert=row[7], timestamp=row[8])
        
    def update_meal_counter(self, meal, change = 1):
        c = self.db.cursor()

        plus_both = change if meal.participants == "Entrambi" else 0 
        plus_l = change if meal.participants == "Luca" else 0
        plus_g = change if meal.participants == "Gioi" else 0

        c.execute(self.__mysql_query_adapter__('''
            SELECT 
                count_total,
                both,
                L,
                G
            FROM meal_counter where meal_id = ?
            LIMIT 1
        '''), [meal.meal_id])

        meal_selected = c.fetchone()

        if meal_selected is None:
            if change == 1:
                c.execute(self.__mysql_query_adapter__('''
                    INSERT INTO meal_counter (
                        meal_id,
                        meal,
                        count_total,
                        both,
                        L,
                        G
                        ) VALUES (?, ?, ?, ?, ?, ?)
                        '''), (meal.meal_id, meal.meal, 1, plus_both, plus_l, plus_g))
            else:
                raise ValueError(f"Unable to update values of {change} for a not tracked meal")
        else:
            c.execute(self.__mysql_query_adapter__('''
                UPDATE meal_counter
                SET
                    count_total = ?,
                    both = ?,
                    L = ?,
                    G = ?
                WHERE meal_id = ?
            '''), (meal_selected[0] + change, meal_selected[1] + plus_both, meal_selected[2] + plus_l, meal_selected[3] + plus_g, meal.meal_id))

        self.db.commit()

    def get_last_week_timestamp(self):
        c = self.db.cursor()

        c.execute('''
            SELECT
                timestamp, start_week
            FROM meals
            WHERE start_week > 1
            ORDER BY timestamp desc
            LIMIT 1
            ''')

        row = c.fetchone()

        if row is None:
            return 0, (0, 1672000000)

        return row[1], (row[0], row[0] + 1209600)

    def __get_week_timestamp__(self, week_number):
        c = self.db.cursor()

        c.execute(self.__mysql_query_adapter__('''
            SELECT
                timestamp
            FROM meals
            WHERE start_week < ? AND start_week >= ?
            ORDER BY timestamp desc
            '''), (week_number + 2, week_number))

        rows = c.fetchall()
        if len(rows) > 2:
            raise Exception("Too many rows selected!!!")
        
        elif len(rows) == 1:
            return week_number, (rows[0][0], rows[0][0] + 30 * 24 * 3600)
        return week_number, (rows[1][0], rows[0][0])

    def __get_select_query__(self):
        return '''
            SELECT 
                date,
                type,
                participants,
                meal,
                notes,
                start_week,
                meal_id,
                dessert,
                timestamp
            FROM meals
            '''

    def insert_meal(self, meal):
        c = self.db.cursor()

        logging.debug("Inserting meal %s" % (meal.__dict__))
        try:
            c.execute(self.__mysql_query_adapter__('''
                    INSERT INTO meals (
                        date,
                        timestamp,
                        start_week,
                        type,
                        participants,
                        meal,
                        meal_id,
                        notes,
                        dessert
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    '''), (meal.date, meal.timestamp, meal.week_number if meal.start_week else 0, meal.meal_type, 
                        meal.participants, meal.meal, meal.meal_id, meal.notes, meal.dessert))

            self.db.commit()

        except (sqlite3.IntegrityError, MySqlIntegrityError):
            raise DuplicateMeal("A meal with same date type and participants already exists")
    
    def delete_meal(self, timestamp, participants):
        c = self.db.cursor()

        logging.debug("Checking meal existence")
        try:
            c.execute(self.__mysql_query_adapter__('''
            SELECT
                COUNT(*)
            FROM meals
            WHERE timestamp = ?
            AND participants = ?
            '''), (timestamp, participants))

            n_meals = c.fetchall()[0][0]

            logging.debug("N_meals: %s", n_meals)

            assert n_meals == 1
        
        except AssertionError:
            raise DuplicateMeal(f"Number of meals with given parameters is {n_meals}, different from 1!")
        
        c.execute(self.__mysql_query_adapter__('''
            DELETE FROM meals
            WHERE timestamp = ?
            AND participants = ?
            '''), (timestamp, participants))

        self.db.commit()

    def get_meal(self, date, meal_type, participants):
        c = self.db.cursor()
        c.execute(self.__mysql_query_adapter__(self.__get_select_query__() + '''
                WHERE date = ?
                AND type = ?
                AND participants = ?
            '''), (date, meal_type, participants))

        meals = [self.__serialize_row__(row) for row in c.fetchall()]
        if len(meals) == 0:
            raise MealNotFound(f"No meal found for date {date}, meal type {meal_type}, participants {participants}")
        return meals[0]

    def get_weekly_meals(self, week_number = None):
        c = self.db.cursor()

        week_number, timestamps = self.get_last_week_timestamp() if week_number is None else self.__get_week_timestamp__(week_number)
        
        c.execute(self.__mysql_query_adapter__(self.__get_select_query__() + '''
            WHERE timestamp >= ? AND timestamp < ?
            ORDER BY timestamp ASC
        '''), (timestamps[0], timestamps[1]))

        return week_number, [self.__serialize_row__(row) for row in c.fetchall()]                

    def get_meals_count(self, who = None):
        c = self.db.cursor()

        allowed_count_fields = ["count_total", "both", "L", "G"]
        count_field = "count_total" if who is None else who
        if count_field not in allowed_count_fields:
            raise ValueError(f"Invalid value for who parameter: {who}")

        c.execute(self.__mysql_query_adapter__(f'''
            SELECT meal_id, meal, {count_field} 
            FROM meal_counter
            ORDER BY {count_field} DESC
        '''
        ))

        return {row[0]: {"name": row[1], "count": row[2]} for row in c.fetchall() if row[1] != ""}

    def get_meal_occurrences(self, meal_id):
        c = self.db.cursor()

        c.execute(self.__mysql_query_adapter__('''
            SELECT 
            participants 
            FROM MEALS WHERE meal_id = ?
        '''), [meal_id])

        participants_list = [x[0] for x in c.fetchall()]

        counts = Counter(participants_list)
        
        return MealOccurrences(meal_id=meal_id, total = len(participants_list), both = counts["Entrambi"],
            l = counts["Luca"], g = counts["Gioi"])
    
    def get_meals_names(self, filter = None):
        c = self.db.cursor()

        c.execute(self.__mysql_query_adapter__('''
            SELECT meal 
            FROM meal_counter
        '''))

        return [x[0] for x in c.fetchall()]

class DuplicateMeal(Exception):
    pass

class MealNotFound(KeyError):
    pass
