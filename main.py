import webapp2
import os
import jinja2
from app.views import *

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


app = webapp2.WSGIApplication([
    ('/blog', MainPage),
    ('/blog/newpost', NewPostHandler),
    ('/blog/(\d+)', ShowPostHandler),
    ('/blog/edit/(\d+)', EditPostHandler),
    ('/blog/delete/(\d+)', DeletePostHandler),
    ('/blog/like/(\d+)', LikePostHandler),
    ('/blog/signup', SignupHandler),
    ('/blog/welcome', WelcomeHandler),
    ('/blog/login', LoginHandler),
    ('/blog/logout', LogoutHandler),
], debug=True)
