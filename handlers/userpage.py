from handlers.blog import BlogHandler
from models.blogpost import BlogPost
from models.user import User
from models.like import Like
from models.comment import Comment
from helpers import *
from google.appengine.ext import db
import logging


class UserPageHandler(BlogHandler):
    """Handler for '/blog/user/[user-id]' page.

    Retrieves user id from url and displays a user summary page.
    404 if user id doesnt exist
    """

    def get_post_subjects(self, entities):
        """Get BlogPost.subject corresponding to a related model.

        Retrieves the subject property of a BlogPost that is related to
         the given entity, i.e the post which a comment was made on, given
         the comment.
        Args:
            entities: List of like/comment model instances with a post_id property.
        Returns:
            List of post subject strings
        """

        post_subjects = []
        for entity in entities:
            post = BlogPost.by_id(entity.post_id)
            post_subjects.append(post.subject)
        return post_subjects

    def get(self, user_id):
        user = User.by_id(user_id)
        posts = user.posts.ancestor(blog_key())
        comments = user.comments.ancestor(comments_key())
        likes = user.likes.ancestor(likes_key())
        # Create lists of (Comment/like instance, post_subject) tuples
        # post_subject = subject of post which the comment/like belongs to
        # Then iterated and accessed as item[0]=Comment/Like, item[1]=subject
        like_subject_tuple = []
        comment_subject_tuple = []
        if comments.count() != 0:
            comment_subjects = self.get_post_subjects(comments)
            comment_subject_tuple = zip(comments, comment_subjects)
        if likes.count() != 0:
            like_subjects = self.get_post_subjects(likes)
            like_subject_tuple = zip(likes, like_subjects)
        self.render("userpage.html.j2", user=user, posts=posts,
                    comment_subject_tuple=comment_subject_tuple,
                    like_subject_tuple=like_subject_tuple)
