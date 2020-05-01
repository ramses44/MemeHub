from data.db_session import create_session, global_init
from data.users import User
from data.memes import Meme
from data.tags import Tag

TOP_LEN = 5
LIKED_MEMES_BASIS = 15
LAST_MEMES_COUNT = 50
TAPE_SIZE = 20


def get_from_memes(lst, bs):
    """Функция для получения количественного диапазона мемов по дате публикации с конца"""
    sted = sorted(lst, key=lambda x: x.publication_date)
    return sted[-bs[0]:-bs[1]] if bs[1] else sted[-bs[0]:]


def get_basis(uid):
    """Функция для получения последних понравившихся пользователю мемов"""

    ses = create_session()
    user = ses.query(User).get(uid)  # Получаем пользователя
    liked = get_from_memes(user.liked, (LIKED_MEMES_BASIS, 0))

    return liked


def get_tags(*memes_list):
    """Функция для получения словаря id тэгов с весами"""

    tags = {}

    for meme in memes_list:
        for tag in meme.tags:
            tags[tag.id] = tags.get(tag.id, 0) + 1

    return tags


def get_related_memes(tags, k):  # k - номер пробега
    """Функция для получения сортированного списка предлагаемых мемов"""

    ses = create_session()
    memes = get_from_memes(ses.query(Meme), (LAST_MEMES_COUNT * k, LAST_MEMES_COUNT * (k - 1)))
    memes_ = {m.id: 0 for m in memes}

    for meme in memes:
        for tag in tags:
            if tag in map(lambda x: x.id, meme.tags):
                memes_[meme.id] += 1

    return [ses.query(Meme).get(id_) for id_ in sorted(memes_.keys(), key=lambda x: memes_[x], reverse=True)]


def get_tape(uid, k=0):  # k - возвращённое ранее значение
    """Функция для получения порции мемов в ленту"""

    tape = []

    while len(tape) < TAPE_SIZE:
        res = get_related_memes(get_tags(*get_basis(uid)), k + 1)
        if not res:
            break
        else:
            tape.extend(res)
            k += 1

    return tape, k


def get_most_popular():
    """Функция для получения списка самых популярных мемов"""

    ses = create_session()
    return sorted(ses.query(Meme), key=lambda x: len(list(x.likes)), reverse=True)[:TOP_LEN]


def get_user_memes(user_id):
    """Функция для получения списка мемов пользователя"""
    session = create_session()
    memes = session.query(Meme).filter(Meme.author.like(user_id)).all()
    return memes


if __name__ == '__main__':
    global_init('../db/memehub.sqlite')
    print(
        get_tape(1)
    )
