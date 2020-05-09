from flask import Flask, render_template, request, redirect, flash, url_for, make_response
from data.__all_models import *
from data.users import User
from data.memes import Meme
from flask_login import login_user, logout_user, current_user, login_required, LoginManager
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request
from data import db_session
from auxiliary import avatar_convert, meme_selector, user_selector
from auxiliary.user_selector import USER_TOP
from werkzeug.utils import secure_filename
from flask_restful import abort
from data.tags import Tag
from datetime import datetime
from gen_api import *
import time
from threading import Thread
import os

ROLES = ['user', 'moder', 'admin']
REFRESH_PERIOD = 12
USER_PAGE = {'is_page': True, 'user_img': '../../static/img/img1.jpg', 'type': 'me', 'role': 'moder',
             'status': 'users_status',
             'subs': 123, 'posts': 321, 'rating': 56, 'top': 15, 'username': 'User', 'user_id': 34,
             'error_message': '',
             'is_sub': True, 'is_block': False}

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


# USER_PAGE
# is_page   True/False показвать блок со страницей пользователя или нет
# user_img  путь к аве пользователя
# type  me/other, отображает страницу как личную или как чужую
# role  отображение роли, при значении '' ничего не отображается
# status    статус пользователя
# subs posts rating top кол-во подписчиков, постов, рейтинг, место в топе
# username имя пользователя
# user_id id пользователя
# error_message сообщение об ошибке(если возникла ошибка при редактировании профиля)
# is_sub is_block нажата или не нажата кнопка подписки/блокировки


def refresh_rating():
    """Функция, исполняемая по расписанию для обновления рейтинга пользователелй"""

    ses = db_session.create_session()

    while True:
        for user in ses.query(User).all():
            user.rating = user_selector.calculate_rating(user.id)

        ses.commit()
        time.sleep(REFRESH_PERIOD * 60 * 60)


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db_session.global_init("db/memehub.sqlite")
app.register_blueprint(blueprint)
login_manager = LoginManager()
login_manager.init_app(app)
Thread(target=refresh_rating).start()  # Обновление рейтингов и запуск потока


def gen_data(do_get_content=True):
    """Функция для генерации данных для подгрузки темплейта"""

    # В зависимости от того, авторизован ли пользователь, генерируем данные
    info = dict(is_auth=False)
    if current_user.is_authenticated:
        info = generate_user_info(current_user.get_id())

    if do_get_content:
        if current_user.is_authenticated:
            res = get_content(uid=current_user.get_id()).json
        else:
            res = get_content().json
    else:
        res = {}

    res['user_page'] = dict(is_page=False)
    res['info'] = info  # Совмещаем данные в один словарь
    res['k'] = res.get('k', 1)

    return res  # Возвращаем его


def get_user_page_data(username_id):
    """Функция для получения данных о пользователе"""
    session = db_session.create_session()
    user = session.query(User).filter(User.id == username_id).first()
    data = user_selector.gen_user_info(username_id, self_uid=current_user.get_id())
    data['user_img'] = '../../static/img/avatars/' + data['user_img']
    # определяется, как будет отображаться страница: как личная или как страница другого пользователя
    if current_user.is_authenticated:
        if str(current_user.get_id()) == str(username_id):
            data['type'] = 'me'
        else:
            data['type'] = 'other'
    else:
        data['type'] = 'other'
    u1 = session.query(User).get(current_user.get_id())
    if u1 and user in u1.subscribed:
        data['is_sub'] = True
    else:
        data['is_sub'] = False
    data['subs'] = len([i for i in session.query(User).all() if user in i.subscribed])
    data['posts'] = (len(list(session.query(Meme).filter(Meme.author == username_id))) +
                     len(list(session.query(Repost).filter(Repost.user == username_id))))
    try:
        data['top'] = list(session.query(User).order_by(User.rating))[::-1].index(user) + 1
    except ValueError:
        data['top'] = 0
    return data


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/top_memes')
def top_memes():
    """Топ мемов"""

    top = meme_selector.get_most_popular()
    content = get_content(uid=current_user.get_id(), data=top).json['content']

    res = gen_data(do_get_content=False)
    res['load_more'] = False
    res['content'] = content
    res['type'] = 'top'

    return render_template('main.html', data=res, title='Топ мемов')


@app.route('/top_users')
def top_users():
    """Топ пользователей"""

    ses = db_session.create_session()
    users = ses.query(User).filter(User.id != 0).order_by(User.rating).all()[::-1][:USER_TOP]

    data = gen_data(do_get_content=False)
    data['content'] = [get_user_page_data(u.id) for u in users]
    data['type'] = 'users'

    # with open('data.json', 'w') as f:
    #     print(data, file=f)

    return render_template('top_users.html', data=data, title='Топ пользователей')


@app.route('/search/<text>')
def search(text):
    """Ф-ия для реализации поиска по публикациям (тегам)"""

    data = gen_data(do_get_content=False)
    data['content'] = do_search(text, int(current_user.get_id())).json['content']
    data['type'] = 'search'
    data['search'] = text

    return render_template('main.html', data=data, title='Поиск: ' + text)


