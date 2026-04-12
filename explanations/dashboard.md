# What makes the Connectivity Check vulnerable: 
---

- the code for the `Connectivity Check` looks like this: 
```python
service = request.form.get("service")
result = subprocess.run(f"ping -c 1 {service}", shell=True, capture_output=True, text=True)

return render_template("dashboard.html", mode=session['mode'], success=result.stdout)
```

- The application uses `subprocess.run()` to execute a system command (`ping`)
- The user input (`service`) is directly embedded into the command string
- The option `shell=True` causes the command to be executed **through a system shell**

- `capture_output=True` → captures `stdout` and `stderr` instead of printing them
- `text=True` → converts the output from bytes to a string
- `shell=True` → executes the command inside a shell (e.g. `/bin/sh`)

- to combine user input and `shell=True` is dangerous, because it leads to `RCE` (Remote Code Execution)
- because the command gets executed in a `shell` an attacker can use the shell features, like: `;` or `&&`  to run additional commands 
- a payload for this could look like this:
```bash
192.168.132.187 && id
```

```bash
PING 192.168.132.187 (192.168.132.187) 56(84) bytes of data.
64 bytes from 192.168.132.187: icmp_seq=1 ttl=64 time=0.039 ms

--- 192.168.132.187 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 0.039/0.039/0.039/0.000 ms
uid=0(root) gid=0(root) groups=0(root)
```

# How to make it secure: 
---

- to make it secure we have to set `shell=false` and have to implement `Direct Process Invocation`: 
```python
service = request.form.get("service")
result = subprocess.run(["ping", "-c", "1", service], shell=False, capture_output=True, text=True)

return render_template("dashboard.html", mode=session['mode'], success=result.stdout)
```

- By setting `shell=False` (which is the default), the command is not executed through a shell  
- This prevents attackers from using shell features such as:
    - command chaining (`;`, `&&`)
    - pipes (`|`)
    - environment variable expansion (`$HOME`)
- Instead of passing a single string, we pass a list of arguments to `subprocess.run()` 
- This technique is called Direct Process Invocation
- Each element in the list is treated as a **separate argument**, meaning:
    - the first element (`"ping"`) is the program being executed
    - all following elements are passed as arguments to that program

# ⚠️ Important note:
---
- While `ping` itself does not provide options that lead to RCE, other Linux commands do
-  A well-known example is: `find . -exec <command>`
- If user input is incorrectly handled, this can still lead to command execution
- A good reference for such cases is: [https://gtfobins.org/](https://gtfobins.org/)