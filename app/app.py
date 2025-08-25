from flask import Flask, render_template, flash, request, redirect, url_for, jsonify
from database.db import get_connection
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

# Ruta de prueba para verificar conexión con base de datos
@app.route('/test')
def test():
    try:
        connection = get_connection()
        with connection.cursor() as cur:
            cur.execute("SELECT VERSION()")
            version = cur.fetchone()
        connection.close()
        return f"MySQL conectado, versión: {version['VERSION()']}"
    except Exception as e:
        return f"Error: {str(e)}"

# Obtener todos los usuarios
@app.route('/data', methods=['GET'])
def get_data():
    try:
        connection = get_connection()
        with connection.cursor() as cur:
            cur.execute("SELECT * FROM users")
            data = cur.fetchall()
        connection.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login',methods=['GET','POST'])
@cross_origin()
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    try:
        connection = get_connection()
        with connection.cursor() as cur:
            sql = "SELECT id FROM users WHERE email = %s AND password = %s"
            cur.execute(sql, (email, password))
            user = cur.fetchone()
        connection.close()

        if user:
            return jsonify({
                'message': 'Usuario encontrado',
                'user_id': user[0]
            })
        else: 
            return jsonify({'error': 'Email o contraseña icorrectas'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/register', methods=['GET', 'POST'])
@cross_origin()
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    try:
        connection = get_connection()
        with connection.cursor() as cur:
            # Verificar que el mail no este registrado
            verif_mail = "SELECT * FROM users WHERE email = %s"
            cur.execute(verif_mail, (email))
            duplicate_mail = cur.fetchone()
            if duplicate_mail:
                return jsonify({'error': 'El correo ya esta registrado'}),400

            # Insertar nuevo usuario
            sql = "INSERT INTO users (`username`, `email`, `password`) VALUES (%s, %s, %s)"
            cur.execute(sql, (username, email, password))
            user_id = cur.lastrowid
        connection.commit()
        connection.close()
        return jsonify({
                        'message': 'Usuario registrado correctamente',
                        'user_id': user_id
                        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/user/<int:user_id>')
@cross_origin()
def home(user_id):
    return render_template('home.html')

# @app.route('/perfil')
# def perfil():
#     return "<h1>Este es tu perfil</h1>"

@app.errorhandler(404)
def page_not_found(e):
    return "Page not found!", 404

if __name__ == "__main__":
    app.run(debug=True, port=3001)
