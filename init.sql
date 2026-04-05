USE vulnapp;

DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS contact;

CREATE TABLE users (  
    id INT AUTO_INCREMENT PRIMARY KEY,  
    username VARCHAR(50) NOT NULL,  
    password VARCHAR(50) NOT NULL,
    role VARCHAR(50) NOT NULL
);

CREATE TABLE contact(
    id INT AUTO_INCREMENT PRIMARY KEY, 
    name VARCHAR(50) NOT NULL,
    email VARCHAR(50) NOT NULL,
    message VARCHAR(255) NOT NULL
); 

INSERT INTO users(username, password, role)  
VALUES 
("admin", "letmein", "admin"),
("josh", "joshisthebest", "user"); 

INSERT INTO contact(name, email, message)
VALUES
("John", "john04@gmail.com", "Nice pictures, can I book you?"),
("Eric", "ericiscrazy@gmx.com", "I really like your website, maybe we can work together"),
("Maria", "mariaflower@gmail.com", "Hi guys, really nice pictures, can I book you?");