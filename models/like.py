from google.appengine.ext import db
from helpers import *


class Like(db.Model):
    post_id = db.IntegerProperty(required=True)
    owner_id = db.IntegerProperty()

    @classmethod
    def by_post_id(cls, post_id):
        """Get stored Like instance corresponding to a post_id.

        Args:
            post_id: Integer, id of a post.
        Returns:
            Query object of Like instances associated with the post
        """
        likes = Like.all().filter('post_id =', int(post_id)).ancestor(likes_key())
        return likes

    @classmethod
    def make(cls, post_id, owner_id):
        """Create new Like() model instance.

        Args:
            post_id: Int, primary ID of post liked
        Returns:
            Instance of Like Model
        """
        return Like(parent=likes_key(), post_id=int(post_id), owner_id=owner_id)
