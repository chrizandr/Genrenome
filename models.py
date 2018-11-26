"""Models for Hydra Classes."""

import os
import pdb
from settings import DB_URL
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, exists
from passlib.hash import bcrypt
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class User(Base):
    """Model for Users.

    Each user has a username and password that matches with their ubuntu login IDs.
    """

    __tablename__ = "users"

    id_ = Column(Integer, primary_key=True)
    username = Column(String(20), unique=True)
    password = Column(String(20))
    name = Column(String(20))
    email = Column(String(20), unique=True)
    age = Column(Integer)
    gender = Column(String(20))

    def __init__(self, username, password, name, email):
        """Create new instance."""
        self.username = username
        self.password = bcrypt.encrypt(password)
        self.name = name
        self.email = email
        self.age = 0
        self.gender = "U"

    def validate_password(self, password):
        """Check encrypted password."""
        return bcrypt.verify(password, self.password)

    def __repr__(self):
        """Verbose object name."""
        return "<id='%s', username='%s'>" % (self.id_, self.username)


class Admin(Base):
    """Model for Admins.

    Normal users can be given admin access to modify exisitng users and manage the server.
    """

    __tablename__ = "admins"

    id_ = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id_"), unique=True)

    def __init__(self, user_id):
        """Create admin."""
        self.user_id = user_id

    def __repr__(self):
        """Verbose object name."""
        return "<userid='%s'>" % (self.user_id)


class Songs(Base):
    """Model prefered songs of a user."""

    __tablename__ = "songs"

    id_ = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id_"), unique=False)
    title = Column(String(50))
    artist = Column(String(50))
    genre = Column(String(50))

    def __init__(self, user_id, title, artist):
        """Create new instance."""
        self.user_id = user_id
        self.title = title
        self.artist = artist
        self.genre = "Unknown"

    def __repr__(self):
        """Verbose object name."""
        return "<userid='%s', artist='%s', title='%s'>" % (self.user_id, self.artist, self.title)


class Personality(Base):
    """Model for OCEAN score."""

    __tablename__ = "personality"

    id_ = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id_"))
    O = Column(Integer)
    C = Column(Integer)
    E = Column(Integer)
    A = Column(Integer)
    N = Column(Integer)

    def __init__(self, user_id, score):
        """Create new instance."""
        self.user_id = user_id
        self.O, self.C, self.E, self.A, self.N = tuple(score)

    def __repr__(self):
        """Verbose object name."""
        return "<userid='%s', score='%s'>" % (self.user_id, ",".join([str(self.O), str(self.C),
                                                                      str(self.E), str(self.A), str(self.N)]))


class GenreProf(Base):
    """Model for Genre Profile."""

    __tablename__ = "genre_prof"

    id_ = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id_"), unique=True)
    genres = ["Blues", "Classical", "Country", "Electronic", "Folk", "Jazz", "New age", "Reggae", "Rock"]

    Blues = Column(Integer)
    Classical = Column(Integer)
    Country = Column(Integer)
    Electronic = Column(Integer)
    Folk = Column(Integer)
    Jazz = Column(Integer)
    New_age = Column(Integer)
    Reggae = Column(Integer)
    Rock = Column(Integer)

    def __init__(self, user_id):
        """Create new instance."""
        self.user_id = user_id
        self.Blues = 0
        self.Classical = 0
        self.Country = 0
        self.Electronic = 0
        self.Folk = 0
        self.Jazz = 0
        self.New_age = 0
        self.Reggae = 0
        self.Rock = 0

    def add_genre(self, Blues=0, Classical=0, Country=0, Electronic=0, Folk=0, Jazz=0, New_age=0, Reggae=0, Rock=0):
        """Add prefered genre to the music profile of the user."""
        self.Blues += Blues
        self.Classical += Classical
        self.Country += Country
        self.Electronic += Electronic
        self.Folk += Folk
        self.Jazz += Jazz
        self.New_age += New_age
        self.Reggae += Reggae
        self.Rock += Rock

    def __repr__(self):
        """Verbose object name."""
        return "<userid='%s'>" % (self.user_id)


def get_debug_session(DB_URL):
    """Get a DB session for debugging."""
    engine = create_engine(DB_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def setup(DB_URL):
    """Setup."""
    # Create database tables
    engine = create_engine(DB_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    # Add admin
    adminuser = User("admin", "genrenome", "admin", "admin@genrenome")
    session.add(adminuser)
    session.commit()

    admin = Admin(adminuser.id_)
    session.add(admin)
    session.commit()
    return session


def combine_users():
    """Merge two data from two different databases into one."""
    sess_aws = get_debug_session("sqlite:///database.db")
    sess_preon = get_debug_session("sqlite:///preon_data.db")
    preon_users = sess_preon.query(User).all()

    print("# create users and add them temporarily")
    new_users = []
    map_dict = {}
    for i, u in enumerate(preon_users):
        map_dict[u.id_] = i
        user = User(u.username, "pass", u.name, u.email)
        user.age = u.age
        user.gender = u.gender
        new_users.append(user)
        sess_aws.add(user)

    sess_aws.flush()
    # pdb.set_trace()

    print("# Songs of all users")
    new_songs = []
    preon_songs = sess_preon.query(Songs).all()
    for s in preon_songs:
        try:
            uid = new_users[map_dict[s.user_id]].id_
        except KeyError:
            continue
        song = Songs(uid, s.title, s.artist)
        new_songs.append(song)

    print("# Personality of all users")
    new_pers = []
    preon_pers = sess_preon.query(Personality).all()
    for p in preon_pers:
        try:
            uid = new_users[map_dict[p.user_id]].id_
        except KeyError:
            continue
        pers = Personality(uid, [p.O, p.C, p.E, p.A, p.N])
        new_pers.append(pers)

    pdb.set_trace()


def clean_data_no_personality():
    """Delete users who did not take quiz."""
    session = get_debug_session(DB_URL)
    users = session.query(User).all()
    personality = session.query(Personality).all()
    uids_all = set([u.id_ for u in users])
    uids_valid = set([u.user_id for u in personality])
    uids_invalid = uids_all - uids_valid

    for id_ in uids_invalid:
        u = session.query(User).filter(User.id_ == id_).one()
        session.delete(u)
    session.commit()


def clean_data_invalid_songs():
    """Delete songs that are blank."""
    session = get_debug_session(DB_URL)
    songs = session.query(Songs).all()
    for s in songs:
        if s.title.strip() == "":
            session.delete(s)
    session.commit()


def clean_data_no_songs():
    """Delete users who did not give songs."""
    session = get_debug_session(DB_URL)
    users = session.query(User).all()
    songs = session.query(Songs).all()
    uids_all = set([u.id_ for u in users])
    uids_valid = set([u.user_id for u in songs])
    uids_invalid = uids_all - uids_valid

    for id_ in uids_invalid:
        u = session.query(User).filter(User.id_ == id_).one()
        session.delete(u)
    session.commit()



if __name__ == "__main__":
    # session = setup(DB_URL)
    session = get_debug_session(DB_URL)
    # combine_users()
    # clean_data_invalid_songs()
    # clean_data_no_songs()
    pdb.set_trace()
