import shutil

import click

from .utilities import timestamp, path_for


def register_commands(app, db=None):

    @app.cli.command(help="create backup of db")
    def backupdb():
        click.echo("saving database")
        shutil.copy(path_for("database", "database.db"), path_for("backups", timestamp("{} - database.db")))
        click.echo("Success!")
