import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
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
migrate = Migrate(app, db)

# Create a CryptContext with the scrypt scheme, matching your hash format
pwd_context = CryptContext(
    schemes=["scrypt"],
    default="scrypt",
    hash__scrypt__salt_size=32
)

categories = ['Food', 'Transport', 'Utilities', 'Entertainment', 'Health', 'KidToys', 'KidEducation', 'KidClothing', 'KidFood', 'KidHealth', 'KidTransport', 'KidUtilities', 'KidEntertainment', 'KidOthers', 'CreditCardBill', 'Loan', 'Insurance', 'Rent', 'Mortgage', 'Others']

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

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

class BudgetCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    target_date = db.Column(db.Date, nullable=False)
    user = db.relationship('User', backref=db.backref('budget_categories', lazy=True))

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
    budget_categories = BudgetCategory.query.filter_by(user_id=user_id).all()

    # Calculate the remaining amount for each budget category
    for category in budget_categories:
        total_expenses = db.session.query(db.func.sum(Expense.amount)).filter_by(user_id=user_id, category=category.category).scalar() or 0.0
        category.current_amount = category.target_amount - total_expenses

    return render_template('dashboard.html', expenses=expenses, username=user.username, budget_categories=budget_categories, categories=categories)

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
    return render_template('add_expense.html', categories=categories)

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


@app.route('/budget', methods=['GET', 'POST'])
@login_required
def budget():
    if request.method == 'POST':
        amount = request.form.get('amount')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')

        if not amount or not start_date_str or not end_date_str:
            flash('All fields are required!', 'danger')
            return redirect(url_for('dashboard'))

        try:
            amount = float(amount)
        except ValueError:
            flash('Invalid amount entered!', 'danger')
            return redirect(url_for('dashboard'))

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        user_id = session['user_id']

        new_budget = Budget(user_id=user_id, amount=amount, start_date=start_date, end_date=end_date)
        db.session.add(new_budget)
        db.session.commit()
        flash('Budget set successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('dashboard.html')

@app.route('/budget_categories', methods=['GET', 'POST'])
@login_required
def budget_categories():
    user_id = session['user_id']
    
    if request.method == 'POST':
        category = request.form.get('category')
        target_amount = request.form.get('target_amount')
        target_date_str = request.form.get('target_date')

        if not category or not target_amount or not target_date_str:
            flash('All fields are required!', 'danger')
            return redirect(url_for('dashboard'))

        try:
            target_amount = float(target_amount)
        except ValueError:
            flash('Invalid target amount entered!', 'danger')
            return redirect(url_for('dashboard'))

        target_date = datetime.strptime(target_date_str, '%Y-%m').date()

        # Create a new Budget Category
        new_category = BudgetCategory(user_id=user_id, category=category, target_amount=target_amount, target_date=target_date)
        db.session.add(new_category)
        db.session.commit()
        flash('Budget category set successfully!', 'success')
        return redirect(url_for('dashboard'))

    # Get all budget categories for the user
    budget_categories = BudgetCategory.query.filter_by(user_id=user_id).all()
    return render_template('dashboard.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)