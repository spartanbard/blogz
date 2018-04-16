from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog: @localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'bonerfart'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(10000))
    
    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        post_title = request.form['post-title']
        post_body = request.form['post-body']
        blog_post = Blog(post_title, post_body)
        db.session.add(blog_post)
        db.session.commit()
        return redirect('/')
    return render_template('newpost.html')


@app.route('/', methods=['POST', 'GET'])
def index():
    posts = Blog.query.all()
    return render_template('blog.html', title="Big Ballin'Blog", posts=posts)


if __name__ == '__main__':
    app.run()