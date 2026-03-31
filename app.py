from flask import *
import mysql.connector
import os 
import time


time.sleep(5)


conn = mysql.connector.connect(
    host="database",
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)


cursor = conn.cursor()

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")


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

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        print("Username: " + username + ", Password: " + password)
        query = f"SELECT * FROM users WHERE username = '{username}' AND password='{password}'"
        cursor.execute(query)
        result = cursor.fetchall()
        if len(result) == 1:
            return "richtig"
        else:
            return "falsch"

    return render_template("login.html")

if __name__ == '__main__':
    app.run()
