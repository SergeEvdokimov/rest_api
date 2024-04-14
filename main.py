import requests

from data.jobs import Jobs
from data.users import User
from data.departments import Department
from data.jobs_resource import JobsResource, JobsListResource
from data.users_resource import UsersResource, UsersListResource

from forms.user import RegisterForm
from forms.new_job import NewJobForm
from forms.login_form import LoginForm
from forms.new_dep import NewDepartForm

from data import db_session, jobs_api, user_api

from flask_restful import Api
from flask import request, Flask, render_template, redirect, abort, make_response, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

API_KEY = '40d1649f-0493-4b70-98ba-98533de7710b'

api.add_resource(UsersListResource, '/api/v2/users')
api.add_resource(UsersResource, '/api/v2/users/<int:users_id>')
api.add_resource(JobsListResource, '/api/v2/jobs')
api.add_resource(JobsResource, '/api/v2/jobs/<int:job_id>')

login_manager = LoginManager()
login_manager.init_app(app)


def geocode(point):
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/"
    geocoder_params = {"apikey": API_KEY, "geocode": point, "format": "json"}

    response = requests.get(geocoder_request, params=geocoder_params)

    if response:
        json_response = response.json()
    else:
        raise RuntimeError(f"""Ошибка выполнения запроса: {geocoder_request}
        Http статус: {response.status_code} ({response.reason})""")

    features = json_response["response"]["GeoObjectCollection"]["featureMember"]
    return features[0]["GeoObject"] if features else None


def adjust_ll_span(address):
    toponym = geocode(address)
    if not toponym:
        return None, None

    envelope = toponym["boundedBy"]["Envelope"]

    left, bottom = envelope["lowerCorner"].split()
    right, top = envelope["upperCorner"].split()

    width = abs(float(left) - float(right))
    height = abs(float(top) - float(bottom))

    return ",".join(toponym["Point"]["pos"].split()), f"{width/2},{height/2}"


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Wrong login or password", form=form)
    return render_template('login.html', title='Authorization', form=form)


@app.route("/")
@app.route("/index")
def index():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).all()
    users = db_sess.query(User).all()
    names = {name.id: (name.surname, name.name) for name in users}
    return render_template("index.html", jobs=jobs, names=names, title='Work log')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form, message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        user = User(name=form.name.data, surname=form.surname.data, email=form.email.data, age=form.age.data,
                    position=form.position.data, speciality=form.speciality.data, address=form.address.data,
                    city_from = form.city_from.data)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Register form', form=form)


@app.route('/addjob', methods=['GET', 'POST'])
def new_order():
    add_form = NewJobForm()
    if add_form.validate_on_submit():
        db_sess = db_session.create_session()
        jobs = Jobs(job=add_form.job.data, team_leader=add_form.team_leader.data, work_size=add_form.work_size.data,
                    collaborators=add_form.collaborators.data, is_finished=add_form.is_finished.data,
                    category=add_form.category.data)
        db_sess.add(jobs)
        db_sess.commit()
        return redirect('/')
    return render_template('new_job.html', title='Adding new job', form=add_form)


@app.route('/jobs/<int:unic_num>', methods=['GET', 'POST'])
@login_required
def job_edit(unic_num):
    form = NewJobForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        jobs = db_sess.query(Jobs).filter(Jobs.id == unic_num,
                                          (Jobs.team_leader == current_user.id) | (current_user.id == 1)).first()
        if not jobs:
            abort(404)
        form.job.data = jobs.job
        form.team_leader.data = jobs.team_leader
        form.work_size.data = jobs.work_size
        form.collaborators.data = jobs.collaborators
        form.is_finished.data = jobs.is_finished
        form.category.data = jobs.category
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        jobs = db_sess.query(Jobs).filter(Jobs.id == unic_num,
                                          (Jobs.team_leader == current_user.id) | (current_user.id == 1)).first()
        if jobs:
            jobs.job = form.job.data
            jobs.team_leader = form.team_leader.data
            jobs.work_size = form.work_size.data
            jobs.collaborators = form.collaborators.data
            jobs.is_finished = form.is_finished.data
            jobs.category = form.category.data
            db_sess.commit()
            return redirect('/')
        abort(404)
    return render_template('new_job.html', title='Job editing', form=form)


@app.route('/job_delete/<int:unic_num>', methods=['GET', 'POST'])
@login_required
def job_delete(unic_num):
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).filter(Jobs.id == unic_num,
                                      (Jobs.team_leader == current_user.id) | current_user.id == 1).first()
    if not jobs:
        abort(404)
    db_sess.delete(jobs)
    db_sess.commit()
    return redirect('/')


@app.route("/departments")
def departments():
    session = db_session.create_session()
    deps = session.query(Department).all()
    users = session.query(User).all()
    names = {name.id: (name.surname, name.name) for name in users}
    return render_template("departments.html", departments=deps, names=names, title='List of Departments')


