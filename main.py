from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import pymysql
# Note: the connection string after :// contains the following info:
# user:password@server:portNumber/databaseName

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:123456789@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'the_secret_key'
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(10000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, user):
        self.title = title
        self.body = body
        self.owner_id = user.id

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='user')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login','view_blog','index','signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/addpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')
            return render_template('login.html',username=username)

    return render_template('login.html')

@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if username == "" or password == "" or verify == "":
            flash('One or more fields are invalid', 'error')
            return render_template('signup.html',username = username)
        elif password != verify:
            flash('Passwords do not match', 'error')
            return render_template('signup.html',username=username)
        elif len(password) < 3 or len(username) < 3:
            flash('Invalid username or password', 'error')
            return render_template('signup.html',username=username)
        
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/addpost')
        else:
            flash('Username already exists', 'error')

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/', methods=['POST', 'GET'])
def index():
    return redirect('/blog')

@app.route('/blog', methods=['GET'])
def view_blog():

    if request.args:
        post_id = request.args.get('id')
        blog = Blog.query.get(post_id)
        return render_template('one_post.html', blog=blog)

    blogs = Blog.query.all()
    return render_template('blog.html', blogs=blogs)

@app.route('/addpost', methods=['POST', 'GET'])
def addpost():
    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_content']
        username = session['username']
        title_error = ''
        content_error = ''

        if (blog_title == ''):
            title_error = 'Please enter a blog title'
        if (blog_body == ''):
            content_error = 'Please enter some blog content'

        if (title_error != '' or content_error != ''):
            return render_template('addpost.html',title = blog_title, content = blog_body, title_error = title_error, content_error = content_error)
        else:
            user = User.query.filter_by(username=username).first()
            new_blog = Blog(blog_title, blog_body, user)
            db.session.add(new_blog)
            db.session.commit()
            blog_id = new_blog.id
            return redirect('/blog?id='+str(blog_id))
    
    if request.method == 'GET':
        return render_template('addpost.html')


if __name__ == '__main__':
    app.run()