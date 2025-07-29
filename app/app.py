from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__) 

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

# Agregar metodo POST
@app.route('/register')
def register():
    return render_template('register.html')


@app.errorhandler(404)
def page_not_found(e):
    return "Page not found!", 404

if __name__ == "__main__":
    app.run(debug=True)
