from flask import Blueprint

from .database.database import Housemate


base_app = Blueprint("base_app",
                     __name__)

# Kinda pointless, but all contents will be registered in app_factory.py
blueprints = []
blueprints.append(base_app)


def add_global_context_processors(app):
    @app.context_processor
    def inject_vars():
        values = {}
        housemate_names = Housemate.names()
        values['names'] = housemate_names
        return values
