from handlers.blog import BlogHandler
from models.like import Like
from helpers import *
from google.appengine.ext import db


class UnlikePostHandler(BlogHandler):

    @BlogHandler.user_logged_in
    @BlogHandler.post_exists
    def post(self, post):
        post_id = post.key().id()
        owner_likes = self.user.likes
        like = self.user.likes.filter('post_id =', int(
            post_id)).ancestor(likes_key()).get()
        if like:
            like.delete()
        self.redirect('/blog/%s' % post_id)
