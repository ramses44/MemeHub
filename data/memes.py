import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
import sqlalchemy.orm as orm
from sqlalchemy_serializer import SerializerMixin


class Meme(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'memes'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    author = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    author_ = orm.relation("User", foreign_keys=[author], lazy='subquery')
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False, default="")
    publication_date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, default=datetime.datetime.now)
    tags = orm.relation('Tag', secondary='tags_to_memes', backref='meme', lazy='dynamic')
    likes = orm.relation('User', secondary='likes', backref='meme', lazy='dynamic')
    picture = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    repostes = orm.relation('Repost', back_populates='meme_', lazy='subquery')

    def __repr__(self):
        return "<Meme> " + self.title

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(str(self.id) + 'm')


class Repost(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'reposts'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False, default="")
    meme = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("memes.id"))
    meme_ = orm.relation("Meme", foreign_keys=[meme])
    user = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user_ = orm.relation("User", foreign_keys=[user])
    publication_date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, default=datetime.datetime.now)

    def __hash__(self):
        return hash(str(self.id) + 'r')

    def __repr__(self):
        return "<Repost> " + self.title + f" //{self.meme_}\\\\"
