import re
import hashlib
import hmac
import random
from string import letters

SECRET = 'secret'

username_re = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username_re.match(username)

password_re = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password_re.match(password)

email_re = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
def valid_email(email):
    return not email or email_re.match(email)

def make_secure_value(s):
    return s + "|" + hmac.new(SECRET, s).hexdigest()

def check_secure_value(h):
    val = h.split('|')[0]
    if h == make_secure_value(val):
        return val

def make_salt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))

def make_password_hash(name, pw, salt=None):
    if not salt:
        salt=make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return h + "|" + salt

def valid_password_hash(name, pw, h):
    salt = h.split('|')[1]
    return h == make_password_hash(name, pw, salt)


