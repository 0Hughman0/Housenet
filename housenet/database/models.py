import datetime

import icalendar as ical

from . import db


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


class Cashflow(db.Model):
    __tablename__ = "cashflows"

    id = db.Column(db.Integer, primary_key=True, unique=True)

    to_name = db.Column(db.String, db.ForeignKey("housemates.name"))
    from_name = db.Column(db.String, db.ForeignKey("housemates.name"))

    _amount = db.Column(db.Float(asdecimal=True, decimal_return_scale=3))

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
        from_name = self.from_name
        to_name = self.to_name
        transaction = Transaction(from_=from_name,
                                  to=to_name,
                                  amount=-amount,
                                  time=datetime.datetime.now())
        return transaction


    def __repr__(self):
        return "{0} owes £{1:,.2f} to {2}".format(self.to_name, self.amount, self.from_name)


class Transaction(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    to = db.Column(db.String, db.ForeignKey("housemates.name"))
    from_ = db.Column(db.String, db.ForeignKey("housemates.name"))

    amount = db.Column(db.Float(asdecimal=True))

    reason = db.Column(db.String(250))
    time = db.Column(db.DateTime)

    def to_row(self):
        return [self.time.strftime("%d/%m/%Y %H:%M"),
                self.reason,
                self.from_,
                self.to, "£{0:,.2f}".format(self.amount)]
