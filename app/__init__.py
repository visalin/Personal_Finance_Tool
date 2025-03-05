from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# Importing pymysql if using PyMySQL as the MySQL driver
import pymysql
pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.config.from_object('app.config.Config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes
