# What makes the gallery preview vulnerable: 
---

- the code to preview the images from the gallery looks like this: 
```python
view = request.args.get("view")
filename = view

try:
    with open(f"static/images/{filename}", "rb") as f:
        content = f.read()
    return Response(content, mimetype="text/plain")
except FileNotFoundError:
    return "File not found", 404
except (ValueError, IsADirectoryError):
    return "not allowed"
```

- you can see that the user input is directly inserted into the file path without any sanitization or filtering  
- this leads to an `LFI` (Local File Inclusion) vulnerability  

- with an LFI vulnerability, it is possible to read sensitive system files, for example the `passwd` file on a Linux system or other files containing confidential information  
- as shown in the write-up, this is dangerous because attackers can gather information about the system and potentially escalate the attack to `RCE` (Remote Code Execution), which is even more critical  

- the `LFI` payload in this case could look like this: 
```html
../../../etc/passwd
```

- here, the attacker uses path traversal to access directories and files outside the intended folder  
- note: attackers can only read files that the application has permission to access  
- typically, a web server on Linux runs as the `www-data` user  

# How to make it secure: 
---

- to secure the gallery image preview, we must sanitize and validate the user input  
- this can be implemented in Python like this: 
```python
import os

view = request.args.get("view")

BASE_DIR = "static/images"
filename = os.path.basename(view)

if not filename.endswith(".jpg"):
    return "not allowed"

try:
    with open(f"{BASE_DIR}/{filename}", "rb") as f:
        content = f.read()
    return Response(content, mimetype="text/plain")

except FileNotFoundError:
    return "File not found", 404
except (ValueError, IsADirectoryError):
    return "not allowed"
```

- we use a base directory where all images are stored  
- additionally, we use `os.path.basename()`, which returns only the file name from a given path  

- example:  
    - input: `/home/user/documents/file.txt`  
    - output: `file.txt`  

- this removes any path traversal sequences like `../`  

- as an additional security measure, we apply a simple whitelist by checking the file extension using `.endswith()`  
- this ensures that only `.jpg` files can be accessed  