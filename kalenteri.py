import datetime
from enum import Enum

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


# päivät on tablessa, ja päivää klikkaamalla mennään varaussivulle, johon syötetään haluttu aika

class Weekday(Enum):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7


WEEKDAYS = [Weekday.MONDAY,
            Weekday.TUESDAY,
            Weekday.WEDNESDAY,
            Weekday.THURSDAY,
            Weekday.FRIDAY,
            Weekday.SATURDAY,
            Weekday.SUNDAY]

weekdays = ['MA', 'TI', 'KE', 'TO', 'PE', 'LA', 'SU']

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///mytestdb.db"
db = SQLAlchemy(app)


class Kalenteri2(db.Model):
    pid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), unique=False, nullable=False)
    description = db.Column(db.String(120), unique=False, nullable=False)
    taken = db.Column(db.Boolean, unique=False, nullable=False)


class Kalenteri(db.Model):
    # sid = db.Column(db.Integer, primary_key=True)
    # weeknumber = db.Column(db.Integer)
    weekday = db.Column(db.String, primary_key=True, nullable=False)
    varattu = db.Column(db.Boolean)
    pvmAika = db.Column(db.DateTime)
    # username = db.Column(db.String, nullable=False)


@app.route("/", methods=["GET"])
def root_view():
    paivat = Kalenteri.query.all()

    for paiva in paivat:
        print(paiva.weekday)

    # return render_template("index.html", weekdays=['MA', 'TI', 'KE', 'TO', 'PE', 'LA', 'SU'], sipsi=2, juusto="moi")
    return render_template("index.html", weekdays=paivat, sipsi=2, juusto="moi")
    # presents=Present.query.filter_by(taken=False)


@app.route("/", methods=["POST"])  # tässä tulee käyttäjän valinta
def root_post():
    """""
    print(request.form["day"])
    users.update(). \
        ...where(users.c.name == 'jack'). \
        ...values(name='ed')
    """
    params = request.form
    print(params["day"])
    print(weekdays[0])

    Kalenteri.query.filter_by(weekday=params['day']) \
        .update({"varattu": True})
    db.session.commit()
    return render_template("index.html", weekdays=Kalenteri.query.all())


@app.route("/varaus")
def varaus():
    params = request.args
    print(params["date"])
    return render_template("varaus.html", date=params["date"])


def dbinit():
    print("installoidaan datapesä")
    db.drop_all()
    db.create_all()
    """""
    if len(Kalenteri.query.all()) < 1:
        available_presents = [ Kalenteri(name="kassi", description="Hieno kassi", taken=False),
                               Kalenteri(name="lusikka", description="Puurolusikka", taken=False),
                               Kalenteri(name="sushi", description="Nakkisushi", taken=False),
                               Kalenteri(name="kieli", description="Jaappanian alkeet", taken=False),
                               Kalenteri(name="tutti", description="Huvitutti", taken=False),
                               Kalenteri(name="matka", description="New Yorkin matka", taken=False),
                               Kalenteri(name="poni", description="Poni", taken=False)
                             ]
        db.session.add_all(available_presents)
    """
    dayz = [Kalenteri(weekday="MA", varattu=False, pvmAika="2000-12-02 12:00:00"),
            Kalenteri(weekday="TI", varattu=True),
            Kalenteri(weekday="KE", varattu=False)
            ]
    db.session.add_all(dayz)
    db.session.commit()
    print(Kalenteri.query.filter_by(varattu=False))
    # ins = db.insert().values(day='MA', varattu=False)


if __name__ == '__main__':
    dbinit()
    app.run(debug=True, use_reloader=True, host="127.0.0.1", port=1234)
