from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
db = SQLAlchemy()



# User Model
class User(db.Model, UserMixin): 
    __tablename__ = 'user' 
    id = db.Column(db.Integer, primary_key=True)  
    name = db.Column(db.String(100), nullable=False)  
    email = db.Column(db.String(120), unique=True, nullable=False)  
    password = db.Column(db.String(255), nullable=False)  
    def __repr__(self):  
        return f'User({self.name}, {self.email})'


# Author Model 
class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    books = db.relationship('Book', backref='author', lazy='select') 
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return f'<Author {self.name}>'


# Book Model
class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    publish_date = db.Column(db.Date, nullable=False)
    price = db.Column(db.Numeric(10,2), nullable=False)
    img = db.Column(db.String(255), nullable=True)  
    appropriate = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)
    def __init__(self, name, publish_date, price, img, appropriate, author_id):
        self.name = name
        self.publish_date = publish_date
        self.price = price
        self.img = img
        self.appropriate = appropriate
        self.author_id = author_id
    def __repr__(self):
        return f'<Book {self.name}>'