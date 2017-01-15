import datetime
import os
from collections import namedtuple

Cell = namedtuple("Cell", ["row", "col", "value"])

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))


def path_for(*relpath):
    return os.path.join(PROJECT_DIR, *relpath)


def timestamp(filename):
    return filename.format(datetime.datetime.now().strftime("%Y-%m-%d %H%M%S"))