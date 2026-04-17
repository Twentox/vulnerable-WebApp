# Why the Signup is vulnerable: 
---

- the signup is vulnerable because this is the code to process the input from the user: 
```python

username = request.form.get('username')
password = request.form.get('password')

...

try:
	query = "SELECT username FROM users WHERE username=%s"
	cursor.execute(query, (username,))
	
	result = cursor.fetchone()

	if result:		
		return render_template("signup.html", mode=session['mode'], success="Username already taken")
		
...
```

- you can see that the username the user put in gets used in a query to check if the username already exists 
- this is common, but what is not common and very dangerous is the message: `Username already taken` that gets displayed when a username is already taken 

- this leads to `username enumeration` and combined with brute force on the login its very possible to get the username and password from other users 
- to exploit this an attacker would for example use the tool `ffuf`: 
```bash
ffuf --request signup.rq --request-proto http -w /usr/share/SecLists/Usernames/Names/names.txt -mr "taken"
```

- here the attacker keeps requesting the signup page with a different username each request and when the word `taken` is in the reponse from the server the attacker knows that this was a valid username 

# How to make it secure: 
---

- to make it secure we can implement `rate limiting` 
- rate limiting reduces the effectiveness of automated enumeration attacks, but does not fully prevent them
- first lets go over the `rate limiting`: 
```python
from flask_limiter import Limiter

limiter = Limiter(
	key_func=lambda: request.remote_addr
)

limiter.init_app(app)

def dynamic_limit():
	if session.get("mode") == "secure":
		return "5 per minute"
	else:
		return "10000 per minute"


@app.route('/signup', methods=['GET', 'POST'])
@limiter.limit(dynamic_limit)
def signup():
	...
```

- you can see that we can use `flask_limiter` to implement `rate limiting` 
- we created a function called `dynamic_limit` that sets the rate limiting corresponding to the current mode of the website 
- then we have to add the limiter to a route 
- we also added the limiter to the `login` route

- now we have to change the success message from the signup: 
```python

username = request.form.get('username')
password = request.form.get('password')

...

try:

	query = "SELECT username FROM users WHERE username=%s"
	cursor.execute(query, (username,))
	result = cursor.fetchone()
	
	if not result:
		query = "INSERT INTO users(username, password, role) VALUES(%s, %s, 'user')"
		cursor.execute(query, (username, password))
		conn.commit()
		
	return render_template(
		"signup.html",
		mode=session['mode'],
		success="If the username is available, the account has been created. You can now try to log in."
	)
```

- you can see here that we are outputing: `If the username is available, the account has been created. You can now try to log in.` even if the username is already taken 
- but even with identical messages, differences in response time or HTTP behavior (e.g., status codes) can still allow attackers to perform username enumeration
- so you can add a fake database operation (e.g., a delay or dummy query), when we username is already taken, so that the response time is the same as when the username would not be taken  
- the application must also return the same HTTP status code and response behavior for all cases, otherwise attackers can distinguish valid usernames through side channels