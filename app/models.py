from datetime import datetime
from app import db, app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from hashlib import md5
from time import time
import jwt

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):   #User class inherits from db.Model, a base class for all models from Flask-SQLAlchemy
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)    #indexing allows efficient search
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')   #not a db field, but a high-level representatn btw users and posts.
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self): #tells Python how to print objects of this class, and useful for debugging
        return '<User {}>'.format(self.username)
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicons&s={}'.format(digest, size)

    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id),
        secondaryjoin=(followers.c.followed_id),
        backref=db.backref('followers',lazy='dynamic'), lazy='dynamic'
    )
    #many-to-many relationship:
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

#password hashing mechanism: user can now do secure password verification, without a need to store original passwords
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    #to add(follow) and remove relationships(unfollow)
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password':self.id, 'exp':time()+expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod   #does not need an object, and so can be invoked directly from d class
    def verify_reset_password_token(token):
        try:
            id=jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password'] #load user
        except:
            return
        return User.query.get(id)

class Post(db.Model):   #Post class inherits from db.Model, a base class for all models from Flask-SQLAlchemy
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow) #indexing helps to retrieve posts in chronological order. We're passing the function set to default and not the result of the fxn. This ensures uniform timestamp for every user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

#the table below is not a model. It is an auxiliary table with only foreign keys.


'''
Each time u make changes to the applicatn, rerun the test to make sure that 
no feature is being affected.
'''

