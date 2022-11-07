"""Blogly application."""

from flask import Flask, redirect, render_template, request
from models import db, connect_db, User, Post, Tag
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.create_all()

#######################
########USERS##########
#######################
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route("/")
def home():
    posts = Post.pull_top_five()
    return render_template('home.html', posts=posts)

@app.route('/users')
def users():
    users = User.get_all_users()
    return render_template('users.html', users=users)

@app.route('/users/new', methods=['GET'])
def show_form():
    return render_template('new_user.html')

@app.route('/users/new', methods=['POST'])
def process_new_user_form():
    first = request.form['firstName']
    last = request.form['lastName']
    img = request.form['image']
    user = User.create_new_user(first, last, img)
    db.session.add(user)
    db.session.commit()
    return redirect('/users')

@app.route('/users/<int:id>')
def specific_user(id):
    user = User.get_specific_user(id)
    posts = Post.get_user_posts(user)
    return render_template('user.html', user=user, posts=posts)

@app.route('/users/<int:id>/edit', methods=['GET'])
def edit_user(id):
    user = User.get_specific_user(id)
    return render_template('edit_user.html', user=user)

@app.route('/users/<int:id>/edit', methods=['POST'])
def process_edit_user_form(id):
    orig_first = request.form['orig_firstName']
    orig_last = request.form['orig_lastName']
    orig_image = request.form['orig_image']

    first = request.form['firstName']
    last = request.form['lastName']
    img = request.form['image']

    user = User.get_specific_user(id)
    
    vibe_check = False
    if orig_first != first and first != '':
        vibe_check = True
        user.first_name = first
    if orig_last != last and last != '':
        vibe_check = True
        user.last_name = last
    if orig_image != img and img != '':
        vibe_check = True
        user.image_url = img
    
    if vibe_check:
        db.session.add(user)
        db.session.commit()
    return redirect ('/users')

@app.route('/users/<int:id>/delete', methods=['POST'])
def delete_user(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return redirect('/users')


#######################
########POSTS##########
#######################

@app.route('/users/<int:id>/posts/new')
def new_post_form(id):
    user = User.get_specific_user(id)
    tags = Tag.return_all_tags()
    return render_template('new_post.html', user=user, id=id, tags=tags)

@app.route('/users/<int:id>/posts/new', methods=['POST'])
def handle_post_form(id):
    title = request.form['title']
    content = request.form['content']
    created_at = datetime.datetime.now()

    tags = request.form.getlist('checktags')

    post = Post.create_new_post(title, content, created_at, id)
    db.session.add(post)
    db.session.commit()

    for tag in tags:
        post.tags.append(Tag.get_specific_tag(tag))
    db.session.commit()

    return redirect(f'/users/{id}')

@app.route('/posts/<int:id>')
def show_post(id):
    post = Post.get_specific_post(id)

    return render_template('post_detail.html', post=post)

@app.route('/posts/<int:id>/edit')
def edit_post(id):
    post = Post.get_specific_post(id)
    user_id = Post.get_associated_user(id)
    tags = Tag.return_all_tags()
    return render_template('edit_post.html', post=post, user_id=user_id, tags=tags)

@app.route('/posts/<int:id>/edit', methods=['POST'])
def handle_edit_post(id):
    post = Post.get_specific_post(id)

    orig_title = request.form['orig_title']
    orig_content = request.form['orig_content']
    title = request.form['title']
    content = request.form['content']

    new_tags = request.form.getlist('post_tags')
    
    vibe_check = False
    if orig_title != title and title != '':
        vibe_check = True
        post.title = title
    if orig_content != content and content != '':
        vibe_check = True
        post.content = content
    for tag in new_tags:
        vibe_check = True
        post.tags.append(Tag.get_specific_tag(tag))
    
    if vibe_check:
        db.session.add(post)
        db.session.commit()
    return redirect(f'/posts/{id}')

@app.route('/posts/<int:id>/delete', methods=['POST'])
def delete_post(id):
    user_id = Post.get_associated_user(id)
    Post.delete_post(id)
    db.session.commit()
    return redirect(f'/users/{user_id}')

#######################
#########TAGS##########
#######################

@app.route('/tags')
def list_tags():
    tags = Tag.return_all_tags()
    return render_template('all_tags.html', tags=tags)

@app.route('/tags/<int:id>')
def tag_detail(id):
    tag = Tag.get_specific_tag(id)
    return render_template('tag_detail.html', tag=tag)

@app.route('/tags/new')
def new_tag_form():
    return render_template('new_tag.html')

@app.route('/tags/new', methods=['POST'])
def process_new_tag_form():
    name = request.form['name']
    new_tag = Tag.create_new_tag(name)
    db.session.add(new_tag)
    db.session.commit()
    return redirect('/tags')

@app.route('/tags/<int:id>/edit')
def edit_tag_form(id):
    tag = Tag.get_specific_tag(id)
    return render_template('edit_tag.html', tag=tag)

@app.route('/tags/<int:id>/edit', methods=['POST'])
def process_edit_tag_form(id):
    tag = Tag.get_specific_tag(id)

    name = request.form['name']
    orig_name = request.form['orig_name']

    if orig_name != name and name != '':
        tag.name = name
        db.session.add(tag)
        db.session.commit()
    return redirect('/tags')

@app.route('/tags/<int:id>/delete', methods=['POST'])
def delete_tag(id):
    Tag.delete_tag(id)
    db.session.commit()
    return redirect('/tags')