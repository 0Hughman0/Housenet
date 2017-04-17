import datetime
import itertools
import random
import shutil
from os import path

# Python version < 3.5
try:
    import stdconfigparser as configparser
except ImportError:
    import configparser

from ez_grid import Grid
import click

from housenet.database import db
from housenet.database.models import Chore, Housemate, Cashflow
from housenet.utilities import path_for


CONFIG_FOLDER = path.dirname(path.realpath(__file__))


def to_date(string):
    return datetime.datetime.strptime(string, "%d/%m/%Y").date()


def load_housemates(config):
    names = config["Housemates"].getlist("names")
    for name in names:
        db.session.add(Housemate(name=name))
    return names


def load_muns(config, housemates):
    if not config.getboolean("Muns", "from_csv"):
        grid = Grid(housemates, housemates, default=0)
    else:
        with open(path.join(CONFIG_FOLDER, "muns.csv")) as f:
            grid = Grid.from_csv_file(f)
    for cell in grid.cells:
        if cell.col != cell.row:
            db.session.add(Cashflow(to_name=cell.row, from_name=cell.col, _amount=float(cell.value)))
    return grid


def load_chores(config, housemates):
    if not config.getboolean("Chores", "from_csv"):
        duration = config.gettimedelta("Chores", "duration")
        grid = generate_chores(housemates,
                               config["Chores"].getlist("names"),
                               config.getdate("Chores", "start_date"),
                               config.getdate("Chores", "end_date"),
                               duration)
    else:
        with open(path.join(CONFIG_FOLDER, "chores.csv")) as f:
            grid = Grid.from_csv_file(f)
            duration = to_date(grid.col_hds[1]) - to_date(grid.col_hds[0])
    for chore in grid.cells:
        start_date = to_date(chore.col) if isinstance(chore.col, str) else chore.col
        db.session.add(Chore(title=chore.value,
                             who_id=chore.row,
                             start_date=start_date,
                             end_date=start_date + duration))
    return grid


def date_range(from_, to, step):
    current = from_
    while current <= to:
        yield current
        current += step


def generate_chores(housemates, chore_names, start_date, end_date, duration, randomly=False):
    dates = (day for day in date_range(start_date, end_date, duration))
    grid = Grid(housemates, dates)
    chore_cycle = itertools.cycle(chore_names)
    for day in grid.col_hds:
        if randomly:
            next_chores = list(chore_names)
            random.shuffle(next_chores)
            chore_cycle = iter(next_chores)
        for housemate in grid.row_hds:
            grid[housemate][day] = next(chore_cycle)
        if len(chore_names) % len(housemates) == 0:
            next(chore_cycle)
    return grid


def move_profile_pics(names):
    for name in names:
        filename = "{}.jpeg".format(name)
        try:
            shutil.copyfile(path.join(CONFIG_FOLDER, "profile_pics", filename), path_for("static", filename))
        except FileNotFoundError:
            click.echo(("Couldn't find a file named {} in profile_pics folder."
                        " To fix: add one, and run reloadconfig --name=pics").format(filename))


def get_config():
    config = configparser.ConfigParser(converters={"date": lambda x: to_date(x),
                                                   "timedelta": lambda x: datetime.timedelta(days=int(x)),
                                                   "list": lambda x: x.split(", ")})
    config.read(path.join(CONFIG_FOLDER, "config.ini"))
    return config


def register_config_tools(app):

    @app.cli.command(with_appcontext=False, help="initialise config, first time run")
    def init():
        db.create_all()
        config = get_config()
        click.echo("Config Loaded")
        click.echo("Loading housemates")
        names = load_housemates(config)
        db.session.commit()
        click.echo("Success")
        click.echo("Loading Muns")
        load_muns(config, names)
        db.session.commit()
        click.echo("Success")
        click.echo("Loading Chores")
        load_chores(config, names)
        db.session.commit()
        click.echo("Success")
        click.echo("Moving profile pics to static folder")
        move_profile_pics(names)
        click.echo("Success")
        click.echo("Initialisation complete! Use 'flask run --host="0.0.0.0" --with-threads' to start the server")

    @app.cli.command(help="reload db from .csv files: chores, muns, pics or all")
    @click.option("--name", "-n")
    def reloadconfig(name):
        if name not in ("chores", "muns", "pics", "all"):
            click.Abort("config name not recognised: {}".format(name))
        config = get_config()
        names = config.getlist("Housemates", "names")
        if name in ("pics", "all"):
            move_profile_pics(names)
            if name != "all":
                click.Abort("Done!")
        click.echo("removing old data")
        if name in ("chores", "all"):
            Chore.query.delete()
        if name in ("muns", "all"):
            Cashflow.query.delete()
        db.session.commit()
        click.echo("Success")
        click.echo("Loading new data")
        click.echo(name)
        if name in ("chores", "all"):
            load_chores(config, names)
        if name in ("muns", "all"):
            load_muns(config, names)
        db.session.commit()
        click.echo("Done!")
