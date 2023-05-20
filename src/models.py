from sqlalchemy import Column, String, Integer, Boolean, Float, ForeignKey, DateTime, Date
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()




class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=True)
    cell_phone = db.Column(db.String(50), nullable=True)
    is_admin = db.Column(db.Boolean(), default=False)


    def __repr__(self):
        return f'<User {self.id}: {self.name}>'

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'date_of_birth': str(self.date_of_birth),
            'is_admin': self.is_admin,
            'cell_phone': self.cell_phone
        }
    
class Hamburger(db.Model):
    __tablename__ = 'hamburgers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float(precision=2), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    hamburger_type = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Hamburger {self.id}: {self.name}>'
    
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'description': self.description,
            'hamburger_type': self.hamburger_type
        }

class Beverage(db.Model):
    __tablename__ = 'beverages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float(precision=2), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    beverage_type = db.Column(db.String(50), nullable=True)

class Acompañamientos(db.Model):
    __tablename__ = 'acompañamientos'
    id = db.Column(db.Integer, primary_key=True)
    size = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float(precision=2), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    acompañmiento_type = db.Column(db.String(50), nullable=True)

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    hamburger_id = db.Column(db.Integer, db.ForeignKey('hamburgers.id'), nullable=False)
    acompañamiento_id = db.Column(db.Integer, db.ForeignKey('acompañamientos.id'), nullable=True)
    beverage_id =  db.Column(db.Integer, db.ForeignKey('beverages.id'), nullable=True)
    quantity = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=db.func.now())
    user = db.relationship('User')
    beverage = db.relationship('Beverage')
    hamburger = db.relationship('Hamburger')
    acompañamiento = db.relationship('Acompañamientos')

    def __repr__(self):
        return f'<Order {self.id}: {self.user.name} ordered {self.quantity} {self.hamburger.name}s with {self.acompañamiento.size} acompañamientos and a {self.beverage.name}>'

    def serialize(self):
        return {
            'id': self.id,
            'user': self.user.name,
            'hamburger': self.hamburger.name,
            'acomp': self.acompañamiento.size,
            'beverage': self.beverage.name,
            'price': self.hamburger.price + self.acompañamiento.price + self.beverage.price,
            'quantity': self.quantity,
            'created_at': str(self.created_at)
        }


