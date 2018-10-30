"""Models for Hydra Classes."""

import pdb
from settings import DB_URL
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
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

    def __init__(self, username, password, name, email):
        """Create new instance."""
        self.username = username
        self.password = bcrypt.encrypt(password)
        self.name = name
        self.email = email

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

    def __repr__(self):
        """Verbose object name."""
        return "<userid='%s'>" % (self.user_id)


class Songs(Base):
    """Model prefered songs of a user."""

    __tablename__ = "songs"

    id_ = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id_"))
    title = Column(String(50))
    artist = Column(String(50))
    genre = Column(String(50))

    def __init__(self, user_id, title, artist):
        """Create new instance."""
        self.user_id = user_id
        self.title = title
        self.artist = artist
        self.genre = "Unkown"

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
        return "<userid='%s', score='%s'>" % (self.user_id, ",".join([self.O, self.C, self.E, self.A, self.N]))


class GenreProf(Base):
    """Model for OCEAN score."""

    __tablename__ = "genre_prof"

    id_ = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id_"))
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

    def __init__(self, user_id, score):
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

    def add_genre(self, genre):
        """Add prefered genre to the music profile of the user."""
        if genre == "Blues":
            self.Blues += 1
        elif genre == "Classical":
            self.Classical += 1
        elif genre == "Country":
            self.Country += 1
        elif genre == "Electronic":
            self.Electronic += 1
        elif genre == "Folk":
            self.Folk += 1
        elif genre == "Jazz":
            self.Jazz += 1
        elif genre == "New age":
            self.New_age += 1
        elif genre == "Reggae":
            self.Reggae += 1
        elif genre == "Rock":
            self.Rock += 1

    def __repr__(self):
        """Verbose object name."""
        return "<userid='%s'>" % (self.user_id)


if __name__ == "__main__":
    engine = create_engine(DB_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    pdb.set_trace()
