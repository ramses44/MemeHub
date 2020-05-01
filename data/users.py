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
    role = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    alias = sqlalchemy.Column(sqlalchemy.String, nullable=False)  # То, как пользователь подписан у других
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    bdate = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    memes = orm.relation("Meme", back_populates='author_')
    avatar = sqlalchemy.Column(sqlalchemy.String, default='default.png')
    liked = orm.relation("Meme", secondary='likes', backref='user', lazy='dynamic')
    reposted = orm.relation("Meme", secondary='reposts', backref='user_', lazy='dynamic')  # lazy='dynamic'

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def __repr__(self):
        return f"<User> {self.id} {self.alias}"

    def get_data(self):
        return {'is_page': True,
                'user_img': self.avatar,
                'type': 'other',
                'role': {'0': '', '1': '', '2': 'moder', '3': 'admin'}[str(self.role)],
                'status': self.about,
                'subs': 666,
                'posts': 666,
                'rating': 666,
                'top': 666,
                'username': self.alias,
                'user_id': self.id,
                'error_message': '',
                'is_sub': False,
                'is_block': False}
