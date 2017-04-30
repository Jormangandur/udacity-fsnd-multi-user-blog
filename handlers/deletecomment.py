from handlers.blog import BlogHandler
from models.comment import Comment
from helpers import *

from google.appengine.ext import db


class DeleteCommentHandler(BlogHandler):
    def post(self, post_id, comment_id):
        key = db.Key.from_path('Comment', int(
            comment_id), parent=comments_key())
        comment = db.get(key)
        comment.delete()

        self.redirect('/blog/%s' % post_id)
