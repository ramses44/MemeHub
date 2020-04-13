import sqlalchemy
from .db_session import SqlAlchemyBase
import sqlalchemy.orm as orm
from sqlalchemy_serializer import SerializerMixin


class Tag(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'tags'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    memes = orm.relation("Meme", secondary='tags_to_memes', backref='tag', lazy='dynamic')

    def __repr__(self):
        return "<Tag> " + self.title

