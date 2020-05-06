import os
from datetime import datetime, timedelta

import requests
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError


NORTHAMPTON_ID = 2641430
TELFORD_ID = 3345439

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Reading(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dt = db.Column(db.DateTime, nullable=False, index=True, unique=True)
    northampton_temp = db.Column(db.Float, nullable=False)
    telford_temp = db.Column(db.Float, nullable=False)

    def get_difference(self):
        return round(abs(self.northampton_temp - self.telford_temp), 2)

    def __repr__(self):
        return f'<Reading {self.dt} - {self.northampton_temp} - {self.telford_temp}'

@app.cli.command("update")
def get_current_temps():
    base_url = 'http://api.openweathermap.org/data/2.5/group'
    params = {
        'id': f'{NORTHAMPTON_ID},{TELFORD_ID}',
        'appid': os.environ.get('API_KEY', ""),
        'units': 'metric'
    } 
    res = requests.get(base_url, params)
    if res.status_code == 200:
        data = res.json()

        # import pprint
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(data)

        dt_northampton = datetime.fromtimestamp(data["list"][0]["dt"])
        dt_telford = datetime.fromtimestamp(data["list"][0]["dt"])
        if abs(dt_northampton - dt_northampton) < timedelta(minutes=10):
            northampton_temp = data["list"][0]["main"]["temp"]
            telford_temp = data["list"][1]["main"]["temp"]
        
            r = Reading(dt=dt_northampton, northampton_temp=northampton_temp,
                telford_temp=telford_temp)
            db.session.add(r)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                print("Duplicate reading")
        else:
            print("Times too far apart")

@app.route('/')
def home():
    readings = Reading.query.all()
    return render_template("index.html.j2", readings=readings)