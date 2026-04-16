# Why the Session is Not Secure:
---

- The session (stored as a cookie) is insecure due to the following configuration:

```python
app.secret_key = "secret"

app.config.update(
    SESSION_COOKIE_HTTPONLY=False,
    SESSION_COOKIE_SAMESITE=None
)
```

### 1. Weak Secret Key
---

- The `secret_key` is used to **sign** the session cookie.
- Signing ensures that users cannot modify the cookie without detection.
- If the key is weak (e.g., `"secret"`), it can be brute-forced.

Example using `flask-unsign`:

```bash
flask-unsign --unsign --cookie "<cookie>" --wordlist /usr/share/rockyou.txt --no-literal-eval
```

- Once the key is known, an attacker can:
  - Modify session data (e.g., change role to `admin`)
  - Re-sign the cookie
  - Gain unauthorized access

### 2. `SESSION_COOKIE_HTTPONLY = False`
---

- Allows JavaScript access to cookies:

```javascript
console.log(document.cookie)
```

- This is dangerous in combination with **XSS vulnerabilities**:
  - An attacker can steal session cookies
  - Leads to **session hijacking**

> Note: This is not a vulnerability on its own, but it significantly increases the impact of XSS.

### 3. `SESSION_COOKIE_SAMESITE = None`
---

- The session cookie is sent with **all requests**, including cross-site requests.
- This enables **Cross-Site Request Forgery (CSRF)** attacks.

- Example attack:
```html
<form action="https://target-app/delete-account" method="POST">
    <input type="submit">
</form>

<script>
document.forms[0].submit()
</script>
```

- The browser automatically includes the session cookie.
- The server assumes the request is legitimate.

### 4. Insecure Cookie Access:
---

- using:

```python
request.cookies.get("session")
```

- Bypasses Flask's session handling.
- **No signature validation is performed**
- An attacker can fully control the cookie content

#  How to Make the Session Secure:
---

### 1. Use a Strong Secret Key

```python
import os
app.secret_key = os.environ["SECRET_KEY"]
```

- Use a securely generated random value
- Never hardcode secrets in source code

### 2. Secure Cookie Configuration:
---

```python
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE="Lax"
)
```

- `HTTPOnly=True` → prevents JavaScript access
- `Secure=True` → cookie only sent over HTTPS
- `SameSite="Lax"` → mitigates most CSRF attacks

### 3. Use HTTPS:
---

- Encrypts all traffic between client and server
- Prevents session cookies from being intercepted (sniffing)


### 4. Implement CSRF Protection:
---

- Use CSRF tokens (e.g., via Flask-WTF)
- Validate `Origin` or `Referer` headers
