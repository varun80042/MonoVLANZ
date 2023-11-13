CREATE DATABASE IF NOT EXISTS VLANZ;
USE VLANZ;


-- Table: customer
CREATE TABLE IF NOT EXISTS customer (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(128) NOT NULL,
    num_orders INT DEFAULT 0,
    PastOrders INT DEFAULT 0,
    LName VARCHAR(50),
    FName VARCHAR(50),
    PhoneNo VARCHAR(15),
    Location VARCHAR(100)
);


-- Table: freelancer
CREATE TABLE IF NOT EXISTS freelancer (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(128) NOT NULL,
    LName VARCHAR(50),
    FName VARCHAR(50),
    PhoneNo VARCHAR(15),
    Location VARCHAR(100)
);


-- Table: service
CREATE TABLE IF NOT EXISTS service (
    id INT AUTO_INCREMENT PRIMARY KEY,
    freelancer_id INT,
    name VARCHAR(50) NOT NULL,
    domain VARCHAR(50) NOT NULL,
    description VARCHAR(200) NOT NULL,
    rating INT,
    cost DECIMAL(10, 2),
    deleted BOOLEAN DEFAULT 0,
    FOREIGN KEY (freelancer_id) REFERENCES freelancer(id)
);


-- Table: orders
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    service_id INT,
    payment_type VARCHAR(50),
    payment_status VARCHAR(50),
    date_and_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    placed_by_id INT,
    FOREIGN KEY (customer_id) REFERENCES customer(id),
    FOREIGN KEY (service_id) REFERENCES service(id),
    FOREIGN KEY (placed_by_id) REFERENCES customer(id)
);


-- Table: customer_phone
CREATE TABLE IF NOT EXISTS customer_phone (
    customer_id INT,
    phone_no VARCHAR(15),
    PRIMARY KEY (customer_id, phone_no),
    FOREIGN KEY (customer_id) REFERENCES customer(id)
);


-- Table: seller_phone
CREATE TABLE IF NOT EXISTS seller_phone (
    freelancer_id INT,
    phone_no VARCHAR(15),
    PRIMARY KEY (freelancer_id, phone_no),
    FOREIGN KEY (freelancer_id) REFERENCES freelancer(id)
);


-- Table: services
CREATE TABLE IF NOT EXISTS services (
    freelancer_id INT,
    service_id INT,
    PRIMARY KEY (freelancer_id, service_id),
    FOREIGN KEY (freelancer_id) REFERENCES freelancer(id),
    FOREIGN KEY (service_id) REFERENCES service(id)
);


-- Table: past_orders
CREATE TABLE IF NOT EXISTS past_orders (
    customer_id INT,
    order_id INT,
    PRIMARY KEY (customer_id, order_id),
    FOREIGN KEY (customer_id) REFERENCES customer(id),
    FOREIGN KEY (order_id) REFERENCES orders(id)
);


-- Trigger to set the minimum cost of service to 500 Rupees
DELIMITER //
CREATE TRIGGER before_insert_service
BEFORE INSERT ON service
FOR EACH ROW
BEGIN
    IF NEW.cost < 500 THEN
        SET NEW.cost = 500;
    END IF;
END;
//
DELIMITER ;


-- Function to get the name of the customer logged in
DELIMITER //
CREATE FUNCTION get_customer_name(customer_id INT) RETURNS VARCHAR(100) DETERMINISTIC
BEGIN
    DECLARE customer_name VARCHAR(100);
    SELECT CONCAT(FName, ' ', LName) INTO customer_name FROM customer WHERE id = customer_id;
    RETURN customer_name;
END;
//
DELIMITER ;


-- Function to get the name of the freelancer logged in
DELIMITER //
CREATE FUNCTION get_freelancer_name(freelancer_id INT) RETURNS VARCHAR(100) DETERMINISTIC
BEGIN
    DECLARE freelancer_name VARCHAR(100);
    SELECT CONCAT(FName, ' ', LName) INTO freelancer_name FROM freelancer WHERE id = freelancer_id;
    RETURN freelancer_name;
END;
//
DELIMITER ;


-- Procedure to "delete" a service by its service ID
DELIMITER //
CREATE PROCEDURE delete_service(IN service_id INT)
BEGIN
    UPDATE service SET deleted = 1 WHERE id = service_id;
END;
//
DELIMITER ;


-- Procedure to update a service by its service ID
DELIMITER //
CREATE PROCEDURE update_service(IN service_id INT, IN new_name VARCHAR(100), IN new_domain VARCHAR(100), IN new_description TEXT, IN new_cost DECIMAL(10, 2))
BEGIN
    UPDATE service
    SET name = new_name, domain = new_domain, description = new_description, cost = new_cost
    WHERE id = service_id;
END;
//
DELIMITER ;