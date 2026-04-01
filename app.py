from flask import *
import mysql.connector


"""
WHAT TO IMPLEMENT: 
IDOR > vielleicht ein link zu einer Galerie in Home
Dashboard -> RCE über Service checker 
LFI > könnte man so machen das man bei Home als Hintergrund ein Bild lädt und dann halt in der URL 
Home -> STORED XSS
SSRF 
Template Injection
USER ENUMERATION -> SIGNUP
UPLOAD VULNERABILITY -> DASHBOARD upload Profile picture

WHAT IS DONE: 
SQLI 
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


@app.route('/')
@app.route('/index')
def choose_mode():
    mode = request.args.get("mode")
    session["isAdmin"] = "false"
    if mode: 
        session["mode"] = mode
        return redirect(url_for('home')) 
    return render_template("index.html")



@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        # HIER DANN SICHERE VARIANTE EINBAUEN
        # HIER AUCH NOCH EINBAUEN DAS MAN USER ENUMERATION MACHEN KANN 
        query = f"SELECT * FROM users WHERE username = '{username}' AND password='{password}'"
        cursor.execute(query)
        result = cursor.fetchall()
        if len(result) == 1:
            session["isAdmin"] = "true"
            return redirect(url_for('dashboard'))
        else:
            return 'Wrong Username or Password'

    return render_template("login.html", mode=session['mode'])


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST': 
        username = request.form.get('username')
        password = request.form.get('password')
        # DANN NOCH MIT JAVASCRIPT CHECKEN OB BEIDE PASSWOERTER IN DER FORM GLEICH SIND
    return render_template("signup.html", mode=session['mode'])


@app.route('/dashboard')
def dashboard(): 
    if session["isAdmin"] == "false":
        return "only admins can visit that page" 
    elif session["isAdmin"] == "true":
        return render_template("dashboard.html", mode=session['mode'])


@app.route('/home')
def home():
    return render_template('home.html', mode=session['mode'])



@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST': 
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        query = f"INSERT INTO contact(name,email,message)VALUES(%s,%s,%s)"
        values = (name,email,message)
        cursor.execute(query, values)
        conn.commit()
        return render_template("home.html", mode=session['mode'], success="Nachricht gesendet!")
    return render_template("home.html", mode=session['mode'])

if __name__ == '__main__':
    app.run()



