import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from logs.logger import logging
from dotenv import load_dotenv

load_dotenv()

try:
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = 'Frontend_operations/uploads'
    app.config['GENERATED_FOLDER'] = 'Frontend_operations/generated'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('user')
    app.config['SECRET_KEY'] = "27c1fcddffc800be09a5aff5"
    bcrypt = Bcrypt(app)
    db = SQLAlchemy(app)
    login_manager = LoginManager(app)
    login_manager.login_view = "loging_page"
    login_manager.login_message_category = "info"
    
    logging.info("Flask application configured successfully.")

except Exception as e:
    logging.error(f"An error occurred while configuring the Flask application: {e}")
    raise

import Frontend_operations.routes as routes