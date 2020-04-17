import sqlalchemy
from .db_session import SqlAlchemyBase
from werkzeug.security import *
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
import sqlalchemy.orm as orm


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True, index=True, nullable=False)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    alias = sqlalchemy.Column(sqlalchemy.String, nullable=False)  # То, как пользователь подписан у других
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    bdate = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    memes = orm.relation("Meme", back_populates='author_')
    avatar = sqlalchemy.Column(sqlalchemy.String, default='default.png')
    liked = orm.relation("Meme", secondary='likes', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def __repr__(self):
        return f"<User> {self.id} {self.alias}"
