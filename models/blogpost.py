from google.appengine.ext import db
from models.like import Like
from models.comment import Comment
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

    def likes_count(self):
        return Like.by_post_id(self.key().id()).count()

    def comments_count(self):
        return Comment.by_post_id(self.key().id()).count()

    @classmethod
    def by_id(cls, post_id):
        """Get stored BlogPost instance corresponding to id.

        Args:
            uid: Integer, id of a stored BlogPost instance.
        Returns:
            Instance of BlogPost
        """
        return BlogPost.get_by_id(int(post_id), parent=blog_key())

    @classmethod
    def make(cls, subject, content, owner_id):
        """Create new BlogPost() model instance.

        Args:
            subject: String, title of post
            content: String, text content of post
            owner_id: Int, primary ID of User who created post
        Returns:
            Instance of BlogPost Model/Class
        """
        return BlogPost(parent=blog_key(),
                        subject=subject,
                        content=content,
                        owner_id=int(owner_id))
