import re
import random
import string
import hashlib
import hmac
from google.appengine.ext import db


USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")
SECRET = 'secret'


def get_env():
    import main
    return main.jinja_env


def render_str(template, **params):
    """Renders a jinja2 template string.

    Retrieves a jinja2 template from jinja_env and renders it with given params.

    Args:
        template: String, path of jinja2 template
        **params: Optional params to pass to template as variable

    Returns:
        Rendered template as unicode string
    """

    jinja_env = get_env()
    t = jinja_env.get_template(template)
    return t.render(params)


def blog_key(name='default'):
    return db.Key.from_path('BlogPost', name)


def likes_key(name='default'):
    return db.Key.from_path('likes', name)


def comments_key(name='default'):
    return db.Key.from_path('Comment', name)


def users_key(group='default'):
    return db.Key.from_path('users', group)


def make_salt():
    """Generates a random 5 character salt string for hashing
    """
    return ''.join(random.choice(string.letters) for x in xrange(5))


def pw_hash(username, password, salt=None):
    """Generates a hash of a users password for secure storage or comparison.

    For a new user a salt is generated and the password is hashed and returned.
    For an existing user, the salt is passed as salt parameter and is then
    hashed and returned for comparison.
    Args:
        username: String
        password: String
        salt: String (optional)

    Returns:
        Hashed password in form 'salt|hash'
    """
    if not salt:
        salt = make_salt()
    hash = hashlib.sha256(username + password + salt).hexdigest()
    return '%s|%s' % (salt, hash)


def valid_pw_hash(username, password, hash):
    """Checks a password for validity against hashed password.

    Retrieves the salt from the pre-hashed value by splitting the string.
    Generates a hash of the password and compares the the pre-hashed value.
    Args:
        username: String
        password: String
        hash: String in format 'salt|hash'

    Returns:
        True if password is valid
        None if invalid
    """
    salt = hash.split('|')[0]
    if hash == pw_hash(username, password, salt):
        return True


# Check validity for user signup credentials against regular expressions


def valid_username(username):
    return USER_RE.match(username)


def valid_password(password):
    return PASS_RE.match(password)


def valid_email(email):
    return EMAIL_RE.match(email)


def make_secure(val):
    """Creates a hashed value.

    Hashes the given value combined with a SECRET key using hmac.

    Args:
        val: String, value to be hashed

    Returns:
        String in format 'val|hash'
    """
    return '%s|%s' % (val, hmac.new(SECRET, val).hexdigest())


def check_secure(secure_val):
    """Checks validity of a hash.

    Compares a given hash pair with a new computed hash based on the value
    portion of the original.

    Args:
        secure_val: String, hash to be tested in format 'value|hash'

    Returns:
        True if secure_val is valid
        None if invalid
    """
    test_val = secure_val.split('|')[0]
    if secure_val == make_secure(test_val):
        return test_val


def findWord(w):
    return re.compile(r"\b({0})\b".format(w), flags=re.IGNORECASE).search
