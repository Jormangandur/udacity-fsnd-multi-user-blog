from handlers.blog import BlogHandler
from models.blogpost import BlogPost
from helpers import *
from google.appengine.ext import db
import logging


class SearchHandler(BlogHandler):

    def render_results(self, posts):
        self.render("searchresults.html.j2", posts=posts)

    def get(self):
        target = self.request.get('search')
        target = target.upper().split()

        posts = BlogPost.by_search_term(target)
        self.render_results(posts)
