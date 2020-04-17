from data import db_session
from flask import Flask, render_template, request, redirect, flash, url_for
from data.__all_models import *
from data.users import User
from flask_login import login_user, logout_user, current_user, login_required, LoginManager
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db_session.global_init("db/memehub.sqlite")
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/', methods=['POST', 'GET'])
def index():
    data = [{'author_name': 'AuthorName1', 'author_img': '../../static/img/img2.jpg', 'date': '01.01.2020',
             'note': 'NoteAboveMeme', 'meme_img': '../../static/img/img1.jpg', 'likes': 123, 'reposts': 321,
             'is_liked': True, 'is_reposted': True},
            {'author_name': 'AuthorName2', 'author_img': '../../static/img/img1.jpg', 'date': '02.02.2022',
             'note': 'NoteAboveMeme', 'meme_img': '../../static/img/img2.jpg', 'likes': 123, 'reposts': 321,
             'is_liked': True, 'is_reposted': True}
            ]
    return render_template('main.html', data=data, current_user=current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        flash("Неправильный логин или пароль")
        return render_template('login.html', form=form, title='Авторизация', current_user=current_user)
    return render_template('login.html', form=form, title='Авторизация', current_user=current_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.rep_password.data:
            flash("Пароли не совпадают")
            return render_template('register.html', title='Регистрация', form=form, current_user=current_user)
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            flash("Этот e-mail уже используется!")
            return render_template('register.html', title='Регистрация', form=form, current_user=current_user)

        if form.avatar.data:
            filename = secure_filename(form.avatar.data.filename)
            form.avatar.data.save('images/avatars/' + form.alias.data + "_" + filename)
            fn = form.alias.data + "_" + filename
        else:
            fn = None
        user = User(
            email=form.email.data,
            alias=form.alias.data,
            about=form.about.data,
            bdate=form.bdate.data,
            avatar=fn
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form, current_user=current_user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
