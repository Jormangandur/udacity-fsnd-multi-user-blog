from handlers.blog import BlogHandler
from models.like import Like
from helpers import *
from google.appengine.ext import db


class UnlikePostHandler(BlogHandler):

    def post(self, post_id):
        likes = Like.by_post_id(post_id)
        if likes and self.user:
            for like in likes:
                if like.owner_id == self.user.key().id():
                    like.delete()
        self.redirect('/blog/%s' % post_id)
