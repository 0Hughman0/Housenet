from flask import Blueprint
from ..app import blueprints

base_app = Blueprint("base_app",
                     __name__,
                     template_folder="templates",
                     static_folder="static",
                     static_url_path="/base_app")
blueprints.append(base_app)