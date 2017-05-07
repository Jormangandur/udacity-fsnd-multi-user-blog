from handlers.blog import BlogHandler
from models.blogpost import BlogPost
from models.like import Like
from helpers import *
from google.appengine.ext import db
import logging


class LikePostHandler(BlogHandler):

    @BlogHandler.user_logged_in
    @BlogHandler.post_exists
    def post(self, post):
        post_id = post.key().id()
        likes = Like.by_post_id(post_id)
        can_like = self.check_like(post, likes)
        if can_like:
            like = Like.make(self.user, post_id)
            like.put()

        self.redirect('/blog/%s' % post_id)
