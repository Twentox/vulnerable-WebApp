from flask import *
import mysql.connector
import subprocess
import os
import re
import markdown
import html
from flask_limiter import Limiter


app = Flask(__name__)

app.secret_key = os.urandom(32)


app.config.update(
    SESSION_COOKIE_HTTPONLY=True, 
    SESSION_COOKIE_SAMESITE="Lax"
)


limiter = Limiter(
    key_func=lambda: request.remote_addr
)

limiter.init_app(app)


def dynamic_limit():
    if session.get("mode") == "secure":
        return "5 per minute"
    else:
        return "10000 per minute"


@app.before_request
def check_session():
    allowed_routes = ["choose_mode", "static"]

    if request.endpoint not in allowed_routes:
        if "role" not in session:
            return redirect("/")


@app.route('/')
@app.route('/index')
def choose_mode():  
    mode = request.args.get("mode") 
    session["role"] = "guest"
    if mode: 
        if mode == "unsecure":
            app.secret_key = "secret"
            app.config.update(
                SESSION_COOKIE_HTTPONLY=False,     
                SESSION_COOKIE_SAMESITE=None   
            )
        elif mode != "secure" or mode != "unsecure":
            return "Value not allowed", 404
        session["mode"] = mode
        return redirect(url_for('home')) 
    return render_template("index.html")



@app.route('/login', methods=['GET', 'POST'])
@limiter.limit(dynamic_limit)
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        conn = mysql.connector.connect(
            host="database",
            user="root",
            password="password",
            database="vulnapp"
        )

        cursor = conn.cursor()

        try:
            if session['mode'] == "unsecure": 
                query = f"SELECT * FROM users WHERE username = '{username}' AND password='{password}'"
                cursor.execute(query)

                result = cursor.fetchall()
                if len(result) != 0:
                    role = result[0][3]
                    session["role"] = role
                    return redirect(url_for('home'))
                else: 
                    return render_template("login.html", mode=session['mode'], success="Wrong Username or Password")

            elif session["mode"] == "secure":
                query = "SELECT * FROM users WHERE username = %s AND password= %s"
                cursor.execute(query, (username, password))

                result = cursor.fetchone()
                if result:
                    role = result[3]
                    session["role"] = role
                    return redirect(url_for('home'))
                else: 
                    return render_template("login.html", mode=session['mode'], success="Wrong Username or Password")


        except Exception:
            return render_template("login.html", mode=session['mode'], success="SQL Error occurred")
        finally:
            cursor.close()
            conn.close()
            
    return render_template("login.html", mode=session['mode'])



def is_valid_username(username):
    return re.match(r'^[a-zA-Z0-9_]+$', username)

@app.route('/signup', methods=['GET', 'POST'])
@limiter.limit(dynamic_limit)
def signup(): 
    if request.method == 'POST': 
        username = request.form.get('username') 
        password = request.form.get('password')

        if not is_valid_username(username):
            return render_template("signup.html", mode=session['mode'], success="Username not allowed")

        conn = mysql.connector.connect(
            host="database",
            user="root",
            password="password",
            database="vulnapp"
        )

        cursor = conn.cursor()

        try:
            query = "SELECT username FROM users WHERE username=%s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()

            if not result:
                query = "INSERT INTO users(username, password, role) VALUES(%s, %s, 'user')"
                cursor.execute(query, (username, password))
                conn.commit()
            else:
                if session["mode"] == "unsecure":
                    return render_template("signup.html", mode=session['mode'], success="Username already taken")

            return render_template(
                "signup.html",
                mode=session['mode'],
                success="If the username is available, the account has been created. You can now try to log in."
            )

        finally:
            cursor.close()
            conn.close()

    return render_template("signup.html", mode=session['mode'])


@app.route('/dashboard', methods=["GET", "POST"])
def dashboard(): 
    if request.method == "POST": 
        service = request.form.get("service")
        print(service)
        if session["mode"] == "unsecure":
            result = subprocess.run(f"ping -c 1 {service}", shell=True, capture_output=True, text=True)
            print(result.stdout)
        else:
            result = subprocess.run(["ping", "-c", "1", service], shell=False, capture_output=True, text=True)
    
        return render_template("dashboard.html", mode=session['mode'], success=result.stdout)
    else:   
        if session["role"] != "admin" and session["role"] != "staff": 
            return "only the admin or staff can visit that page"  
        else:   
            return render_template("dashboard.html", mode=session['mode'], role=session["role"]) 



@app.route("/explanations/<name>")
def explanation(name):
    safe_name = os.path.basename(name)  
    path = os.path.join("explanations", safe_name + ".md")

    if not os.path.exists(path):
        return "Not found", 404

    with open(path) as f:
        content = f.read()

    html = markdown.markdown(content, extensions=["fenced_code"])
    return render_template("explanation.html", content=html, page=name)


     
@app.route('/home', methods=["GET", "POST"]) 
def home():
    view = request.args.get("view")

    conn = mysql.connector.connect(
            host="database",
            user="root",
            password="password",
            database="vulnapp"
        )

    cursor = conn.cursor()

    if view:
        if session["mode"] == "secure":
            BASE_DIR = "/static/images"
            filename = os.path.basename(view)
            if not filename.endswith(".jpg"): 
                return "not allowed"
        else:
            filename = view
        try:
            with open(f"static/images/{filename}", "rb") as f:
                content = f.read() 
            return Response(content, mimetype="text/plain")
        except FileNotFoundError: 
            return "File not found", 404
        except (ValueError, IsADirectoryError): 
            return "not allowed"
        finally:
            cursor.close()
            conn.close()

    logged_in = session["role"] != "guest"
    if request.method == 'POST': 
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        try:
            query = "INSERT INTO contact(name,email,message) VALUES (%s,%s,%s)"
            values = (name, email, message)
            cursor.execute(query, values)
            conn.commit()
        finally:
            cursor.close()
            conn.close()
    
        return render_template("home.html", mode=session['mode'], success="message sent")
    return render_template("home.html", mode=session['mode'], logged_in=logged_in)


@app.route('/staff', methods=['GET'])
def staff():

    conn = mysql.connector.connect(
            host="database",
            user="root",
            password="password",
            database="vulnapp"
        )

    cursor = conn.cursor()

    if session["role"] != "staff":
        return "Forbidden, 403"
    else: 
        try:
            cur = conn.cursor(dictionary=True)
            query = f"SELECT * FROM contact"
            cur.execute(query)
            result = cur.fetchall()
        finally:
            cursor.close()
            conn.close()
        return render_template("staff.html", messages=result, mode=session["mode"])

  

@app.route("/logout", methods=['GET']) 
def logout():
    session["role"] = "guest"
    return redirect(url_for("home"))


 
if __name__ == '__main__':
    app.run()



