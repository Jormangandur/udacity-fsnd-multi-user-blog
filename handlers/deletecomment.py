from handlers.blog import BlogHandler
from models.comment import Comment
from helpers import *

from google.appengine.ext import db


class DeleteCommentHandler(BlogHandler):

    @BlogHandler.user_logged_in
    @BlogHandler.comment_exists
    @BlogHandler.user_owns_comment
    def post(self, comment, post_id):
        comment = comment
        comment.delete()
        self.redirect('/blog/%s' % post_id)
