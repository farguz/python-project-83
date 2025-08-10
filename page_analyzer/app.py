import os

from dotenv import load_dotenv
from flask import Flask

app = Flask(__name__)
load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

