from flask import Flask

app = Flask(__name__)

app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

__factory = None


@app.route('/')
def index():
    return 'main'


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
