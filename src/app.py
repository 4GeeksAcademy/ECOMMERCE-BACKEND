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
from models import db, User, Order, Hamburger, Cheeseburger, VeggieBurger, Beverage, Acompañamientos, OnionRings, FrenchFries
from flask_login import login_required
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import datetime

#from models import Person

ENV = os.getenv("FLASK_ENV")
static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../public/')
app = Flask(__name__)
app.url_map.strict_slashes = False

jwt=JWTManager(app)

# database condiguration
db_url = os.getenv("DATABASE_URL")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db, compare_type = True)
db.init_app(app)

# Allow CORS requests to this API
CORS(app)

# add the admin
setup_admin(app)

# add the admin
setup_commands(app)

# Add all endpoints form the API with a "api" prefix
app.register_blueprint(api, url_prefix='/api')

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    if ENV == "development":
        return generate_sitemap(app)
    return send_from_directory(static_file_dir, 'index.html')

# any other endpoint will try to serve it like a static file
@app.route('/<path:path>', methods=['GET'])
def serve_any_other_file(path):
    if not os.path.isfile(os.path.join(static_file_dir, path)):
        path = 'index.html'
    response = send_from_directory(static_file_dir, path)
    response.cache_control.max_age = 0 # avoid cache memory
    return response


    return jsonify(response_body), 200
from flask import Flask, jsonify, request

app = Flask(__name__)

# Rutas para manejar usuarios
@app.route('/users', methods=['GET'])
def get_users():
    # Obtener todos los usuarios de la base de datos
    users = User.query.all()
    user_list = [user.serialize() for user in users]
    return jsonify(user_list), 200

@app.route('/users', methods=['POST'])
def create_user():
    # Obtener los datos del usuario del cuerpo de la solicitud
    name = request.json.get('name')
    email = request.json.get('email')
    password = request.json.get('password')

    # Crear un nuevo objeto de usuario
    new_user = User(name=name, email=email, password=password)

    # Guardar el nuevo usuario en la base de datos
    db.session.add(new_user)
    db.session.commit()

    return jsonify(new_user.serialize()), 201

# Rutas para manejar las hamburguesas
@app.route('/hamburgers', methods=['GET'])
def get_hamburgers():
    # Obtener todas las hamburguesas de la base de datos
    hamburgers = Hamburger.query.all()
    hamburger_list = [hamburger.serialize() for hamburger in hamburgers]
    return jsonify(hamburger_list), 200

@app.route('/hamburgers', methods=['POST'])
def create_hamburger():
    # Obtener los datos de la hamburguesa del cuerpo de la solicitud
    name = request.json.get('name')
    price = request.json.get('price')
    description = request.json.get('description')
    is_vegetarian = request.json.get('is_vegetarian')

    # Crear un nuevo objeto de hamburguesa
    new_hamburger = Hamburger(name=name, price=price, description=description, is_vegetarian=is_vegetarian)

    # Guardar la nueva hamburguesa en la base de datos
    db.session.add(new_hamburger)
    db.session.commit()

    return jsonify(new_hamburger.serialize()), 201


@app.route('/signup', methods=['POST'])
def signup():
    body = request.get_json()
    user = User.query.filter_by(email=body['email']).first
    if not user:
        new_user = User(email=body['email'], password=body['password'], is_active=True)
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




# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=PORT, debug=True)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin',"*")
    response.headers.add('Access-Control-Allow-Headers','Content-type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GEt,PUT,POST,DELETE,OPTIONS')
    return response
