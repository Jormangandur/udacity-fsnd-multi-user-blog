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
        likes = post.likes.ancestor(likes_key())
        can_like = self.check_like(post, likes)
        if can_like:
            like = Like.make(self.user, post)
            like.put()

        self.redirect('/blog/%s' % post.key().id())
