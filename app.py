import random
import time
from flask import Flask, make_response, request, redirect, session, url_for
from flask_socketio import SocketIO, send, emit, join_room, leave_room

app = Flask(__name__,
            static_url_path = "",
            static_folder = "static")
app.config['SECRET_KEY'] = "abcdefgh"
socketio = SocketIO(app)

users = {}
users2 = {}
games = {}

@socketio.on('connect')
def test_connect(auth):
    emit('my response', {'data': 'Connected'})

@socketio.on('disconnect')
def test_disconnect():
    userdata = users[users2[request.sid]]
    user = userdata[0]
    print(users)
    print(users2)
    print(games)
    print("=====")
    del users[users2[request.sid]]
    del users2[request.sid]
    del games[user]
    for u in games:
        if user in games[u]:
            del games[u][user]
    print(userdata)
    print(users)
    print(users2)
    print(games)
    emit("lobby message", f"{user} has left the lobby", to="lobby")
    emit("leave lobby", user, to="lobby")
    print("Disconnected")

@socketio.on('join lobby')
def join_lobby(uname, uid):
    room = "lobby"
    print(request.sid)
    join_room("lobby")
    users2[request.sid] = uid
    emit("lobby message", f"{uname} has joined the lobby", to="lobby")
    emit("join lobby", uname, to="lobby")
    print(users, users2)
    
@socketio.on('lobby message')
def lobby_message(msg):
    print('received message:', msg)
    if len(msg) < 1:
        return
    emit("lobby message", msg, to="lobby")

@socketio.on('play card')
def play_card(msg):
    print(msg)

@socketio.on('lobby challenge')
def challenge(data):
    print(data)
    player1, player2 = data["from"], data["to"]
    if player1 in games[player2]:
        print("Challenge accepted")
    elif player2 in games[player1]:
        return
    else:
        games[player1][player2] = {}
        print(player1, player2)
        emit("lobby challenge", data, to="lobby")

@app.route('/')
def splash():
    check = request.cookies.get("uid"), request.cookies.get("uname")
    print(check)
    print(users)
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
    for user in users:
        print(uname)
        print(users[user])
        if users[user][0] == uname:
            return redirect(url_for('splash'))
    res = make_response(redirect('/'))
    res.set_cookie("uname", value = uname)
    res.set_cookie("uid", value = uid)
    users[uid] = [uname, str(int(time.time()))]
    games[uname] = {}
    return res

@app.route('/lobby')
def lobby():
    check = request.cookies.get("uid"), request.cookies.get("uname")
    if check[0] not in users:
        return redirect("/")

    room = "lobby"
    out = ["<ul id='players'>"]
    for u in users:
        username = users[u][0]
        if username == check[1]:
            continue
        out.append(f"<li id={username}> {username}")
        out[-1] += (f" <button class='challenge' value='{username}'>Challenge</button>")
        out[-1] += (" </li>")
    out.append("</ul>")
    out = "\n".join(out)
    with open("html/lobby.html", "r") as page:
        page = page.read()
    page = out + page
    return page

@app.route('/game', methods=["GET", "POST"])
def game():
    print(request.form.keys())
    try:
        mode = request.args["mode"]
    except:
        mode = "slave"
    try:
        card = request.args["card"]
    except:
        card = None
        
    with open("html/game.html", "r") as page:
        page = page.read()
    page = page.replace("MODE", mode)
    if card:
        page = page.replace("CARD", f"<h2>You selected: {card}</h2>")
    else:
        page = page.replace("CARD", "")
    return page

if __name__ == "__main__":
    socketio.run(app)


