import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps
from passlib.context import CryptContext

# Importing pymysql if using PyMySQL as the MySQL driver
import pymysql
pymysql.install_as_MySQLdb()

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Load the database configuration from environment variables
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}@{os.environ['DB_HOST']}/{os.environ['DB_NAME']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Create a CryptContext with the scrypt scheme, matching your hash format
pwd_context = CryptContext(
    schemes=["scrypt"],
    default="scrypt",
    hash__scrypt__salt_size=32
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

    def set_password(self, password):  
        self.password = pwd_context.hash(password)

    def check_password(self, password):  
        return pwd_context.verify(password, self.password)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow, nullable=False)  

# Initialize the database
@app.before_request
def create_tables():
    db.create_all()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    expenses = Expense.query.filter_by(user_id=user_id).order_by(Expense.date.desc()).all()
    user = User.query.get(user_id)
    return render_template('dashboard.html', expenses=expenses, username=user.username)

@app.route('/add_expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        description = request.form.get('description')
        amount = request.form.get('amount')
        category = request.form.get('category')
        date_str = request.form.get('date')

        if not description or not amount or not category:
            flash('All fields are required!', 'danger')
            return redirect(url_for('add_expense'))

        try:
            amount = float(amount)
        except ValueError:
            flash('Invalid amount entered!', 'danger')
            return redirect(url_for('add_expense'))

        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        user_id = session['user_id']

        new_expense = Expense(user_id=user_id, description=description, amount=amount, category=category, date=date)
        db.session.add(new_expense)
        db.session.commit()
        flash('Expense added successfully!', 'success')
        return redirect(url_for('add_expense'))
    return render_template('add_expense.html')

# User registration and login routes
@app.route('/register', methods=['GET', 'POST'])  
def register():  
    if request.method == 'POST':  
        username = request.form.get('username')  
        password = request.form.get('password')
        hashed_password = pwd_context.hash(password)  # Use scrypt hashing
        user = User(username=username, password=hashed_password)
        db.session.add(user)  
        db.session.commit()  
        flash('Registration successful! Please log in.', 'success')  
        return redirect(url_for('login'))  
    return render_template('register.html')  

@app.route('/login', methods=['GET', 'POST'])  
def login():  
    if request.method == 'POST':  
        username = request.form.get('username')  
        password = request.form.get('password')
        print(f"Login attempt with username: {username}")  # Debugging line
        user = User.query.filter_by(username=username).first()  
        if user:
            print(f"User found: {user.username}")  # Debugging line
            if pwd_context.verify(password, user.password):
                session['user_id'] = user.id 
                print(f"Password matched for user: {username}")
                return redirect(url_for('dashboard')) 
            else:
                print("Password does not match")  # Debugging line
        else:
            flash('Invalid username or password', 'danger')  
    return render_template('login.html')  

@app.route('/logout')  
def logout():  
    session.pop('user_id', None)  
    flash('You have been logged out.', 'success')  
    return redirect(url_for('login'))  

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)

