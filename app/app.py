from flask import Flask, render_template, request, redirect, url_for
from database.db import get_db_connection
PORT = 3001

app = Flask(__name__) 

@app.route('/user/<int:user_id>')
def home(user_id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users;')
    results = cursor.fetchall()
    # db.close()
    return render_template('index.html', users=results)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
        db.commit()
        db.close()

        return redirect(url_for('login'))
    return render_template('register.html')

@app.errorhandler(404)
def page_not_found(e):
    return "Page not found!", 404

if __name__ == "__main__":
    print(f"App running on port {PORT}")
    app.run(port=PORT, debug=True)
