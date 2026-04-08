from flask import *
import mysql.connector
import subprocess
import os


"""
WHAT IS DONE: 
Cookie-Forgery mit (flask-unsign --unsign --cookie "eyJpc0FkbWluIjoiZmFsc2UiLCJtb2RlIjoidW5zZWN1cmUifQ.ac5j0w.x5q50P5UVRdOEyyZbymN4H57ofE" --wordlist /usr/share/rockyou.txt --no-literal-eval) 
"""

"""
WAS MUSS ALLES NOCH GEMACHT WERDEN: 
- TEMPLATE INJECTION (HIER DANN EINFACH UNTEN BEI CONTACT EIN PREVIEW MACHEN VON DER ABGESENDETEN NACHRICHT)
- CODE AUFRÄUMEN
- BEI LOGIN BEIM INPUT TAG EIN BISSCHEN PADDING LINKS NOCH REINMACHEN 
- STORED XSS AM ENDE NOCHMAL PROBIEREN UM ZU CHECKEN OB DER COOKIE NOCH GÜLTIG IST 


SECURE: 
SQLI: https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html (prepared Statements)
      - funktioniert aber nicht bei Dynamische SQL-Teile, also zum Beispiel Tabellennamen oder Spaltennamen 
      - query = f"SELECT * FROM users ORDER BY {order}" das ist wieder unsicher wenn man prepared Statements benutzt 
      - bei unserer Query gibt das aber eine Sicherheitsrate von 100%
LFI: 
      - EINFACH MIT BASENAME UND DANN ABFRAGEN OB .JPG AM ENDE VORKOMMT 


"""


conn = mysql.connector.connect(
    host="database",
    user="root",
    password="password",
    database="vulnapp"
)


cursor = conn.cursor()

app = Flask(__name__)

app.secret_key = "secret"


@app.before_request
def check_session():
    allowed_routes = ["choose_mode"]

    if request.endpoint not in allowed_routes:
        if "role" not in session:
            return redirect("/")


@app.route('/')
@app.route('/index')
def choose_mode():
    mode = request.args.get("mode")
    session["role"] = "guest"
    if mode: 
        session["mode"] = mode
        if session["mode"] == "unsecure":
            app.config['SESSION_COOKIE_HTTPONLY'] = True
        else:
            app.config['SESSION_COOKIE_HTTPONLY'] = False

        return redirect(url_for('home')) 
    return render_template("index.html")



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        if session['mode'] == "unsecure": 
            query = f"SELECT * FROM users WHERE username = '{username}' AND password='{password}'"
            cursor.execute(query)
        elif session["mode"] == "secure":
            query = "SELECT * FROM users WHERE username = %s AND password= %s"
            cursor.execute(query, (username, password))
        result = cursor.fetchall()
        if len(result) == 1:
            role = result[0][3]
            session["role"] = role
            return redirect(url_for('home'))
        else: 
            return render_template("login.html", mode=session['mode'], success="Wrong Username or Password")
            
    return render_template("login.html", mode=session['mode'])


@app.route('/signup', methods=['GET', 'POST'])
def signup(): 
    if request.method == 'POST': 
        username = request.form.get('username') 
        password = request.form.get('password')
        query = f"SELECT username FROM users WHERE username='{username}'"
        cursor.execute(query)
        result = cursor.fetchall()
        if(len(result) >= 1):
            return render_template("signup.html", mode=session['mode'], success="Username already taken")
        else:
            query = f"INSERT INTO users(username, password, role)VALUES('{username}', '{password}', 'user')"
            cursor.execute(query)
            conn.commit()
    else:
        return render_template("signup.html", mode=session['mode'])


@app.route('/dashboard', methods=["GET", "POST"])
def dashboard(): 
    if request.method == "POST": 
        file_name = request.form.get("file")
        result = subprocess.run(f"cat {file_name}", shell=True, capture_output=True, text=True)
        print(result)
        print(result.stdout) 
        return render_template("dashboard.html", mode=session['mode'], success=result.stdout)
    else: 
        if session["role"] != "admin": 
            return "only the admin or staff can visit that page" 
        elif session["role"] == "admin":   
            return render_template("dashboard.html", mode=session['mode'], role=session["role"]) 


     
@app.route('/home', methods=["GET", "POST"]) 
def home():
    view = request.args.get("view")
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
        except ValueError: 
            return "not allowed"

    logged_in = session["role"] != "guest"
    if request.method == 'POST': 
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        query = f"INSERT INTO contact(name,email,message)VALUES(%s,%s,%s)"
        values = (name,email,message)
        cursor.execute(query, values)
        conn.commit()
        return render_template("home.html", mode=session['mode'], success="message sended")
    return render_template("home.html", mode=session['mode'], logged_in=logged_in)


@app.route('/staff', methods=['GET'])
def staff():
    if session["role"] != "staff":
        return "Forbidden, 403"
    else: 
        cur = conn.cursor(dictionary=True)
        query = f"SELECT * FROM contact"
        cur.execute(query)
        result = cur.fetchall()
        print(result)
        return render_template("staff.html", messages=result, mode=session["mode"])

  

@app.route("/logout", methods=['GET']) 
def logout():
    session["role"] = "guest"
    return redirect(url_for("home"))


 
if __name__ == '__main__':
    app.run()



