from handlers.blog import BlogHandler
from models.user import User
from helpers import *


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

        user = User.login(username, password)
        if user:
            self.login(user)
            self.redirect('/blog')
        else:
            error = "Invalid login"
            self.render_form(error)
