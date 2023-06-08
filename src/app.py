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
from models import db, User, Order, Order_Hamburger, Order_Beverage, Order_Acompañamiento, Hamburger, Beverage, Acompañamientos
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
import datetime
import re
import requests

# from models import Person
key = os.environ.get('API_KEYS')
app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

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
    response.cache_control.max_age = 0  # avoid cache memory
    return response

####################### ORDENES################################
# Route for getting all orders


@app.route('/orders', methods=['GET'])
def get_all_orders():
    orders = Order.query.all()
    return jsonify([order.serialize() for order in orders]), 200


@app.route('/create/order', methods=['POST'])
def new_order():
    user_id = request.json.get('user_id')
    hamburgers = request.json.get('hamburgers', [])  # List of hamburger items
    acompañamientos = request.json.get(
        'acompañamientos', [])  # List of acompañamiento items
    beverages = request.json.get('beverages', [])  # List of beverage items

    order = Order(user_id=user_id, created_at=datetime.datetime.now())
    db.session.add(order)
    db.session.commit()

    order_id = int(order.id)
    # Add hamburgers to the order

    for hamburger in hamburgers:
        hamburger_id = hamburger.get('hamburger_id')
        quantity = hamburger.get('quantity')
        order_hamburger = Order_Hamburger(
            hamburgers_id=hamburger_id, quantity=quantity, order_id=order_id)
        db.session.add(order_hamburger)
        db.session.commit()

    # Add acompañamientos to the order
    for acompañamiento in acompañamientos:
        acompañamiento_id = acompañamiento.get('acompañamientos_id')
        quantity = acompañamiento.get('quantity')
        order_acompañamiento = Order_Acompañamiento(
            acompañamiento_id=acompañamiento_id, quantity=quantity, order_id=order_id)
        db.session.add(order_acompañamiento)
        db.session.commit()

    # Add beverages to the order
    for beverage in beverages:
        beverage_id = beverage.get('beverages_id')
        quantity = beverage.get('quantity')
        order_beverage = Order_Beverage(
            beverage_id=beverage_id, quantity=quantity, order_id=order_id)
        db.session.add(order_beverage)
        db.session.commit()

    return jsonify(order.serialize()), 201


####################### FIN ORDENES#############################

# Rutas para manejar usuarios
@app.route('/users', methods=['GET'])
def get_users():
    # Obtener todos los usuarios de la base de datos
    users = User.query.all()
    user_list = [user.serialize() for user in users]
    return jsonify(user_list), 200


"""
@app.route('/users/<string:email>', methods=['GET'])
def get_user(email):
    # Retrieve the user from the database based on the provided email
    user = User.query.filter_by(email=email).first()

    if user:
        user_data = {
            'name': user.name,
            'email': user.email,
            'apellido': user.apellido,
            'password': user.password,
            'cell_phone': user.cell_phone,
            'date_of_birth': user.date_of_birth.strftime('%Y-%m-%d')
        }
        return jsonify(user_data), 200

    else:
        return jsonify({'error': 'User not found'}), 404
"""

# Admin Route


@app.route('/admin', methods=['GET', 'PUT'])
@jwt_required()
def admin():
    current_user = get_jwt_identity()
    print(current_user)
    # hacer un query filter by email
    if current_user and current_user['is_admin']:
        if request.method == 'PUT':
            order_id = request.json.get('order_id')
            # retrieve orders and filter by datetime.now
            order = Order.query.filter_by(
                id=order_id, created_at=datetime.now()).first()
            if order:
                # update the order details with new values
                user_id = request.json.get('user_id')
                hamburger_id = request.json.get('hamburger_id')
                acompañamiento_id = request.json.get('acompañamiento_id')
                beverage_id = request.json.get('beverage_id')
                quantity = request.json.get('quantity')

                order.user_id = user_id
                order.hamburger_id = hamburger_id
                order.acompañamiento_id = acompañamiento_id
                order.beverage_id = beverage_id
                order.quantity = quantity

                db.session.commit()

                return jsonify({"msg": "Order updated successfully."}), 200
            else:
                return jsonify({"msg": "Order not found."}), 404

    return jsonify({"msg": "Access Denied. Admin privileges required."}), 403


