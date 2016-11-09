import csv
import datetime
import os
from collections import OrderedDict, namedtuple, defaultdict
import itertools

Cell = namedtuple("Cell", ["row", "col", "value"])

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))


def path_for(*relpath):
    return os.path.join(PROJECT_DIR, *relpath)


def timestamp(filename):
    return filename.format(datetime.datetime.now().strftime("%Y-%m-%d %H%M%S"))


class ConfigGrid:

    def __init__(self):
        self.data = OrderedDict()
        self.path = ""
        self.col_headings = []
        self.row_headings = []

    def __repr__(self):
        header_row = "\t" + "\t".join(self.row_headings)
        data_rows = []
        for row_heading, row_cells in self.rows:
            data_rows.append(row_heading + "\t" + "\t".join((cell.value for cell in row_cells)))
        return "\n".join([header_row] + data_rows)

    def load_from_path(self, path):
        self.path = path
        with open(path) as raw_table:
            raw_table.seek(0)
            reader_obj = csv.reader(raw_table)
            self.col_headings = reader_obj.__next__()[1:]
            for row in reader_obj:
                row_heading = row.pop(0)
                self.row_headings.append(row_heading)
                col = OrderedDict()
                for col_heading, value in zip(self.col_headings, row):
                    col[col_heading] = value
                self.data[row_heading] = col

    def save_to_file(self, path=None):
        if path is None:
            path = self.path
        with open(path, "w", newline="") as file:
            writer = csv.writer(file)
            fieldnames = [""] + self.col_headings
            writer.writerow(fieldnames)
            for row_title, row in self.rows:
                combined = [row_title] + [cell.value for cell in row]
                writer.writerow(combined)

    @property
    def rows(self):
        for row_heading, row in self.data.items():
            yield row_heading, (Cell(row=row_heading, col=column_heading, value=value)
                                for column_heading, value in row.items())

    @property
    def cols(self):
        for col_heading in self.col_headings:
            yield col_heading, (Cell(row=row_heading, col=col_heading, value=row[col_heading])
                                for row_heading, row in self.data.items())

    @property
    def cells(self):
        for row_heading in self.row_headings:
            for column_heading in self.col_headings:
                yield Cell(row=row_heading, col=column_heading, value=self.data[row_heading][column_heading])

    def value_at(self, row_name, col_name):
        return self.data[row_name][col_name]

    def load_from_grid_positions(self, data):
        row_headings_dict = defaultdict(list)
        col_headings_dict = defaultdict(list)
        for grid_position in data:
            row_headings_dict[grid_position.row].append(grid_position)
            col_headings_dict[grid_position.col].append(grid_position)
        self.row_headings = list(row_headings_dict.keys())
        self.col_headings = list(col_headings_dict.keys())
        for row_heading in self.row_headings:
            self.data[row_heading] = OrderedDict()
            for col_heading in self.col_headings:
                self.data[row_heading][col_heading] = None
        for grid_position in data:
            self.data[grid_position.row][grid_position.col] = grid_position.value


def auto_gen_chores(chore_names, duration=7, cycles=52, random=False):
    raise NotImplementedError
    col_headings = []
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=today.weekday())
    while cycles > 1:
        col_headings.append(start_date.strftime("%Y-%m-%d %H%M%S"))
        start_date + datetime.timedelta(days=7)
        cycles += -1

    with open(path_for("chores.csv")) as chore_file:
        writer = csv.writer(chore_file)


