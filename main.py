from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'windroc-nwpc-project'

socketio = SocketIO(app)


@app.route('/')
def get_index_page():
    return render_template('base.html')


@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my response', {'data': 'Connected', 'count': 0})


@socketio.on('my event', namespace='/test')
def test_message(message):
    print(message)
    emit('my response', {'data': message['data'], 'count': 2})


if __name__ == "__main__":
    socketio.run(app)

