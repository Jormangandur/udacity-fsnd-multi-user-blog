import app.models
import app.credential_helpers
from blog_handler import *
from google.appengine.ext import db


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

        self.render("front.html.j2", posts=posts)

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
            post = app.models.BlogPost(subject=subject, content=content)
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
        post = app.models.BlogPost.get_by_id(post_id)
        if post:
            self.render("permalink.html.j2", post=post)
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

        if not (app.credential_helpers.valid_username(username)):
            error_name = "Username is invalid"
            error = True
        user = app.models.User.by_name(username)
        if user:
            error_name = "That user already exists"
            error = True
        if not (app.credential_helpers.valid_password(password)):
            error_password = "Password is invalid"
            error = True
        else:
            if (password != verify):
                error_pass_match = "Passwords do not match"
                error = True

        if (email and (not app.credential_helpers.valid_email(email))):
            error_email = "Email is invalid"
            error = True

        if (error):
            self.render_form(username, email, error_name,
                             error_password, error_pass_match, error_email)
        else:
            user = app.models.User.register(username, password, email)
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
        if user_id_cookie and app.credential_helpers.check_secure(user_id_cookie):
            user_id = int(user_id_cookie.split('|')[0])
            user = app.models.User.by_id(user_id)
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

        user = app.models.User.login(username, password)
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
