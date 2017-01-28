from .database.models import Housemate

blueprints = []


def add_global_context_processors(app):
    @app.context_processor
    def inject_vars():
        values = {}
        housemate_names = Housemate.names()
        values['names'] = housemate_names
        return values
