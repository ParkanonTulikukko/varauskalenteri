import datetime

from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///mytestdb.db"
db = SQLAlchemy(app)


#antaa kuluvan viikon päivät
def annaViikko():

    tanaan = datetime.date.today().isocalendar()
    tamaViikko = tanaan[1]
    tamaVuosi = tanaan[0]

    viikonPvmt = []  
    for x in range(1,7):
        viikonpaiva = datetime.datetime.strptime(f'{tamaVuosi}-W{int(tamaViikko) - 1}-{x}', "%Y-W%W-%w").date()
        viikonPvmt.append(PaivaAika(viikonpaiva))
        print(viikonpaiva, x)
        if (x == 6):
            viikonPvmt.append(PaivaAika((datetime.datetime.strptime(f'{tamaVuosi}-W{int(tamaViikko) - 1}-{0}', "%Y-W%W-%w"))))

    return viikonPvmt


class Varaus(db.Model):
    aloitus = db.Column(db.DateTime, primary_key=True)
    lopetus = db.Column(db.DateTime)
    varaaja = db.Column(db.String(120))


#pitää sisällään datetime-objektin ja funkkarin joka kääntää viikonpäivät suomeksi
class PaivaAika:

    def __init__(self, pvm):
        self.pvm = pvm

    #getteri
    @property
    def pvm(self):
        return self.__pvm

    #setteri
    @pvm.setter
    def pvm(self, pvm):
        self.__pvm = pvm

    #suomentaja
    def suomenna(self):
        day = self.__pvm.strftime("%A")
        if day == "Friday":
            return "perjantai"
        elif day == "Saturday":
            return "lauantai"
        elif day == "Sunday":
            return "sunnuntai"
        elif day == "Monday":
             return "maanantai"
        elif day == "Tuesday":
            return "tiistai"
        elif day == "Wednesday":
            return "keskiviikko"
        elif day == "Thursday":
            return "torstai"


#tarkistetaan onko paallekkaisyytta varausten kanssa
#ja että varauksen alku on aiemmin kuin loppu
def tarkistaPaallekkaisyys(aloitus, lopetus):
    varaukset = Varaus.query.all()

    for var in varaukset:
        #tsekataan ensin onko sama päivä ja edetään kelloon sit:
        print("comparison: " + aloitus.strftime("%x") + " ja " + var.aloitus.strftime("%x"))
        if (aloitus.strftime("%x") == var.aloitus.strftime("%x")):
            #If TRUE, then the ranges overlap.
            if var.aloitus.strftime("%X") < lopetus.strftime("%X") and aloitus.strftime("%X") < var.lopetus.strftime("%X"):
                return True
            else:
                return False

    return False

def tulostaVaraukset():
    varaukset = Varaus.query.all()
    for var in varaukset:
        print(var.aloitus.strftime("%m/%d/%Y %H:%M") + "-" + var.lopetus.strftime("%H:%M"))


@app.route("/", methods=["GET"])
def root_view():
    print("luulen että ollaan täällä, eli route / ja GET")
    varaukset = Varaus.query.all()
    varauslista = []
    for var in varaukset:
        varauslista.append(var)
    varauslista.sort(key=lambda x: x.aloitus, reverse=False)
    return render_template("index.html", weekdays=annaViikko(), varaukset=varauslista)


