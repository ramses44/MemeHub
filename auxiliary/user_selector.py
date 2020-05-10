from data.db_session import create_session, global_init
from data.users import User
from data.memes import Meme, Repost
from datetime import datetime, timedelta
from gen_api import ROLES

ACTIVITY_COEFFICIENT = 1.3
ACTIVITY_DAYS = 7
USER_TOP = 5


def is_active(user_id):
    """Функция определяет, активен ли пользователь (были ли публикации в последние ACTIVITY_DAYS дней"""

    ses = create_session()
    user = ses.query(User).get(user_id)

    pubs = ses.query(Meme).filter(Meme.publication_date >= datetime.now() - timedelta(days=ACTIVITY_DAYS)).first() or \
        ses.query(Repost).filter(Repost.publication_date >= datetime.now() - timedelta(days=ACTIVITY_DAYS)).first()

    return pubs


def calculate_rating(uid):
    """Функция вычисляет рейтинг пользователя по формуле:
    (лайки_его_мемов + подписчики * 2 + его_лайки( + репосты) * 0.25 + репосты_его_мемов * 3) * ACTIVITY_COEFFICIENT"""

    ses = create_session()
    user = ses.query(User).get(uid)

    likes = sum(map(lambda x: len(list(x.likes)), user.memes))
    subs = len(list(user.subscribers))
    liked = len(list(user.liked)) + len(list(user.repostes))
    repostes = sum(map(lambda x: len(list(x.repostes)), user.memes))

    rating = likes + subs * 2 + liked * 0.25 + repostes * 3
    rating = rating * ACTIVITY_COEFFICIENT if is_active(uid) else rating

    return round(rating)


def gen_user_info(uid, self_uid=0):

    ses = create_session()
    user = ses.query(User).get(uid)
    me = ses.query(User).get(self_uid)
    users = ses.query(User).filter(User.id != 0).all()
    users = sorted(users, key=lambda x: x.rating, reverse=True)[:USER_TOP]

    return {
        'is_page': True,
        'user_img': user.avatar,
        'type': 'other',
        'role': ROLES[user.role],
        'status': user.about,
        'subs': len(list(user.subscribers)),
        'posts': len(list(user.memes)) + len(list(user.repostes)),
        'rating': user.rating,
        'top': users.index(user) + 1 if user in users else '-',
        'username': user.alias,
        'user_id': uid,
        'error_message': '',
        'is_sub': me in user.subscribers,
        'is_block': user.is_blocked
    }
