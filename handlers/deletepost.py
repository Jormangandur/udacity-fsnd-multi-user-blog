from handlers.blog import BlogHandler
from models.blogpost import BlogPost
from models.like import Like
from models.comment import Comment
from helpers import *
from google.appengine.ext import db


class DeletePostHandler(BlogHandler):
    @BlogHandler.user_logged_in
    @BlogHandler.post_exists
    @BlogHandler.user_owns_post
    def get(self, post):
        post_id = post.key().id()
        likes = post.likes.ancestor(likes_key())
        comments = post.comments.ancestor(comments_key())
        post.delete()
        db.delete(likes)
        db.delete(post)
        self.redirect('/blog')
