import os

import psycopg2
import validators
from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

app = Flask(__name__)
app.config.from_pyfile('config.py')


def connect_database():
    load_dotenv()
    DATABASE_URL = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(DATABASE_URL)
    return conn


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html',
                           url = '')


@app.route('/', methods=['POST'])
def post_url():
    data = request.form.to_dict()
    url = data['url']
    correct_url = validators.url(url)
    correct_length = True if len(url) < 255 else False
    # correct_length = validators.length(url, 0, 255) ПОЧЕМУ НЕ РАБОТАЕТ???

    if correct_url is True and correct_length:
        conn = connect_database()
        sql = "INSERT INTO urls (name) VALUES (%s);"

        with conn.cursor() as curs:
            curs.execute(sql, (data['url'], ))
        flash("Страница успешно добавлена", "success")
        return redirect(url_for("index"))
    
    flash("Некорректный URL", "error")
    return render_template('index.html',
                           url = url), 422


"""@app.route('/urls', methods = ['GET'])
def urls_list():
    sql = 'SELECT id, name FROM urls;'
    conn = connect_database()
    with conn.cursor() as curs:
        curs.execute(sql)
        data = curs.fetchall()
    return render_template('urls.html',
                           urls = data)



@app.route('/urls/<int:id>', methods = ['GET'])
def get_url_info(id):
    return render_template('url.html')

def create_table(conn):
    sql = '''
    CREATE TABLE urls (
        id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
        name varchar(255) NOT NULL,
        created_at TIMESTAMP
    );'''
    with conn.cursor() as curs:
        curs.execute(sql)"""



