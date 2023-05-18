"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Hamburger, Cheeseburger, VeggieBurger#, Beverage, Acompañamientos, OnionRings, FrenchFries , Order
from flask_login import login_required
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import datetime

#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
jwt=JWTManager(app)
db_url = os.getenv("DATABASE_URL")



app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

jwt=JWTManager(app)

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

# Route for getting all users
@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

# Route for creating a new user
@app.route('/users', methods=['POST'])
def create_user():
    name = request.json.get('name')
    email = request.json.get('email')
    password = request.json.get('password')
    is_admin = request.json.get('is_admin')
    user = User(name=name, email=email, password=password, is_admin=is_admin)

    db.session.add(user)
    db.session.commit()

    return jsonify(user.serialize()), 201
#


@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        return 'This is the admin page'


# Route for getting all orders
@app.route('/orders', methods=['GET'])
def get_all_orders():
    orders = Order.query.all()
    return jsonify([order.serialize() for order in orders]), 200

#agregar query filter by date.

# Route for creating a new order
@app.route('/orders', methods=['POST'])
def create_order():
    user_id = request.json.get('user_id')
    hamburger_id = request.json.get('hamburger_id')
    acompañamiento_id = request.json.get('acompañamiento_id')
    beverage_id = request.json.get('beverage_id')
    quantity = request.json.get('quantity')
    order = Order(user_id=user_id, hamburger_id=hamburger_id, acompañamiento_id=acompañamiento_id, beverage_id=beverage_id, quantity=quantity)
    db.session.add(order)
    db.session.commit()
    return jsonify(order.serialize()), 201
#si Q se refiere a cada una, o a la orden en si.

# Route for getting all hamburgers
@app.route('/hamburgers', methods=['GET'])
def get_all_hamburgers():
    hamburgers = Hamburger.query.all()
    return jsonify([hamburger.serialize() for hamburger in hamburgers]), 200

# Route for getting all cheeseburgers
@app.route('/cheeseburgers', methods=['GET'])
def get_all_cheeseburgers():
    cheeseburgers = Cheeseburger.query.all()
    return jsonify([cheeseburger.serialize() for cheeseburger in cheeseburgers]), 200

# Route for getting all veggieburgers
@app.route('/veggieburgers', methods=['GET'])
def get_all_veggieburgers():
    veggieburgers = VeggieBurger.query.all()
    return jsonify([veggieburger.serialize() for veggieburger in veggieburgers]), 200

# Route for getting all beverages
@app.route('/beverages', methods=['GET'])
def get_all_beverages():
    beverages = Beverage.query.all()
    return jsonify([beverage.serialize() for beverage in beverages]), 200

# Route for getting all acompañamientos
@app.route('/acomp', methods=['GET'])
def get_all_acompañamientos():
    acompañamientos = Acompañamientos.query.all()
    return jsonify([acompañamiento.serialize() for acompañamiento in acompañamientos]), 200

# Route for getting all onion rings
@app.route('/onion_rings', methods=['GET'])
def get_all_onion_rings():
    onion_rings = OnionRings.query.all()
    return jsonify([onion_ring.serialize() for onion_ring in onion_rings]), 200

# Route for getting all french fries
@app.route('/french_fries', methods=['GET'])
def french_fries():
    french_fries = FrenchFries.query.all()
    french_fries_json = [ff.serialize() for ff in french_fries]
    return jsonify(french_fries_json)
#rutas por crear: CREATE HAMBURGER, CRREATE BEBIDA, CREATE ACOMPAÑAMIENTO.
# PLUS: CREAR POSTRES

@app.route('/signup', methods=['POST'])
def signup():
    body = request.get_json()
    user = User.query.filter_by(email=body['email']).first()
    if not user:
        new_user = User(email=body['email'], password=body['password'], is_admin = False)
        db.session.add(new_user)
        db.session.commit()
        expire =  datetime.timedelta(minutes=1)
        new_token = create_access_token(identity=new_user.email,expires_delta=expire)
        return jsonify({
                "msg":"User was created",
                "token":new_token,
                "exp":expire.total_seconds()
            })
    else:
        return jsonify({"msg":"The email entered already has an associated account. Please Log in"})
<<<<<<< HEAD
    
=======

>>>>>>> refs/remotes/origin/benbungle
@app.route("/login", methods=['POST'])
def login():
    body = request.get_json()
    user = User.query.filter_by(email=body['email']).first()
    if user:
        if user.password == body["password"]:
            if user.is_admin:
                # Perform admin login actions
                expire = datetime.timedelta(minutes=1)
                token = create_access_token(identity=user.email, expires_delta=expire)
                return jsonify({
                    "msg": "Admin login successful",
                    "token": token,
                    "exp": expire.total_seconds(),
                })
            else:
                # Perform regular user login actions
                expire = datetime.timedelta(minutes=1)
                token = create_access_token(identity=user.email, expires_delta=expire)
                return jsonify({
                    "msg": "User login successful",
                    "token": token,
                    "exp": expire.total_seconds(),
                })
        else:
            return jsonify({
                "msg": "Wrong email or password. Please try again."
            }), 401
    else:
        return jsonify({
            "msg": "Wrong email or password. Please try again."
<<<<<<< HEAD
        }), 401    
=======
        }), 401
>>>>>>> refs/remotes/origin/benbungle


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin',"*")
    response.headers.add('Access-Control-Allow-Headers','Content-type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GEt,PUT,POST,DELETE,OPTIONS')
    return response