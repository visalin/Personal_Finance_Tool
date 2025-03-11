from flask import render_template, request, redirect, url_for, flash, session
from app import app, db
from app.models import User, Expense, SetBudget, BudgetCategory
from app.utils import login_required, calculate_budget_summary
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from passlib.context import CryptContext


# Create a CryptContext with the scrypt scheme, matching your hash format
pwd_context = CryptContext(
    schemes=["scrypt"],
    default="scrypt",
    hash__scrypt__salt_size=32
)

categories = ['Food', 'Transport', 'Utilities', 'Entertainment', 'Health', 'KidToys', 'KidEducation', 'KidClothing', 'KidFood', 'KidHealth', 'KidTransport', 'KidUtilities', 'KidEntertainment', 'KidOthers', 'CreditCardBill', 'Loan', 'Insurance', 'Rent', 'Mortgage', 'clothing','shopping','Others']

# Home route
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    expenses = Expense.query.filter_by(user_id=user_id).order_by(Expense.date.desc()).all()
    user = User.query.get(user_id)

    # Calculate total budget, expenses, and savings for all months
    budget_data = db.session.query(
        SetBudget.month,
        SetBudget.amount.label('total_budget'),
        db.func.sum(Expense.amount).label('total_expenses')
    ).outerjoin(Expense, db.and_(
        SetBudget.user_id == Expense.user_id,
        db.func.date_format(Expense.date, '%Y-%m') == SetBudget.month
    )).filter(SetBudget.user_id == user_id).group_by(SetBudget.month).all()

    budget_summary = []
    for data in budget_data:
        total_budget = data.total_budget or 0.0
        total_expenses = data.total_expenses or 0.0
        savings = total_budget - total_expenses
        budget_summary.append({
            'month': data.month,
            'total_budget': total_budget,
            'total_expenses': total_expenses,
            'savings': savings
        })

    budget_categories = BudgetCategory.query.filter_by(user_id=user_id).all()

    # Calculate the remaining amount for each budget category
    for category in budget_categories:
        total_expenses_category = db.session.query(db.func.sum(Expense.amount)).filter_by(user_id=user_id, category=category.category).scalar() or 0.0
        category.current_amount = category.target_amount - total_expenses_category

    return render_template('dashboard.html', expenses=expenses, firstname=user.firstname,lastname=user.lastname, budget_categories=budget_categories, categories=categories, budget_summary=budget_summary)

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
        return redirect(url_for('dashboard'))
    return render_template('add_expense.html', categories=categories)

# User registration and login routes
@app.route('/register', methods=['GET', 'POST'])  
def register():  
    if request.method == 'POST': 
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        username = request.form.get('username')   
        password = request.form.get('password')
        hashed_password = pwd_context.hash(password)  # Use scrypt hashing
        user = User(firstname=firstname,lastname=lastname,email=email,username=username, password=hashed_password)
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


@app.route('/Setbudget', methods=['GET', 'POST'])
@login_required
def Setbudget():
    if request.method == 'POST':
        amount = request.form.get('amount')
        print (amount)
        month = request.form.get('month')
        print (month)

        if not amount or not month:
            flash('All fields are required!', 'danger')
            return redirect(url_for('dashboard'))

        try:
            amount = float(amount)
        except ValueError:
            flash('Invalid amount entered!', 'danger')
            return redirect(url_for('dashboard'))

        user_id = session['user_id']

        # Check if a budget already exists for the month
        existing_budget = SetBudget.query.filter_by(user_id=user_id, month=month).first()
        print (existing_budget)
        if existing_budget:
            existing_budget.amount = amount
            print (existing_budget.amount)
        else:
            new_budget = SetBudget(user_id=user_id, amount=amount, month=month)
            print (new_budget)
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


        # Check if the category already exists for the user
        existing_category = BudgetCategory.query.filter_by(user_id=user_id, category=category, target_date=target_date).first()
        if existing_category:
            existing_category.target_amount = target_amount
        else:
            # Create a new Budget Category
            new_category = BudgetCategory(user_id=user_id, category=category, target_amount=target_amount, target_date=target_date)
            db.session.add(new_category)
        db.session.commit()
        flash('Budget category set successfully!', 'success')
        return redirect(url_for('dashboard'))

    # Get all budget categories for the user
    budget_categories = BudgetCategory.query.filter_by(user_id=user_id).all()
    return render_template('dashboard.html', categories=categories, budget_categories=budget_categories)


# Route for the "Forgot Password" page
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        
        user = User.query.filter_by(email=email).first()  # Check if the email exists in the database
        if user:
            # If the email exists, redirect to the reset password page (without any token or email)
            return redirect(url_for('reset_password', email=email))
        else:
            flash('Email address not found!', 'danger')
            return redirect(url_for('forgot_password'))  # Stay on the same page if email not found
    
    return render_template('forgot_password.html')


# Route for the "Reset Password" page
@app.route('/reset_password/<email>', methods=['GET', 'POST'])
def reset_password(email):
    if request.method == 'POST':
        new_password = request.form.get('password')
        
        # Find the user by the email passed in the URL
        user = User.query.filter_by(email=email).first()
        
        if user:
            hashed_password = pwd_context.hash(new_password) 
            user.password = hashed_password
            db.session.commit()  # Save the new password to the database
            flash('Your password has been updated!', 'success')
            return redirect(url_for('login'))  # Redirect to login page after password reset
        else:
            flash('User not found.', 'danger')
            return redirect(url_for('forgot_password'))  # If user not found, go back to the forgot password page
    
    return render_template('reset_password.html', email=email)