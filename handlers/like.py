from handlers.blog import BlogHandler
from models.blogpost import BlogPost
from models.like import Like
from helpers import *
from google.appengine.ext import db


class LikePostHandler(BlogHandler):

    def post(self, post_id):
        likes = Like.all().filter('post_id =', int(
            post_id)).ancestor(likes_key())
        key = db.Key.from_path('BlogPost', int(
            post_id), parent=blog_key())
        post = db.get(key)
        if post and likes:
            can_like = self.check_like(post, likes)
            if can_like:
                like = Like(parent=likes_key(
                ), post_id=post.key().id(), liked_by_id=self.user.key().id())
                like.put()

        self.redirect('/blog/%s' % post_id)
