from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:lc101@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'chamberofsecrets'

class Blog_post(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(120))
    blog_body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, blog_title, blog_body, owner):
        self.blog_title = blog_title
        self.blog_body = blog_body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog_post', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blogs', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        users = User.query.all()

        if user not in users:
            flash('Username does not exist', 'error')
            return render_template('login.html')

        if user in users:
            if password != user.password:
                flash('Password incorrect, please re-enter', 'error')
                return render_template('login.html')

        if user and user.password == password:
            session['username'] = username
            flash('Logged in')
            return render_template('new_post.html')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    user_error = ''
    password_error = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username=username).first()
        if username == '' or password == '' or verify == '':
            flash("one or more fields are invalid, please re-enter.", 'error')
            return render_template('signup.html')

        if existing_user:
            user_error = 'Username already exists, please try another username.'
            return render_template('signup.html', user_error=user_error)

        if not existing_user:
            if password != verify:
                password_error = 'Passwords do not match, please try again'
                return render_template('signup.html', password_error=password_error)

            if len(password) < 3:
                password_error = 'Password must be more than 3 characters'
                return render_template('signup.html', password_error=password_error)
            
            
            else:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return render_template('new_post.html')

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')



@app.route('/new_post', methods=['POST', 'GET'])
def new_post():

    return render_template('new_post.html')
    

@app.route('/blogs', methods = ['POST', 'GET'])
def blogs():

    posts = Blog_post.query.all()
    return render_template('blog_list.html', posts=posts)

@app.route('/')
def index():
    owner = User.query.filter_by(username=session['username']).first()

    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/blog', methods=['GET', 'POST'])
def blog_page():

    title_error = ''
    body_error = ''

    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']

        
        
        errors = 0

        if blog_title == '':
            title_error = "Please fill in title"
            errors = errors + 1
        if blog_body == '':
            body_error = "Please fill in body"
            errors = errors + 1
        
        if errors > 0:
            return render_template('new_post.html', blog_title=blog_title, blog_body=blog_body, title_error=title_error, body_error=body_error)

        else:
            blog_post = Blog_post(blog_title, blog_body, owner)
            db.session.add(blog_post)
            db.session.commit()
            blog_id = blog_post.id

            return redirect('/blog?id={0}'.format(blog_id))

    else:
        blog_id = request.args.get('id')
        blog_post = Blog_post.query.get(blog_id)
        
        return render_template('blog_page.html', blog_post=blog_post)

if __name__ == '__main__':
    app.run()