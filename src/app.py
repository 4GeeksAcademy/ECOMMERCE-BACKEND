"""
This a module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for, send_from_directory
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Hamburger, Beverage, Acompañamientos, Order
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import datetime

#from models import Person

ENV = os.getenv("FLASK_ENV")
static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../public/')
app = Flask(__name__)
app.url_map.strict_slashes = False
jwt=JWTManager(app)
db_url = os.getenv("DATABASE_URL")

if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db, compare_type = True)
db.init_app(app)

# Allow CORS requests to this API
CORS(app)

# add the admin
setup_admin(app)





# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    
    return generate_sitemap(app)

# any other endpoint will try to serve it like a static file
@app.route('/<path:path>', methods=['GET'])
def serve_any_other_file(path):
    if not os.path.isfile(os.path.join(static_file_dir, path)):
        path = 'index.html'
    response = send_from_directory(static_file_dir, path)
    response.cache_control.max_age = 0 # avoid cache memory
    return response

# Rutas para manejar usuarios
@app.route('/users', methods=['GET'])
def get_users():
    # Obtener todos los usuarios de la base de datos
    users = User.query.all()
    user_list = [user.serialize() for user in users]
    return jsonify(user_list), 200

@app.route('/users/<string:email>', methods=['GET'])
def get_user(email):
    # Retrieve the user from the database on the provided email
    user = User.query.filter_by(email=email).first()

    if user:
        return jsonify(user.serialize()), 200
    else:
        return jsonify({'error': 'User not found'}), 404

# Route for getting all orders
@app.route('/orders', methods=['GET'])
def get_all_orders():
    orders = Order.query.filter_by(created_at=datetime.now).all()
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
    created_at = datetime.now()
    order = Order(user_id=user_id, hamburger_id=hamburger_id, acompañamiento_id=acompañamiento_id, beverage_id=beverage_id, quantity=quantity, created_at=created_at)
    db.session.add(order)
    db.session.commit()
    return jsonify(order.serialize()), 201

#si Q se refiere a cada una, o a la orden en si.

# Rutas para manejar las hamburguesas
@app.route('/hamburgers', methods=['GET'])
def get_hamburgers():
    # Obtener todas las hamburguesas de la base de datos
    hamburgers = Hamburger.query.all()
    hamburger_list = [hamburger.serialize() for hamburger in hamburgers]
    return jsonify(hamburger_list), 200

@app.route('/crear_hamburgers', methods=['POST'])
def create_hamburger():
    # Obtener los datos de la hamburguesa del cuerpo de la solicitud
    name = request.json.get('name')
    price = request.json.get('price')
    description = request.json.get('description')
    hamburger_type = request.json.get('hamburger_type')

    hamburger = Hamburger(name=name, price=price, description=description, hamburger_type=hamburger_type)
    db.session.add(hamburger)
    db.session.commit()
    return jsonify(hamburger.serialize()), 201


# Route for getting all beverages
@app.route('/beverages', methods=['GET'])
def get_all_beverages():
    beverages = Beverage.query.all()
    return jsonify([beverage.serialize() for beverage in beverages]), 200

@app.route('/crear_beverages', methods=['POST'])
def create_beverages():
    name = request.json.get('name')
    price = request.json.get('price')
    description = request.json.get('description')
    beverages_type = request.json.get('beverages_type')

    beverage = Beverage(name=name, price=price, description=description, beverages_type=beverages_type)
    db.session.add(beverage)
    db.session.commit()
    return jsonify(beverage.serialize()), 201



# Route for getting all acompañamientos
@app.route('/acomp', methods=['GET'])
def get_all_acompañamientos():
    acompañamientos = Acompañamientos.query.all()
    return jsonify([acompañamiento.serialize() for acompañamiento in acompañamientos]), 200



#rutas por crear: CREATE HAMBURGER, CRREATE BEBIDA, CREATE ACOMPAÑAMIENTO.
# PLUS: CREAR POSTRES

@app.route('/signup', methods=['POST'])
def signup():
    body = request.get_json()
    user = User.query.filter_by(email=body['email']).first()
    if not user:
        print(body)
        new_user = User(email=body['email'], password=body['password'], name=body['name'], is_admin = False, date_of_birth=body['date_of_birth'], cell_phone=body['cell_phone'])
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
    
@app.route("/login", methods=['POST'])
def login():
    body = request.get_json()
    user = User.query.filter_by(email=body['email']).first()
    if user:
        if user.password == body["password"]:
            expire = datetime.timedelta(minutes=1)
            token = create_access_token(identity=user.email, expires_delta=expire)
            if user.is_admin:
                # Perform admin login actions
                return jsonify({
                    "msg": "Admin login successful",
                    "token": token,
                    "exp": expire.total_seconds(),
                })
            else:
                # Perform regular user login actions
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
        }), 401


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
