from decimal import Decimal
from io import BytesIO

from flask import request, render_template, send_file

from ...base_app import base_app
from ...database import db
from ...database.models import Housemate, Cashflow


@base_app.route('/')
def home():
    housemates = Housemate.query.all()
    data = []
    for housemate in housemates:
        data.append(tuple((housemate.name, housemate.current_chore.title)))
    return render_template("base_app/home.html", title="Home", data=data)


@base_app.route("/profile/<name>", methods=["POST", "GET"])
def profile(name):
    housemate = Housemate.query.get(name)
    if housemate:
        if request.method == "POST":
            change_dict = request.form
            for payee_name, amount in change_dict.items():
                if not amount:
                    continue
                debt = Cashflow.query.filter(Cashflow.from_name == housemate.name,
                                             Cashflow.to_name == payee_name).first()
                if debt:
                    debt.add(Decimal(amount))
            db.session.commit()
        current_chore = housemate.current_chore
        debts = (cashflow.as_tuple for cashflow in housemate.out_flow)
        debits = (cashflow.as_tuple for cashflow in housemate.in_flow)
        quits = (cashflow.as_tuple for cashflow in housemate.quits)
        return render_template("base_app/profile.html", title=name, current_chore=current_chore, debts=debts, debits=debits,
                               quits=quits)
    return "<a>You're drunk, go </a><a href='/'>home</a>"


@base_app.route("/profile/<name>/ical")
def get_ical(name):
    housemate = Housemate.query.get(name)
    return send_file(BytesIO(housemate.get_ical_feed()),
                     attachment_filename="{}_chores.ics".format(name),
                     as_attachment=True)
