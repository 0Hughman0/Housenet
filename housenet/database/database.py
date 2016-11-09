import datetime
import shutil

from flask_sqlalchemy import SQLAlchemy
from ..utilities import ConfigGrid, Cell, path_for, timestamp
import icalendar as ical

db = SQLAlchemy()


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


class Cashflow(db.Model):
    __tablename__ = "cashflows"

    id = db.Column(db.Integer, primary_key=True, unique=True)

    to_name = db.Column(db.String, db.ForeignKey("housemates.name"))
    from_name = db.Column(db.String, db.ForeignKey("housemates.name"))

    _amount = db.Column(db.Float(asdecimal=True))

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


def load_housemates():
    housemates_grid = ConfigGrid()
    housemates_grid.load_from_path(path_for("config", "housemates.csv"))
    for housemate in housemates_grid.cells:
        db.session.add(Housemate(name=housemate.row))


def load_chores():
    chores_grid = ConfigGrid()
    chores_grid.load_from_path(path_for("config", "chores.csv"))
    for chore in chores_grid.cells:
        start_date = datetime.datetime.strptime(chore.col, "%d/%m/%Y")
        end_date = start_date + datetime.timedelta(days=7)
        chore = Chore(title=chore.value, who_id=chore.row, start_date=start_date, end_date=end_date)
        db.session.add(chore)


def load_muns():
    debts_grid = ConfigGrid()
    debts_grid.load_from_path(path_for("config", "muns.csv"))
    for debt in debts_grid.cells:
        if not debt.row == debt.col:
            db.session.add(Cashflow(to_name=debt.row, from_name=debt.col, _amount=float(debt.value)))


def export_housemates():
    housemates = Housemate.query.all()
    housemates_grid = ConfigGrid()
    housemates_grid.load_from_grid_positions([Cell(row=housemate.name,
                                                   col="pointless",
                                                   value="more pointless") for housemate in housemates])
    housemates_grid.save_to_file(path_for("exports", timestamp("{} - housemates.csv")))


def save_chores():
    chores = Chore.query.all()
    chores_grid = ConfigGrid()
    chores_grid.load_from_grid_positions([Cell(row=chore.who_id,
                                               col=chore.start_date,
                                               value=chore.title) for chore in chores])
    chores_grid.save_to_file(path_for("exports", timestamp("{} - chores.csv")))


def export_muns():
    muns = Cashflow.query.all()
    muns_grid = ConfigGrid()
    muns_grid.load_from_grid_positions([Cell(row=mun.from_name,
                                             col=mun.to_name,
                                             value=mun.amount) for mun in muns])
    muns_grid.save_to_file(path_for("exports", timestamp("{} - muns.csv")))


def export_database():
    export_housemates()
    save_chores()
    export_muns()


def save_database():
    shutil.copy(path_for("database.db"), path_for("backups", timestamp("{} - database.db")))

