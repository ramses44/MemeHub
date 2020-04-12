import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
import sqlalchemy.orm as orm
from sqlalchemy_serializer import SerializerMixin


class Meme(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'memes'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    author = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    author_ = orm.relation("User", foreign_keys=[author])
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False, default="")
    publication_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    tags = orm.relation('Tag', secondary='tags_to_memes', backref='meme', lazy='dynamic')
    likes = orm.relation('User', secondary='likes', backref='meme', lazy='dynamic')
    picture = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    def __repr__(self):
        return "<Meme> " + self.title

