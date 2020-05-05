import sqlalchemy
from .db_session import SqlAlchemyBase
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, validators
from flask_wtf.file import FileField, FileAllowed
from wtforms.fields.html5 import EmailField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired

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


class LoginForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    email = EmailField('E-mail', validators=[DataRequired(), validators.Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    rep_password = PasswordField('Повтор пароля', validators=[DataRequired()])
    alias = StringField('Псевдоним', validators=[DataRequired()])
    bdate = DateField("Дата рождения", validators=(validators.Optional(),))
    about = StringField("Немного о себе")
    avatar = FileField("Изображение профиля", validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    submit = SubmitField("Зарегистрироваться")


class TagAddingForm(FlaskForm):
    title = StringField('Тег (без "#")', validators=(DataRequired(),))
    submit = SubmitField("Добавить")


class MemeAddingForm(FlaskForm):
    title = StringField("Заголовок", validators=[DataRequired()])
    picture = FileField("Загрузите мем", validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    submit = SubmitField("Добавить")


class EditProfileForm(FlaskForm):
    key = StringField()
    alias = StringField('Псевдоним')
    about = StringField("Немного о себе")
    avatar = FileField("Изображение профиля", validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    submit = SubmitField("Зарегистрироваться")


class MemePublishForm(FlaskForm):
    note = StringField()
    tags = StringField()
    img = FileField(validators=[FileAllowed(['jpg', 'png'], 'Images only!'), DataRequired()])
    submit = SubmitField("Опубликовать")
