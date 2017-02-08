from decimal import Decimal
from io import BytesIO

from flask import request, render_template, send_file, json

from housenet import base_app
from housenet.database import db
from housenet.database.models import Housemate, Cashflow, Transaction


@base_app.route('/')
def home():
    housemates = Housemate.query.all()
    data = []
    for housemate in housemates:
        data.append(tuple((housemate.name, housemate.current_chore.title)))
    return render_template("home.html", title="Home", data=data)


@base_app.route("/profile/<name>", methods=["POST", "GET"])
def profile(name):
    housemate = Housemate.query.get(name)
    if not housemate:
        return "<a>You're drunk, go </a><a href='/'>home</a>"
    if request.method == "POST":
        change_dict = request.form.copy()
        reason = change_dict.pop("reason")
        for payment_type, payments in change_dict.items():
            payments_list = (payment for payment in json.loads(payments) if payment['value'])
            for payment in payments_list:
                debt = Cashflow.query.filter(Cashflow.from_name == housemate.name,
                                             Cashflow.to_name == payment["name"]).first()
                if not debt:
                    continue
                amount = Decimal(payment['value'])
                if payment_type == "your_owed":
                    debt = debt.mirror
                    amount = -amount
                transaction = debt.add(amount)
                transaction.reason = reason
                db.session.add(transaction)
        db.session.commit()
    current_chore = housemate.current_chore
    debts = (cashflow.as_tuple for cashflow in housemate.out_flow)
    debits = (cashflow.as_tuple for cashflow in housemate.in_flow)
    quits = (cashflow.as_tuple for cashflow in housemate.quits)
    return render_template("profile.html", title=name, current_chore=current_chore, debts=debts, debits=debits,
                           quits=quits)


@base_app.route("/transactions_history")
def transactions():
    return render_template("transactions.html", title="Transactions")


@base_app.route("/api/get_transactions")
def get_transactions():
    all_transactions = Transaction.query.all()
    return json.dumps({"data": tuple(transaction.to_row() for transaction in all_transactions)})


@base_app.route("/api/ical/<name>")
def get_ical(name):
    housemate = Housemate.query.get(name)
    return send_file(BytesIO(housemate.get_ical_feed()),
                     attachment_filename="{}_chores.ics".format(name),
                     as_attachment=True)
