"""Blogly application."""

from flask import Flask, redirect, render_template, request
from models import db, connect_db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.create_all()

@app.route("/")
def home():
    return redirect('/users')

@app.route('/users')
def users():
    users = User.get_all_users()
    return render_template('users.html', users=users)

@app.route('/users/new', methods=['GET'])
def show_form():
    return render_template('newuser.html')

@app.route('/users/new', methods=['POST'])
def process_new_form():
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
    return render_template('user.html', user=user)

@app.route('/users/<int:id>/edit', methods=['GET'])
def edit_user(id):
    user = User.get_specific_user(id)
    return render_template('edituser.html', user=user)

@app.route('/users/<int:id>/edit', methods=['POST'])
def process_edit_form(id):
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
    User.delete_user(id)
    db.session.commit()
    return redirect('/users')