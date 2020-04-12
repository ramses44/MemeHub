from data import db_session
from flask import Flask, render_template, request

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db_session.global_init("db/memehub.sqlite")


@app.route('/', methods=['POST', 'GET'])
def index():
    data = [{'author_name': 'AuthorName1', 'author_img': '../../static/img/img2.jpg', 'date': '01.01.2020',
             'note': 'NoteAboveMeme', 'meme_img': '../../static/img/img1.jpg', 'likes': 123, 'reposts': 321,
             'is_liked': True, 'is_reposted': True},
            {'author_name': 'AuthorName2', 'author_img': '../../static/img/img1.jpg', 'date': '02.02.2022',
             'note': 'NoteAboveMeme', 'meme_img': '../../static/img/img2.jpg', 'likes': 123, 'reposts': 321,
             'is_liked': True, 'is_reposted': True}
            ]
    return render_template('main.html', data=data)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