@app.route('/privada', methods=['GET', 'PUT'])
@jwt_required()
def privada():
    identidad = get_jwt_identity()
    user = User.query.filter_by(email=identidad).first()

    if request.method == 'PUT':
        # Obtener los datos enviados en el cuerpo de la solicitud
        body = request.get_json()

        # Actualizar los datos del usuario
        user.name = body["name"]
        user.apellido = body["apellido"]
        user.cell_phone = body["cell_phone"]
        user.date_of_birth = body["date_of_birth"]
        # Guardar los cambios en la base de datos
        db.session.commit()
        return jsonify({"user": user.serialize()})

    # Devolver los datos actualizados del usuario
    return jsonify({"user": user.serialize()})


@app.route('/edit_users/<string:email>', methods=['PUT'])
def email_validity_check(email):
    # Regular expression pattern for email validation
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None


def edit_user(email):
    # Check if the email is valid
    if not email_validity_check(email):
        return jsonify({'error': 'Invalid email format'}), 400

    # Check if the email exists in the database
    user = User.query.filter_by(email=email.first())

    # If email exists, continue with the user update logic

    if user:
        user.name = request.json.get('name', user.name)
        user.apellido = request.json.get('apellido', user.apellido)
        user.cell_phone = request.json.get('cell_phone', user.cell_phone)
        date_of_birth = request.json.get('date_of_birth')
        if date_of_birth:
            user.date_of_birth = datetime.strptime(
                date_of_birth, '%Y-%m-%d'.date())

        db.session.commit()

        user_data = {
            'name': user.name,
            'email': user.email,
            'appelido': user.apellido,
            'cell_phone': user.cell_phone,
            'date_of_birth': user.date_of_birth.strftime('%Y-%m-%d')
        }
        return jsonify(user_data), 200

    else:
        return jsonify({'error': 'User not found'}), 404

# Rutas para manejar las hamburguesas, beverages y acompañamientos


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

    hamburger = Hamburger(name=name, price=price,
                          description=description, hamburger_type=hamburger_type)
    db.session.add(hamburger)
    db.session.commit()
    return jsonify(hamburger.serialize()), 201


@app.route('/hamburgers/<int:hamburger_id>', methods=['GET', 'PUT'])
def update_hamburger(hamburger_id):
    hamburger = Hamburger.query.get(hamburger_id)
    if not hamburger:
        return jsonify({'error': 'Hamburger not Found'}), 404
    if request.method == 'PUT':
        # Update the attributes of the hamburger

        hamburger.name = request.json.get('name', hamburger.name)
        hamburger.price = request.json.get('price', hamburger.price)
        hamburger.description = request.json.get(
            'description', hamburger.description)
        hamburger.hamburger_type = request.json.get(
            'hamburger_type', hamburger.hamburger_type)

    # Save the changes to the Database
    db.session.commit()

    return jsonify({
        'message': 'Hamburger updated sucessfully',
        'hamburger': hamburger.serialize()
    }), 200


# ROUTE FOR BEVERAGES (GET, POST, PUT)

@app.route('/beverages', methods=['GET'])
def get_all_beverages():
    beverages = Beverage.query.all()
    return jsonify([beverage.serialize() for beverage in beverages]), 200


@app.route('/crear_beverages', methods=['POST'])
def create_beverages():
    name = request.json.get('name')
    price = request.json.get('price')
    description = request.json.get('description')
    beverage_type = request.json.get('beverage_type')

    beverage = Beverage(name=name, price=price,
                        description=description, beverage_type=beverage_type)
    db.session.add(beverage)
    db.session.commit()
    return jsonify(beverage.serialize()), 201


@app.route('/beverages/<int:beverage_id>', methods=['GET', 'PUT'])
def update_beverage(beverage_id):
    beverage = Beverage.query.get(beverage_id)
    if not beverage:
        return jsonify({'error': 'Beverage not found'}), 404
    if request.method == 'PUT':
        # Update the attribute  of the beverage
        beverage.name = request.json.get('name', beverage.name)
        beverage.price = request.json.get('price', beverage.price)
        beverage.description = request.json.get(
            'description', beverage.description)
        beverage.hamburger_type = request.json.get(
            'beverage_type', beverage.beverage_type)

    # Save the changes to the Database
    db.session.commit()

    return jsonify({
        'message': 'Beverage updated sucessfully',
        'beverage': beverage.serialize()
    }), 200

