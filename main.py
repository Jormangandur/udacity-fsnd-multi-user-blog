import webapp2
import os
import jinja2
# from app.views import *

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir), autoescape=True)

from models.user import User
from models.blogpost import BlogPost
from models.comment import Comment
from models.like import Like

from handlers.frontpage import FrontPageHandler
from handlers.newpost import NewPostHandler
from handlers.showpost import ShowPostHandler
from handlers.editpost import EditPostHandler
from handlers.deletepost import DeletePostHandler
from handlers.like import LikePostHandler
from handlers.unlike import UnlikePostHandler
from handlers.comment import CommentHandler
from handlers.deletecomment import DeleteCommentHandler
from handlers.signup import SignupHandler
from handlers.welcome import WelcomeHandler
from handlers.login import LoginHandler
from handlers.logout import LogoutHandler
from handlers.userpage import UserPageHandler

app = webapp2.WSGIApplication([
    ('/blog', FrontPageHandler),
    ('/blog/newpost', NewPostHandler),
    ('/blog/(\d+)', ShowPostHandler),
    ('/blog/edit/(\d+)', EditPostHandler),
    ('/blog/delete/(\d+)', DeletePostHandler),
    ('/blog/like/(\d+)', LikePostHandler),
    ('/blog/unlike/(\d+)', UnlikePostHandler),
    ('/blog/newcomment/(\d+)', CommentHandler),
    ('/blog/deletecomment/(\d+)/(\d+)', DeleteCommentHandler),
    ('/blog/signup', SignupHandler),
    ('/blog/welcome', WelcomeHandler),
    ('/blog/login', LoginHandler),
    ('/blog/logout', LogoutHandler),
    ('/blog/user/(\d+)', UserPageHandler),
], debug=True)
