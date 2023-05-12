from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<User {self.id}: {self.name}>'

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'is_admin': self.is_admin
        }

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('orders', lazy=True))
    hamburger_id = db.Column(db.Integer, db.ForeignKey('hamburger.id'), nullable=False)
    hamburger = db.relationship('Hamburger', backref=db.backref('orders', lazy=True))
    quantity = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f'<Order {self.id}: {self.user.name} ordered {self.quantity} {self.hamburger.name}s>'

    def serialize(self):
        return {
            'id': self.id,
            'user': self.user.name,
            'hamburger': self.hamburger.name,
            'price': self.hamburger.price,
            'quantity': self.quantity,
            'created_at': self.created_at
        }

class Hamburger(Base):
    __tablename__ = 'hamburgers'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    price = Column(Float(precision=2), nullable=False)
    description = Column(String(255), nullable=True)
    is_vegetarian = Column(Boolean, default=False)
    type = Column(String(50))

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'hamburger'
    }

class Cheeseburger(Hamburger):
    __mapper_args__ = {
        'polymorphic_identity': 'cheeseburger'
    }
    cheese_type = Column(String(50), nullable=False)

class VeggieBurger(Hamburger):
    __mapper_args__ = {
        'polymorphic_identity': 'veggieburger'
    }
    has_tofu = Column(Boolean, default=False)

