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
from models import db, User, Hamburger
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
