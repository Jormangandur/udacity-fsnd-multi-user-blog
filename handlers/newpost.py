from handlers.blog import BlogHandler
from models.blogpost import BlogPost
from helpers import *


class NewPostHandler(BlogHandler):
    """Handler for '/blog/newpost'.
    """

    def render_new_post(self, subject="", content="", error=""):
        self.render("new_post.html.j2", subject=subject,
                    content=content, error=error)

    @BlogHandler.user_logged_in
    def get(self):
        self.render_new_post()

    @BlogHandler.user_logged_in
    def post(self):
        """Gets data from input form.

        Retrieves post subject and title from input form and creates a new User
        model then redirects to a permalink for the post.

        If subject and content are invalid the form is re-loaded with
        appropriate error messages.
        """
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            owner_id = self.user.key().id()
            post = BlogPost.make(subject, content, owner_id)
            post.put()
            self.redirect("/blog/%s" % str(post.key().id()))
        else:
            error = "Please enter subject and content!"
            self.render_new_post(subject, content, error)
