import shutil

from flask_sqlalchemy import SQLAlchemy

from ..utilities import path_for, timestamp


db = SQLAlchemy()


def save_database():
    shutil.copy(path_for("database", "database.db"), path_for("backups", timestamp("{} - database.db")))