from handlers.blog import BlogHandler
from models.like import Like
from helpers import *
from google.appengine.ext import db


class UnlikePostHandler(BlogHandler):

    @BlogHandler.user_logged_in
    @BlogHandler.post_exists
    def post(self, post):
        post_id = post.key().id()
        owner_id = self.user.key().id()
        like = Like.by_post_id(post_id).filter(
            'owner_id =', int(owner_id)).ancestor(likes_key()).get()
        if like:
            like.delete()
        self.redirect('/blog/%s' % post_id)
