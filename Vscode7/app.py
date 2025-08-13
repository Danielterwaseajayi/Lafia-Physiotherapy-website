from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clinic.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'         # Replace with your email
app.config['MAIL_PASSWORD'] = 'your_app_password_here'       # Use an app password
mail = Mail(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True)
    phone = db.Column(db.String(20))
    is_admin = db.Column(db.Boolean, default=False)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(150))
    email = db.Column(db.String(150))
    phone = db.Column(db.String(20))
    date = db.Column(db.String(20))
    time = db.Column(db.String(20))
    reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    email = db.Column(db.String(150))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        if not username or not password or not email:
            return "<h3>All fields are required.</h3><p><a href='/signup'>Go back</a></p>"

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "<h3>User already exists!</h3><p><a href='/signup'>Try again</a></p>"

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, email=email)
        db.session.add(new_user)
        db.session.commit()

        # Send welcome email
        try:
            msg = Message(
                subject="Welcome to Lafia Physiotherapy!",
                sender=app.config['MAIL_USERNAME'],
                recipients=[email],
                body=f"Hi {username},\n\nThank you for signing up with Lafia Physiotherapy. We're excited to have you on board!\n\nYou can now book appointments, view your history, and contact us anytime.\n\nWarm regards,\nThe Lafia Team"
            )
            mail.send(msg)
        except Exception as e:
            print(f"Email failed to send: {e}")

        return redirect(url_for('index'))

    return render_template('signup.html')

@app.route('/home', methods=['POST'])
def home():
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        session['username'] = username
        session['is_admin'] = user.is_admin
        return redirect(url_for('dashboard'))
    return "<h3>Invalid credentials.</h3><p><a href='/'>Try again</a></p>"

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/book', methods=['GET', 'POST'])
def book():
    if request.method == 'POST':
        user = User.query.filter_by(username=session['username']).first()
        appointment = Appointment(
            user_id=user.id,
            name=request.form['name'],
            email=request.form['email'],
            phone=request.form['phone'],
            date=request.form['date'],
            time=request.form['time'],
            reason=request.form['reason']
        )
        db.session.add(appointment)
        db.session.commit()
        return render_template('confirmation.html', appointment=appointment)
    return render_template('book.html')

@app.route('/history')
def history():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        appointments = Appointment.query.filter_by(user_id=user.id).order_by(Appointment.created_at.desc()).all()
        return render_template('history.html', appointments=appointments)
    return redirect(url_for('index'))

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/message', methods=['POST'])
def message():
    msg = Message(
        name=request.form['name'],
        email=request.form['email'],
        content=request.form['message']
    )
    db.session.add(msg)
    db.session.commit()
    return render_template('message_sent.html', name=msg.name)

@app.route('/conditions')
def conditions():
    return render_template('conditions.html')

@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/profile')
def profile():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        return render_template('profile.html', user=user)
    return redirect(url_for('index'))

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        user.email = request.form.get('email')
        user.phone = request.form.get('phone')
        db.session.commit()
        return redirect(url_for('profile'))
    return redirect(url_for('index'))

@app.route('/admin', methods=['GET'])
def admin():
    if session.get('is_admin'):
        search = request.args.get('search')
        users = User.query.all()
        appointments = Appointment.query.order_by(Appointment.created_at.desc()).all()
        messages = Message.query.order_by(Message.created_at.desc()).all()

        if search:
            users = User.query.filter(User.username.contains(search)).all()
            appointments = Appointment.query.filter(Appointment.reason.contains(search)).all()

        return render_template('admin.html', users=users, appointments=appointments, messages=messages)
    return "<h3>Access denied.</h3>"

@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if session.get('is_admin'):
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return redirect(url_for('admin'))
    return "<h3>User not found or access denied.</h3>"

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
import os

app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.secret_key = os.environ.get('SECRET_KEY')
if __name__ == '__main__':
    app.run(debug=True)