@app.route("/", methods=["POST"])  # tässä tulee käyttäjän valinta (nyt varaussivun kautta)
def root_post():
    params = request.form
    paramsArgs = request.args

    #parsitaan tunnit ja minuutit talteen argumenteista
    aloitus=params["aloitus"]
    aloitusTunti = aloitus[0:2]
    aloitusMinsat = aloitus[3:5]
    lopetus=params["lopetus"]
    lopetusTunti = lopetus[0:2]
    lopetusMinsat = lopetus[3:5]

    #parsitaan vuosi, kk ja päivämäärä "pvm"-argumentista
    vuosi = int(paramsArgs["pvm"][0:4])
    kk = int(paramsArgs["pvm"][5:7])
    paiva = int(paramsArgs["pvm"][8:10])

    #luodaan datetime-objektit merkitsemään varauksen alkua ja loppua
    aloitus = datetime.datetime(vuosi, kk, paiva, int(aloitusTunti), int(aloitusMinsat))
    lopetus = datetime.datetime(vuosi, kk, paiva, int(lopetusTunti), int(lopetusMinsat))

    if (paramsArgs["muokataan"]=="True"):

        #otetaan alkuperäinen varaus talteen
        aloitusTunti = int(params["vanhaAloitus"][0:2])
        aloitusMinsat = int(params["vanhaAloitus"][3:])
        lopetusTunti = params["vanhaLopetus"][0:1]
        lopetusMinsat = params["vanhaLopetus"][3:4]
        temp = Varaus(aloitus=aloitus, lopetus=lopetus, varaaja=params["varaaja"])

        #poistetaan vanha varaus taulusta
        vanhanAloitus = datetime.datetime(year=vuosi, month=kk, day=paiva, hour=aloitusTunti, minute=aloitusMinsat)
        vanhaVaraus = Varaus.query.filter(Varaus.aloitus == vanhanAloitus).one()
        db.session.delete(vanhaVaraus)
        db.session.commit()

        varaukset = Varaus.query.all()
        for var in varaukset:
            print("muokataan var in varaukset" + var.aloitus.strftime("%m/%d/%Y %H:%M"))

    #tarkistetaan ettei aloitusaika ole myöhemmin kuin lopetusaika
    if (lopetus.strftime("%X") <= aloitus.strftime("%X")):
        if (paramsArgs["muokataan"] == "True"):
            #uusi muokkaus ei ollut oikeellinen, joten palautetaan alkuperäinen takaisin tietokantaan
            db.session.add(temp)
            db.session.commit()
            return render_template("varaus.html", viikonpv=paramsArgs["viikonpv"], pvm=paramsArgs["pvm"],
                                   varausvirhe=True, aloitus=params["aloitus"], lopetus=params["lopetus"],
                                   muokataan=True, varaaja=params["varaaja"])
        return render_template("varaus.html", viikonpv=paramsArgs["viikonpv"], pvm=paramsArgs["pvm"],
                                   varausvirhe=True, aloitus=params["aloitus"], lopetus=params["lopetus"],
                                   muokataan=False, varaaja=params["varaaja"])

    if tarkistaPaallekkaisyys(aloitus, lopetus):
        if (paramsArgs["muokataan"] == "True"):
            #uusi muokkaus meni vanhojen varauksien päälle, joten palautetaan alkuperäinen muokkaamaton takaisin db:hen
            db.session.add(temp)
            db.session.commit()
            return render_template("varaus.html", viikonpv=paramsArgs["viikonpv"], pvm=paramsArgs["pvm"],
                                   varattuJo=True, aloitus=params["aloitus"], lopetus=params["lopetus"],
                                   muokataan=True, varaaja=params["varaaja"])
        return render_template("varaus.html", viikonpv=paramsArgs["viikonpv"], pvm=paramsArgs["pvm"],
                                   varattuJo=True, aloitus=params["aloitus"], lopetus=params["lopetus"],
                                   muokataan=False, varaaja=params["varaaja"])


    varaaja=params["varaaja"]
    db.session.add(Varaus(aloitus=aloitus, lopetus=lopetus, varaaja=varaaja))
    db.session.commit()

    return render_template("index.html", weekdays=annaViikko(), varaukset=haeVaraukset())


def haeVaraukset():
    varaukset = Varaus.query.all()
    varauslista = []
    for var in varaukset:
        varauslista.append(var)
    varauslista.sort(key=lambda x: x.aloitus, reverse=False)
    return varauslista


@app.route("/poista")
def poista():
    ra = request.args
    return render_template("poista.html",  viikonpv=ra["viikonpaiva"], pvm=ra["date"], aloitus=ra["aloitus"],
                           lopetus=ra["lopetus"], varaaja=ra["varaaja"])


@app.route("/poistaOikeasti")
def poistaOikeasti():
    paramsArgs = request.args
    aloitusTunti = int(paramsArgs["aloitus"][0:2])
    aloitusMinsat = int(paramsArgs["aloitus"][3:5])
    vuosi = int(paramsArgs["pvm"][0:4])
    kk = int(paramsArgs["pvm"][5:7])
    paiva = int(paramsArgs["pvm"][8:10])
    aloitus = datetime.datetime(vuosi, kk, paiva, aloitusTunti, aloitusMinsat)

    poistettavanAloitus = aloitus
    vanhaVaraus = Varaus.query.filter(Varaus.aloitus == poistettavanAloitus).one()
    db.session.delete(vanhaVaraus)
    db.session.commit()

    return redirect('/')

@app.route("/varaus")
def varaus():

    params = request.args
    if params["muokataan"] == "True":
        return render_template("varaus.html", viikonpv=params["viikonpaiva"], pvm=params["date"],
                               aloitus=params["aloitus"], lopetus=params["lopetus"], muokataan=True,
                               varaaja=params["varaaja"])
    else:
        return render_template("varaus.html", viikonpv=params["viikonpaiva"], pvm=params["date"], aloitus="14:00",
                               lopetus="15:00", muokataan=False)


def dbinit():
    db.drop_all()
    db.create_all()

if __name__ == '__main__':
    dbinit()
    app.run(debug=True, use_reloader=True, host="127.0.0.1", port=1234)



