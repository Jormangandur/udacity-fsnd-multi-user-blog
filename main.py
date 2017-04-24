import webapp2
import os
import jinja2
import re
import random
import string
import hashlib
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class BlogPost(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

    def render(self):
        return render_str("post.html.j2", post=self)


class User(db.Model):
    username = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    email = db.StringProperty()


class MainPage (Handler):
    def render_front(self):
        posts = db.GqlQuery(
            "SELECT * FROM BlogPost ORDER BY created desc limit 10")

        self.render("front.html.j2", posts=posts)

    def delete_all(self):
        posts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created desc")
        db.delete(posts)

    def get(self):
        self.render_front()


class NewPostHandler(Handler):
    def render_new_post(self, subject="", content="", error=""):
        self.render("new_post.html.j2", subject=subject,
                    content=content, error=error)

    def get(self):
        self.render_new_post()

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            post = BlogPost(subject=subject, content=content)
            post.put()
            self.redirect("/blog/%s" % str(post.key().id()))
        else:
            error = "Please enter subject and content!"
            self.render_new_post(subject, content, error)


class ShowPostHandler(Handler):
    def render_post(self, post_id):
        post = BlogPost.get_by_id(post_id)
        if post:
            self.render("permalink.html.j2", post=post)

    def get(self, post_id):
        post_id = int(post_id)
        self.render_post(post_id)


class CredentialsHandler(Handler):
    USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
    PASS_RE = re.compile(r"^.{3,20}$")
    EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")

    def make_salt(self):
        return ''.join(random.choice(string.letters) for x in xrange(5))

    def make_user_hash(self, username, salt=""):
        if not salt:
            salt = self.make_salt()
        h = hashlib.sha256(username + salt).hexdigest()
        return '%s|%s|%s' % (username, h, salt)

    def make_pw_hash(self, username, pw, salt=""):
        if not salt:
            salt = self.make_salt()
        h = hashlib.sha256(username + pw + salt).hexdigest()
        return '%s|%s' % (h, salt)

    def valid_username(self, username):
        return self.USER_RE.match(username)

    def valid_password(self, password):
        return self.PASS_RE.match(password)

    def valid_email(self, email):
        return self.EMAIL_RE.match(email)


class SignupHandler(CredentialsHandler):

    def render_form(self, username="", email="", error_name="",
                    error_password="", error_pass_match="", error_email=""):

        self.render("signup.html.j2", username=username, email=email,
                    error_name=error_name, error_password=error_password,
                    error_pass_match=error_pass_match, error_email=error_email)

    def add_new_user(self, username, password, email=""):
        new_user = User(username=username, password=password,
                        email=email)
        new_user.put()

    def get(self):
        self.render_form()

    def post(self):
        username = str(self.request.get('username'))
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')
        error_name = ""
        error_password = ""
        error_pass_match = ""
        error_email = ""
        error = False

        if not (self.valid_username(username)):
            error_name = "Username is invalid"
            error = True
        if not (self.valid_password(password)):
            error_password = "Password is invalid"
            error = True
        else:
            if (password != verify):
                error_pass_match = "Passwords do not match"
                error = True

        if (email and (not self.valid_email(email))):
            error_email = "Email is invalid"
            error = True

        if (error):
            self.render_form(username, email, error_name,
                             error_password, error_pass_match, error_email)
        else:
            username_cookie = self.make_user_hash(username)
            self.add_new_user(username, self.make_pw_hash(
                username, password), email)
            self.response.headers.add_header(
                'Set-Cookie', 'username=%s;Path=/' % username_cookie)
            self.redirect("/blog/welcome")


class WelcomeHandler(CredentialsHandler):
    def valid_username_cookie(self, username, h):
        salt = h.split('|')[2]
        if self.make_user_hash(username, salt) == h:
            return True

    def get(self):
        username_cookie = self.request.cookies.get('username')
        username = username_cookie.split('|')[0]
        if self.valid_username_cookie(username, username_cookie):
            self.render("welcome.html.j2", username=username)
        else:
            self.redirect('/blog/signup')


class LoginHandler(CredentialsHandler):
    def render_form(self, error=""):
        self.render("login.html.j2", error=error)

    def check_pw(self, user, password):
        salt = user.password.split('|')[1]
        if self.make_pw_hash(user.username, password, salt) == user.password:
            return True

    def get(self):
        self.render_form()

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        q = db.GqlQuery("SELECT * FROM User WHERE username =:username",
                        username=username)
        user = q.get()
        pw = self.check_pw(user, password)
        if user and pw:
            username_cookie = self.make_user_hash(str(username))
            self.response.headers.add_header(
                'Set-Cookie', 'username=%s;Path=/' % username_cookie)
            self.redirect('/blog/welcome')
        else:
            error = "Invalid login"
            self.render_form(error)


class LogoutHandler(Handler):
    def get(self):
        self.response.headers.add_header(
            'Set-Cookie', 'username=;Path=/')
        self.redirect('/blog/signup')


app = webapp2.WSGIApplication([
    ('/blog', MainPage),
    ('/blog/newpost', NewPostHandler),
    ('/blog/(\d+)', ShowPostHandler),
    ('/blog/signup', SignupHandler),
    ('/blog/welcome', WelcomeHandler),
    ('/blog/login', LoginHandler),
    ('/blog/logout', LogoutHandler),
], debug=True)
