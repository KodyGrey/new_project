from flask import Flask, request, url_for, redirect, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, IntegerField
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


@app.route('/<string:title>')
@app.route('/index/<string:title>')
def index(title):
    return render_template('base.html', title=title)


@app.route('/training/<string:prof>')
def training(prof):
    return render_template('training.html', prof=prof)


@app.route('/list_prof/<list>')
def list_prof(list):
    professions = ['инженер исследователь', 'пилот', 'строитель', 'экзобиолог', 'врач']
    return render_template('list_prof.html', list=list, professions=professions)


@app.route('/answer')
@app.route('/auto_answer')
def answer():
    dtc = {
        'title': 'Анкета',
        'surname': 'Букин',
        'name': 'Геннадий',
        'education': 'начально',
        'profession': 'бизнесмен',
        'sex': 'мужской',
        'motivation': 'Хочу подальше от Земли',
        'ready': True
    }
    return render_template('answer.html', title=dtc['title'], dtc=dtc)


class LoginForm(FlaskForm):
    astronaut_id = StringField('Id астронавта', validators=[DataRequired()])
    astronaut_password = PasswordField('Пароль астронавта', validators=[DataRequired()])
    captain_id = StringField('Id капитана', validators=[DataRequired()])
    captain_password = PasswordField('Пароль капитана', validators=[DataRequired()])
    submit = SubmitField('Доступ')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect('/success')
    return render_template('login.html', title='Аварийный доступ', form=form)


@app.route('/distribution')
def distribution():
    lst = ['Gennadiy Bukin', 'Alex Miller', 'Kody Grey']
    return render_template('distribution.html', list=lst)


@app.route('/table_params/<string:sex>/<int:age>')
def table(sex, age):
    return render_template('table.html', sex=sex, age=age)


class ImageField(FlaskForm):
    file = FileField('Загрузить картинку')
    submit = SubmitField('Добавить')


mars_landscape_images = ['mars1.jpg']


@app.route('/gallery', methods=['GET', 'POST'])
def gallery():
    global mars_landscape_images
    form = ImageField()
    if form.validate_on_submit():
        f = form.file.data
        filename = secure_filename(f.filename)
        f.save(f'static/img/{filename}')
        mars_landscape_images.append(filename)
        return redirect('/gallery')
    return render_template('gallery.html', form=form, lst=mars_landscape_images)


@app.route('/member')
def member():
    with open('templates/members.json', encoding='utf-8') as f:
        dtc = json.load(f)
    return render_template('member.html', dtc=dtc)


@app.route('/')
def jobs_table():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs)
    return render_template('jobs_table.html', jobs=jobs)


class RegisterForm(FlaskForm):
    email = StringField('Login/email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    repeated_password = PasswordField('Repeat password', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    position = StringField('Position', validators=[DataRequired()])
    speciality = StringField('Speciality', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = User()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', form=form,
                                   error_message="User is already exists")
        user.email = form.email.data
        if form.password.data != form.repeated_password.data:
            return render_template('register.html', form=form,
                                   error_message="Passwords doesn't match")
        user.set_password(form.password.data)
        user.surname = form.surname.data
        user.name = form.name.data
        user.age = form.age.data
        user.position = form.position.data
        user.speciality = form.speciality.data
        user.address = form.address.data
        db_sess.add(user)
        db_sess.commit()

    return render_template('register.html', form=form)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
