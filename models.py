from flask_login import UserMixin
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


db=SQLAlchemy()

saved_plants = db.Table(
    'saved_plants',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('plant_id', db.Integer, db.ForeignKey('plant.id'))
)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username= db.Column(db.String(20), unique=True, nullable=False)
    email= db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60),nullable=False)

    comments = db.relationship('Comment', backref='author', lazy=True)

    saved = db.relationship(
        'Plant',
        secondary=saved_plants,
        backref='saved_by',
        lazy='dynamic'
    )

    def __repr__(self):
         return f"User('{self.username}','{self.email}','{self.password}')"
class Comment(db.Model):
     id = db.Column(db.Integer, primary_key=True)
     text = db.Column(db.Text, nullable=False)
     date_commented = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
     plant_id = db.Column(db.Integer, db.ForeignKey('plant.id'), nullable=False)

     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

     def __repr__(self):
        return f"Comment('{self.text[:30]}','{self.date_commented}')"


class Plant(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    latin_name= db.Column(db.String(120))
    description = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(20), nullable=True, default='default.jpg')
    comments = db.relationship('Comment', backref='plant', lazy=True)

    def __repr__(self):
        return f"Plant('{self.name}','{self.latin_name}','{self.image_file}')"

   