@app.route('/add_depart', methods=['GET', 'POST'])
def new_depart():
    add_form = NewDepartForm()
    if add_form.validate_on_submit():
        session = db_session.create_session()
        depart = Department(title=add_form.title.data, chief=add_form.chief.data,
                            members=add_form.members.data, email=add_form.email.data)
        session.add(depart)
        session.commit()
        return redirect('/')
    return render_template('new_dep.html', title='Adding new department', form=add_form)


@app.route('/departments/<int:unic_num>', methods=['GET', 'POST'])
@login_required
def depart_edit(unic_num):
    form = NewDepartForm()
    if request.method == "GET":
        session = db_session.create_session()
        depart = session.query(Department).filter(
            Department.id == unic_num, (Department.chief == current_user.id) | (current_user.id == 1)).first()
        if not depart:
            abort(404)
        form.title.data = depart.title
        form.chief.data = depart.chief
        form.members.data = depart.members
        form.email.data = depart.email
    if form.validate_on_submit():
        session = db_session.create_session()
        depart = session.query(Department).filter(
            Department.id == unic_num, (Department.chief == current_user.id) | (current_user.id == 1)).first()
        if not depart:
            abort(404)
        depart.title = form.title.data
        depart.chief = form.chief.data
        depart.members = form.members.data
        depart.email = form.email.data
        session.commit()
        return redirect('/')
    return render_template('new_dep.html', title='Department editing', form=form)


@app.route('/depart_delete/<int:unic_num>', methods=['GET', 'POST'])
@login_required
def depart_delete(unic_num):
    session = db_session.create_session()
    depart = session.query(Department).filter(Department.id == unic_num,
                                              (Department.chief == current_user.id) | (current_user.id == 1)).first()
    if not depart:
        abort(404)
    session.delete(depart)
    session.commit()
    return redirect('/')


@app.route('/users_show/<int:user_id>', methods=['GET', 'POST'])
@login_required
def show_user(user_id):
    js = requests.get(f'http://localhost:5000/api/users_show/{user_id}').json()['users']
    map_request = f"http://static-maps.yandex.ru/1.x/?ll={adjust_ll_span(js['city_from'])[0]}&spn=0.1,0.1&l=map"
    open(f'static/img/{user_id}.png', "wb").write(requests.get(map_request).content)
    return render_template("map.html", surname=js["surname"], name=js["name"], user_id=user_id, city=js['city_from'])


def main():
    db_session.global_init("db/blogs.db")
    app.register_blueprint(jobs_api.blueprint)
    app.register_blueprint(user_api.blueprint)
    app.run()

    # from data.category import Category
    #
    # user = User()
    # user.surname = "Scott"
    # user.name = "Ridley"
    # user.age = 21
    # user.position = "captain"
    # user.speciality = "research engineer"
    # user.address = "module_1"
    # user.email = "scott_chief@mars.org"
    #
    # user2 = User()
    # user2.surname = "gDsty"
    # user2.name = "Ol"
    # user2.age = 16
    # user2.position = "vice"
    # user2.speciality = "music"
    # user2.address = "module_2"
    # user2.email = "TOF@mars.org"
    #
    # user3 = User()
    # user3.surname = "SmR"
    # user3.name = "Nkt"
    # user3.age = 16
    # user3.position = "trainee"
    # user3.speciality = "CS"
    # user3.address = "module_3"
    # user3.email = "2500elo@mars.org"
    #
    # user4 = User()
    # user4.surname = "Kent"
    # user4.name = "Slavics"
    # user4.age = 16
    # user4.position = "coach"
    # user4.speciality = "gaming"
    # user4.address = "module_4"
    # user4.email = "200_by_day@mars.org"
    #
    # job = Jobs()
    # job.team_leader = 1
    # job.job = "deployment of residential modules 1 and 2"
    # job.work_size = 15
    # job.collaborators = "1, 2"
    # job.is_finished = False
    #
    # dep = Department()
    # dep.title = 'geological exploration'
    # dep.email = '1@dep.ru'
    # dep.chief = 1
    # dep.members = '1, 2, 3, 4'
    #
    # cat = Category()
    # cat.name = 'hazard category 1'
    #
    # cat2 = Category()
    # cat2.name = 'hazard category 2'
    #
    # cat3 = Category()
    # cat3.name = 'hazard category 3'
    #
    # cat4 = Category()
    # cat4.name = 'hazard category 4'
    #
    # db_sess = db_session.create_session()
    # db_sess.add(user)
    # db_sess.add(user2)
    # db_sess.add(user3)
    # db_sess.add(user4)
    # db_sess.add(job)
    # db_sess.add(dep)
    # db_sess.add(cat)
    # db_sess.add(cat2)
    # db_sess.add(cat3)
    # db_sess.add(cat4)
    # db_sess.commit()


if __name__ == '__main__':
    main()
