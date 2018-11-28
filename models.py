"""Models for Hydra Classes."""
import numpy as np
import matplotlib.pyplot as plt
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

    def get_vector(self):
        return [self.O, self.C, self.E, self.A, self.N]


class GenreProf(Base):
    """Model for Genre Profile."""

    __tablename__ = "genre_prof"

    id_ = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id_"), unique=True)
    genres = ["Blues", "Contemporary", "Country", "Electronic", "Rap", "Pop", "Reggae", "Rock", "Others"]

    Blues = Column(Integer)
    Contemporary = Column(Integer)
    Country = Column(Integer)
    Electronic = Column(Integer)
    Rap = Column(Integer)
    Pop = Column(Integer)
    Reggae = Column(Integer)
    Rock = Column(Integer)
    Others = Column(Integer)

    def __init__(self, user_id):
        """Create new instance."""
        self.user_id = user_id
        self.Blues = 0
        self.Contemporary = 0
        self.Country = 0
        self.Electronic = 0
        self.Rap = 0
        self.Pop = 0
        self.Reggae = 0
        self.Rock = 0
        self.Others = 0

    def add_genre(self, Blues=0, Contemporary=0, Country=0, Electronic=0, Rap=0, Pop=0, Reggae=0, Rock=0, Others=0):
        """Add prefered genre to the music profile of the user."""
        self.Blues += Blues
        self.Contemporary += Contemporary
        self.Country += Country
        self.Electronic += Electronic
        self.Rap += Rap
        self.Pop += Pop
        self.Reggae += Reggae
        self.Rock += Rock
        self.Others += Others

    def __repr__(self):
        """Verbose object name."""
        return "<userid='%s'>" % (self.user_id)

    def get_vector(self):
        vector = [self.Blues, self.Contemporary, self.Country,
                  self.Electronic, self.Rap, self.Pop, self.Reggae,
                  self.Rock, self.Others]
        return vector


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


def cluster_personalities():
    users = session.query(Personality).all()
    arr = np.zeros((5 ,5))
    codes = ['O', 'C', 'E', 'A', 'N']
    for each in users:
        pvec = each.get_vector()
        ids = np.argsort(pvec)
        arr[ids[-1], ids[-2]] += 1
        arr[ids[-2], ids[-1]] += 1

    hist = []
    labels = []
    for i in range(5):
        for j in range(5):
            if i<j:
                hist.append(arr[i,j])
                labels.append(codes[i]+'&'+codes[j])

    plt.bar(labels, hist)
    plt.xlabel('Different combinations of 5 personality traits')
    plt.ylabel('Frequencies')
    plt.show()
    pdb.set_trace()

def cluster_genres():
    users_genres = session.query(GenreProf).all()
    genres = ["Blues", "Contemporary", "Country", "Electronic", "Rap", "Pop", "Reggae", "Rock"]
    gvecs = []
    for user in users_genres:
        gvec = user.get_vector()
        gvec = np.array(gvec)/ sum(gvec)
        gvecs.append(gvec[:-1])  ## removing others
    
    gvecs = np.array(gvecs)
    plt.bar(genres, gvecs.sum(axis=0))
    plt.xlabel('Different genres of music identified')
    plt.ylabel('Normalized Frequencies')
    plt.show()
    
    gvecs = np.transpose(gvecs)
    corr = np.corrcoef(gvecs)

    fig, ax = plt.subplots()
    im = ax.imshow(corr, cmap='hot', interpolation='nearest')
    ax.set_xticks(np.arange(len(genres)))
    ax.set_yticks(np.arange(len(genres)))

    ax.set_xticklabels(genres)
    ax.set_yticklabels(genres)

    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel('Correlation coefficients', rotation=-90, va="bottom")
    plt.show()
    pdb.set_trace()


def cluster_ages():
    users = session.query(User).all()
    age_clusters = {'0':[], '1':[], '2':[]}
    for user in users:
        if user.age!=0:
            gvec = session.query(GenreProf).filter_by(user_id = user.id_).first().get_vector()
            gvec = np.array(gvec)/ sum(gvec)
            if user.age <= 20:
                age_clusters['0'].append(gvec[:-1]) 
            elif user.age <= 30:
                age_clusters['1'].append(gvec[:-1])
            else:
                age_clusters['2'].append(gvec[:-1])
    
    genres = ["Blues", "Contemporary", "Country", "Electronic", "Rap", "Pop", "Reggae", "Rock"]
    cluster_codes = ['Age <= 20', '20 < Age <= 30', 'Age > 30']

    for cluster in age_clusters.keys():
        gvecs = np.array(age_clusters[cluster])
        plt.bar(genres, gvecs.sum(axis=0)/gvecs.shape[0])
        plt.xlabel('Different music genres')
        plt.ylabel('Normalized Frequencies')
        plt.title('Distribution of music genres for age group given by '+cluster_codes[int(cluster)])
        plt.show()

    pdb.set_trace()

