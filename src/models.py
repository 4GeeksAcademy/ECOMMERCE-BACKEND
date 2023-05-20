from sqlalchemy import Column, String, Integer, Boolean, Float, ForeignKey, DateTime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()




class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    is_admin = db.Column(db.Boolean(), default=False)


    def __repr__(self):
        return f'<User {self.id}: {self.name}>'

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'is_admin': self.is_admin
        }
    
class Hamburger(db.Model):
    __tablename__ = 'hamburgers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float(precision=2), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    is_vegetarian = db.Column(db.Boolean, default=False)
    type = db.Column(db.String(50))

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'hamburger'
    }


class Cheeseburger(Hamburger):
    __mapper_args__ = {
        'polymorphic_identity': 'cheeseburger'
    }
    cheese_type = db.Column(db.String(50), nullable=False)


class VeggieBurger(Hamburger):
    __mapper_args__ = {
        'polymorphic_identity': 'veggieburger'
    }
    has_tofu = db.Column(db.Boolean, default=False)


class Beverage(db.Model):
    __tablename__ = 'beverages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float(precision=2), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    type = db.Column(db.String(50))

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'beverage'
    }


class Acompañamientos(db.Model):
    __tablename__ = 'acompañamientos'
    id = db.Column(db.Integer, primary_key=True)
    size = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float(precision=2), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    type = db.Column(db.String(50))

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'acompañamientos'
    }


class OnionRings(Acompañamientos):
    __mapper_args__ = {
        'polymorphic_identity': 'onion_rings'
    }


class FrenchFries(Acompañamientos):
    __mapper_args__ = {
        'polymorphic_identity': 'french_fries'
    }
@app.route('/acompañamiento', methods=['POST'])
def create_acompañamiento():
name = request.json.get('name')
price = request.json.get('price')
description = request.json.get('description')
acompañamiento_type = request.json.get('acompañamiento_type')

acompañamiento = Acompañamiento(name=name, price=price, description=description, acompañamiento_type=acompañamiento_type)
db.session.add(acompañamiento)
db.session.commit()

return jsonify(acompañamiento.serialize()), 201




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
            'created_at': self.created_at
        }

#alta cohesion y acoplamiento
#principio de atomicidad
#lo mas indivisible posible perfect

@app.route('/beverages', methods=['POST'])
def create_beverage():
    # Obtener los datos de la bebida del cuerpo de la solicitud
    name = request.json.get('name')
    price = request.json.get('price')
    description = request.json.get('description')
    beverage_type = request.json.get('beverage_type')

    beverage = None

    if beverage_type == 'COCA':
        beverage = Coca(name=name, price=price, description=description)
    elif beverage_type == 'SPRITE':
        beverage = Sprite(name=name, price=price, description=description)
    elif beverage_type == 'FANTA':
        beverage = Fanta(name=name, price=price, description=description)
    elif beverage_type == 'NORDIC':
        beverage = Nordic(name=name, price=price, description=description)
    elif beverage_type == 'INKA KOLA':
        beverage = InkaKola(name=name, price=price, description=description)
    elif beverage_type == 'AGUAS':
        beverage = Agua(name=name, price=price, description=description)
    elif beverage_type == 'BENEDICTINO':
        beverage = Benedictino(name=name, price=price, description=description)
    elif beverage_type == 'AQUARIUS':
        beverage = Aquarius(name=name, price=price, description=description)

    if beverage:
        db.session.add(beverage)
        db.session.commit()
        return jsonify(beverage.serialize()), 201
    else:
        return jsonify({'error': 'Tipo de bebida inválido'}), 400
