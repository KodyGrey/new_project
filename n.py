from flask import Flask, request, url_for, redirect, render_template, abort
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, IntegerField, \
    BooleanField, DateField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
from data import db_session
from data.users import User
from data.jobs import Jobs
from data.departments import Department
from data.category import Category
from flask_login import LoginManager, login_required, login_user, logout_user, \
    current_user
import datetime
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'poprobuy_vzlomat'
db_session.global_init('db/mission_mars.db')
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


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
        login_user(user)
        return redirect('/')

    return render_template('register.html', form=form)


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        return render_template('login.html', form=form, message='Wrong password or email')

    return render_template('login.html', form=form)


class AddJob(FlaskForm):
    job = StringField('Job name', validators=[DataRequired()])
    team_leader = IntegerField('Team Leader ID', validators=[DataRequired()])
    work_size = IntegerField('Work size in hours', validators=[DataRequired()])
    collaborators = StringField('Collaborators IDs', validators=[DataRequired()])
    category = IntegerField('Hazard category ID', validators=[DataRequired()])
    is_finished = BooleanField('Is job finished?')
    submit = SubmitField('Add')


@app.route('/add_job', methods=["GET", "POST"])
def add_job():
    form = AddJob()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        job = Jobs()
        job.team_leader = form.team_leader.data
        job.job = form.job.data
        job.work_size = form.work_size.data
        job.collaborators = form.collaborators.data
        job.is_finished = form.is_finished.data
        category = db_sess.query(Category).filter(
            Category.id == form.category.data).first()
        job.category.append(category)
        db_sess.add(job)
        db_sess.commit()
        return redirect('/')

    return render_template('add_job.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/edit_job/<int:job_id>', methods=["GET", "POST"])
@login_required
def edit_job(job_id):
    form = AddJob()
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).filter(Jobs.id == job_id).first()
    if current_user.id not in [1, job.team_leader]:
        abort(404)
    if form.validate_on_submit():
        job.team_leader = form.team_leader.data
        job.is_finished = form.is_finished.data
        job.job = form.job.data
        job.collaborators = form.collaborators.data
        job.work_size = form.work_size.data
        job.category.remove(
            db_sess.query(Category).filter(Category.id == job.category[0].id).first())
        category = db_sess.query(Category).filter(
            Category.id == form.category.data).first()
        job.category.append(category)
        db_sess.commit()
        return redirect('/')
    form.category.data = job.category[0].id
    form.team_leader.data = job.team_leader
    form.is_finished.data = job.is_finished
    form.job.data = job.job
    form.collaborators.data = job.collaborators
    form.work_size.data = job.work_size

    return render_template('add_job.html', form=form)


@app.route('/delete_job/<int:job_id>')
@login_required
def delete_job(job_id):
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).filter(Jobs.id == job_id).first()
    if current_user.id in [1, job.team_leader]:
        db_sess.delete(job)
        db_sess.commit()
    return redirect('/')


@app.route('/departments')
def department_table():
    db_sess = db_session.create_session()
    departments = db_sess.query(Department)
    return render_template('departments_table.html', departments=departments)


class AddDepartment(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    chief = IntegerField('Chief ID', validators=[DataRequired()])
    members = StringField('Members')
    email = EmailField('Department Email', validators=[DataRequired()])
    submit = SubmitField('Add')


@app.route('/add_department', methods=["GET", "POST"])
def add_department():
    form = AddDepartment()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        department = Department()
        department.title = form.title.data
        department.chief = form.chief.data
        department.members = form.members.data
        department.email = form.email.data
        db_sess.add(department)
        db_sess.commit()
        return redirect('/departments')

    return render_template('add_department.html', form=form)


@app.route('/edit_department/<int:department_id>', methods=["GET", "POST"])
@login_required
def edit_department(department_id):
    form = AddDepartment()
    db_sess = db_session.create_session()
    department = db_sess.query(Department).filter(Department.id == department_id).first()
    if current_user.id not in [1, department.chief]:
        abort(404)
    if form.validate_on_submit():
        department.title = form.title.data
        department.chief = form.chief.data
        department.members = form.members.data
        department.email = form.email.data
        db_sess.commit()
        return redirect('/departments')
    form.title.data = department.title
    form.chief.data = department.chief
    form.members.data = department.members
    form.email.data = department.email

    return render_template('add_department.html', form=form)


@app.route('/delete_department/<int:department_id>')
@login_required
def delete_department(department_id):
    db_sess = db_session.create_session()
    department = db_sess.query(Department).filter(Department.id == department_id).first()
    if current_user.id in [1, department.chief]:
        db_sess.delete(department)
        db_sess.commit()
    return redirect('/departments')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
