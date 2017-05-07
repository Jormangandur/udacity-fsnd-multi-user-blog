from google.appengine.ext import db
from models.user import User
from helpers import *


class Like(db.Model):
    owner = db.ReferenceProperty(User,
                                 collection_name="likes")
    post_id = db.IntegerProperty(required=True)

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
    def by_owner_id(cls, owner_id):
        """Get stored Like instance corresponding to a user_id.

        Args:
            owner_id: Integer, id of a user.
        Returns:
            Query object of Like instances associated with the user
        """
        likes = Like.all().filter('owner_id =', int(owner_id)).ancestor(likes_key())
        return likes

    @classmethod
    def make(cls, owner, post_id):
        """Create new Like() model instance.

        Args:
            post_id: Int, primary ID of post liked
        Returns:
            Instance of Like Model
        """
        return Like(parent=likes_key(),
                    owner=owner,
                    post_id=int(post_id))
