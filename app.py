import random
import time
from flask import Flask, make_response, request, redirect, url_for
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = "setiostsetihest"
socketio = SocketIO(app)

users = {}

@socketio.on('connect')
def test_connect(auth):
    emit('my response', {'data': 'Connected'})

@socketio.on('disconnect')
def test_disconnect():
    print("Disconnected")

@socketio.on('lobby message')
def lobby_message(msg):
    print('received message:', msg)
    if len(msg) < 1:
        return
    emit("lobby message", msg, broadcast=True)

@app.route('/')
def splash():
    check = request.cookies.get("uid"), request.cookies.get("uname")
    print(check)
    if check[0] in users:
        return redirect("/lobby")
    userid = random.randrange(1001, 5000)
    with open("html/splash.html", "r") as test_p:
        test_p = test_p.read()
    return test_p.format(userid)
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return redirect(url_for('splash'))
    uname = request.form['uname']
    uid = request.form['uid']
    res = make_response(redirect('/'))
    res.set_cookie("uname", value = uname)
    res.set_cookie("uid", value = uid)
    users[uid] = [uname, str(int(time.time()))]
    return res

@app.route('/lobby')
def lobby():
    check = request.cookies.get("uid"), request.cookies.get("uname")
    if check[0] not in users:
        return redirect("/")
    out = []
    out.append(" ".join(check))
    for u in users:
        out.append(" ".join([u, *users[u]]))
    with open("html/lobby.html", "r") as page:
        page = page.read()
    page += "<br>".join(out)
    return page

if __name__ == "__main__":
    socketio.run(app)


