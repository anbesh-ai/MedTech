from flask import Flask, flash, render_template, url_for , session , redirect
from flask import request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///patients.db'
db= SQLAlchemy( app )

class patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    appointment_date = db.Column(db.DateTime(100), nullable=False)
    confirmed = db.Column(db.Boolean, default=False)

with app.app_context( ):
        db.create_all( )

@app.route('/')
def home():
    return "It works"

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/patients')
def show_patients( ):
    patients = patient.query.all( )
    return render_template('patients.html', patients=patients)


@app.route('/add' , methods=['GET', 'POST'])
def add_patient():
    if request.merhod == 'POST' :
         name = request.form.get('name')
         phone = request.form.get('phone_number')
         appt_date = request.form.get('appointment_date')

         new_patient = patient(
              name=name,
              phone_number=phone,
              appointment_date=datetime.strp(appt_date, '%Y-%m-%d')
         )
         db.session.add(new_patient)
         db.session.commit()
         return redirect(url_for('show_patients'))
    return render_template('add_patient.html')



if __name__ == '__main__':
    app.run(debug=True)
