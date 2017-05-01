from handlers.blog import BlogHandler
from models.comment import Comment
from helpers import *

from google.appengine.ext import db


class DeleteCommentHandler(BlogHandler):
    def post(self, post_id, comment_id):
        comment = Comment.by_id(comment_id)
        comment.delete()
        self.redirect('/blog/%s' % post_id)
