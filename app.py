from flask import Flask, flash, render_template, url_for, session, redirect, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from twilio.rest import Client
from dotenv import load_dotenv
import os

load_dotenv()

account_sid = os.getenv('TWILIO_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_phone_number = os.getenv('TWILIO_PHONE')

client = Client(account_sid, auth_token)

app = Flask(__name__)
app.secret_key = "med"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///patients.db'
db = SQLAlchemy(app)


class patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    confirmed = db.Column(db.Boolean, default=False)


with app.app_context():
    db.create_all()


#Home
@app.route('/')
def home():
    return render_template('home.html')


#ADMIN LOGIN
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    ADMIN_USERNAME = 'pew'
    ADMIN_PASSWORD = 'pew_'

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['is_admin'] = True
            flash("Logged in successfully!", "success")
            return redirect(url_for('show_patients'))
        else:
            flash("Invalid credentials. Please try again.", "danger")
            return redirect(url_for('admin_login'))

    return render_template('admin_login.html')


#ADMIN LOGOUT
@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    flash('Logged out.', 'success')
    return redirect(url_for('admin_login'))


#About
@app.route('/about')
def about():
    return render_template('about.html')


#Patients
@app.route('/patients')
def show_patients():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))

    patients = patient.query.all()
    return render_template('patients.html', patients=patients)


#Add
@app.route('/patients/add', methods=['GET', 'POST'])
def add_patient():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone_number')
        appt_date = request.form.get('appointment_date')

        if not phone.isdigit() or len(phone) != 10:
            flash("Phone number must be exactly 10 digits.", "danger")
            return redirect(url_for('add_patient'))

        full_phone = '+977' + phone

        new_patient = patient(
            name=name,
            phone_number=full_phone,
            appointment_date=datetime.strptime(appt_date, '%Y-%m-%d')
        )
        db.session.add(new_patient)
        db.session.commit()
        flash("Patient added successfully!", "success")
        return redirect(url_for('show_patients'))

    return render_template('add_patient.html')


#Mark as Confirmed
@app.route('/patients/confirm/<int:id>')
def confirm_patient(id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))

    p = patient.query.get_or_404(id)
    p.confirmed = True
    db.session.commit()
    flash("Patient confirmed successfully!", "success")
    return redirect(url_for('show_patients'))


#Edit
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_patient(id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))

    p = patient.query.get_or_404(id)

    if request.method == 'POST':
        p.name = request.form.get('name')
        p.phone_number = request.form.get('phone_number')
        p.appointment_date = datetime.strptime(request.form.get('appointment_date'), '%Y-%m-%d')

        db.session.commit()
        flash("Patient updated successfully!", "success")
        return redirect(url_for('show_patients'))

    return render_template('edit_patient.html', patient=p)


#Delete
@app.route('/patients/delete/<int:id>', methods=['POST'])
def delete_patient(id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))

    p = patient.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    flash("Patient deleted.", "success")
    return redirect(url_for('show_patients'))


#Send Reminder
@app.route('/patients/remind/<int:id>')
def send_reminder(id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))

    p = patient.query.get_or_404(id)
    client.messages.create(
        body="sms_appointment_reminders",
        to=p.phone_number,
        from_=os.getenv('TWILIO_PHONE')
    )
    flash(f"Reminder sent to {p.name}!", "success")
    return redirect(url_for('show_patients'))


#View Patient Details
@app.route('/details/<int:id>')
def view_patient(id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))

    p = patient.query.get_or_404(id)
    return render_template('patient_details.html', patient=p)

#Dashboard
@app.route('/dashboard')
def dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    total = patient.query.count()
    confirmed = patient.query.filter_by(confirmed=True).count()
    pending = total - confirmed
    confirmed_pct = round((confirmed/total * 100),1) if total > 0 else 0
    
    upcoming = patient.query.filter(patient.appointment_date>=datetime.now()).order_by(patient.appointment_date).limit(5).all()
    
    return render_template('dashboard.html', total=total, confirmed=confirmed, pending=pending, confirmed_pct=confirmed_pct, upcoming=upcoming)
    



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)