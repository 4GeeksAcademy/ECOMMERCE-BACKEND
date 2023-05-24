from sqlalchemy import Column, String, Integer, Boolean, Float, ForeignKey, DateTime, Date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
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
#agregar apellido

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

    def __repr__(self):
        return f'<Beverage {self.id}: {self.name}>'
    
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'description': self.description,
            'beverage_type': self.beverage_type
        }

class Acompañamientos(db.Model):
    __tablename__ = 'acompañamientos'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    size = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float(precision=2), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    acompañamiento_type = db.Column(db.String(50), nullable=True)
    
    def __repr__(self): 
        return f'<Acompañamientos {self.id}: {self.name}>'

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'size': self.size,
            'price': self.price,
            'description': self.description,
            'compañamientos': self.acompañamiento_type
        }



#TABLAS INTERMEDIARIAS

# Intermediate table for hamburgers in an order
class Order_Hamburger(db.Model):
  __tablename__ = 'order_hamburger'
  id = db.Column(db.Integer, primary_key=True)
  hamburgers_id = db.Column(db.Integer, db.ForeignKey("hamburgers.id"))
  quantity =  db.Column(db.Integer, default=1)
  order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))
  rel_hamburger = db.relationship("Hamburger")
  hamburgers = db.relationship('Order')



# Intermediate table for beverages in an order
class Order_Beverage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    beverage_id = db.Column(db.Integer,db.ForeignKey("beverages.id"))
    quantity =  db.Column(db.Integer, default=1)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))
    rel_brevages = db.relationship("Beverage")
    beverages = db.relationship('Order')
   

# Intermediate table for acompañamientos in an order
class Order_Acompañamiento(db.Model):
    __tablename__ = 'order_acompañamiento'
    id = db.Column(db.Integer, primary_key=True)
    acompañamiento_id = db.Column(db.Integer,db.ForeignKey("acompañamientos.id"))
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))
    quantity =  db.Column(db.Integer, default=1)
    acompañamientos = db.relationship('Order')


   
class Order(db.Model):
    __tablename__ ='orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    user = db.relationship('User')

    

    def __repr__(self):
        return f'<Order {self.id}: {self.user.name} ordered {self.get_total_quantity()} items>'
    
    def serialize(self):
        hamburgers = [{'id':hamburger.id, 'name': hamburger.name, 'quantity': quantity}
                        for hamburger, quantity in self.hamburgers]
        beverages = [{'id':beverage.id, 'name': beverage.name, 'quantity': quantity }
                        for beverage, quantity in self.beverages]
        acompañamientos = [{'id':acompañamiento.id, 'name': acompañamientos.name, 'quantity': quantity}
                        for acompañamientos, quantity in self.acompañamientos]
        
        return {
            'id': self.id,
            'user': self.user.serialize(),
            'hamburgers': hamburgers,
            'beverages': beverages,
            'acompañamientos': acompañamientos,
            'created_at': self.created_at,
            'total_quantity': self.get_total_quantity()
        }

    def get_total_quantity(self):
        hamburger_quantity = sum(quantity for _, quantity in self.hamburgers)
        beverage_quantity = sum(quantity for _, quantity in self.beverages)
        acompañamiento_quantity = sum(quantity for _, quantity in self.acompañamientos)

        return hamburger_quantity + beverage_quantity + acompañamiento_quantity


# alta cohesion y acoplamiento
# principio de atomicidad
# lo mas indivisible posible perfect
# deberia crear clases de ingredientes?
#nop
