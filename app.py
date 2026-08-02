from flask import Flask, flash, render_template, url_for , session , redirect
from flask import request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.secret_key = "med"

#Database

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///patients.db'
db= SQLAlchemy( app )

class patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    confirmed = db.Column(db.Boolean, default=False)
    

with app.app_context( ):
        db.create_all( )

#Home
@app.route('/')
def home():
    return "It works"

#About
@app.route('/about')
def about():
    return render_template('about.html')

#Patients  
@app.route('/patients')
def show_patients( ):
    patients = patient.query.all( )
    return render_template('patients.html', patients=patients)

#Add 
@app.route('/patients/add' , methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST' :
         name = request.form.get('name')                              # there should be a variable that holds value and POST on db variable
         phone = request.form.get('phone_number')
         appt_date = request.form.get('appointment_date')   #new variable= line 18 db variable (for name, no.too)

         new_patient = patient(         #called a new_patient variable which stores the entred data and assign data in db variables
              name=name,                  #db variable= current data holder variable
              phone_number=phone,
              appointment_date=datetime.strptime(appt_date, '%Y-%m-%d')   #vice versa line 46
         )
         db.session.add(new_patient)
         db.session.commit()

         flash("Patient added successfully !", "success")
         return redirect(url_for('show_patients'))
    return render_template('add_patient.html')

#Mark as Confirmed
@app.route('/patients/confirm/<int:id>')
def confirm_patient(id):
     p= patient.query.get_or_404(id)
     p.confirmed =True
     db.session.commit( )
     flash("Patient confirmed successfully !", "success")
     return redirect(url_for('show_patients'))

#Edit
@app.route('/edit/<int:id>', methods=['GET', 'POST' ])
def edit_patient(id):

     p=patient.query.get_or_404(id)

     if request.method == 'POST':
          p.name = request.form.get('name')
          p.phone_number = request.form.get('phone_number')
          p.appointment_date = datetime.strptime(request.form.get('appointment_date'), '%Y-%m-%d')

          db.session.commit( )
          flash("Patient updated successfully !", "success")
          return redirect(url_for('show_patients'))
     return render_template('edit_patient.html', patient=p)



#Delete
@app.route('/patients/delete/<int:id>', methods=['POST'])
def delete_patient(id):

     p=patient.query.get_or_404(id)
     db.session.delete(p)
     db.session.commit( )
     return redirect(url_for('show_patients'))


#ADMIN LOGIN
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
     ADMIN_USERNAME = 'pew'
     ADMIN_PASSWORD = 'pew_'

     if request.method == 'POST':
          username = request.form.get('username')
          password = request.form.get('password')

          if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
               session['admin_logged_in'] = True
               flash("Logged in successfully !", "success")
               return redirect(url_for('show_patients'))
          else:
               flash("Invalid credentials. Please try again.", "danger")

     return render_template('admin_login.html')



if __name__ == '__main__':
    app.run(debug=True)