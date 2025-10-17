from flask import Flask, render_template, flash, request, redirect, url_for, jsonify
from datetime import datetime, timedelta
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

@app.route('/user/<int:user_id>', methods=['GET','POST','PUT','DELETE','PATCH'])
@cross_origin()
def home(user_id):
    if request.method == 'GET':
        connection = None
        try:
            connection = get_connection()
            if connection is None:
                return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

            with connection.cursor() as cur:
                # Traer todos los hábitos del usuario
                cur.execute('SELECT * FROM habits WHERE user_id = %s', (user_id,))
                habits = cur.fetchall()  # cada habit debe ser dict (DictCursor)

                today = datetime.now().date()
                updated_habits = []

                for habit in habits:
                    habit_id = habit['id']

                    # --- 1) Rellenar logs faltantes desde último log o desde created_at ---
                    # Obtener último log date
                    cur.execute(
                        "SELECT log_date FROM habit_logs WHERE habit_id = %s ORDER BY log_date DESC LIMIT 1",
                        (habit_id,)
                    )
                    last_log = cur.fetchone()

                    # Determinar fecha inicial para insertar (si no hay logs usamos created_at)
                    if last_log and last_log.get('log_date') is not None:
                        last_date = last_log['log_date']
                        if isinstance(last_date, datetime):
                            last_date = last_date.date()
                        insert_from = last_date + timedelta(days=1)
                    else:
                        # tomar created_at del hábito si existe, sino hoy
                        created = habit.get('created_at')
                        if created is None:
                            insert_from = today
                        else:
                            if isinstance(created, datetime):
                                insert_from = created.date()
                            else:
                                # intentar parsear si viene como string tipo "YYYY-MM-DD" o "YYYY-MM-DD HH:MM:SS"
                                try:
                                    insert_from = datetime.strptime(str(created), "%Y-%m-%d %H:%M:%S").date()
                                except Exception:
                                    try:
                                        insert_from = datetime.strptime(str(created), "%Y-%m-%d").date()
                                    except Exception:
                                        insert_from = today

                    # Insertar logs faltantes (status = 0)
                    cur_date = insert_from
                    # si querés insertar hasta ayer en lugar de hoy, usar while cur_date < today
                    while cur_date <= today:
                        # comprobar que no exista ese log (evita duplicados)
                        cur.execute(
                            "SELECT 1 FROM habit_logs WHERE habit_id = %s AND log_date = %s",
                            (habit_id, cur_date)
                        )
                        exists = cur.fetchone()
                        if not exists:
                            cur.execute(
                                """
                                INSERT INTO habit_logs (habit_id, user_id, log_date, status, created_at)
                                VALUES (%s, %s, %s, %s, NOW())
                                """,
                                (habit_id, user_id, cur_date, 0)
                            )
                            
                            # Reiniciar el estado general del hábito si se crea un nuevo log
                            cur.execute(
                                "UPDATE habits SET is_complete = 0 WHERE id = %s",
                                (habit_id,)
                            )

                        cur_date += timedelta(days=1)

                    # --- 2) Obtener el log de hoy (para mostrar estado actual) ---
                    cur.execute(
                        "SELECT * FROM habit_logs WHERE habit_id = %s AND log_date = CURDATE() LIMIT 1",
                        (habit_id,)
                    )
                    latest_log = cur.fetchone()  # puede ser None o dict

                    # --- 3) Calcular racha actual (consecutividad hacia atrás desde hoy) ---
                    cur.execute(
                        """
                        SELECT log_date
                        FROM habit_logs
                        WHERE habit_id = %s AND user_id = %s AND status = 1
                        ORDER BY log_date DESC
                        """,
                        (habit_id, user_id)
                    )
                    completed_logs = cur.fetchall()  # lista de dicts con 'log_date'

                    streak = 0
                    expected_date = today
                    for l in completed_logs:
                        ld = l.get('log_date')
                        if isinstance(ld, datetime):
                            ld = ld.date()
                        # Si ld coincide con la fecha esperada -> incrementa racha y esperada--.
                        if ld == expected_date:
                            streak += 1
                            expected_date = expected_date - timedelta(days=1)
                        else:
                            break

                    # --- 4) Calcular porcentaje de cumplimiento (opcional) ---
                    cur.execute(
                        """
                        SELECT 
                        SUM(CASE WHEN status = 1 THEN 1 ELSE 0 END) AS completed_days,
                        COUNT(*) AS total_days
                        FROM habit_logs
                        WHERE habit_id = %s AND user_id = %s
                        """,
                        (habit_id, user_id)
                    )
                    stats = cur.fetchone()
                    completed_days = stats.get('completed_days') or 0
                    total_days = stats.get('total_days') or 1
                    completion_rate = round((completed_days / total_days) * 100, 2)

                    # Añadir info al objeto habit que pasaremos al template
                    habit['latest_log'] = latest_log
                    habit['current_streak'] = streak
                    habit['completion_rate'] = completion_rate

                    # DEBUG: imprimir en consola (puedes quitar luego)
                    print(f"[DEBUG] habit_id={habit_id} name={habit.get('name')} streak={streak} completed_days={completed_days}/{total_days}")

                    updated_habits.append(habit)

                # --- 5) Progreso de hoy global ---
                cur.execute(
                    """
                    SELECT 
                    SUM(CASE WHEN status = 1 THEN 1 ELSE 0 END) AS completed_today,
                    SUM(CASE WHEN status = 0 THEN 1 ELSE 0 END) AS pending_today
                    FROM habit_logs
                    WHERE user_id = %s AND log_date = CURDATE()
                    """,
                    (user_id,)
                )
                today_progress = cur.fetchone()
                metrics = {
                    "total_today": (today_progress.get('completed_today') or 0) + (today_progress.get('pending_today') or 0),
                    "completed_today": today_progress.get('completed_today') or 0,
                    "pending_today": today_progress.get('pending_today') or 0
                }

                connection.commit()

            # renderizar (cerrado en finally)
            return render_template('home.html', habits=updated_habits, metrics=metrics)

        except Exception as e:
            print("Error en GET de hábitos:", e)
            return jsonify({'error': str(e)}), 500

        finally:
            if connection:
                connection.close()
  
    elif request.method == 'POST':
        try:
            connection = get_connection()
            if connection is None:
                return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

            data = request.get_json()
            name = data.get('name')
            description = data.get('description')

            with connection.cursor() as cur:
                sql = """
                    INSERT INTO habits (user_id, name, description, is_complete, created_at)
                    VALUES (%s, %s, %s, %s, NOW())
                """
                cur.execute(sql, (user_id, name, description, 0))

                habit_id = cur.lastrowid  

                sql_log = """
                    INSERT INTO habit_logs (habit_id, user_id, log_date, status, created_at)
                    VALUES (%s, %s, NOW(), %s, NOW())
                """
                cur.execute(sql_log, (habit_id, user_id, 0))

                connection.commit()

            return jsonify({'message': 'Hábito insertado con éxito'})

        except Exception as e:
            print("Error al insertar hábito:", e)
            return jsonify({'error': 'Error del servidor'}), 500

        finally:
            if connection:
                connection.close()
                
    elif request.method == 'PUT':
        try:
            connection = get_connection()
            with connection.cursor() as cur:
                data = request.get_json()
                habit_id = data.get('habitId')

                sql = "SELECT is_complete FROM habits WHERE id = %s"
                cur.execute(sql, (habit_id,))
                result = cur.fetchone()
                if not result:
                    return jsonify({'error': 'Hábito no encontrado'}), 404

                new_status = 0 if result['is_complete'] == 1 else 1

                # Actualizar habits
                cur.execute("UPDATE habits SET is_complete = %s WHERE id = %s", (new_status, habit_id))

                # Verificar log de hoy
                sql_check_today = """
                    SELECT id FROM habit_logs WHERE habit_id = %s AND log_date = CURDATE()
                """
                cur.execute(sql_check_today, (habit_id,))
                today_log = cur.fetchone()

                if today_log:
                    cur.execute("UPDATE habit_logs SET status = %s WHERE id = %s", (new_status, today_log['id']))
                else:
                    sql_new_log = """
                        INSERT INTO habit_logs (habit_id, user_id, log_date, status, created_at)
                        VALUES (%s, %s, CURDATE(), %s, NOW())
                    """
                    cur.execute(sql_new_log, (habit_id, user_id, new_status))

                connection.commit()

            return jsonify({'message': 'Hábito actualizado con éxito'}), 200

        except Exception as e:
            print("Error al actualizar hábito:", e)
            return jsonify({'error': str(e)}), 500

        finally:
            if connection:
                connection.close()
  
    elif request.method == 'DELETE':
        try:
            connection = get_connection()
            if connection is None:
                return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

            data = request.get_json()
            habit_id = data.get('habitId')

            with connection.cursor() as cur:
                sql = "DELETE FROM habits WHERE id = %s"
                cur.execute(sql, (habit_id,))
                connection.commit()

            return jsonify({'message': 'Hábito eliminado con éxito'})

        except Exception as e:
            print("Error al eliminar hábito:", e)
            return jsonify({'error': 'Error del servidor'}), 500

        finally:
            if connection:
                connection.close()

    elif request.method == 'PATCH':
        try:
            connection = get_connection()
            if connection is None:
                return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

            data = request.get_json()
            habit_id = data.get('habitId')
            name = data.get('name')
            description = data.get('description')

            if name is None or description is None:
                return jsonify({'error': "Faltan datos obligatorios"}), 400

            with connection.cursor() as cur:
                # Funcion para actualizar los datos del habito
                sql = "UPDATE habits SET name = %s, description = %s WHERE id = %s"
                cur.execute(sql,(name, description, habit_id))
                connection.commit()
            return jsonify({'message': 'Hábito actualizado con éxito'}), 200

        except Exception as e:
            print("Error al actualizar hábito:", e)
            return jsonify({'error': 'Error del servidor'}), 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')

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
                'user_id': user['id']
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
            cur.execute(verif_mail, (email,))
            duplicate_mail = cur.fetchone()
            if duplicate_mail:
                return jsonify({'error': 'El correo ya está registrado'}), 400

            # Insertar nuevo usuario
            sql = "INSERT INTO users (`username`, `email`, `password`) VALUES (%s, %s, %s)"
            cur.execute(sql, (username, email, password))
            user_id = cur.lastrowid

        connection.commit()
        return jsonify({
            'user_id': user_id,
            'message': 'Usuario insertado con exito'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        if connection:
            connection.close()

@app.errorhandler(404)
def page_not_found(e):
    return "Page not found!", 404

if __name__ == "__main__":
    app.run()