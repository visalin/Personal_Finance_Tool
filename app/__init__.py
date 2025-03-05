from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import Config
from flask_migrate import Migrate
# Importing pymysql if using PyMySQL as the MySQL driver
import pymysql
pymysql.install_as_MySQLdb()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'
    
    # Load configuration
    config = Config()
    app.config.from_object(config)
    
    return app

app = create_app()
db = SQLAlchemy(app)

from app import routes
