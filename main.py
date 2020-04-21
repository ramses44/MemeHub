from flask import Flask, render_template, request
from data import db_session

app = Flask(__name__)

app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db_session.global_init("db/memehub.sqlite")


@app.route('/', methods=['GET', 'POST'])
def index():
    data = {'info': {'is_auth': True, 'user_img': '../../static/img/img1.jpg', 'username': 'User'},
            'content': [
                {'type': 'meme', 'id': '1', 'author_name': 'AuthorName1', 'author_img': '../../static/img/img2.jpg',
                 'date': '01.01.2020',
                 'note': '', 'meme_img': '../../static/img/img1.jpg', 'likes': 3674,
                 'reposts': 25,
                 'is_liked': False, 'is_reposted': True, 'category': 'category1', 'place': 13, 'delete': False},
                {'type': 'meme', 'id': '2', 'author_name': 'AuthorName2', 'author_img': '../../static/img/img1.jpg',
                 'date': '02.02.2022',
                 'note': 'NoteAboveMeme2', 'meme_img': '../../static/img/img2.jpg', 'likes': 277,
                 'reposts': 178,
                 'is_liked': True, 'is_reposted': False, 'category': 'category2', 'place': 0, 'delete': True},
                {'type': 'repost', 'id': '3', 'delete': True, 'author_name': 'AuthorName3',
                 'author_img': '../../static/img/img1.jpg',
                 'date': '02.02.2022', 'reposted_content': {'id': '2', 'author_name': 'AuthorName2',
                                                            'author_img': '../../static/img/img1.jpg',
                                                            'date': '02.02.2022',
                                                            'note': 'NoteAboveMeme2',
                                                            'meme_img': '../../static/img/img2.jpg',
                                                            'likes': 277,
                                                            'reposts': 178,
                                                            'is_liked': True, 'is_reposted': False,
                                                            'category': 'category2',
                                                            'place': 0, 'delete': False}}]
            }
    return render_template('main.html', data=data)


@app.route('/post', methods=['POST'])
def post():
    if request:
        print(request.json)
    return 'return'


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
