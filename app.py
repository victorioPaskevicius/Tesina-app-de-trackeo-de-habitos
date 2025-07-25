from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__) 

@app.route('/')
def home():
    return "Welcome to the Flask App!"

@app.route('/login')
def login():
    return "This is the Login page."

# Corregir error (No encuentra el archivo a renderizar)
@app.route('/register')
def register():
    render_template('/app/pages/Register/index.html')

@app.errorhandler(404)
def page_not_found(e):
    return "Page not found!", 404

if __name__ == "__main__":
    app.run(debug=True)
    print("Flask app is running...")