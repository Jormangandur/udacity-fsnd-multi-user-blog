import jinja2
from credentialhelpers import *
from google.appengine.ext import db


def render_str(template, env, **params):
    """Renders a jinja2 template string.

    Retrieves a jinja2 template from jinja_env and renders it with given params.

    Args:
        template: String, path of jinja2 template
        env: jina2 environment for rendering
        **params: Optional params to pass to template as variable

    Returns:
        Rendered template as unicode string
    """

    jinja_env = env
    t = jinja_env.get_template(template)
    return t.render(params)


class BlogPost(db.Model):
    """Model class for blog posts.
    """
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

    def render(self, env):
        return render_str("post.html.j2", env, post=self)


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
        return User.get_by_id(uid)

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
        return User(username=username,
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
