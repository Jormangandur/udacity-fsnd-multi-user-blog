import webapp2
import jinja2
import app.credential_helpers
import app.models
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

    Args:
        secure_val: String, hash to be tested in format 'value|hash'

    Returns:
        True if secure_val is valid
        None if invalid
    """

    def initialize(self, *a, **kw):
        """Get currently logged in user on every HTTP request

        Extends GAE RequestHandler.initialize() method to retrieve logged in
        user from browser cookie. Sets the current user to BlogHandler variable
        self.user.
        """
        webapp2.RequestHandler.initialize(self, *a, **kw)
        user_id_cookie = self.get_cookie('user_id')
        self.user = user_id_cookie and app.models.User.by_id(
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
        cookie = app.credential_helpers.make_secure(val)
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
            return app.credential_helpers.check_secure(cookie)

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

    def prev_like(self, likes, user_id):
        for like in likes:
            if like.liked_by_id == user_id:
                return True

    def check_like(self, post, likes):
        if not self.user:
            self.set_cookie('error', 'no_user')
            return
        if self.user.key().id() == post.owner_id:
            self.set_cookie('error', 'like_own_post')
            return
        if self.prev_like(likes, self.user.key().id()):
            self.set_cookie('error', 'prev_like')
            return

        return True
