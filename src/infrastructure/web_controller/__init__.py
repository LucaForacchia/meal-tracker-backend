from flask_restx import Api
from .welcome_controller import api as welcome_api
from .meals_controller import api as meals_api


api = Api(title='Meal Tracker',
            version='0.2.1',
            description='This service stores the meals for the Foracchia-Manini family',
            default_mediatype='application/json',
            doc="/doc"
            )

api.add_namespace(welcome_api, path='/welcome')
api.add_namespace(meals_api, path='/meal')
