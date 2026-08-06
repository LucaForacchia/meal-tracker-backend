import logging
from flask import request
from flask_restx import Namespace, Resource, fields
from datetime import datetime, timezone

from domain.meal import Meal

from .configuration import get_meal_service
from .views.error_view import ErrorModel
from .views.meals_view import MealModel

api = Namespace("insertion",
                description="data reception service")

error_model = ErrorModel(api)
meal_model = MealModel(api)

def validate_input_datetime(arg_name, req_args, default = None):
    if arg_name in req_args:
        try:
            logging.info("Input parameter %s: %s" % (arg_name, req_args[arg_name]))
            timestamp_start = int(datetime.timestamp(datetime.fromisoformat(req_args[arg_name])))
        except ValueError as err:
            raise ValueError("Error in parameter %s: %s" % (arg_name, str(err)))
    else:
        if default is None:
            raise ValueError("Missing required parameter: " + arg_name)
        else:
            timestamp_start = default
    
    return timestamp_start

def validate_meal_form(form):
    # Check the meal form is well-formed, all fields are legal
    if form is None:
        raise InvalidFormError("request sent without meal_form")

    try:
        # Meal should become a domain object
        form["date"] = datetime.fromisoformat(form["date"])
        form["start_week"] = bool(form["start_week"])
    except ValueError as err:
        raise InvalidFormError("Invalid value in input form, %s" % str(err))

    if form["meal_type"] not in ["Pranzo", "Cena"]:
        raise InvalidFormError("Invalid value for meal_type field. Allowed values are Pranzo, Cena")
    
    return Meal(**form)

def validate_replacement_form(form):
    # Check the meal form is well-formed, all fields are legal
    if form is None:
        raise InvalidFormError("request sent without form!")

    try:
        return form["meal_id"], form["replacement"]
    except ValueError as err:
        raise InvalidFormError("Invalid value in input form, %s" % str(err))

def validate_select_form(form):
    if not(set(form.keys()) ==  set(["date", "meal_type", "participants"])):
        raise InvalidFormError("Invalid input form. Expected date, meal_type, participants")
    try:
        form["date"] = datetime.fromisoformat(form["date"])
    except ValueError as err:
        raise InvalidFormError("Invalid value in input form, %s" % str(err))

    if form["meal_type"] not in ["Pranzo", "Cena"]:
        raise InvalidFormError("Invalid value for meal_type field. Allowed values are Pranzo, Cena")

    if form["participants"] not in ["Luca", "Gioi", "Entrambi"]:
        raise InvalidFormError("Invalid value for participants field. Allowed values are Luca, Gioi, Entrambi")

    return form

@api.route('/')
class SingleMeal(Resource):
    @api.doc('receive a session notification, compute chunks and store them into table')
    @api.response(201, 'Meal inserted')
    @api.response(400, 'Bad Request', model=error_model.error_view)
    @api.expect(meal_model.meal_form)
    def post(self):
        logging.info("meal received")        
        form = request.get_json()

        try:
            meal = validate_meal_form(form)
        except (KeyError, InvalidFormError) as err:
            return (error_model.represent_error(str(err)), 400)

        logging.info("Meal received, store")
        
        get_meal_service().store_meal(meal)

        return ("Meal stored", 201)

@api.route('/single')
class SingleMeal(Resource):
    @api.doc('delete a meal')
    @api.response(204, 'Meal Deleted')
    @api.response(400, 'Bad Request', model=error_model.error_view)
    @api.response(404, 'Not Found', model=error_model.error_view)
    @api.expect()
    def delete(self):
        logging.info("Request to delete a meal")
        try:
            form = validate_select_form(request.get_json())
        except InvalidFormError as err:
            return (error_model.represent_error(str(err)), 400)

        get_meal_service().delete_meal(Meal(
            form["date"], 
            form["meal_type"], 
            form["participants"],
            "ToDelete",
            ""
        ))

        return "", 204

@api.route('/week')
class WeeklyMealList(Resource):
    @api.doc('return weekly meal list')
    @api.response(200, 'Meal', model=meal_model.weekly_meals)
    @api.response(400, 'Bad Request', model=error_model.error_view)
    @api.response(404, 'Not Found', model=error_model.error_view)
    def get(self):
        logging.info("Requested week meals")
        week_number = int(request.args["week-number"]) if "week-number" in request.args else None

        week_number, meals_list = get_meal_service().get_weekly_meals(week_number)
        return meal_model.represent_meal_week(week_number, meals_list)

@api.route('/counts')
class MealsCount(Resource):
    @api.doc('return count of meals', params={'who': 'filter count by person: count_total, both, L, G'})
    @api.response(200, 'Meal', model=meal_model.meal_counts)
    @api.response(400, 'Bad Request', model=error_model.error_view)
    def get(self):
        who = request.args.get('who') 
        logging.info("returning meals count for %s" % (str(who)))
        try:
            meal_counts = get_meal_service().get_meals_count(who)
        except ValueError as err:
            return (error_model.represent_error(str(err)), 400)
        return meal_model.represent_meal_count(meal_counts)

@api.route('/names')
class MealsNames(Resource):
    @api.doc('return meals list')
    @api.response(200, 'Meal List', model=meal_model.meal_list)
    @api.response(400, 'Bad Request', model=error_model.error_view)
    def get(self):
        logging.info("returning meal list")
        meals_list = get_meal_service().get_meal_list()
        return meal_model.represent_meal_list(meals_list)

@api.route('/replacement')
class ReplaceMealId(Resource):
    @api.doc('replace a meal id with another of choice')
    @api.response(201, 'Replacement stored')
    @api.response(400, 'Bad Request', model=error_model.error_view)
    # TODO: document
    def post(self):
        logging.info("Replacement received")
        form = request.get_json()

        try:
            meal_id, replacement = validate_replacement_form(form)
        except (KeyError, InvalidFormError) as err:
            return (error_model.represent_error(str(err)), 400)

        logging.info("Insert replacement %s for id %s" % (replacement, meal_id))
        
        get_meal_service().insert_aka(meal_id, replacement)

        return ("Meal stored", 201)

    @api.doc('get replacements')
    @api.response(200, 'Replacements') # TODO: add model
    # TODO: document
    def get(self):
        logging.info("Required replacement table")
        
        replacement = get_meal_service().get_replacements()

        return (replacement, 201)
    
class InvalidFormError(Exception):
    pass