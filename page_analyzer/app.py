import os
from datetime import datetime
from urllib.parse import urlparse

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


def validate_url(url: str) -> bool:
    correct_url = validators.url(url)
    correct_length = True if len(url) < 255 else False
    # correct_length = validators.length(url, 0, 255) ПОЧЕМУ НЕ РАБОТАЕТ???
    if correct_url is True and correct_length:
        return True
    return False


def normalize_url(url: str) -> str:
    lowercase_url = url.lower()
    normalized_url = urlparse(lowercase_url)
    return f'{normalized_url.scheme}://{normalized_url.netloc}'


def check_is_not_double(url: str) -> bool | int:
    conn = connect_database()
    sql = "SELECT * FROM urls WHERE name = (%s);"
    with conn.cursor() as curs:
        curs.execute(sql, (url, ))
        conn.commit()
        id = curs.fetchone()
        conn.close()
        if id is None:
            return True
        return id[0]


def save_to_db(website):
    pass


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html',
                           url='')


@app.route('/', methods=['POST'])
def post_url():
    data = request.form.to_dict()
    url = data['url']
    normalized_url = normalize_url(url)
    correctness = validate_url(normalized_url)
    doubleness = check_is_not_double(normalized_url)
    if doubleness is not True:
        flash("Страница уже существует", "info")
        return redirect(url_for("get_url_info", id=doubleness))
    if correctness:
        conn = connect_database()
        sql = """INSERT INTO urls (name, created_at) 
                VALUES (%s, %s) RETURNING id;"""
        with conn.cursor() as curs:
            curs.execute(sql, (url, datetime.now(), ))
            conn.commit()
            id = curs.fetchone()[0]
            conn.close()
        flash("Страница успешно добавлена", "success")
        return redirect(url_for("get_url_info", id=id))
    
    flash("Некорректный URL", "error")
    return render_template('index.html',
                           url=url), 422


@app.route('/urls/<int:id>', methods=['GET'])
def get_url_info(id):
    sql = 'SELECT id, name, created_at FROM urls WHERE urls.id = (%s);'
    conn = connect_database()
    with conn.cursor() as curs:
        curs.execute(sql, (id, ))
        conn.commit()
        data = curs.fetchall()
        conn.close()
    return render_template('url_id.html',
                           data=data)


@app.route('/urls', methods=['GET'])
def urls_list():
    sql = 'SELECT id, name FROM urls ORDER BY id DESC;'
    conn = connect_database()
    with conn.cursor() as curs:
        curs.execute(sql)
        data = curs.fetchall()
        conn.commit()
        conn.close()
    return render_template('urls.html',
                           urls=data)


def create_table():
    sql = '''
    CREATE TABLE urls (
        id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
        name VARCHAR(255) NOT NULL,
        created_at NOT NULL
    );'''
    conn = connect_database()
    with conn.cursor() as curs:
        curs.execute(sql)
        conn.commit()
        conn.close()
