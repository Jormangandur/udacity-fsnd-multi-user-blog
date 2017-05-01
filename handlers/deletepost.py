from handlers.blog import BlogHandler
from models.blogpost import BlogPost
from models.like import Like
from models.comment import Comment
from helpers import *
from google.appengine.ext import db


class DeletePostHandler(BlogHandler):
    def get(self, post_id):
        post = BlogPost.by_id(post_id)
        likes = Like.by_post_id(post_id)
        comments = Comment.by_post_id(post_id)
        if self.user and post and self.user.key().id() == post.owner_id:
            post.delete()
            for like in likes:
                like.delete()
            for comment in comments:
                comment.delete()
        self.redirect('/blog')
