from handlers.blog import BlogHandler
from helpers import *


class WelcomeHandler(BlogHandler):
    """Handler for '/blog/Welcome' new user page.

    Generates a personalised welcome page for new users with their username
    present.
    """

    @BlogHandler.user_logged_in
    def get(self):
        """Generates page with personalised welcome message.

        Gets user_id from browser cookie, retrieves corresponding user from
        datastore and passes the username to the welcome template.

        Redirect to '/blog/signup' if cookie is not present or invalid
        to prevent malicious access.
        """
        if self.user:
            username = self.user.username
            self.render("welcome.html.j2", username=username)
        else:
            self.redirect('/blog/signup')
