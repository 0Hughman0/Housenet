#! /home/serverman/CromDotCom/env/bin/python

from flask import Blueprint

from .utilities import path_for
from .database.models import Housemate


blueprints = []

base_app = Blueprint("base_app",
                     __name__,
                     template_folder="templates",
                     static_folder="static",
                     static_url_path="/content")

blueprints.append(base_app)


def add_global_context_processors(app):
    @app.context_processor
    def inject_vars():
        values = {}
        housemate_names = Housemate.names()
        values['names'] = housemate_names
        return values

