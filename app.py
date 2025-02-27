from flask import Flask, render_template, request, redirect, url_for, flash, session  
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash  
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finances.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

    def set_password(self, password):  
        self.password = generate_password_hash(password)  

    def check_password(self, password):  
        return check_password_hash(self.password, password)  

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, default=datetime, nullable=False)  

# Initialize the database
@app.before_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    expenses = Expense.query.filter_by(user_id=user_id).order_by(Expense.date.desc()).all()
    user = User.query.get(user_id)
    return render_template('dashboard.html', expenses=expenses, username=user.username)


@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        description = request.form.get('description')
        amount = float(request.form.get('amount'))
        category = request.form.get('category')
        date_str = request.form.get('date')
        date=datetime.strptime(date_str, '%Y-%m-%d').date()  # Convert string to date object
        userid = session['user_id']

        new_expense = Expense(user_id=userid, description=description, amount=amount, category=category, date=date)  # Assuming user ID 1 for now
        db.session.add(new_expense)
        db.session.commit()
        flash('Expense added successfully!', 'success')
        return redirect(url_for('add_expense'))
    else: 
        return render_template('add_expense.html')

# New routes for user registration, login, and logout
@app.route('/register', methods=['GET', 'POST'])  
def register():  
    if request.method == 'POST':  
        username = request.form.get('username')  
        password = request.form.get('password')  
        user = User(username=username)  
        user.set_password(password)  
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
        user = User.query.filter_by(username=username).first()  
        if user and user.check_password(password):  
            session['user_id'] = user.id 
            #flash(f'Hello {user.username}, Welcome to the Personal Finance Tracker!', 'success')
            return redirect(url_for('dashboard')) 
        else:
            flash('Invalid username or password', 'danger')  
    return render_template('login.html')  

@app.route('/logout')  
def logout():  
    session.pop('user_id', None)  
    flash('You have been logged out.', 'success')  
    return redirect(url_for('login'))  

if __name__ == '__main__':
        app.run(debug=True)

