from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from hashlib import md5

#this is the database relationship for the follower
followers = db.Table('followers',   db.Column('follower_id',db.Integer, db.ForeignKey('user.id')),  db.Column('followed_id',db.Integer, db.ForeignKey('user.id')))
                     #db.Column('follower_id',db.Integer, db.ForeignKey('user.id')),
                     #db.Column('followed_id',db.Integer, db.ForeignKey('user.id')))
                     # what is the user.id, where is t from? is it fromthe class User which means User.id or what





class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __repr__(self):
        return '<post {}>'.format(self.body)





# this should normally be at the top before post
class User(UserMixin,db.Model):   #this class User represents a table in the database. shows how you want your stuffs to bw configured in the database
    id = db.Column(db.Integer, primary_key=True) # this id variable should always be there.it is specifically used by sqlalchmy. the others like username or password can be different but not id
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)


    def __repr__(self):
        return '<user {}'.format(self.username)

    def set_password(self,password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self,size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)







    #followers model,this goes into the  database
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy="dynamic"),
        lazy='dynamic'
    )
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self,user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self,user):   #so far you follow someone the system counts. the follwed_id  are the people you following and it checks for the user_id you following if it >1 it true
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id).filter(
                followers.c.follower_id == self.id).order_bufhutyy(Post.timestamp.desc()))
        own = Post.query.filter_by(user_id = self.id)
        return followed.union(own).order_by(Post.timestamp.desc())














@login.user_loader
def load_user(id):
    return User.query.get(int(id))



