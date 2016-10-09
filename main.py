import webapp2
import os
import jinja2
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),autoescape = True)

class Post(db.Model):
    title = db.StringProperty(required = True)
    post = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

# class ViewPostHandler(webapp2.RequestHandler):
#     def get(self, id):
#         pass

class Blog(Handler):
    def render_front(self, title="", post=""):
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 5")
        self.render("front.html", title = title, post = post, posts = posts)

    def get(self):
        self.render_front()

class Newpost(Handler):
    def render_newpost(self, title="", post="", error=""):
        self.render("newpost.html", title = title, post = post, error = error)

    def get(self):
        self.render_newpost()

    def post(self):
        title = self.request.get("title")
        post = self.request.get("post")



        if title and post:
            p = Post(title = title, post = post)
            p.put()
            id = p.key().id()
            #post_id = Post.get_by_id(int(post))
            self.redirect("/blog")
        else:
            error = "we need both the title and Content!"
            self.render_newpost(title, post, error )
class ViewPostHandler(Handler):
    def render_singlePost(self, post = ""):
        self.render("post.html", post = post)

    def render_404(self, error = ""):
        self.render("404.html", error =error)

    def get(self,id):
        post = Post.get_by_id(int(id))
        if post:
            self.render_singlePost()
        else:
            error = "There is no post with id %s" %id
            self.render_404()

app = webapp2.WSGIApplication([
    ('/blog', Blog),
    ('/newpost',Newpost),
    webapp2.Route('/blog/<id:\d+>',ViewPostHandler)
], debug=True)
