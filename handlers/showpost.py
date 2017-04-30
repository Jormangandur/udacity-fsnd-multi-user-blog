from handlers.blog import BlogHandler
from models.blogpost import BlogPost
from models.like import Like
from models.comment import Comment
from helpers import *
from google.appengine.ext import db


class ShowPostHandler(BlogHandler):
    """Handler for '/blog/[post-id]' post permalink page.

    Retrieves post id from url and displays a permalink page for the post.
    404 if post id doesnt exist
    """

    def render_post(self, post, error="", unlike=False, comments=""):
        error_msg = ""
        if post:
            can_edit = False
            current_user_id = ""
            if self.user:
                if self.user.key().id() == post.owner_id:
                    can_edit = True
                current_user_id = self.user.key().id()
            if error == "like_own_post":
                error_msg = "Cannot like own post"
            elif error == "no_user":
                error_msg = "You must be logged in to like a post"
            elif error == "prev_like":
                error_msg = "You can only like a post once"
            self.set_cookie("error", "")
            self.render("permalink.html.j2", post=post,
                        error_msg=error_msg, unlike=unlike, can_edit=can_edit,
                        comments=comments, current_user_id=current_user_id)
        else:
            self.error(404)
            return

    def get(self, post_id):
        unlike = False
        error = self.get_cookie('error')
        key = db.Key.from_path('BlogPost', int(
            post_id), parent=blog_key())
        post = db.get(key)
        likes = Like.all().filter('post_id =', int(
            post_id)).ancestor(likes_key())

        if self.user and self.prev_like(likes, self.user.key().id()):
            unlike = True

        comments = Comment.all().filter(
            'post_id =', int(post_id)).ancestor(
                comments_key()).order('-created')
        self.render_post(post, error, unlike, comments)
