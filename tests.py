from datetime import datetime, timedelta
import unittest #library used for testing
from app import app,db
from app.models import User, Post

class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQL_ALCHEMY_URI'] = 'sqlite:///'
        db.create_all()


    def  tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashng(self):
        u = User(username='Tolu')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))



    def test_follow(self):
        u1=User(username='john', email='john@email.com')
        u2=User(username='mohammed', email='mohammed@email.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u1.followers.all(), [])

        u1.follow(u2)
        db.session.commt()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, 'mohammed')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, 'john')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)

    def test_followed_posts(self):
        #create users
        u1=User(username='tomi', email='tomi@example.com')
        u2=User(username='alex', email='alex@example.com')
        u3=User(username='daniel', email='daniel@example.com')
        u4=User(username='bolaji', email='bolaji@example.com')
        db.session.add_all([u1,u2,u3,u4])

        #create posts
        now = datetime.utcnow()
        p1 = Post(body='post from tomi', author=u1, timestamp=now + timedelta(seconds=1))
        p2 = Post(body='post from alex', author=u2, timestamp=now + timedelta(seconds=2))
        p3 = Post(body='post from danel', author=u3, timestamp=now + timedelta(seconds=3))
        p4 = Post(body='post from bolaji', author=u4, timestamp=now + timedelta(seconds=4))
        db.session.add_all([p1,p2,p3,p4])
        db.session.commit()

        #follow users
        u1.follow(u2)
        u1.follow(u4)
        u2.follow(u3)
        u3.follow(u4)

        #return followed posts for each user
        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()

        self.assertEqual(f1, [u2,u4,u1])
        self.assertEqual(f2, [u3,u2])
        self.assertEqual(f3, [u4,u3])
        self.assertEqual(f4, [u4])

if __name__ == '__main __':
   unittest.main(verbosity=2)