@app.route('/subscribe/<int:uid>')
def subscribe(uid):
    """Ф-ия для подписки на пользователя, id которого передан"""

    if not current_user.is_authenticated:
        abort(401, message="Вы не авторизованы!")
    else:
        ses = db_session.create_session()

        u1 = ses.query(User).get(current_user.get_id())
        u2 = ses.query(User).get(uid)
        u1.subscribed.append(u2)
        u2.subscribers.append(u1)

        ses.commit()

        return redirect('#')


@app.route('/', methods=['GET', 'POST'])
def index():
    """Главная страница"""

    data = gen_data()
    data['type'] = 'main'
    # with open('data.json', 'w', encoding='utf-8') as f:
    #     print(data, file=f)
    return render_template('main.html', data=data, title='Главная')


@app.route('/post', methods=['POST'])
def post():
    """Функция для обработки запросов лайков, репостов, и тд."""
    # в request.json
    # type - тип действия like repost delete sub unsub block unblock
    # user_id - id пользователя
    # target_id - id мема, который лайкнули/репостнули/удалили
    # или id пользователя, на которого подписались/отписались
    # или id пользователя, которого заблокировали/разблокировали
    if request:
        req = request.json
        session = db_session.create_session()
        if req['type'] == 'like':  # обработка лайков
            user = session.query(User).filter(User.id == req['user_id']).first()
            target = session.query(Meme).filter(Meme.id == req['target_id']).first()
            if target in user.liked:
                user.liked.remove(target)
            else:
                user.liked.append(target)
        elif req['type'] == 'repost':  # обработка репостов
            user = session.query(User).filter(User.id == req['user_id']).first()
            target = session.query(Meme).filter(Meme.id == req['target_id']).first()
            print('repost-test')
            if target in [session.query(Meme).filter(Meme.id == r.meme).first() for r in user.repostes]:
                # если репост уже был
                repost = session.query(Repost).filter(Repost.meme == target.id, Repost.user == user.id).first()
                user.repostes.remove(repost)
                target.repostes.remove(repost)
                session.query(Repost).filter(Repost.id == repost.id).delete()
            else:
                # если репоста не было
                print('append')
                repost = Repost(
                    title='title',
                    meme=req['target_id'],
                    user=req['user_id']
                )
                session.add(repost)
                user.repostes.append(repost)
                target.repostes.append(repost)
        elif req['type'] == 'delete':  # обработка запросов на удаление мемов
            target = session.query(Meme).filter(Meme.id == req['target_id']).first()
            # удаление лайков
            for i in target.likes:
                i.liked.remove(target)
            # удаление тегов
            for tag in session.query(Tag).all():
                if tag in list(target.tags):
                    target.tags.remove(tag)
            target.tags = []
            # удаление репостов мема
            session.query(Repost).filter(Repost.meme == target.id).delete()
            # удаление мема
            session.query(Meme).filter(Meme.id == req['target_id']).delete()
        elif req['type'] == 'sub' or req['type'] == 'unsub':  # обработка подписок
            u1 = session.query(User).get(current_user.get_id())
            u2 = session.query(User).get(req['target_id'])
            if u2 in u1.subscribed:
                u1.subscribed.remove(u2)
            else:
                u1.subscribed.append(u2)
        elif req['type'] == 'block' or req['type'] == 'unblock':  # обработка блокировок
            target = session.query(User).filter(User.id == req['target_id']).first()
            if target.is_blocked:
                target.is_blocked = False
            else:
                target.is_blocked = True
        elif req['type'] == 'delete_tag':  # обработка запросов на удаление тегов
            tag = req['target'][4:]
            _tag_ = session.query(Tag).filter(Tag.title == tag)
            tag_ = _tag_.first()
            for meme in tag_.memes:
                meme.tags.remove(tag_)
            _tag_.delete()
        session.commit()
    return 'qwerty'


