import webapp2
import os
import jinja2
import re
import random
import string
import hashlib
import hmac
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir), autoescape=True)

SECRET = 'secret'

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")


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


def render_str(template, **params):
    """Renders a jinja2 template string.

    Retrieves a jinja2 template from jinja_env and renders it with given params.

    Args:
        template: String, path of jinja2 template
        **params: Optional params to pass to template as variable

    Returns:
        Rendered template as unicode string
    """
    t = jinja_env.get_template(template)
    return t.render(params)


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


class BlogHandler(webapp2.RequestHandler):
    """Base class for blog-related handlers.

    Contains base functionality for all blog-related handlers:
        - HTML generation
        - Cookie handling
        - User Login/Logout

    Args:
        secure_val: String, hash to be tested in format 'value|hash'

    Returns:
        True if secure_val is valid
        None if invalid
    """

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        """Renders a jinja2 template into unicode.

        Retrieves a jinja2 template from jinja_env and renders it with given params.

        Args:
            template: String, path of jinja2 template
            **params: Optional params to pass to template as variable

        Returns:
            Rendered template as unicode string
        """
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        """Generates HTML.

        Passes a template and optional keywords to render_str() and then
        write() for output to browser

        Args:
            template: String, path of jinja2 template
            **kw: Optional params to pass to template as variable

        Returns:
            HTML page
        """
        self.write(self.render_str(template, **kw))

    def set_cookie(self, name, val):
        """Creates and sets a cookie.

        Args:
            name: String, name of the cookie to be set
            val: String, value for the cookie
        """
                self.write(self.rende
        cookie=make_secure(val)
        self.response.headers.add_header(
            'Set-Cookie', '%s=%s;Path=/' % (name, cookie))

    def get_cookie(self, name):
        """Retrieves a cookie from browser.

        Checks to see whether specific cookie exists and returns its value
        Args:
            name: String, name of the cookie to retrieve
        Returns:
            String containing the reqested cookie
            None if cookie did not exist
        """
        cookie=self.request.cookies.get(name)
        if cookie and check_secure(cookie):
            return cookie

    def login(self, user):
        """Sets 'user_id' cookie to logged in user.

        Gets the id key of a stored user and sets a corresponding cookie.
        Args:
            user: Instance of User() model/class.
        """
        self.set_cookie('user_id', str(user.key().id()))

    def logout(self):
        """Removes 'user_id' cookie from browser.
        """
        self.response.headers.add_header('Set-Cookie', 'user_id=;Path=/')


class MainPage (BlogHandler):
    """Loads all-post homepage view.

    Loads the homepage with the 10 most recent posts displayed
    """
    def render_front(self):
        """Renders front page with recent posts.

        Gets 10 most recent posts from datastore and passes them as variables
        into front template.
        """
        posts=db.GqlQuery(
            "SELECT * FROM BlogPost ORDER BY    created desc limit 10")

        self.render("front.html.j2", posts=posts)

    def get(self):
        self.render_front()

class BlogPost(db.Model):
    """Model class for blog posts.
    """
    subject=db.StringProperty(required=True)
    content=db.TextProperty(required=True)
    created=db.DateTimeProperty(auto_now_add=True)

    def render(self):
        return render_str("post.html.j2", post=self)


class User(db.Model):
    """Model class for user account information.
    """

    username=db.StringProperty(required=True)
    pw_hash=db.StringProperty(required=True)
    email=db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        """Get stored User instance corresponding to user id.

        Args:
            uid: Integer, id of a stored User instance.
        Returns:
            Instance of User Model/Class
        """
        return User.get_by_id(uid)

    @classmethod
    def by_name(cls, username):
        """Get stored User instance corresponding to username.

        Args:
            username: String, username of a stored User instance.
        Returns:
            Instance of User Model/Class
        """
        user=User.all().filter('username =', username).get()
        return user

    @classmethod
    def register(cls, username, password, email=None):
        """Create new User() model instance.

        Generate a hash of the password and assigns it along with username and
        email arguments to instance variables in a new User() model instance.
        Args:
            username: String
            password: String, raw password.
            email: String
        Returns:
            Instance of User Model/Class
        """
        password_hash=pw_hash(username, password)
        return User(username=username,
                    pw_hash=password_hash,
                    email=email)

    @classmethod
    def login(cls, username, password):
        """Check is user exists and password is correct.

        Args:
            username: String
            password: String, raw password.
        Returns:
            Instance of User Model/Class
        """
        user=cls.by_name(username)
        if user and valid_pw_hash(name, pw, user.pw_hash):
            return user


class NewPostHandler(BlogHandler):
    """Handler for '/blog/newpost'.
    """
    def render_new_post(self, subject="", content="", error=""):
        self.render("new_post.html.j2", subject=subject,
                    content=content, error=error)

    def get(self):
        self.render_new_post()

    def post(self):
        """Gets data from input form.

        Retrieves post subject and title from input form and creates a new User
        model then redirects to a permalink for the post.

        If subject and content are invalid the form is re-loaded with
        appropriate error messages.
        """
        subject=self.request.get("subject")
        content=self.request.get("content")

        if subject and content:
            post=BlogPost(subject=subject, content=content)
            post.put()
            self.redirect("/blog/%s" % str(post.key().id()))
        else:
            error="Please enter subject and content!"
            self.render_new_post(subject, content, error)


class ShowPostHandler(BlogHandler):
    """Handler for '/blog/[post-id]' post permalink page.

    Retrieves post id from url and displays a permalink page for the post.
    404 if post id doesnt exist
    """
    def render_post(self, post_id):
        post=BlogPost.get_by_id(post_id)
        if post:
            self.render("permalink.html.j2", post=post)
        else:
            self.error(404)
            return

    def get(self, post_id):
        post_id=int(post_id)
        self.render_post(post_id)


class SignupHandler(BlogHandler):
    """Handler for '/blog/signup' user signup page.
    """
    def render_form(self, username="", email="", error_name="",
                    error_password="", error_pass_match="", error_email=""):

        self.render("signup.html.j2", username=username, email=email,
                    error_name=error_name, error_password=error_password,
                    error_pass_match=error_pass_match, error_email=error_email)

    def get(self):
        self.render_form()

    def post(self):
        """Gets data from input form and creates a new user.

        Retrieves inputted user credentials to generate and store a new user
        and redirect to a welcome page.
        Will reload page with appropriate error messages if user already exists
        or any information is invalid.
        """
        username=str(self.request.get('username'))
        password=self.request.get('password')
        verify=self.request.get('verify')
        email=self.request.get('email')
        error_name=""
        error_password=""
        error_pass_match=""
        error_email=""
        error=False

        if not (valid_username(username)):
            error_name="Username is invalid"
            error=True
        user=User.by_name(username)
        if user:
            error_name="That user already exists"
            error=True
        if not (valid_password(password)):
            error_password="Password is invalid"
            error=True
        else:
            if (password != verify):
                error_pass_match="Passwords do not match"
                error=True

        if (email and (not valid_email(email))):
            error_email="Email is invalid"
            error=True

        if (error):
            self.render_form(username, email, error_name,
                             error_password, error_pass_match, error_email)
        else:
            user=User.register(username, password, email)
            user.put()
            self.login(user)
            self.redirect("/blog/welcome")


class WelcomeHandler(BlogHandler):
    """Handler for '/blog/Welcome' new user page.

    Generates a personalised welcome page for new users with their username
    present.
    """
    def get(self):
        """Generates page with personalised welcome message.

        Gets user_id from browser cookie, retrieves corresponding user from
        datastore and passes the username to the welcome template.

        Redirect to '/blog/signup' if cookie is not present or invalid
        to prevent malicious access.
        """
        user_id_cookie=self.get_cookie('user_id')
        if user_id_cookie and check_secure(user_id_cookie):
            user_id=int(user_id_cookie.split('|')[0])
            user=User.by_id(user_id)
            username=user.username
            self.render("welcome.html.j2", username=username)
        else:
            self.redirect('/blog/signup')


class LoginHandler(BlogHandler):
    """Handler for '/blog/Login' page.

    Takes username and password from input form and logs in corresponding user.

    Form is reloaded with appropriate error messages if user doesn't exist or
    if password doesn't match the stored value for that user.
    """
    def render_form(self, error=""):
        self.render("login.html.j2", error=error)

    def check_pw(self, user, password):
        """Checks if user password matches stored value.

        Creates a hash of the entered password from login form and compares it
        to the stored value for that user in the database.
        """
        salt=user.password.split('|')[1]
        if self.make_pw_hash(user.username, password, salt) == user.password:
            return True

    def get(self):
        self.render_form()

    def post(self):
        username=self.request.get('username')
        password=self.request.get('password')

        user=User.login(username, password)
        if user:
            self.login(user)
            self.redirect('/blog')
        else:
            error="Invalid login"
            self.render_form(error)


class LogoutHandler(BlogHandler):
    """Handler for '/blog/logout'

    Calls parent BlogHandler logout() method to remove user_id cookie then
    redirects to '/blog'
    """
    def get(self):
        self.logout()
        self.redirect('/blog')


app=webapp2.WSGIApplication([
    ('/blog', MainPage),
    ('/blog/newpost', NewPostHandler),
    ('/blog/(\d+)', ShowPostHandler),
    ('/blog/signup', SignupHandler),
    ('/blog/welcome', WelcomeHandler),
    ('/blog/login', LoginHandler),
    ('/blog/logout', LogoutHandler),
], debug=True)
