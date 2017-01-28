import click

from .database.models import (Housemate,
                              Chore,
                              Cashflow,
                              save_database,
                              export_config,
                              load_config,
                              obj_map)


def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()

def register_commands(app, db):

    @app.cli.command(with_appcontext=False, help="run app locally in debug mode")
    def debug():
        db.create_all()
        app.run(debug=True)

    @app.cli.command(help="create backup of db")
    def savedb():
        click.echo("saving database")
        save_database()
        click.echo("Success!")

    @app.cli.command(help="export config to .csv files")
    @click.option("--name", "-n")
    def exportconfig(name):
        click.echo("exporting database tables")
        export_config(name)
        click.echo("Success!")

    @app.cli.command(help="reload db from .csv files")
    @click.option("--name", "-n")
    def reloadconfig(name):
        click.echo("removing old data")
        obj_map[name].model.query.delete()
        click.echo("loading new data")
        load_config(name)
        db.session.commit()
        click.echo("Success!")

    @app.cli.command(help="wipe and then reload the db from config")
    def reloaddb():
        for name in ("housemates", "muns", "chores"):
            click.echo("removing old {} data".format(name))
            obj_map[name].model.query.delete()
            click.echo("success")
            click.echo("loading new data")
            load_config(name)
            click.echo("success")
        db.session.commit()
        click.echo("Done!")