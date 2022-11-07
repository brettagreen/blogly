from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
def connect_db(app):
    """Connect to database."""
    db.app = app
    db.init_app(app)

class User(db.Model):
    """User"""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(20), nullable=False, unique=False)
    last_name = db.Column(db.String(30), nullable=False)
    image_url = db.Column(db.String, default='https://webstockreview.net/images/clown-clipart-emoji.jpg')
    posts = db.relationship("Post", backref="user", cascade="all, delete")


    def get_full_name(self):
        return self.first_name + ' ' + self.last_name

    @classmethod
    def get_all_users(cls):
        return cls.query.order_by(User.last_name, User.first_name).all()
    
    #overloaded method
    @classmethod
    def create_new_user(cls, first, last, img):
        return User(first_name=first, last_name=last, image_url=img)

    @classmethod
    def get_specific_user(cls, id):
        return cls.query.get(id)


class Post(db.Model):
    """Post"""
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(25), nullable=False)
    content = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
        
    @classmethod
    def pull_top_five(cls):
        return cls.query.order_by(Post.created_at.desc()).limit(5).all()

    @classmethod
    def create_new_post(cls, title, content, created_at, id):
        return Post(title=title, content=content, created_at=created_at, user_id=id)
    
    @classmethod
    def get_specific_post(cls, id):
        return cls.query.get(id)
    
    @classmethod
    def get_associated_user(cls, id):
        post = cls.query.get(id)
        return post.user.id
    
    @classmethod
    def delete_post(cls, id):
        cls.query.filter_by(id=id).delete()

    @classmethod
    def get_user_posts(cls, user):
        return cls.query.filter_by(user_id=user.id).all()

class Tag(db.Model):
    """TAG"""
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False, unique=True)
    posts = db.relationship('Post', secondary='post_tags', backref='tags')

    @classmethod
    def return_all_tags(cls):
        return cls.query.all()

    @classmethod
    def get_specific_tag(cls, id):
        return cls.query.get(id)

    @classmethod
    def create_new_tag(cls, name):
        return Tag(name=name)

    @classmethod
    def delete_tag(cls, id):
        cls.query.filter_by(id=id).delete()

class PostTag(db.Model):
    """POSTTAG"""
    __tablename__ = "post_tags"
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey("tags.id"), primary_key=True)