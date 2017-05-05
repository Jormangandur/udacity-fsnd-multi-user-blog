from handlers.blog import BlogHandler
from models.blogpost import BlogPost
from helpers import *


class FrontPageHandler (BlogHandler):
    """Loads all-post homepage view.

    Loads the homepage with the 10 most recent posts displayed
    """

    def render_front(self):
        """Renders front page with recent posts.

        Gets 10 most recent posts from datastore and passes them as variables
        into front template.
        """
        posts = BlogPost.all()
        if posts:
            posts = posts.order(
                '-created').ancestor(blog_key()).fetch(limit=10)

        self.render("front.html.j2", posts=posts)

    def get(self):
        self.render_front()
