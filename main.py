from flask import Flask, render_template, request, redirect, flash, url_for
from data.__all_models import *
from data.users import User
from flask_login import login_user, logout_user, current_user, login_required, LoginManager
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request
from data import db_session
from auxiliary import avatar_convert
from werkzeug.utils import secure_filename
from flask_restful import abort
from data.tags import Tag

ROLES = ['user', 'moder', 'admin']
DATA = {'info': {'is_auth': True, 'user_img': '../../static/img/img1.jpg', 'username': 'User'},
        'content': [
            {'type': 'meme', 'id': '1', 'author_name': 'AuthorName1', 'author_img': '../../static/img/img2.jpg',
             'date': '01.01.2020',
             'note': '', 'meme_img': '../../static/img/img1.jpg', 'likes': 3674,
             'reposts': 25,
             'is_liked': False, 'is_reposted': True, 'category': 'category1', 'place': 13, 'delete': False},
            {'type': 'meme', 'id': '2', 'author_name': 'AuthorName2', 'author_img': '../../static/img/img1.jpg',
             'date': '02.02.2022',
             'note': 'NoteAboveMeme2', 'meme_img': '../../static/img/img2.jpg', 'likes': 277,
             'reposts': 178,
             'is_liked': True, 'is_reposted': False, 'category': 'category2', 'place': 0, 'delete': True},
            {'type': 'repost', 'id': '3', 'delete': True, 'author_name': 'AuthorName3',
             'author_img': '../../static/img/img1.jpg',
             'date': '02.02.2022', 'reposted_content': {'id': '2', 'author_name': 'AuthorName2',
                                                        'author_img': '../../static/img/img1.jpg',
                                                        'date': '02.02.2022',
                                                        'note': 'NoteAboveMeme2',
                                                        'meme_img': '../../static/img/img2.jpg',
                                                        'likes': 277,
                                                        'reposts': 178,
                                                        'is_liked': True, 'is_reposted': False,
                                                        'category': 'category2',
                                                        'place': 0, 'delete': False}}]
        }

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db_session.global_init("db/memehub.sqlite")
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/', methods=['GET', 'POST'])
def index():
    # в info информация о пользователе:
    # is_auth авторизирован или нет
    # user_img путь к аватарке пользователя
    # username имя пользователя

    # в content информация о мемах
    # в type там может быть или 'meme' или 'repost'
    # id номер публикации
    # autor_name имя автора
    # autor_img путь к аватарке автора
    # date дата
    # note подпись к публикации
    # meme_img путь к мему
    # likes/reposts количество лайков/репостов
    # is_liked/is_reposted поставлен ли лайк/репост
    # category категория
    # place место в топе, если 0, то ничего не отображается
    # delete наличие или отсутствие кнопки удаления

    # если публикация является репостом, то в reposted_content содержиться информация о репостнутой публикации
    data = DATA
    return render_template('main.html', data=data, title='Главная')


@app.route('/post', methods=['POST'])
def post():
    if request:
        print(request.json)
    return 'return'


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Механизм авторизации пользователя"""
    form = LoginForm()
    if form.validate_on_submit():
        # Если нажата кнопка (POST-запрос)
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            # Если данные валидные, логиним пользователя
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        # Иначе кидаем ошибку
        flash("Неправильный логин или пароль")
        return render_template('login.html', form=form, title='Авторизация', current_user=current_user, data=DATA)
    # Если GET-запрос
    # Просто выводим страницу авторизации
    return render_template('login.html', form=form, title='Авторизация', current_user=current_user, data=DATA)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Механизм регистрации пользователя"""
    form = RegisterForm()
    if form.validate_on_submit():
        # Если кнопка нажата (POST-запрос)
        if form.password.data != form.rep_password.data:
            # Если пароли не совпадают, сообщаем пользователю
            flash("Пароли не совпадают")
            return render_template('register.html', title='Регистрация', form=form, current_user=current_user,
                                   data=DATA)

        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            # Если e-mail уже занят, сообщаем пользователю
            flash("Этот e-mail уже используется!")
            return render_template('register.html', title='Регистрация', form=form, current_user=current_user,
                                   data=DATA)

        if form.avatar.data:
            # Если загружена аватарка, обрабатываем и сохраняем её
            filename = secure_filename(form.avatar.data.filename)
            form.avatar.data.save('images/avatars/' + form.alias.data + "_" + filename)
            fn = form.alias.data + "_" + filename
            try:
                avatar_convert.convert('images/avatars/' + fn)
            except FileNotFoundError:
                fn = None

        else:
            fn = None

        # Создаём нового пользоваетля
        user = User(
            email=form.email.data,
            alias=form.alias.data,
            about=form.about.data,
            bdate=form.bdate.data,
            avatar=fn
        )
        user.set_password(form.password.data)

        # и добавляем его в БД
        session.add(user)

        # Сохраняем изменения
        session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form, current_user=current_user, data=DATA)


@app.route('/logout')
@login_required
def logout():
    """Выход пользователя из аккаунта"""
    logout_user()
    return redirect("/")


@app.route('/addtag', methods=['GET', 'POST'])
def addtag():
    """Механизм добавления тега"""
    form = TagAddingForm()
    sess = db_session.create_session()

    if not current_user.is_authenticated:
        # Если пользователь не вошёл в систему, кидаем ошибку
        abort(401, message="Пожалуйста, авторизуйтесь!")

    elif ROLES[sess.query(User).get(current_user.get_id()).role] != 'admin':
        # Если пользователь не админ, кидаем ошибку
        abort(423, message="Только администратор может добавлять теги!")

    # Если пользователь имеет права, идём дальше

    elif form.validate_on_submit():
        # Если кнопка нажата (POST-запрос)
        sess.add(Tag(title=form.title.data))
        sess.commit()
        flash("Тег успешно добавлен")
        return redirect('/addtag')

    else:
        # GET-запрос
        return render_template('tag_adding.html', title='Добавить тег', form=form, current_user=current_user, data=DATA)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
