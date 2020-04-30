from data.db_session import create_session, global_init
from data.users import User
from data.memes import Meme
from data.tags import Tag

TOP_LEN = 5
LIKED_MEMES_BASIS = 15
LAST_PUBS_COUNT = 50
FROM_SUBSCRIBES_COEFFICIENT = 0.5
LAST_FROM_SUB_COUNT = int(LAST_PUBS_COUNT * FROM_SUBSCRIBES_COEFFICIENT)
LAST_MEMES_COUNT = LAST_PUBS_COUNT - LAST_FROM_SUB_COUNT
TAPE_SIZE = 20


def get_from_memes(lst, bs=(0, 0)):  # bs - barriers
    """Функция для получения количественного диапазона мемов по дате публикации с конца"""
    sted = sorted(lst, key=lambda x: x.publication_date)
    return sted[-bs[0]:-bs[1]] if bs[1] else sted[-bs[0]:]


def get_pubs(*us, bs=(0, 0)) -> list:  # bs - barriers
    """Функция для получения всех публикация пользователя,
     отсортированных по дате публикации (определённое кол-во)"""
    res = []
    for u in us:
        res += sorted(list(u.repostes) + list(u.memes), key=lambda x: x.publication_date, reverse=True)
    if bs:
        res = res[-bs[0]:-bs[1]] if bs[1] else res[-bs[0]:]
    return res


def get_basis(uid):
    """Функция для получения последних понравившихся пользователю мемов
    и последних, опубликованных теми, на кого он подписан"""

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


def get_related(tags, k):  # k - номер пробега
    """Функция для получения сортированного списка предлагаемых публикаций"""

    ses = create_session()
    memes = get_from_memes(ses.query(Meme), (LAST_MEMES_COUNT * k, LAST_MEMES_COUNT * (k - 1)))
    memes_ = {m.id: 0 for m in memes}

    for meme in memes:
        for tag in tags:
            if tag in map(lambda x: x.id, meme.tags):
                memes_[meme.id] += 1

    return [ses.query(Meme).get(id_) for id_ in sorted(memes_.keys(), key=lambda x: memes_[x], reverse=True)]


def get_tape(uid, k=0):  # k - возвращённое ранее значение
    """Функция для получения порции мемов в ленту (мемы перемешаны по умолчанию)"""

    tape = set()
    ses = create_session()
    subs = ses.query(User).get(uid).subscribed

    while len(tape) < TAPE_SIZE:
        res = set(get_related(get_tags(*get_basis(uid)), k + 1) +
                  get_pubs(*subs, bs=(LAST_FROM_SUB_COUNT * k, LAST_FROM_SUB_COUNT * (k - 1))))
        if not res:
            break
        else:
            tape |= res
            k += 1

    return list(tape), k


def get_most_popular():
    """Функция для получения списка самых популярных мемов"""

    ses = create_session()
    return sorted(ses.query(Meme), key=lambda x: len(list(x.likes)), reverse=True)[:TOP_LEN]


if __name__ == '__main__':
    global_init('../db/memehub.sqlite')
    print(
        get_tape(2)
    )
