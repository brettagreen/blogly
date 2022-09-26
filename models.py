from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

class User(db.Model):
    """User"""
    __tablename__ = "users"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    first_name = db.Column(db.String(20),
                     nullable=False,
                     unique=False)
    last_name = db.Column(db.String(30), nullable=False)
    image_url = db.Column(db.String, nullable=False, default='https://webstockreview.net/images/clown-clipart-emoji.jpg')

    def get_full_name(self):
        return self.first_name + ' ' + self.last_name

    @classmethod
    def get_all_users(cls):
        return cls.query.order_by(User.last_name, User.first_name).all()
    
    @classmethod
    def create_new_user(cls, first, last, img):
        return User(first_name=first, last_name=last, image_url=img)

    @classmethod
    def get_specific_user(cls, id):
        return cls.query.get(id)

    @classmethod
    def delete_user(cls, id):
        cls.query.filter_by(id=id).delete()
