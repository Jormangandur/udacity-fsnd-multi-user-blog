from handlers.blog import BlogHandler
from models.comment import Comment
from helpers import *


class CommentHandler(BlogHandler):

    @BlogHandler.user_logged_in
    @BlogHandler.post_exists
    def post(self, post):
        content = self.request.get('content')
        owner_id = self.user.key().id()
        post_id = post.key().id()

        if content and owner_id and post_id:
            comment = Comment.make(content, owner_id, post_id)
            comment.put()
        self.redirect('/blog/%s' % post_id)
