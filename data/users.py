import sqlalchemy
from .db_session import SqlAlchemyBase
from werkzeug.security import *
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
import sqlalchemy.orm as orm

followers = sqlalchemy.Table(
    'subscribes',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('author', sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id')),
    sqlalchemy.Column('subscriber', sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
)


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True, index=True, nullable=False)
    role = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    alias = sqlalchemy.Column(sqlalchemy.String, nullable=False)  # То, как пользователь подписан у других
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    bdate = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    memes = orm.relation("Meme", back_populates='author_')
    avatar = sqlalchemy.Column(sqlalchemy.String, default='default.png')
    liked = orm.relation("Meme", secondary='likes', backref='user', lazy='dynamic')
    repostes = orm.relation("Repost", back_populates='user_')
    subscribed = orm.relationship("User", secondary='subscribes',
                                  primaryjoin=(followers.c.subscriber == id),
                                  secondaryjoin=(followers.c.author == id),
                                  backref='subscriber', lazy='dynamic')
    subscribers = orm.relation("User", secondary='subscribes',
                               primaryjoin=(followers.c.author == id),
                               secondaryjoin=(followers.c.subscriber == id),
                               backref='author', lazy='dynamic')
    rating = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    is_blocked = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def __repr__(self):
        return f"<User> {self.id} {self.alias}"

    def __hash__(self):
        return hash(str(self.id) + 'u')

