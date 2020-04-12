import sqlalchemy
from .db_session import SqlAlchemyBase

sqlalchemy.Table(
    'tags_to_memes',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('tag', sqlalchemy.Integer, sqlalchemy.ForeignKey('tags.id')),
    sqlalchemy.Column('meme', sqlalchemy.Integer, sqlalchemy.ForeignKey('memes.id'))
)

sqlalchemy.Table(
    'likes',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('user', sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id')),
    sqlalchemy.Column('meme', sqlalchemy.Integer, sqlalchemy.ForeignKey('memes.id'))
)

from . import memes
from . import tags
from . import users