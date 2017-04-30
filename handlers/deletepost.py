from handlers.blog import BlogHandler
from models.blogpost import BlogPost
from models.like import Like
from helpers import *
from google.appengine.ext import db


class DeletePostHandler(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('BlogPost', int(
            post_id), parent=blog_key())
        post = db.get(key)
        likes = Like.all().filter('post_id =', int(
            post_id)).ancestor(likes_key())
        if self.user and post and self.user.key().id() == post.owner_id:
            post.delete()
            for like in likes:
                like.delete()
        self.redirect('/blog')
