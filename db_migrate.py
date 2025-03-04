import os
import subprocess
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv

# Importing pymysql if using PyMySQL as the MySQL driver
import pymysql
pymysql.install_as_MySQLdb()

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Load the database configuration from environment variables
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}@{os.environ['DB_HOST']}/{os.environ['DB_NAME']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Import your models here
from app import  Budget, Expense, FinancialGoal

def perform_migration():
    with app.app_context():
        # Set the FLASK_APP environment variable
        os.environ['FLASK_APP'] = 'db_migrate.py'
        
        # Initialize the migration repository if it doesn't exist
        if not os.path.exists('migrations'):
            subprocess.run(["flask", "db", "init"], check=True)
        
        # Apply any pending migrations
        subprocess.run(["flask", "db", "upgrade"], check=True)
        
        # Generate a new migration if there are changes to the models
        subprocess.run(["flask", "db", "migrate", "-m", "Initial migration"], check=True)
        
        # Apply the new migration to the database
        subprocess.run(["flask", "db", "upgrade"], check=True)

if __name__ == '__main__':
    perform_migration()