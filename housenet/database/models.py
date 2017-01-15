import datetime
import shutil
from collections import namedtuple


import icalendar as ical
from ez_grid import Grid

from . import db
from ..utilities import path_for, timestamp


class HousematesGrid(Grid):

    def add_to_db(self):
        for housemate in self.cells:
            db.session.add(Housemate(name=housemate.row))


class ChoresGrid(Grid):

    def add_to_db(self):
        for chore in self.cells:
            start_date = datetime.datetime.strptime(chore.col, "%d/%m/%Y")
            end_date = start_date + datetime.timedelta(days=7)
            db.session.add(Chore(title=chore.value, who_id=chore.row, start_date=start_date, end_date=end_date))


class MunsGrid(Grid):

    def add_to_db(self):
        for debt in self.cells:
            if not debt.row == debt.col:
                db.session.add(Cashflow(to_name=debt.row, from_name=debt.col, _amount=float(debt.value)))


class Housemate(db.Model):
    __tablename__ = "housemates"

    name = db.Column(db.String(250), primary_key=True, unique=True)

    chores = db.relationship("Chore", backref="who", lazy="dynamic")

    out_flow = db.relationship("Cashflow",
                               primaryjoin="and_(Cashflow.from_name==Housemate.name, Cashflow._amount > 0)",
                               backref="to")
    in_flow = db.relationship("Cashflow",
                              primaryjoin="and_(Cashflow.to_name==Housemate.name, Cashflow._amount > 0)",
                              backref="from_")

    quits = db.relationship("Cashflow",
                            primaryjoin="and_(Cashflow.to_name==Housemate.name, Cashflow._amount==0)")

    @staticmethod
    def names():
        return (housemate.name for housemate in Housemate.query.all())

    @staticmethod
    def as_grid():
        housemates_grid = HousematesGrid(Housemate.names(), ["null"], "Housemates")
        for housemate in Housemate.query.all():
            housemates_grid[housemate.name]["null"] = "null"
        return housemates_grid

    @property
    def current_chore(self):
        return self.chore_on(datetime.date.today())

    def chore_on(self, date):
        return self.chores.filter(Chore.start_date <= date,
                                  Chore.end_date > datetime.date.today()).first()

    def get_ical_feed(self):
        calendar = ical.Calendar()
        for chore in self.chores:
            event = ical.Event()
            event.add("dtstart", chore.start_date)
            event.add("dtend", chore.end_date)
            event.add("summary", chore.title)
            calendar.add_component(event)
        return calendar.to_ical()

    def __repr__(self):
        return "Housemate: {}:\n\tcurrent chore: {}\n\tforward:".format(self.name, self.current_chore)


class Chore(db.Model):
    __tablename__ = "chores"

    id = db.Column(db.Integer, primary_key=True, unique=True)
    title = db.Column(db.String(250), nullable=False)

    who_id = db.Column(db.Integer, db.ForeignKey("housemates.name"))

    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)

    @staticmethod
    def dates():
        dates = list(set((chore.start_date for chore in Chore.query.all())))
        dates.sort()
        return dates

    @staticmethod
    def as_grid():
        chores_grid = ChoresGrid(Housemate.names(), Chore.dates(), "Chores")
        for chore in Chore.query.all():
            chores_grid[chore.who_id][chore.start_date] = chore.title
        return chores_grid


class Cashflow(db.Model):
    __tablename__ = "cashflows"

    id = db.Column(db.Integer, primary_key=True, unique=True)

    to_name = db.Column(db.String, db.ForeignKey("housemates.name"))
    from_name = db.Column(db.String, db.ForeignKey("housemates.name"))

    _amount = db.Column(db.Float(asdecimal=True))

    @staticmethod
    def as_grid():
        muns_grid = MunsGrid(Housemate.names(), Housemate.names(), "Muns")
        for mun in Cashflow.query.all():
            muns_grid[mun.to_name][mun.from_name] = mun.amount
        return muns_grid

    @property
    def amount(self):
        return self._amount

    @property
    def mirror(self):
        return Cashflow.query.filter(Cashflow.to_name == self.from_name, Cashflow.from_name == self.to_name).first()

    @property
    def forwards(self):
        if self.amount > 0:
            return True
        return False

    @property
    def quits(self):
        if self.amount == 0 and self.to_name != self.from_name:
            return True
        return False

    @property
    def as_tuple(self):
        return self.from_name, self.to_name, "{0:,.2f}".format(self.amount)

    def add(self, amount):
        self._amount += amount
        self.mirror._amount += -amount

    def __repr__(self):
        return "{} owes £{0:,.2f} to {}".format(self.to_name, self.amount, self.from_name)

Pair = namedtuple("Pair", ("model", "grid"))

obj_map = {"housemates": Pair(Housemate, HousematesGrid),
               "muns": Pair(Cashflow, MunsGrid),
               "chores": Pair(Chore, ChoresGrid)}


def load_config(config_name):
    with open(path_for("config", "{}.csv".format(config_name)), "r") as f:
        grid = obj_map[config_name].grid.from_csv_file(f)
    grid.add_to_db()


def export_config(config_name):
    with open(path_for("exports", timestamp("{}" + " - {}.csv".format(config_name))), "w") as f:
        grid = obj_map[config_name].model.as_grid()
        grid.save_to_file(f)


def export_database():
    for config in ("housemates", "muns", "chores"):
        export_config(config)


def save_database():
    shutil.copy(path_for("database", "database.db"), path_for("backups", timestamp("{} - database.db")))
