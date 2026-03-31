from flask import *

app = Flask(__name__)

app.secret_key = "secret"


@app.route('/')
@app.route('/index')
def choose_mode():
    mode = request.args.get("mode")
    session["isAdmin"] = "false"
    if mode: 
        session["mode"] = mode
        return redirect(url_for('login')) 
    return render_template("index.html")


@app.route('/login', methods=["GET", "POST"])
def login():

    if request.methode == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
    return render_template("login.html")

if __name__ == '__main__':
    app.run()
