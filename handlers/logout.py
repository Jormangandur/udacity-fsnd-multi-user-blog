from handlers.blog import BlogHandler
from helpers import *


class LogoutHandler(BlogHandler):
    """Handler for '/blog/logout'

    Calls parent BlogHandler logout() method to remove user_id cookie then
    redirects to '/blog'
    """

    def get(self):
        if self.user:
            self.logout()
            self.redirect('/blog')
        else:
            self.redirect('/blog/login')