@app.route('/author/<username_id>', methods=['GET', 'POST'])
def user_page(username_id):
    """Cтраница пользователя"""
    form = EditProfileForm()
    form2 = MemePublishForm()
    error_message = ''

    if form2.validate_on_submit():
        if form.alias.data == '' and form.about.data == '' and form.avatar.data is None:
            # обработка публикаций мемов

            if not current_user.is_authenticated:
                # Если пользователь не вошёл в систему, кидаем ошибку
                abort(401,
                      message="Только авторизованные пользователи могут добавлять мемы! Пожалуйста, авторизуйтесь.")

            # Сохраняем картинку
            filename = secure_filename(form2.img.data.filename)
            fn = str(datetime.now()).replace(":", "_").replace(" ", "_") + filename[-4:]
            form2.img.data.save('static/img/memes/' + fn)

            # Создаём мем
            session = db_session.create_session()
            print(form2.tags.data)
            meme = Meme(
                title=form2.note.data,
                tags=
                [session.query(Tag).filter(Tag.title == i).first() for i in form2.tags.data.replace("#", "").split()],
                author=current_user.get_id(),
                picture=fn
            )

            # for i in meme.tags:
            #     print(i.title)

            # Сохраняем
            session.add(meme)
            session.commit()

    if form.validate_on_submit():
        if not(form.alias.data == '' and form.about.data == '' and form.avatar.data is None):
            # print('profile-profile-profile')
            # print(form.alias.data)
            # print(form.about.data)
            # print(form.avatar.data)
            # обработка изменений профиля
            session = db_session.create_session()
            user = session.query(User).filter(User.id == current_user.get_id()).first()

            if form.alias.data != user.alias:  # обработка изменений имени пользователя
                if not form.alias.data:
                    error_message = 'Такое имя пользователя недопустимо'
                else:
                    if form.alias.data in [i.alias for i in session.query(User).all()]:
                        error_message = 'Такое имя пользователя уже существует'
                    else:
                        user.alias = form.alias.data

            if form.about.data != user.about:  # обработка изменений статуса
                user.about = form.about.data

            if form.avatar.data:  # обработка изменений аватарки
                filename = secure_filename(form.avatar.data.filename)
                fn = str(datetime.now()).replace(":", "_").replace(" ", "_") + filename[-4:]
                form.avatar.data.save('static/img/avatars/' + fn)
                try:
                    avatar_convert.convert('static/img/avatars/' + fn)
                except FileNotFoundError:
                    fn = None
            else:
                fn = None
            if fn is not None:
                user.avatar = fn

            session.commit()
    data = gen_data(do_get_content=False)
    id_ = int(current_user.get_id()) if current_user.is_authenticated else 0
    data['content'] = get_user_content(username_id, id_).json['content']
    data['user_page'] = get_user_page_data(username_id)
    data['user_page']['error_message'] = error_message
    data['type'] = 'page'

    if data['user_page']['role'] == 'user':
        data['user_page']['role'] = ''

    session = db_session.create_session()
    data['user_page']['tags'] = [i.title for i in session.query(Tag).all()]

    return render_template('main.html', data=data, title=data['user_page']['username'], form=form, form2=form2)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Механизм авторизации пользователя"""
    data = {'info': {'is_auth': False}}
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
        return render_template('login.html', form=form, title='Авторизация', current_user=current_user, data=data)
    # Если GET-запрос
    # Просто выводим страницу авторизации
    return render_template('login.html', form=form, title='Авторизация', current_user=current_user, data=data)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Механизм регистрации пользователя"""
    data = {'info': {'is_auth': False}}
    form = RegisterForm()
    if form.validate_on_submit():
        # Если кнопка нажата (POST-запрос)
        if form.password.data != form.rep_password.data:
            # Если пароли не совпадают, сообщаем пользователю
            flash("Пароли не совпадают")
            return render_template('register.html', title='Регистрация', form=form, current_user=current_user,
                                   data=data)

        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            # Если e-mail уже занят, сообщаем пользователю
            flash("Этот e-mail уже используется!")
            return render_template('register.html', title='Регистрация', form=form, current_user=current_user,
                                   data=data)

        if form.avatar.data:
            # Если загружена аватарка, обрабатываем и сохраняем её
            filename = secure_filename(form.avatar.data.filename)
            fn = str(datetime.now()).replace(":", "_").replace(" ", "_") + filename[-4:]
            form.avatar.data.save('static/img/avatars/' + fn)
            try:
                avatar_convert.convert('static/img/avatars/' + fn)
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
    return render_template('register.html', title='Регистрация', form=form, current_user=current_user, data=data)


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
    data = gen_data()
    data['tags'] = [i.title for i in sess.query(Tag).all()]

    if not current_user.is_authenticated:
        # Если пользователь не вошёл в систему, кидаем ошибку
        abort(401, message="Пожалуйста, авторизуйтесь!")

    elif ROLES[sess.query(User).get(current_user.get_id()).role] != 'admin':
        # Если пользователь не админ, кидаем ошибку
        abort(423, message="Только администратор может добавлять теги!")

    # Если пользователь имеет права, идём дальше

    elif form.validate_on_submit():
        # Если кнопка нажата (POST-запрос)
        sess.add(Tag(title=form.title.data.replace(" ", "_")))
        sess.commit()
        flash("Тег успешно добавлен")
        return redirect('/addtag')

    else:
        # GET-запрос
        return render_template('tag_adding.html', title='Добавить тег', form=form, current_user=current_user, data=data)


@app.route('/subscribed', methods=['GET', 'POST'])
def subscribed():
    """Страница подписок"""
    session = db_session.create_session()
    data = gen_data()
    data['subscribes'] = [i.get_info() for i in load_user(current_user.id).subscribed]
    return render_template('subscribed.html', title='Добавить тег', current_user=current_user, data=data)


@app.route('/me')
def get_my_profile():
    """Функция для переадресации пользователя на собственную страницу автора"""

    if not current_user.is_authenticated:
        # Если пользователь не авторизован, то перенаправляем на главную
        return redirect('/')
    else:
        # Иначе, направляем его на свою страничку
        return redirect(f'/author/{current_user.get_id()}')


if __name__ == '__main__':
    # app.run(port=8080, host='127.0.0.1')
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
