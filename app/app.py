from datetime import datetime
from flask import Flask
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

app.config['SECRET_KEY'] = '9e248f39acbe5154cec120cccd988e6c'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///internships.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static'
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024


db = SQLAlchemy(app)
migrate = Migrate(app, db)

import routes, models