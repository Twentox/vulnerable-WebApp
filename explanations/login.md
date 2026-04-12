# What makes the login vulnerable:
---

- in the unsecure version of the website, the code to process the login input looked like this:
```python
if request.method == "POST":
    username = request.form.get('username')
    password = request.form.get('password')
    
    ...

    try:
        if session['mode'] == "unsecure":
            query = f"SELECT * FROM users WHERE username = '{username}' AND password='{password}'"
            cursor.execute(query)

    except Exception:
        return render_template("login.html", mode=session['mode'], success="SQL Error occurred")

    result = cursor.fetchall()
    if len(result) != 0:
        role = result[0][3]
        session["role"] = role
        
    ...
```

- you can see that the input from the user gets put directly into the query without any sanitization or prevention mechanisms  
- this leads to SQL Injection and is very dangerous  

- the goal of SQL Injection is to create a query that always evaluates to true without knowing the correct values for the username or password  
- this can be done by injecting SQL operators like `AND` or `OR`  

- in our case, the SQL Injection could look like this:
```sql
admin' OR '1'='1' --
```

- the query would then look like this: 
```sql
SELECT * FROM users WHERE username='admin' OR '1'='1' -- AND password='something'; 
```

- in SQL, `AND` has a higher priority than `OR`, so without the comment (`--`), the query would look like this: 
```sql
SELECT * FROM users WHERE username='admin' OR ('1'='1' AND password='something'); 
```

- the query would only evaluate to true when the username is correct or the password is correct  
- this could work, but an attacker would have to know one of the two values  
- so we add a comment to make SQL ignore the password part  

# How to make the login secure: 
---

- specific to our case, we can use `prepared statements` to make our query secure  
- with `prepared statements`, SQL treats our input as data and not as executable code  
- this works by separating the input from the query execution  

- the query is first prepared without the input like this: 
```sql
SELECT * FROM users WHERE username=? AND password=?
```

- with this query, SQL can create an execution plan on how to execute it later  
- after that, the input is sent separately and treated as a string, and automatically escaped if needed  

- in Python, we can implement `prepared statements` like this: 
```python
username = request.form.get('username')
password = request.form.get('password')

query = "SELECT * FROM users WHERE username = %s AND password = %s"
cursor.execute(query, (username, password))
```

- one thing to note is that when you use a query like this:  
```python  
order = request.args.get("sort")  
query = f"SELECT * FROM users ORDER BY {order}"  
```  
  
- you cannot use `prepared statements` to make this query secure, prepared statements only protect values, not SQL structure like column names
- this means the user input becomes part of the SQL structure, which can lead to SQL Injection  

- the best way to make this query secure is to use a `whitelist`:  
```python  
allowed_columns = ["username", "created_at", "role"]  
order = request.args.get("sort")  
  
if order not in allowed_columns:  
order = "username"  
  
query = f"SELECT * FROM users ORDER BY {order}"  
```