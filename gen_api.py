from flask import Blueprint, jsonify, request, make_response, url_for
from data.users import User
from data import db_session
from auxiliary import meme_selector

ROLES = ['user', 'moder', 'admin']  # Индекс соответствует номеру роли в БД

blueprint = Blueprint('gen_api', __name__, template_folder='templates')


@blueprint.route('/get_user_info/<int:uid>')
def generate_user_info(uid):
    """Функция для генерации пользовательских данных"""

    ses = db_session.create_session()
    user = ses.query(User).get(uid)

    return {
        'is_auth': True,
        'user_img': url_for('static', filename=f'img/avatars/{user.avatar}'),
        'id': uid,
        'alias': user.alias,
        'role': ROLES[user.role]
    }


@blueprint.route('/get_content/<int:uid>')
def get_content(uid=0, by_server=False):
    """Функция для AJAX запроса по кнопке "Загрузить ещё"
    Если пользователь авторизован, нужно передавать его id,
    иначе uid=0 - это анонимный пользователь
    (в БД должен быть user с id=0 ("чистый" пользователь), его данные не будут меняться).
    Также используется для генерации начального контента другими ф-ями"""

    k = int(request.cookies.get("k", 0))

    # Если пользователь авторизован, получаем рекомендуемые мемы, иначе последние опубликованные
    tape, k = meme_selector.get_tape(uid, k)
    ses = db_session.create_session()

    content = []
    for meme in tape:
        content.append({
            'type': 'meme',
            'id': str(meme.id),
            'author_name': meme.author_.alias,
            'author_id': meme.author,
            'author_img': url_for('static', filename=f'img/avatars/{meme.author_.avatar}'),
            'date': str(meme.publication_date.date()),
            'note': meme.title,
            'meme_img': url_for('static', filename=f'img/memes/{meme.picture}'),
            'likes': len(list(meme.likes)),
            'reposts': len(list(meme.repostes)),
            'is_liked': uid in map(lambda x: x.id, meme.likes),
            'is_reposted': uid in map(lambda x: x.id, meme.repostes),
            'category': ", ".join(map(lambda x: x.title, meme.tags)),
            'place': meme_selector.get_most_popular().index(meme) + 1,
            'delete': uid == meme.author_.id or ses.query(User).get(uid).role != ROLES.index('user')
        })

    if not by_server:
        # Если запрос был отправлен клиентом (кнопкой "загрузить ещё"), а не серверной генеративной ф-ией
        # Обновляем куки
        res = make_response(jsonify(dict(content=content)))
        res.set_cookie("k", str(k), max_age=600)
    else:
        res = dict(content=content)

    return res  # Возвращаем ответ









