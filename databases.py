import re
from google.appengine.ext import db

class User(db.Model):
    username = db.StringProperty(required = True)
    password_hashed = db.StringProperty(required = True)
    email = db.StringProperty()

    @classmethod
    def by_name(cls, username):
        user = cls.all().filter('username =', username).get()
        return user

class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

    def newline_replace(self):
        self.content = re.sub(r"[\r\n]+(?=.+)", "</p><p>", self.content)
        return self.content

    def as_dict(self):
        time_fmt = '%c'
        d = {'subject': self.subject,
             'content': self.content,
             'created': self.created.strftime(time_fmt),
            }
        return d


