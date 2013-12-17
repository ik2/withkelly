import jinja2
import os
import webapp2
import re
import json
from databases import *
from utils import *
from google.appengine.api import memcache

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def blog_front(update = False):
    key = 'recent'
    r = memcache.get(key)
    if r:
        posts = r
    else:
        posts = None
    if posts is None or update:
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 5")
        posts = list(posts)
        memcache.set(key, posts)
    return posts

class BlogHandler(webapp2.RequestHandler):
    def markup(self, template, **values):
        self.response.write(JINJA_ENVIRONMENT.get_template(template).render(values))

    def set_cookie(self, name, value):
        self.response.headers.add_header('Set-Cookie', name + '=' + make_secure_value(value) + '; Path=/')

    def check_cookie(self, template):
        cookie_str = self.request.cookies.get('user_id')
        if cookie_str and check_secure_value(cookie_str):
            uid = cookie_str.split('|')[0]
            user = User.get_by_id(int(uid))
            self.markup(template, username = user.username)
        else:
            self.redirect("/signin")

class Signup(BlogHandler):
    def get(self):
        self.markup('signup.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')
        user = User.by_name(username)
        values = {}
        if not valid_username(username):
            values['error_username'] = "That's not a valid username."
        if user:
            values['error_username2'] = "Username already exists."
        if not valid_password(password):
            values['error_password'] = "That wasn't a valid password."
        if password != verify:
            values['error_verify'] = "Your passwords didn't match."
        if not valid_email(email):
            values['error_email'] = "That's not a valid email."
        if values:
            values.update({'username' : username, 'email' : email})
            self.markup('signup.html', **values)
        else:
            password_hashed = make_password_hash(username, password)
            user = User(username = username, password_hashed = password_hashed, email = email)
            user.put()
            self.set_cookie("user_id", str(user.key().id()))
            self.redirect("/dashboard")

class Dashboard(BlogHandler):
    def get(self):
        self.check_cookie("dashboard.html")

class Signin(BlogHandler):
    def get(self):
        self.markup('signin.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        user = User.by_name(username)
        if user and valid_password_hash(username, password, user.password_hashed):
            self.set_cookie("user_id", str(user.key().id()))
            self.redirect("/dashboard")
        else:
            msg = "Invalid signin"
            self.markup('signin.html', username = username, error = msg)

class Logout(BlogHandler):
    def get(self):
        self.response.delete_cookie('user_id')
        self.redirect("/signin")

class Blog(BlogHandler):
    def get(self):
        top5 = [("First slide", "holder.js/900x500/auto/#888:#8a8a8a/text:First slide"),
                ("Second slide", "holder.js/900x500/auto/#777:#7a7a7a/text:Second slide"),
                ("Third slide", "holder.js/900x500/auto/#666:#6a6a6a/text:Third slide"),
                ("Fourth slide", "holder.js/900x500/auto/#555:#5a5a5a/text:Fourth slide"),
                ("Fifth slide", "holder.js/900x500/auto/#444:#4a4a4a/text:Fifth slide"),
                ]
        posts = blog_front()
        self.markup("blog.html", posts = posts, top5 = top5)

class NewPost(BlogHandler):
    def get(self):
        self.check_cookie("newpost.html")

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")
        if subject and content:
            b = Post(subject = subject, content = content)
            b.put()
            blog_front(True)
            permalink = str(b.key().id())
            self.redirect("/post/" + permalink)
        else:
            msg = "subject and content, please!"
            self.markup("newpost.html", subject = subject, content = content, error = msg)

class PostPage(BlogHandler):
    def get(self, post_id):
        post = Post.get_by_id(int(post_id))
        self.markup("post.html", post = post)

app = webapp2.WSGIApplication([
    ('/?', Blog),
    ('/post/([0-9]+)', PostPage),
    ('/signup', Signup),
    ('/signin', Signin),
    ('/dashboard', Dashboard),
    ('/newpost', NewPost),
    ('/logout', Logout),
], debug=True)
