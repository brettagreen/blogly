from app import app
from unittest import TestCase
from models import User, Post, Tag, db, connect_db
from jinja2.exceptions import UndefinedError
from sqlalchemy.exc import DataError
import datetime

app.config['TESTING'] = True

class BloglyTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        connect_db(app)
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        db.drop_all()

    def test_home(self):
        with app.test_client() as client:
            resp = client.get('/')
            self.assertEqual(resp.status_code, 200)

    def test_bad_route(self):
        with app.test_client() as client:
            resp = client.get('/donkeys/zebras/turtles/ohmy')
            html = resp.get_data(as_text=True)
            self.assertIn('<h1>Page Not Found!!!</h1>', html)
    
    def test_new_user_form(self):
        with app.test_client() as client:
            resp = client.get('/users/new')
            html = resp.get_data(as_text=True)
            self.assertIn('<input type="text" name="lastName" placeholder="Enter a last name">', html)

            resp = client.post('/users/new', data={'firstName': 'Mayor', 'lastName': 'McCheese', 'image':''}, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertIn('Mayor McCheese', html)

            with self.assertRaises(DataError):
                resp = client.post('/users/new', data={'firstName':'abcdefghijklmnopqrstuvwxyz', 'lastName':'jenkins', 'image':''},
                follow_redirects=True)

            with self.assertRaises(DataError):
                resp = client.post('/users/new', data={'firstName':'Steve', 'lastName':'abcdefghijklmnopqrstuvwxyzabcdefghij', 'image':''},
                follow_redirects=True)

    def test_user_profile(self):
        with app.test_client() as client:
            client.post('/users/new', data={'firstName': 'Mayor', 'lastName': 'McCheese', 'image':''}, follow_redirects=True)
            user = User.query.filter_by(first_name='Mayor').first()
            resp = client.get(f'/users/{user.id}')
            html = resp.get_data(as_text=True)
            self.assertIn('Mayor McCheese', html)

            
            with self.assertRaises(AttributeError):
                resp = client.get(f'/users/250')
                
    def test_edit_user_profile(self):
        with app.test_client() as client:
            client.post('/users/new', data={'firstName': 'Mayor', 'lastName': 'McCheese', 'image':''}, follow_redirects=True)
            user = User.query.first()
            orig_name = user.get_full_name()

            resp = client.get(f'/users/{user.id}/edit')
            html = resp.get_data(as_text=True)
            self.assertIn('<h2>Edit a user</h2>', html)

            resp = client.post(f'users/{user.id}/edit', data={'firstName': 'Sandy', 'lastName': 'Smothers', 'image': '',
            'orig_firstName':'Mayor', 'orig_lastName':'McCheese', 'orig_image':''}, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertIn('Sandy Smothers', html)
            self.assertNotIn(orig_name, html)

            with self.assertRaises(UndefinedError):
                resp = client.get(f'/users/250/edit')

    def test_new_post_form(self):
        with app.test_client() as client:
            user = User(first_name='billy', last_name='goat!', image_url='')
            db.session.add(user)
            db.session.commit()
            resp = client.get(f'/users/{user.id}/posts/new')
            html = resp.get_data(as_text=True)
            self.assertIn('<h2>Add new post for billy goat!</h2>', html)

            with self.assertRaises(UndefinedError):
                client.get('/users/9000000/posts/new')

            resp = client.post(f'/users/{user.id}/posts/new', data={'title':'first post', 'content':'keep it short n sweet'}, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertIn('<h2>billy goat!</h2>', html)
            self.assertIn('first post', html)

    def test_post_detail(self):
        with app.test_client() as client:
            user = User(first_name='jon', last_name='white', image_url='')
            db.session.add(user)
            db.session.commit()          
            post = Post(title="first post", content="nothing to see here", created_at=datetime.datetime.now(), user_id=user.id)
            db.session.add(post)
            db.session.commit()   
            resp = client.get(f'/posts/{post.id}')
            html = resp.get_data(as_text=True)
            self.assertIn(f'<h2>{post.title}</h2>', html)          

    def test_edit_post(self):
        with app.test_client() as client:
            user = User(first_name='jamie', last_name='brown', image_url='')
            db.session.add(user)
            db.session.commit()          
            post = Post(title="second post", content="fish larva are nature's candy", created_at=datetime.datetime.now(), user_id=user.id)
            db.session.add(post)
            db.session.commit()   
            resp = client.get(f'/posts/{post.id}/edit')
            html = resp.get_data(as_text=True)
            self.assertIn(f'<input type="text" name="title" placeholder="{post.title}">', html)

            resp = client.post(f'/posts/{post.id}/edit', data={'title':'oopsie!','content':'',
            'orig_title':'second post', 'orig_content':'fish larva are nature\'s candy'}, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertIn('<h2>oopsie!</h2>', html)
            self.assertIn('<h3>fish larva are nature&#39;s candy</h3>', html)

    def test_all_tags(self):
        with app.test_client() as client:
            tag = Tag(name="funkymoves")
            db.session.add(tag)
            db.session.commit()

            resp = client.get('/tags')
            html = resp.get_data(as_text=True)
            self.assertIn('funkymoves</a></li>', html)

    def test_add_tag(self):
        with app.test_client() as client:
            resp = client.get('/tags/new')
            html = resp.get_data(as_text=True)
            self.assertIn('<form id="postform" action="/tags/new" method="post">', html)