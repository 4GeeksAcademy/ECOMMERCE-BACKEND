from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User
from api.utils import generate_sitemap, APIException
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import datetime


api = Blueprint('api', __name__)


app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Clave secreta para firmar los tokens JWT
jwt = JWTManager(app)

# Ruta de registro
@api.route('/registro', methods=['POST'])
def registro():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        raise APIException('Se requiere el nombre de usuario y la contraseña', status_code=400)


    return jsonify({'message': 'Registro exitoso'})

# Ruta de inicio de sesión
@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        raise APIException('Se requiere el nombre de usuario y la contraseña', status_code=400)
    return jsonify({'access_token': access_token})

# Ruta de recuperar contraseña
@api.route('/recuperar-contraseña', methods=['POST'])
def recuperar_contraseña():
    data = request.get_json()
    email = data.get('email')

    if not email:
        raise APIException('Se requiere el correo electrónico', status_code=400)
    return jsonify({'message': 'Correo electrónico enviado'})

# Ruta de favoritos (requiere autenticación)
@api.route('/favoritos', methods=['GET'])
@jwt_required()
def favoritos():
    current_user = get_jwt_identity()
    return jsonify({'favorites': favorites})

# Ruta para generar el sitemap
@api.route('/sitemap.xml', methods=['GET'])
def sitemap():
    return generate_sitemap()

# Manejador de excepciones personalizado
@api.errorhandler(APIException)
def handle_api_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

if __name__ == '__main__':
    app.register_blueprint(api, url_prefix='/api')
    app.run()
