from flask import Blueprint, request, jsonify
from app import db
from models import User

routes = Blueprint('routes', __name__)

@routes.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'error': 'Todos los campos son obligatorios'}), 400

    # Verificar si ya existe el usuario o email
    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        return jsonify({'error': 'Usuario o email ya registrados'}), 409

    # Crear nuevo usuario
    try:
        new_user = User(username=username, email=email,password=password)
        db.session.add(new_user)
        db.session.commit() 
        print('Usuario registrado')
    except:
        print('ha ocurrido un error')

    return jsonify({'message': 'Usuario registrado exitosamente'}), 201
