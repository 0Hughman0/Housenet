from decimal import Decimal
from io import BytesIO

from flask import Flask, request
from flask import render_template, send_file
import click
from sqlalchemy.exc import OperationalError

from .database.database import (db,
                                Housemate, Chore, Cashflow,
                                load_housemates, load_chores, load_muns, save_database, export_database)


app = Flask(__name__)

db.app = app
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database/database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


@app.context_processor
def inject_vars():
    values = {}
    housemate_names = (housemate.name for housemate in Housemate.query.all())
    values['names'] = housemate_names
    return values


@app.route('/')
def home():
    housemates = Housemate.query.all()
    data = []
    for housemate in housemates:
        data.append(tuple((housemate.name, housemate.current_chore.title)))
    return render_template("home.html", title="Home", data=data)


@app.route("/profile/<name>", methods=["POST", "GET"])
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
        return render_template("profile.html", title=name, current_chore=current_chore, debts=debts, debits=debits,
                               quits=quits)
    return "<a>You're drunk, go </a><a href='/'>home</a>"


@app.route("/profile/<name>/ical")
def get_ical(name):
    housemate = Housemate.query.get(name)
    return send_file(BytesIO(housemate.get_ical_feed()),
                     attachment_filename="{}_chores.ics".format(name),
                     as_attachment=True)


@app.cli.command(with_appcontext=False, help="run app locally in debug mode")
def debug():
    db.create_all()
    app.run(debug=True)


@app.cli.command(help="create backup of db")
def savedb():
    click.echo("saving database")
    save_database()
    click.echo("Success!")


@app.cli.command(help="export db to .csv files")
def exportdb():
    click.echo("exporting database tables")
    export_database()
    click.echo("Success!")


@app.cli.command(help="reload db from .csv files")
def reloaddb():
    click.echo("removing old data")
    for table in (Housemate, Chore, Cashflow):
        try:
            table.query.delete()
        except OperationalError:
            click.echo("No table found, will try to rebuild in next step")
    click.echo("loading new data")
    db.create_all()
    load_housemates()
    load_muns()
    load_chores()
    db.session.commit()
    click.echo("Success!")

if __name__ == "__main__":
    db.create_all()
    app.run(host="0.0.0.0", debug=True)
