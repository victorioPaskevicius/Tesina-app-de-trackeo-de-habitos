from flask import Flask, render_template, request, redirect, url_for
from database.db import get_all_users
PORT = 3001

app = Flask(__name__) 

@app.route('/user/<int:user_id>')
def home(user_id):
    users = get_all_users()
    return render_template('index.html',users=users)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')

@app.route('/perfil')
def perfil():
    return "<h1>Este es tu perfil</h1>"

@app.errorhandler(404)
def page_not_found(e):
    return "Page not found!", 404

if __name__ == "__main__":
    print(f"App running on port {PORT}")
    app.run(port=PORT, debug=True)
