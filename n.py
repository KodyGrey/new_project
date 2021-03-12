from flask import Flask, request, url_for, redirect, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
from data import db_session
from data.users import User
from data.jobs import Jobs
import datetime
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'poprobuy_vzlomat'
db_session.global_init('db/mission_mars.db')


@app.route('/')
def jobs_table():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs)
    return render_template('jobs_table.html', jobs=jobs)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
