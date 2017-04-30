from google.appengine.ext import db
from helpers import *


class User(db.Model):
    """Model class for user account information.
    """

    username = db.StringProperty(required=True)
    pw_hash = db.StringProperty(required=True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        """Get stored User instance corresponding to user id.

        Args:
            uid: Integer, id of a stored User instance.
        Returns:
            Instance of User Model/Class
        """
        return User.get_by_id(uid, parent=users_key())

    @classmethod
    def by_name(cls, username):
        """Get stored User instance corresponding to username.

        Args:
            username: String, username of a stored User instance.
        Returns:
            Instance of User Model/Class
        """
        user = User.all().filter('username =', username).get()
        return user

    @classmethod
    def register(cls, username, password, email=None):
        """Create new User() model instance.

        Generate a hash of the password and assigns it along with username and
        email arguments to instance variables in a new User() model instance.
        Args:
            username: String
            password: String, raw password.
            email: String
        Returns:
            Instance of User Model/Class
        """
        password_hash = pw_hash(username, password)
        return User(parent=users_key(),
                    username=username,
                    pw_hash=password_hash,
                    email=email)

    @classmethod
    def login(cls, username, password):
        """Check is user exists and password is correct.

        Args:
            username: String
            password: String, raw password.
        Returns:
            Instance of User Model/Class
        """
        user = cls.by_name(username)
        if user and valid_pw_hash(username, password, user.pw_hash):
            return user
