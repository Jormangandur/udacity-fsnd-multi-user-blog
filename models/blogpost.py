from google.appengine.ext import db
from models.like import Like
from models.user import User
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
        owner = User.by_id(self.owner_id)
        owner_name = owner.username
        return render_str("post.html.j2", post=self, owner_name=owner_name)

    def likes_count(self):
        return Like.by_post_id(self.key().id()).count()

    def comments_count(self):
        return Comment.by_post_id(self.key().id()).count()

    @classmethod
    def by_id(cls, post_id):
        """Get stored BlogPost instance corresponding to id.

        Args:
            post_id: Integer, id of a stored BlogPost instance.
        Returns:
            Instance of BlogPost
        """
        return BlogPost.get_by_id(int(post_id), parent=blog_key())

    @classmethod
    def by_owner_id(cls, owner_id):
        """Get stored BlogPost instances corresponding to user ID of owner.

        Args:
            owner_id: Integer, id of a User.
        Returns:
            Query object of Posts
        """
        posts = BlogPost.all().filter('owner_id =', int(owner_id)).ancestor(blog_key())
        return posts

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
