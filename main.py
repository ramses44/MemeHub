from flask import Flask
from data import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db_session.global_init("db/memehub.sqlite")


@app.route('/')
def index():
    return 'main'


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
