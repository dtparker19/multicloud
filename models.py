from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property
from random import SystemRandom

from backports.pbkdf2 import pbkdf2_hmac, compare_digest
# from sqlalchemy import Column, Integer, String
from data import CRUDMixin, db

engine = create_engine('sqlite:///database.db', echo=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

# Set your classes here.
class Site(db.Model):
    __tablename__ = 'sites'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    url = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('users_user.id'), nullable=False, index=True)
    user = db.relationship('User', backref=db.backref('user_sites', lazy='dynamic'),foreign_keys=[user_id])

    def __repr__(self):
        return '<Site %r>' % self.name


class Visit(db.Model):
    __tablename__ = 'visits'
    id = db.Column(db.Integer, primary_key=True)
    browser = db.Column(db.String)
    date = db.Column(db.DateTime)
    event = db.Column(db.String)
    url = db.Column(db.String)
    ip_address = db.Column(db.String)
    site_id = db.Column(db.Integer, db.ForeignKey('site.id'))
    site = db.relationship('Site', backref=db.backref('site_visits', lazy='dynamic'),foreign_keys=[site_id])
    def __repr__(self):
        r = '<Visit for site ID {:d}: {} - {:%Y-%m-%d %H:%M:%S}>'
        return r.format(self.site_id, self.url, self.date)

class User(UserMixin, CRUDMixin, db.Model):
    __tablename__ = 'users_user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True)
    _password = db.Column(db.LargeBinary(120))
    _salt = db.Column(db.String(120))
    sites = db.relationship('Site', backref='user_sites', lazy='dynamic')

    @hybrid_property
    def password(self):
        return self._password

    # In order to ensure that passwords are always stored
    # hashed and salted in our database we use a descriptor
    # here which will automatically hash our password
    # when we provide it (i. e. user.password = "12345")
    @password.setter
    def password(self, value):
        # When a user is first created, give them a salt
        if self._salt is None:
            self._salt = bytes(SystemRandom().getrandbits(128))
        self._password = self._hash_password(value)

    def is_valid_password(self, password):
        """Ensure that the provided password is valid.

        We are using this instead of a ``sqlalchemy.types.TypeDecorator``
        (which would let us write ``User.password == password`` and have the incoming
        ``password`` be automatically hashed in a SQLAlchemy query)
        because ``compare_digest`` properly compares **all***
        the characters of the hash even when they do not match in order to
        avoid timing oracle side-channel attacks."""
        new_hash = self._hash_password(password)
        return compare_digest(new_hash, self._password)

    def _hash_password(self, password):
        pwd = password.encode("utf-8")
        salt = bytes(self._salt)
        buff = pbkdf2_hmac("sha512", pwd, salt, iterations=100000)
        return bytes(buff)

    def __repr__(self):
        return "<User #{:d}>".format(self.id)


# Create tables.
Base.metadata.create_all(bind=engine)

