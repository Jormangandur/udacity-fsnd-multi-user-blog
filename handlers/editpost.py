from handlers.blog import BlogHandler
from models.blogpost import BlogPost
from helpers import *
from google.appengine.ext import db


class EditPostHandler(BlogHandler):
    def render_edit(self, post):
        subject = post.subject
        content = post.content
        self.render("edit.html.j2", subject=subject,
                    content=content, post=post)

    @BlogHandler.user_logged_in
    @BlogHandler.post_exists
    @BlogHandler.user_owns_post
    def get(self, post):
        self.render_edit(post)

    @BlogHandler.user_logged_in
    @BlogHandler.post_exists
    @BlogHandler.user_owns_post
    def post(self, post):
        subject = self.request.get('subject')
        content = self.request.get('content')
        post_id = self.request.get('post_id')
        if post:
            post.subject = subject
            post.content = content
            post.put()
        self.redirect('/blog/%s' % post_id)
