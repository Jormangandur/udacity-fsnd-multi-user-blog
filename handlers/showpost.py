from handlers.blog import BlogHandler
from models.blogpost import BlogPost
from models.like import Like
from models.comment import Comment
from helpers import *
from google.appengine.ext import db
import logging


class ShowPostHandler(BlogHandler):
    """Handler for '/blog/[post-id]' post permalink page.

    Retrieves post id from url and displays a permalink page for the post.
    404 if post id doesnt exist
    """

    def render_post(self, post, error="", unlike=False, comments=""):
        error_msg = ""
        if post:
            can_edit = False
            current_user = ""
            if self.user:
                if self.user.key() == post.owner.key():
                    can_edit = True
                current_user = self.user
            if error == "like_own_post":
                error_msg = "Cannot like own post"
            elif error == "no_user":
                error_msg = "You must be logged in to like a post"
            elif error == "prev_like":
                error_msg = "You can only like a post once"
            self.set_cookie("error", "")
            self.render("permalink.html.j2", post=post,
                        error_msg=error_msg, unlike=unlike, can_edit=can_edit,
                        comments=comments, current_user=current_user)
        else:
            self.error(404)
            return

    @BlogHandler.post_exists
    def get(self, post):
        unlike = False
        error = self.get_cookie('error')
        likes = post.likes.ancestor(comments_key())

        if self.user and self.prev_like(likes, self.user):
            unlike = True
        comments = post.comments.ancestor(comments_key())
        self.render_post(post, error, unlike, comments)
