import jinja2
import webapp2

from handlers.auth.encrypt import make_secure_val, check_secure_val
from models.model_users import User

# Defining Jinja Template Directory and render template function
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader('templates'),
    autoescape=True
)


def render_template(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


class BlogHandler(webapp2.RequestHandler):
    # Template Helpers

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        params['user_id_check'] = self.user_id_check
        return render_template(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    # Cookie Helpers

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    # User Management

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))
        self.user_id_check = uid


