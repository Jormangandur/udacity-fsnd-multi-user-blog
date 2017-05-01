from handlers.blog import BlogHandler
from models.blogpost import BlogPost
from models.like import Like
from helpers import *
from google.appengine.ext import db


class LikePostHandler(BlogHandler):

    def post(self, post_id):
        likes = Like.by_post_id(post_id)
        post = BlogPost.by_id(post_id)
        if post and likes:
            can_like = self.check_like(post, likes)
            if can_like:
                like = Like.make(post_id, self.user.key().id())
                like.put()

        self.redirect('/blog/%s' % post_id)
