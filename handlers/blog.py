import webapp2
import jinja2
from models.user import User
from helpers import *
from functools import wraps
from models.blogpost import BlogPost
from models.comment import Comment
from google.appengine.ext import db
import logging


def get_env():
    import main
    return main.jinja_env


class BlogHandler(webapp2.RequestHandler):
    """Base class for blog-related handlers.

    Contains base functionality for all blog-related handlers:
        - HTML generation
        - Cookie handling
        - User Login/Logout
    """

    @staticmethod
    def post_exists(function):
        @wraps(function)
        def wrapper(self, post_id, *args, **kwargs):
            post = BlogPost.by_id(post_id)
            if post:
                return function(self, post, *args, **kwargs)
            else:
                self.error(404)
                return
        return wrapper

    @staticmethod
    def user_logged_in(function):
        @wraps(function)
        def wrapper(self, *args, **kwargs):
            if self.user:
                return function(self, *args, **kwargs)
            else:
                self.redirect('/blog/login')
                return
        return wrapper

    @staticmethod
    def user_owns_post(function):
        @wraps(function)
        def wrapper(self, post, *args, **kwargs):
            if self.user.key() == post.owner.key():
                return function(self, post, *args, **kwargs)
            else:
                self.redirect('/blog/%s' % post_id)
                return
        return wrapper

    @staticmethod
    def comment_exists(function):
        @wraps(function)
        def wrapper(self, comment_id, *args, **kwargs):
            logging.info(comment_id)
            comment = Comment.by_id(comment_id)
            if comment:
                return function(self, comment, *args, **kwargs)
            else:
                self.error(404)
                return
        return wrapper

    @staticmethod
    def user_owns_comment(function):
        @wraps(function)
        def wrapper(self, comment, *args, **kwargs):
            logging.info(comment)
            if self.user.key() == comment.owner.key():
                return function(self, comment, *args, **kwargs)
            else:
                self.redirect('blog/%s' % comment.post_id)
                return
        return wrapper

    def initialize(self, *a, **kw):
        """Get currently logged in user on every HTTP request

        Extends GAE RequestHandler.initialize() method to retrieve logged in
        user from browser cookie. Sets the current user to BlogHandler variable
        self.user.
        """
        webapp2.RequestHandler.initialize(self, *a, **kw)
        user_id_cookie = self.get_cookie('user_id')
        self.user = user_id_cookie and User.by_id(
            int(user_id_cookie))

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
        env = get_env()
        t = env.get_template(template)
        if self.user:
            params['user_id'] = self.user.key().id()
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
        cookie = make_secure(val)
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
        cookie = self.request.cookies.get(name)
        if cookie:
            return check_secure(cookie)

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

    def prev_like(self, likes, user):
        for like in likes:
            if like.owner.key() == user.key():
                return True

    def check_like(self, post, likes):
        if not self.user:
            self.set_cookie('error', 'no_user')
            return
        if self.user.key() == post.owner.key():
            self.set_cookie('error', 'like_own_post')
            return
        if self.prev_like(likes, self.user):
            self.set_cookie('error', 'prev_like')
            return

        return True