# ROUTES FOR ACOMPAÑAMIENTOS (GET, POST, PUT)


@app.route('/acomp', methods=['GET'])
def get_all_acompañamientos():
    acompañamientos = Acompañamientos.query.all()
    return jsonify([acompañamiento.serialize() for acompañamiento in acompañamientos]), 200


@app.route('/crear_acomp', methods=['POST'])
def create_acompañamientos():
    name = request.json.get('name')
    size = request.json.get('size')
    price = request.json.get('price')
    description = request.json.get('description')
    acompañamiento_type = request.json.get('acompañamiento_type')

    acompañamiento = Acompañamientos(name=name, price=price,
                                     description=description, acompañamiento_type=acompañamiento_type, size=size)
    db.session.add(acompañamiento)
    db.session.commit()
    return jsonify(acompañamiento.serialize()), 201


@app.route('/acompañamientos/<int:acompanamiento_id>', methods=['GET', 'PUT'])
def update_acompanamiento(acompanamiento_id):
    acompañamiento = Acompañamientos.query.get(acompanamiento_id)
    if not acompañamiento:
        return jsonify({'error': 'Acompañamiento not found'}), 404
    if request.method == 'PUT':
        # Update the attributes of the acompañamiento

        acompañamiento.name = request.json.get('name', acompañamiento.name)
        acompañamiento.price = request.json.get('price', acompañamiento.price)
        acompañamiento.size = request.json.get('size', acompañamiento.size)
        acompañamiento.description = request.json.get(
            'description', acompañamiento.description)
        acompañamiento.acompañamiento_type = request.json.get(
            'acompañamiento_type', acompañamiento.acompañamiento_type)

    # Save the cambios to the basedatos wey
    db.session.commit()

    return jsonify({
        'message': 'Acompañamiento updated sucessfully',
        'acompañamiento': acompañamiento.serialize()
    }), 200

# RUTAS PARA SIGN UP Y LOGIN (FALTA REESTABLECER CONTRASEÑA)


@app.route('/signup', methods=['POST'])
def signup():
    body = request.get_json()
    email = body['email']
    password = body['password']
    name = body['name']
    apellido = body['apellido']
    date_of_birth = body['date_of_birth']
    cell_phone = body['cell_phone']

    # validate email format
    if not email or not re.search(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        return jsonify({"msg": "Invalid email format"}), 400

    # Validate password strength (at least 8 characters with letters and numbers)
    if len(password) < 8 or not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password):
        return jsonify({"msg": "Password must be at least 8 characters long and contain both letters and numbers"}), 400

    # Validate name and apellido are not empty or blank
    if not name or name.strip() == "":
        return jsonify({"msg": "Name is required"}), 400

    if not apellido or apellido.strip() == "":
        return jsonify({"msg": "Apellido is required"}), 400

    # Validate Phone Number (exactly 8 digits)
    if not cell_phone or not re.search(r'^\d{8}$', cell_phone):
        return jsonify({"msg": "Invalid cell phone number format. it should contain exactly 8 digits."}), 400

    user = User.query.filter_by(email=body['email']).first()
    if not user:
        print(body)

        # Hash the password using bcrypt
        new_user = User(email=email, password=password, name=name, apellido=apellido,
                        is_admin=False, date_of_birth=date_of_birth, cell_phone=cell_phone)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"msg": "User was created"}), 200
    else:
        return jsonify({"msg": "The email entered already has an associated account. Please Log in"}), 400


