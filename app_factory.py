from flask import Flask
from flask_migrate import Migrate
from housenet.config import DefaultConfig, DebugConfig


config_dict = {}

config_dict["DEFAULT"] = DefaultConfig
config_dict["DEBUG"] = DebugConfig


def create_app(config="DEFAULT"):
    app = Flask(__name__,
                static_folder="housenet/static",
                template_folder="housenet/templates")

    # Init config
    app.config.from_object(config_dict[config])

    from housenet.database import db
    db.app = app
    db.init_app(app)

    # For use with flask_migrate commands
    migrate = Migrate(app, db, directory=r"housenet/database/migrations")

    from housenet import blueprints
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    from config.tools import register_config_tools
    register_config_tools(app)

    from housenet.cli import register_commands
    register_commands(app, db)

    from housenet import add_global_context_processors
    add_global_context_processors(app)

    return app, db
