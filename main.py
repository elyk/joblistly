
import string
import os
import re
import jinja2
import webapp2
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)



def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)
    
    
class MainHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
        
    def render_str(self, template, **params):
        return render_str(template, **params)
    
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

def render_post(response, post):
    response.out.write('<b>' + post.subject + '</b><br>')
    response.out.write(post.content)


class Jobs(db.Model):
    message = db.TextProperty(required=True)
    when = db.DateTimeProperty(auto_now_add=True)
    company = db.StringProperty(required=True)
    title = db.StringProperty(required=True)
    sector = db.StringProperty(required=True)
    
    def render(self):
        self._render_text = self.message.replace('\n', '<br>')
        return render_str("new_job.html", p = self)
        
        
    def urlrender(self):
        self.word=(str(self.key().id()))
        self.url=(str(self.title))
        message=self.message
        self.title=("<a href='/"+str(self.key().id())+"'>"+str(self.title)+"</a>")
        return render_str("main.html", j = self)
        
    
    
def job_key(name = 'default'):
    return db.Key.from_path('job', name)
    
class MainPage(MainHandler):
    def get(self):
        
        jobs = db.GqlQuery(
            'SELECT * FROM Jobs '
            'ORDER BY when DESC')
        
        self.render('front.html', jobs = jobs)
    

class NewPost(MainHandler):
    def get(self):
      self.render("new_post.html")
        
        
    def post(self):
        message = self.request.get('message')
        title = self.request.get('title')
        company = self.request.get('company')
        sector = self.request.get('sector')
        
        p = Jobs(parent = job_key(), message = message, title = title, company = company, sector=sector)
        p.put()
        self.redirect('/%s' % str(p.key().id()))
 
class JobPost(MainHandler):
    def get(self, job_id):
        key = db.Key.from_path('Jobs', int(job_id), parent=job_key())
        job = db.get(key)
        
        self.render("permalink.html", job = job)
        
        
app = webapp2.WSGIApplication([
        ('/', MainPage),
        ('/newpost', NewPost),
        ('/([0-9]+)', JobPost),
        ],
        debug=True)

    
    