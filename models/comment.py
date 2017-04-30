from google.appengine.ext import db
from helpers import *


class Comment(db.Model):
    content = db.TextProperty(required=True)
    owner_id = db.IntegerProperty(required=True)
    post_id = db.IntegerProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

    def render(self, post_id="", current_user_id=""):
        key = db.Key.from_path('User', int(
            self.owner_id), parent=users_key())
        owner = db.get(key)
        owner_name = owner.username
        return render_str("comment.html.j2", comment=self, post_id=post_id,
                          current_user_id=current_user_id, owner_name=owner_name)
