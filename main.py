from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz: @localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'bonerfart'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(10000))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, title, body, user):
        self.title = title
        self.body = body
        self.user = user

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='user')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
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
            print(session)
            return redirect('/newpost')
        else:
            flash("User password incorrect, or user does not exist", 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        # TODO - validate this shit

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            # TODO - use better response messaging
            return "<h1>Duplicate user</h1>"

    return render_template('signup.html')


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    user = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        post_title = request.form['post-title']
        post_body = request.form['post-body']
        if post_title == "" or post_body == "":
            flash("You must enter both a post title, and a post body.")
            return render_template('newpost.html', post_title=post_title, post_body=post_body)
        blog_post = Blog(post_title, post_body, user)
        db.session.add(blog_post)
        db.session.commit()
        new_post = "/blog?id=" + str(blog_post.id)
        return redirect(new_post)
    return render_template('newpost.html')


@app.route('/blog')
def blog():
    post_id = request.args.get('id')
    user_id = request.args.get('user')
    if post_id == None and user_id == None:
        posts = Blog.query.all()
        return render_template('blog.html', title="Big Ballin' Blog", posts=posts)
    elif user_id == None:
        post = Blog.query.filter_by(id=post_id).first()
        return render_template('post.html', title="Big Ballin' Blog", post=post)
    else:
        posts = Blog.query.filter_by(user_id=user_id).all()
        return render_template('blog.html',  title="Big Ballin' Blog", posts=posts)


@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html', title="Big Ballin' Blog", users=users)


if __name__ == '__main__':
    app.run()