#! /home/serverman/CromDotCom/env/bin/python
from flask import Blueprint

from .database.models import Housemate

blueprints = []

base_app = Blueprint("base_app",
                     __name__)
blueprints.append(base_app)


def add_global_context_processors(app):
    @app.context_processor
    def inject_vars():
        values = {}
        housemate_names = Housemate.names()
        values['names'] = housemate_names
        return values

from .views import views
