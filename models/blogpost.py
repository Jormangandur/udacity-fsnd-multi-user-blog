from google.appengine.ext import db
from helpers import *


class BlogPost(db.Model):
    """Model class for blog posts.
    """
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    owner_id = db.IntegerProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

    def render(self):
        return render_str("post.html.j2", post=self)
