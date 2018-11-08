"""Main application code."""
import billboard

from flask import Flask
from flask import request
from flask import session
from flask import render_template, url_for, redirect, flash

import pdb
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, exists
from sqlalchemy.orm.exc import NoResultFound
from models import User, Admin
from models import Songs, GenreProf, Personality
from settings import DB_URL
from settings import Key
import sys

from quiz import quiz, score_quiz


print("Loading billboard top 100...")
chart = billboard.ChartData('hot-100')
print("Setting up app...")
app = Flask(__name__)
app.secret_key = Key
print("Creating database link and session...")
engine = create_engine(DB_URL)
db_session = scoped_session(sessionmaker(bind=engine))


@app.route('/', methods=['GET', 'POST'])
def index():
    """Index Page."""
    context = {"index": True, "songs": False, "personality": False}
    if 'admin' in session:
        return redirect(url_for("admin"))
    if 'user' in session:
        # Check if the user filled the quiz.
        p = db_session.query(exists().where(Personality.user_id == session['user'])).scalar()
        context["personality_check"] = p
        # Check if the user provided 5 songs
        s = db_session.query(Songs).filter(Songs.id_ == session['user']).all()
        if len(s) > 5:
            context["music_check"] = True
        return render_template("index.html", **context)
    else:
        return redirect(url_for("login"))


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    """Admin Index Page."""
    context = {"admin": True}
    if 'admin' in session:
        context["admin"] = True
        return render_template("admin.html", **context)
    else:
        return redirect(url_for("index"))


@app.route('/annotate', methods=['GET', 'POST'])
def annotate():
    """Annotation Page."""
    context = {"annotate": True}
    if 'admin' in session:
        if request.method == "GET":
            # Get all songs not in GenreProf.
            # List the songs one by one, and then ask for an Annotation
            pass
        if request.method == "POST":
            # The song will have a GenreProf created if it was not made before.
            # If GenreProf exists then increment the genre value to which it belongs.
            pass
        return render_template("admin.html")
        if admin:
            return render_template("admin.html", **context)
        return render_template("index.html", **context)
    else:
        return redirect(url_for("index"))


@app.route('/music', methods=['GET', 'POST'])
def music():
    """Index Page."""
    context = {"music": True}
    return render_template("index.html", **context)
    if 'admin' in session:
        return redirect(url_for("admin"))
    if 'user' in session:
        return render_template("index.html", **context)
    else:
        return redirect(url_for("login"))


@app.route('/personality', methods=['GET', 'POST'])
def personality():
    """Index Page."""
    context = {"personality": True, "quiz": quiz}
    if 'admin' in session:
        return redirect(url_for("admin"))
    if 'user' in session:
        p = db_session.query(exists().where(Personality.user_id == session['user'])).scalar()
        # context["taken"] = p
        if request.method == "GET":
            return render_template("quiz.html", **context)
        elif request.method == "POST":
            score = {}
            for key in request.form:
                score[int(key)] = int(request.form[key])
            ocean_score = score_quiz(score)
            p = Personality(session["user"], ocean_score)
            db_session.add(p)
            db_session.commit()
            return redirect(url_for("personality"))
    else:
        return redirect(url_for("login"))


@app.route('/logout')
def logout():
    """Logout."""
    session.pop('user', None)
    session.pop('admin', None)
    flash("You have successfully logged out")
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if 'user' in session:
        return redirect(url_for('index'))
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = None
        # Check if user exists
        try:
            user = db_session.query(User).filter(User.username == username).one()
        except NoResultFound:
            flash("User does not exist")
            return redirect(url_for('login'))
        # Check the password
        if not user.validate_password(password):
            flash("Wrong password")
            return redirect(url_for('login'))
        # Login session
        session['user'] = user.id_
        # Check if user is admin
        if db_session.query(exists().where(Admin.user_id == user.id_)).scalar():
            session['admin'] = True
        return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if 'user' in session:
        return redirect(url_for('index'))
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        name = request.form["name"]
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        if password != confirm_password:
            flash("Passwords don't match")
            return redirect(url_for('register'))
        if db_session.query(exists().where(User.username == username)).scalar():
            flash("User already exists")
            return redirect(url_for('register'))
        new_user = User(username, password, name, email)
        db_session.add(new_user)
        db_session.commit()
        flash("You have successfully registered, please login")
        return redirect(url_for('register'))


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("Usage:\n\tpython app.py [host address] [port]\n")
        sys.exit(0)

    IP_addr = sys.argv[1]
    port = sys.argv[2]
    try:
        print("Running server...")
        app.run(host=IP_addr, debug=True, port=int(port))

    # http_server = WSGIServer((IP_addr, int(port)), app)
    # print("Server running on http://{}:{}".format(IP_addr, port))
    # try:
    #     http_server.serve_forever()
    except KeyboardInterrupt:
        print("Exiting server")
        sys.exit(0)
