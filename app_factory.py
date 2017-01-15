from flask import Flask


def create_app(config="default"):
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = r"sqlite:///housenet/database/database.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    from housenet.database import db
    db.app = app
    db.init_app(app)

    from housenet.views import views

    from housenet import blueprints
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    from housenet.cli import register_commands
    register_commands(app, db)

    from housenet import add_global_context_processors
    add_global_context_processors(app)

    print(app.url_map)
    return app

