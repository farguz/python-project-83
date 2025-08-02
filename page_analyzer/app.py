from flask import Flask, render_template
import psycopg2
import os
from dotenv import load_dotenv

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

# temporary
@app.route('/urls')
def urls():
    return render_template('urls.html')

@app.route('/url/<int:id>')
def url():
    return render_template('url.html')