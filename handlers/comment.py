from handlers.blog import BlogHandler
from models.comment import Comment
from helpers import *


class CommentHandler(BlogHandler):
    def create_comment(self, content, owner_id, post_id):
        comment = Comment(
            parent=comments_key(), content=content,
            owner_id=owner_id, post_id=post_id)
        comment.put()

    def post(self, post_id):
        content = self.request.get('content')
        owner_id = self.user.key().id()
        post_id = int(post_id)

        if content and owner_id and post_id:
            self.create_comment(content, owner_id, post_id)
        self.redirect('/blog/%s' % post_id)
