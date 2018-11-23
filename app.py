"""Main application code."""
from flask import Flask
from flask import request
from flask import session
from flask import render_template, url_for, redirect, flash

from gevent.pywsgi import WSGIServer

from settings import DB_URL

import pdb
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, exists
from sqlalchemy.orm.exc import NoResultFound
from models import User, Admin
from models import Songs, GenreProf, Personality
from settings import Key
import sys

from quiz import quiz, score_quiz


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
        s = db_session.query(Songs).filter(Songs.user_id == session['user']).all()
        if len(s) >= 5:
            context["music_check"] = True
        return render_template("index.html", **context)
    else:
        return redirect(url_for("login"))


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    """Admin Index Page."""
    context = {"index": True}
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
        context["admin"] = True
        context["genre_list"] = GenreProf.genres
        if request.method == "GET":
            songs = db_session.query(Songs).filter(Songs.genre == "Unknown").all()
            context["toannotate"] = songs
            return render_template("annotate.html", **context)
        if request.method == "POST":
            profile = db_session.query(GenreProf).filter(GenreProf.user_id == session['user']).all()
            if len(profile) < 1:
                profile = GenreProf(session['user'])
                db_session.add(profile)
                db_session.commit()
            else:
                profile = profile[0]

            for sid in request.form:
                sgenre = request.form[sid]
                if sgenre != "Unknown":
                    db_session.query(Songs).filter(Songs.id_ == sid).one().genre = sgenre
                    profile.add_genre(**{sgenre: 1})
            db_session.commit()
            return redirect(url_for("annotate"))
    else:
        return redirect(url_for("index"))


@app.route('/songs', methods=['GET', 'POST'])
def songs():
    """Index Page."""
    context = {"songs": True}
    if 'admin' in session:
        return redirect(url_for("admin"))
    if 'user' in session:
        if request.method == "GET":
            submitted = db_session.query(Songs).filter(Songs.user_id == session['user']).all()
            if len(submitted) > 0:
                context["submitted"] = submitted
            return render_template("songs.html", **context)
        if request.method == "POST":
            songs = {}
            for k in request.form:
                field, num = k.split('_')
                if num not in songs:
                    songs[num] = {}
                songs[num][field] = request.form[k]
            for s in songs:
                print(s)
                db_session.add(Songs(session['user'], **songs[s]))
            db_session.commit()
            return redirect(url_for('songs'))
    else:
        return redirect(url_for("login"))


@app.route('/personality', methods=['GET', 'POST'])
def personality():
    """Index Page."""
    context = {"personality": True, "quiz": quiz, "score": {}}
    if 'admin' in session:
        return redirect(url_for("admin"))
    if 'user' in session:
        p = db_session.query(exists().where(Personality.user_id == session['user'])).scalar()
        if p:
            context["taken_quiz"] = p
            return render_template("quiz.html", **context)

        if request.method == "GET":
            return render_template("quiz.html", **context)
        elif request.method == "POST":
            score = {}
            context['age'] = request.form['age']
            context['gender'] = request.form['gender']

            for key in request.form:
                if key not in ['gender', 'age']:
                    score[int(key)] = int(request.form[key])

            context["score"] = score

            try:
                ocean_score = score_quiz(score)
            except KeyError:
                flash("You have not filled all the questions")
                return render_template("quiz.html", **context)

            if request.form['age'] == '' or request.form['gender'] == 'U':
                flash("You have not provided age or gender")
                return render_template("quiz.html", **context)

            user = db_session.query(User).filter(User.id_ == session['user']).one()
            user.age = request.form['age']
            user.gender = request.form['gender']

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
        return redirect(url_for('login'))


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
