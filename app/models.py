import jinja2
from credential_helpers import *
from google.appengine.ext import db


def get_env():
    import main
    return main.jinja_env


def render_str(template, **params):
    """Renders a jinja2 template string.

    Retrieves a jinja2 template from jinja_env and renders it with given params.

    Args:
        template: String, path of jinja2 template
        **params: Optional params to pass to template as variable

    Returns:
        Rendered template as unicode string
    """

    jinja_env = get_env()
    t = jinja_env.get_template(template)
    return t.render(params)


def blog_key(name='default'):
    return db.Key.from_path('BlogPost', name)


class BlogPost(db.Model):
    """Model class for blog posts.
    """
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    owner_id = db.IntegerProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

    def render(self):
        return render_str("post.html.j2", post=self)


def likes_key(name='default'):
    return db.Key.from_path('likes', name)


class Likes(db.Model):
    post_id = db.IntegerProperty(required=True)
    liked_by_id = db.IntegerProperty()


def comments_key(name='default'):
    return db.Key.from_path('Comment', name)


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


def users_key(group='default'):
    return db.Key.from_path('users', group)


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
