from google.appengine.ext import db
from models.user import User
import re
from helpers import *
import logging


class BlogPost(db.Model):
    """Model class for blog posts.
    """
    owner = db.ReferenceProperty(User,
                                 collection_name="posts")

    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

    def render(self):
        owner = self.owner
        return render_str("post.html.j2", post=self, owner=owner)

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
    def by_search_term(cls, search_phrase):
        """Get stored BlogPost instances with subject containing a search term.

        Args:
            target: List of strings, search terms to find
        Returns:
            Query object of Post
        """
        posts = BlogPost.all().ancestor(blog_key())
        results = []
        if posts:
            for post in posts:
                for s in search_phrase:
                    if findWord(s)(post.subject):
                        results.append(post)
                        break
        return results

    @classmethod
    def make(cls, owner, subject, content):
        """Create new BlogPost() model instance.

        Args:
            subject: String, title of post
            content: String, text content of post
            owner_id: Int, primary ID of User who created post
        Returns:
            Instance of BlogPost Model/Class
        """
        return BlogPost(parent=blog_key(),
                        owner=owner,
                        subject=subject,
                        content=content)
