CREATE vulnapp;
USE vulnapp; 



CREATE TABLE users (  
id INT AUTO_INCREMENT PRIMARY KEY,  
username VARCHAR(50) NOT NULL,  
password VARCHAR(50) NOT NULL  
);


CREATE TABLE contact(
   id INT AUTO_INCREMENT PRIMARY KEY, 
   name VARCHAR(50) NOT NULL,
   email VARCHAR(50) NOT NULL,
   message VARCHAR(255) NOT NULL
); 


INSERT INTO users (username, password)  
VALUES 
("admin", "password"),
("josh", "joshisthebest"),
("staff", "letmein")