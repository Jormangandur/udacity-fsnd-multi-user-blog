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

    def get(self, post_id):
        key = db.Key.from_path('BlogPost', int(
            post_id), parent=blog_key())
        post = db.get(key)
        if self.user:
            if self.user.key().id() == post.owner_id:
                self.render_edit(post)
            else:
                self.redirect('/blog/%s' % post_id)
        else:
            self.redirect('/blog/login')

    def post(self, post_id):
        subject = self.request.get('subject')
        content = self.request.get('content')
        post_id = self.request.get('post_id')
        key = db.Key.from_path('BlogPost', int(
            post_id), parent=blog_key())
        post = db.get(key)
        if post:
            post.subject = subject
            post.content = content
            post.put()
        self.redirect('/blog/%s' % post_id)
