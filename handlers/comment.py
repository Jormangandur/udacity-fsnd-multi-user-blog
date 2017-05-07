from handlers.blog import BlogHandler
from models.comment import Comment
from helpers import *


class CommentHandler(BlogHandler):

    @BlogHandler.user_logged_in
    @BlogHandler.post_exists
    def post(self, post):
        content = self.request.get('content')

        if content:
            comment = Comment.make(self.user, post, content)
            comment.put()
        self.redirect('/blog/%s' % post.key().id())