@app.route("/login", methods=['POST'])
def login():
    body = request.get_json()
    email = body['email']
    password = body['password']

    # Validate Email format
    if not email or not re.search(r'^[\w\.-]+@[\w\.-]+\.\w+$', ['email']):
        return jsonify({
            "msg": "Invalid email format. Please enter a valid email adress."
        }), 400

    # Validate  password format
    if not password or not re.search(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', password):
        return jsonify({
            "msg": "Invalid password format. Password must be  at least 8 characters long and contain both letters and numbers."
        }), 400
    user = User.query.filter_by(email=body['email']).first()
    if user:
        if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            expire = datetime.timedelta(minutes=25)
            token = create_access_token(
                identity=user.email, expires_delta=expire)
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


@app.route('/procesar_pago', methods=['POST'])
def procesar_pago():

    # URL de la API o servidor al que deseas hacer la petición
    url = "https://biz-sandbox.soymach.com/payments"

    # Datos a enviar en la petición POST
    payload = {
        "payment": {
            "amount": 1,
            "message": "Cheese",
            "title": "BURGERFLY",
            "metadata": {
                "product_id": "dd6af8f6-4ba0-47d9-8c38-a4313e08b456",
                "customer_id": "ae0d6762-114b-480c-b60c-51df45110d61"
            }
        }
    }
# Encabezados de la petición con el token de autorización
    headers = {
        "Authorization": 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJidXNpbmVzc01hY2hJZCI6IjI1NDU4MDM5LWYwM2UtNDE1OS04Y2IxLTAzYzA5MzMwMmEzYyIsImJ1c2luZXNzU2VjcmV0SWQiOiJmM2MxMmFhOS04NWI5LTRmYzMtYjA2NS1hYzQwZTYwYmMwMzEiLCJzY29wZXMiOlsicGF5bWVudHMuY3JlYXRlIiwicGF5bWVudHMuZ2V0Il0sImlhdCI6MTY4NTU5MzYwNn0.I3jyKytAIb0m0E_2MeakWtf8bVbkNNOHbs3G6Nh6nf8'
    }
# crear orden(carrito), procesar pago(esperar confirmacion de la api de match, si fue cancelado, DELETE order, si fue correcto, POST order), confirmar pago y enviar resumen de comprar y por ende un GET de la orden al todolist (vista admin)

# Realizar la petición POST
    response = requests.post(url, json=payload, headers=headers)

# Verificar si la petición fue exitosa (código de estado 200)
    if response.status_code == 200:
        # Acceder al contenido de la respuesta
        data = response.json()  # Si la respuesta es un JSON
    # data = response.text  # Si la respuesta es texto plano
        print(data["token"])
        tok = data["token"]
        resp = requests.get(
            f"https://biz-sandbox.soymach.com/payments/{tok}/qr", headers=headers)
        mach_data = resp.json()
        print(mach_data)
        return jsonify({
            "mach_data": mach_data,
            "token_key": tok
        })
    else:
        print("Error en la petición:", response.status_code)


@app.route('/revisar_pago', methods=["GET"])
def revisar_pago():
    global tok

    url = f"https://biz-sandbox.soymach.com/payments/{tok}"
    headers = {
        "Authorization": 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJidXNpbmVzc01hY2hJZCI6IjI1NDU4MDM5LWYwM2UtNDE1OS04Y2IxLTAzYzA5MzMwMmEzYyIsImJ1c2luZXNzU2VjcmV0SWQiOiIzNGZlYWNmOC02MzU0LTQ0OTUtYjYxMS0zM2YxZmYxNmFhYmIiLCJzY29wZXMiOlsicGF5bWVudHMuY3JlYXRlIiwicGF5bWVudHMuZ2V0Il0sImlhdCI6MTY4NjAxNjQwNH0.-raE-hpnhrmJNikCxeRfvsvsX2-z4-ZzQYGJ1iUDMKY'
    }

    while True:
        response = requests.get(url, headers=headers)
        data = response.json()
        print(data["status"])
        
        if data["status"] == "COMPLETED":
            url = f"https://biz-sandbox.soymach.com/payments/{tok}/confirm"
            payload = {
             "payment": {
             "amount": 1,
             "message": "Cheese",
             "title": "BURGERFLY",
             "metadata": {
            "product_id": "dd6af8f6-4ba0-47d9-8c38-a4313e08b456",
            "customer_id": "ae0d6762-114b-480c-b60c-51df45110d61"
             }
             }
             } 
            resp = requests.post(url,json=payload, headers=headers)
            confirmed_data = resp.json()
            print(confirmed_data)
            return jsonify({"data": "Pago confirmado"}),200
        
        time.sleep(5)  # Wait for 5 seconds before checking again


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', "*")
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-type,Authorization')
    response.headers.add('Access-Control-Allow-Methods',
                         'GEt,PUT,POST,DELETE,OPTIONS')
    return response
# agarrar toda la data del post
# enviar todos los objetos a ese endpoint (id,quantity y price)
