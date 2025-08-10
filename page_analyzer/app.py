import os

from dotenv import load_dotenv
from flask import Flask

from .handlers import handlers_blueprint

load_dotenv()
app = Flask(__name__)
app.register_blueprint(handlers_blueprint)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