def cluster_gender():
    users = session.query(User).all()
    age_clusters = {'0':[], '1':[]}
    for user in users:
        if user.gender!='U':
            gvec = session.query(GenreProf).filter_by(user_id = user.id_).first().get_vector()
            gvec = np.array(gvec)/ sum(gvec)
            if user.gender == 'M':
                age_clusters['0'].append(gvec[:-1]) 
            elif user.gender <= 'F':
                age_clusters['1'].append(gvec[:-1])
            
    genres = ["Blues", "Contemporary", "Country", "Electronic", "Rap", "Pop", "Reggae", "Rock"]
    cluster_codes = ['Male', 'Female']

    for cluster in age_clusters.keys():
        gvecs = np.array(age_clusters[cluster])
        plt.bar(genres, gvecs.sum(axis=0)/gvecs.shape[0])
        plt.xlabel('Different music genres')
        plt.ylabel('Normalized Frequencies')
        plt.title('Distribution of music genres for gender given by '+cluster_codes[int(cluster)])
        plt.show()

    pdb.set_trace()


def dominant_personality_music(g1, g2):

    genre_g1 = [0, 2, 5, 6]
    genre_g2 = [3, 4, 1, 7]
    upersonalities = session.query(Personality).all()
    ugenre_profiles = session.query(GenreProf).all()
    arr = np.zeros((2, 2))
    for pvec in upersonalities:
        user_id = pvec.user_id
        pvec = np.array(pvec.get_vector())
        pvec_g1 = pvec[g1].sum()
        pvec_g2 = pvec[g2].sum()
        if pvec_g1 > pvec_g2:
            dom_pvec = 0
        else:
            dom_pvec = 1

        try:
            gvec = session.query(GenreProf).filter_by(user_id = user_id).first().get_vector()
            gvec = np.array(gvec)
            gvec_g1 = gvec[genre_g1].sum()
            gvec_g2 = gvec[genre_g2].sum()
            if gvec_g1 > gvec_g2:
                dom_gvec = 0
            else:
                dom_gvec = 1
            
            arr[dom_pvec, dom_gvec] += 1
        except:
            continue

    from scipy.stats import chi2_contingency
    chi2, pvalue, _, _ = chi2_contingency(arr)
    #pdb.set_trace()
    return pvalue

def corr_personality_genre():
    codes = {'0_1':0, '0_2':1, '0_3':2, '0_4':3, '1_2':4, '1_3':5, '1_4':6, '2_3':7, '2_4':8, '3_4':9} 
    upersonalities = session.query(Personality).all()
    ugenre_profiles = session.query(GenreProf).all()
    arr = np.zeros((10, 8))
    for pvec in upersonalities:
        user_id = pvec.user_id
        pvec = np.array(pvec.get_vector())
        ids = np.argsort(pvec)
        id1, id2 = ids[-1], ids[-2]
        if id1>id2:
            code = '{}_{}'.format(id2, id1)
        else:
            code = '{}_{}'.format(id1, id2)

        try:
            gvec = session.query(GenreProf).filter_by(user_id = user_id).first().get_vector()
            gvec = np.array(gvec)
            arr[codes[code]] += gvec[:-1]
        except:
            continue
    pdb.set_trace()
    from scipy.stats import chi2_contingency
    chi2, pvalue, _, _ = chi2_contingency(arr)
    #pdb.set_trace()
    return pvalue

    
    


if __name__ == "__main__":
    # session = setup(DB_URL)
    session = get_debug_session(DB_URL)
    
    corr_personality_genre()

    #p = dominant_personality_music([0, 1, 2], [3, 4]) # 0.1774461657461066
    #print (p)
    #p = dominant_personality_music([0, 1, 3], [2, 4]) ##invalid
    #print (p)
    #p = dominant_personality_music([0, 1, 4], [2, 3]) ## pvalue: 0.7031687608980215
    #print (p)
    #p = dominant_personality_music([0, 2, 4], [1, 3])  ## pvalue: 0.6615391927567419
    #print (p)

    # cluster_personalities()
    # cluster_genres()
    # cluster_ages()
    # cluster_gender() 

    # combine_users()
    # clean_data_invalid_songs()
    # clean_data_no_songs()
    pdb.set_trace()
