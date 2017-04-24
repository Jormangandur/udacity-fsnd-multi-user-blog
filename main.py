import webapp2
import os
import jinja2
import models
import credentialhelpers
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


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
        cookie = credentialhelpers.make_secure(val)
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
        if cookie and credentialhelpers.check_secure(cookie):
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
        posts = db.GqlQuery(
            "SELECT * FROM BlogPost ORDER BY created desc limit 10")

        self.render("front.html.j2", posts=posts, env=jinja_env)

    def get(self):
        self.render_front()


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
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            post = models.BlogPost(subject=subject, content=content)
            post.put()
            self.redirect("/blog/%s" % str(post.key().id()))
        else:
            error = "Please enter subject and content!"
            self.render_new_post(subject, content, error)


class ShowPostHandler(BlogHandler):
    """Handler for '/blog/[post-id]' post permalink page.

    Retrieves post id from url and displays a permalink page for the post.
    404 if post id doesnt exist
    """

    def render_post(self, post_id):
        post = models.BlogPost.get_by_id(post_id)
        if post:
            self.render("permalink.html.j2", post=post, env=jinja_env)
        else:
            self.error(404)
            return

    def get(self, post_id):
        post_id = int(post_id)
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
        username = str(self.request.get('username'))
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')
        error_name = ""
        error_password = ""
        error_pass_match = ""
        error_email = ""
        error = False

        if not (credentialhelpers.valid_username(username)):
            error_name = "Username is invalid"
            error = True
        user = models.User.by_name(username)
        if user:
            error_name = "That user already exists"
            error = True
        if not (credentialhelpers.valid_password(password)):
            error_password = "Password is invalid"
            error = True
        else:
            if (password != verify):
                error_pass_match = "Passwords do not match"
                error = True

        if (email and (not credentialhelpers.valid_email(email))):
            error_email = "Email is invalid"
            error = True

        if (error):
            self.render_form(username, email, error_name,
                             error_password, error_pass_match, error_email)
        else:
            user = models.User.register(username, password, email)
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
        user_id_cookie = self.get_cookie('user_id')
        if user_id_cookie and credentialhelpers.check_secure(user_id_cookie):
            user_id = int(user_id_cookie.split('|')[0])
            user = models.User.by_id(user_id)
            username = user.username
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
        salt = user.password.split('|')[1]
        if self.make_pw_hash(user.username, password, salt) == user.password:
            return True

    def get(self):
        self.render_form()

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        user = models.User.login(username, password)
        if user:
            self.login(user)
            self.redirect('/blog')
        else:
            error = "Invalid login"
            self.render_form(error)


class LogoutHandler(BlogHandler):
    """Handler for '/blog/logout'

    Calls parent BlogHandler logout() method to remove user_id cookie then
    redirects to '/blog'
    """

    def get(self):
        self.logout()
        self.redirect('/blog')


app = webapp2.WSGIApplication([
    ('/blog', MainPage),
    ('/blog/newpost', NewPostHandler),
    ('/blog/(\d+)', ShowPostHandler),
    ('/blog/signup', SignupHandler),
    ('/blog/welcome', WelcomeHandler),
    ('/blog/login', LoginHandler),
    ('/blog/logout', LogoutHandler),
], debug=True)
