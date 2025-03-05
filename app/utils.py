from functools import wraps
from flask import session, redirect, url_for
from app import db
from app.models import SetBudget, Expense
from sqlalchemy import func
from functools import wraps
from app import app

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


def calculate_budget_summary(user_id):
    budget_data = db.session.query(
        SetBudget.month,
        SetBudget.amount.label('total_budget'),
        func.sum(Expense.amount).label('total_expenses')
    ).outerjoin(Expense, db.and_(
        SetBudget.user_id == Expense.user_id,
        func.date_format(Expense.date, '%Y-%m') == SetBudget.month
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

    return budget_summary
