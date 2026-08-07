from flask_restx import fields

class VersionModel:
    def __init__(self, api):
        self.software_version_view = api.model("software_version",
        {
        "name": fields.String(required = True, description = "service name"),
        "description": fields.String(required = False, description = "short description of the service"),
        "version": fields.String(required = True, description= "version used"),
        "status": fields.String(required = False, description = "status of the service development")
        } )

        self.software_status = {
            "name": "Meal Tracker",
            "description": "This service stores the meals for the Foracchia-Manini family",
            "version": "0.2.2",
            "status": "Towards a production-ready version, but still in development"
        }

    def represent_software_status(self):
        return {
            "name": self.software_status["name"],
            "description": self.software_status["description"],
            "version": self.software_status["version"],
            "status": self.software_status["status"]
        }