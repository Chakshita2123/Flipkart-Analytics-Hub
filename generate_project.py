"""
Flipkart Analytics Hub - SQL Project Generator
===============================================
Save this file as generate_project.py inside your project folder, then run:
    python generate_project.py

It will create 4 files in the same directory:
    schema.sql       - 8-table database schema
    sample_data.sql  - 100 users, 20 sellers, 50 products, 155+ orders
    queries.sql      - 15 advanced analytical SQL queries
    README.md        - Complete project documentation
"""

import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ─────────────────────────────────────────────────────────────────────────────
# FILE 1: SCHEMA.SQL
# ─────────────────────────────────────────────────────────────────────────────
SCHEMA_SQL = """\
-- =============================================================================
-- Flipkart Analytics Hub - Database Schema
-- =============================================================================
-- Author  : Flipkart Analytics Hub Project
-- Purpose : E-commerce analytics database modelled on Indian marketplace data
-- Engine  : MySQL 8.0+
-- =============================================================================

DROP DATABASE IF EXISTS flipkart_analytics;
CREATE DATABASE flipkart_analytics
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
USE flipkart_analytics;

-- Table 1: users
CREATE TABLE users (
    user_id      INT             NOT NULL AUTO_INCREMENT,
    username     VARCHAR(80)     NOT NULL,
    email        VARCHAR(120)    NOT NULL UNIQUE,
    city         VARCHAR(60)     NOT NULL,
    region       ENUM('North','South','East','West') NOT NULL,
    signup_date  DATE            NOT NULL,
    user_type    ENUM('Regular','Premium','VIP') NOT NULL DEFAULT 'Regular',
    PRIMARY KEY (user_id)
);

-- Table 2: sellers
CREATE TABLE sellers (
    seller_id        INT          NOT NULL AUTO_INCREMENT,
    seller_name      VARCHAR(120) NOT NULL,
    rating           DECIMAL(3,2) NOT NULL DEFAULT 4.00,
    total_products   INT          NOT NULL DEFAULT 0,
    established_date DATE         NOT NULL,
    user_id          INT          NOT NULL,
    PRIMARY KEY (seller_id),
    CONSTRAINT fk_seller_user FOREIGN KEY (user_id)
        REFERENCES users (user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Table 3: categories
CREATE TABLE categories (
    category_id    INT         NOT NULL AUTO_INCREMENT,
    category_name  VARCHAR(80) NOT NULL,
    subcategory    VARCHAR(80) NOT NULL,
    PRIMARY KEY (category_id)
);

-- Table 4: products
CREATE TABLE products (
    product_id    INT           NOT NULL AUTO_INCREMENT,
    product_name  VARCHAR(200)  NOT NULL,
    category_id   INT           NOT NULL,
    seller_id     INT           NOT NULL,
    price         DECIMAL(10,2) NOT NULL,
    rating        DECIMAL(3,2)  NOT NULL DEFAULT 0.00,
    stock         INT           NOT NULL DEFAULT 0,
    created_date  DATE          NOT NULL,
    PRIMARY KEY (product_id),
    CONSTRAINT fk_product_category FOREIGN KEY (category_id)
        REFERENCES categories (category_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_product_seller FOREIGN KEY (seller_id)
        REFERENCES sellers (seller_id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Table 5: orders
CREATE TABLE orders (
    order_id       INT           NOT NULL AUTO_INCREMENT,
    user_id        INT           NOT NULL,
    order_date     DATE          NOT NULL,
    total_amount   DECIMAL(12,2) NOT NULL,
    payment_method ENUM('COD','UPI','Credit Card','Debit Card','Wallet') NOT NULL,
    order_status   ENUM('Pending','Confirmed','Shipped','Delivered','Cancelled','Returned')
                                 NOT NULL DEFAULT 'Pending',
    region         ENUM('North','South','East','West') NOT NULL,
    PRIMARY KEY (order_id),
    CONSTRAINT fk_order_user FOREIGN KEY (user_id)
        REFERENCES users (user_id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Table 6: order_items
CREATE TABLE order_items (
    order_item_id INT           NOT NULL AUTO_INCREMENT,
    order_id      INT           NOT NULL,
    product_id    INT           NOT NULL,
    quantity      INT           NOT NULL DEFAULT 1,
    unit_price    DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (order_item_id),
    CONSTRAINT fk_item_order   FOREIGN KEY (order_id)
        REFERENCES orders (order_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_item_product FOREIGN KEY (product_id)
        REFERENCES products (product_id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Table 7: reviews
CREATE TABLE reviews (
    review_id   INT      NOT NULL AUTO_INCREMENT,
    product_id  INT      NOT NULL,
    user_id     INT      NOT NULL,
    rating      TINYINT  NOT NULL CHECK (rating BETWEEN 1 AND 5),
    review_text TEXT,
    review_date DATE     NOT NULL,
    PRIMARY KEY (review_id),
    CONSTRAINT fk_review_product FOREIGN KEY (product_id)
        REFERENCES products (product_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_review_user   FOREIGN KEY (user_id)
        REFERENCES users (user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Table 8: returns
CREATE TABLE returns (
    return_id   INT          NOT NULL AUTO_INCREMENT,
    order_id    INT          NOT NULL,
    product_id  INT          NOT NULL,
    return_date DATE         NOT NULL,
    reason      VARCHAR(200) NOT NULL,
    status      ENUM('Requested','Approved','Rejected','Completed')
                             NOT NULL DEFAULT 'Requested',
    PRIMARY KEY (return_id),
    CONSTRAINT fk_return_order   FOREIGN KEY (order_id)
        REFERENCES orders (order_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_return_product FOREIGN KEY (product_id)
        REFERENCES products (product_id) ON DELETE RESTRICT ON UPDATE CASCADE
);
"""

# ─────────────────────────────────────────────────────────────────────────────
# FILE 2: SAMPLE_DATA.SQL
# ─────────────────────────────────────────────────────────────────────────────
SAMPLE_DATA_SQL = """\
-- =============================================================================
-- Flipkart Analytics Hub - Sample Data (Realistic Indian E-commerce)
-- =============================================================================
USE flipkart_analytics;

-- USERS (100 rows)
INSERT INTO users (username, email, city, region, signup_date, user_type) VALUES
('Aarav_Sharma','aarav.sharma@gmail.com','Delhi','North','2023-01-15','VIP'),
('Priya_Gupta','priya.gupta@yahoo.com','Delhi','North','2023-02-10','Premium'),
('Rohit_Verma','rohit.verma@outlook.com','Jaipur','North','2023-03-05','Regular'),
('Sneha_Singh','sneha.singh@gmail.com','Lucknow','North','2023-04-20','Regular'),
('Amit_Kumar','amit.kumar01@gmail.com','Delhi','North','2023-05-12','Premium'),
('Kavita_Rao','kavita.rao@rediffmail.com','Chandigarh','North','2023-06-08','Regular'),
('Vikas_Jain','vikas.jain@gmail.com','Noida','North','2023-07-14','VIP'),
('Pooja_Mishra','pooja.mishra@gmail.com','Agra','North','2023-08-25','Regular'),
('Deepak_Tiwari','deepak.tiwari@gmail.com','Lucknow','North','2023-09-18','Regular'),
('Anjali_Saxena','anjali.saxena@gmail.com','Delhi','North','2023-10-02','Premium'),
('Rahul_Pandey','rahul.pandey@gmail.com','Varanasi','North','2023-11-15','Regular'),
('Nisha_Agarwal','nisha.agarwal@gmail.com','Noida','North','2023-12-01','Regular'),
('Suresh_Yadav','suresh.yadav@gmail.com','Delhi','North','2024-01-10','Regular'),
('Rekha_Dwivedi','rekha.dwivedi@gmail.com','Jaipur','North','2024-02-14','Regular'),
('Manish_Trivedi','manish.trivedi@gmail.com','Agra','North','2024-03-20','Regular'),
('Suman_Bhatt','suman.bhatt@gmail.com','Dehradun','North','2024-04-05','Regular'),
('Ajay_Chauhan','ajay.chauhan@gmail.com','Jaipur','North','2024-05-18','Regular'),
('Meena_Rawat','meena.rawat@gmail.com','Delhi','North','2024-06-12','Premium'),
('Vijay_Pathak','vijay.pathak@gmail.com','Chandigarh','North','2024-07-22','Regular'),
('Geeta_Shukla','geeta.shukla@gmail.com','Lucknow','North','2024-08-08','Regular'),
('Arjun_Reddy','arjun.reddy@gmail.com','Hyderabad','South','2023-01-20','VIP'),
('Lakshmi_Iyer','lakshmi.iyer@gmail.com','Chennai','South','2023-02-28','Premium'),
('Karthik_Nair','karthik.nair@gmail.com','Bangalore','South','2023-03-15','Regular'),
('Divya_Menon','divya.menon@gmail.com','Kochi','South','2023-04-10','Regular'),
('Suresh_Pillai','suresh.pillai@gmail.com','Trivandrum','South','2023-05-25','Regular'),
('Preethi_Rao','preethi.rao@gmail.com','Bangalore','South','2023-06-18','Premium'),
('Venkat_Subbu','venkat.subbu@gmail.com','Chennai','South','2023-07-08','Regular'),
('Ananya_Krishna','ananya.krishna@gmail.com','Hyderabad','South','2023-08-14','VIP'),
('Ravi_Shankar','ravi.shankar@gmail.com','Mysore','South','2023-09-05','Regular'),
('Poornima_Bhat','poornima.bhat@gmail.com','Mangalore','South','2023-10-20','Regular'),
('Sunil_Varma','sunil.varma@gmail.com','Hyderabad','South','2023-11-12','Regular'),
('Kavya_Prasad','kavya.prasad@gmail.com','Bangalore','South','2023-12-08','Regular'),
('Naresh_Babu','naresh.babu@gmail.com','Visakhapatnam','South','2024-01-15','Regular'),
('Sudha_Murthy','sudha.murthy99@gmail.com','Bangalore','South','2024-02-20','VIP'),
('Ganesh_Rajan','ganesh.rajan@gmail.com','Coimbatore','South','2024-03-14','Regular'),
('Meera_Pillai','meera.pillai@gmail.com','Kochi','South','2024-04-28','Regular'),
('Arun_Kumar_S','arun.kumar.s@gmail.com','Chennai','South','2024-05-10','Regular'),
('Sridevi_R','sridevi.r@gmail.com','Bangalore','South','2024-06-22','Regular'),
('Prakash_K','prakash.k@gmail.com','Hyderabad','South','2024-07-04','Regular'),
('Usha_Rani','usha.rani@gmail.com','Chennai','South','2024-08-15','Regular'),
('Rahul_Mehta','rahul.mehta@gmail.com','Mumbai','West','2023-01-25','VIP'),
('Priya_Patel','priya.patel@gmail.com','Ahmedabad','West','2023-02-18','Premium'),
('Nikhil_Shah','nikhil.shah@gmail.com','Pune','West','2023-03-22','Regular'),
('Ruchi_Desai','ruchi.desai@gmail.com','Mumbai','West','2023-04-15','Regular'),
('Hardik_Trivedi','hardik.trivedi@gmail.com','Surat','West','2023-05-08','Regular'),
('Mira_Kapoor','mira.kapoor@gmail.com','Mumbai','West','2023-06-28','Premium'),
('Yash_Modi','yash.modi@gmail.com','Vadodara','West','2023-07-18','Regular'),
('Swati_Joshi','swati.joshi@gmail.com','Pune','West','2023-08-05','Regular'),
('Kiran_Parekh','kiran.parekh@gmail.com','Ahmedabad','West','2023-09-24','VIP'),
('Dipti_Kulkarni','dipti.kulkarni@gmail.com','Nagpur','West','2023-10-14','Regular'),
('Akash_Bhatt','akash.bhatt@gmail.com','Mumbai','West','2023-11-20','Regular'),
('Sonali_Thakur','sonali.thakur@gmail.com','Pune','West','2023-12-12','Regular'),
('Rohan_Sawant','rohan.sawant@gmail.com','Goa','West','2024-01-08','Regular'),
('Neha_Shirke','neha.shirke@gmail.com','Mumbai','West','2024-02-25','Regular'),
('Pramod_Naik','pramod.naik@gmail.com','Nashik','West','2024-03-18','Regular'),
('Smita_Chavan','smita.chavan@gmail.com','Pune','West','2024-04-10','Regular'),
('Tushar_Gaikwad','tushar.gaikwad@gmail.com','Aurangabad','West','2024-05-05','Regular'),
('Varsha_Patil','varsha.patil@gmail.com','Kolhapur','West','2024-06-15','Regular'),
('Aditya_Rane','aditya.rane@gmail.com','Mumbai','West','2024-07-10','Premium'),
('Sheetal_Londhe','sheetal.londhe@gmail.com','Pune','West','2024-08-20','Regular'),
('Sourav_Das','sourav.das@gmail.com','Kolkata','East','2023-01-30','VIP'),
('Rina_Chatterjee','rina.chatterjee@gmail.com','Kolkata','East','2023-02-22','Regular'),
('Bikash_Saha','bikash.saha@gmail.com','Bhubaneswar','East','2023-03-10','Regular'),
('Debojit_Roy','debojit.roy@gmail.com','Guwahati','East','2023-04-25','Regular'),
('Moumita_Sen','moumita.sen@gmail.com','Kolkata','East','2023-05-15','Regular'),
('Tanmoy_Ghosh','tanmoy.ghosh@gmail.com','Durgapur','East','2023-06-08','Regular'),
('Sanchita_Mondal','sanchita.mondal@gmail.com','Kolkata','East','2023-07-22','Premium'),
('Pritam_Banerjee','pritam.banerjee@gmail.com','Howrah','East','2023-08-18','Regular'),
('Anamika_Dutta','anamika.dutta@gmail.com','Siliguri','East','2023-09-12','Regular'),
('Krishanu_Pal','krishanu.pal@gmail.com','Kolkata','East','2023-10-28','Regular'),
('Sayani_Bose','sayani.bose@gmail.com','Asansol','East','2023-11-18','Regular'),
('Riju_Nath','riju.nath@gmail.com','Guwahati','East','2023-12-22','Regular'),
('Biplab_Mitra','biplab.mitra@gmail.com','Kolkata','East','2024-01-20','Regular'),
('Chandrani_Paul','chandrani.paul@gmail.com','Patna','East','2024-02-08','Regular'),
('Subhro_Saha','subhro.saha@gmail.com','Kolkata','East','2024-03-25','VIP'),
('Pampa_Roy','pampa.roy@gmail.com','Bhubaneswar','East','2024-04-15','Regular'),
('Niloy_Chakraborty','niloy.chakraborty@gmail.com','Kolkata','East','2024-05-08','Regular'),
('Supriya_Maity','supriya.maity@gmail.com','Siliguri','East','2024-06-18','Regular'),
('Arnab_Biswas','arnab.biswas@gmail.com','Kolkata','East','2024-07-28','Regular'),
('Debarati_Majhi','debarati.majhi@gmail.com','Ranchi','East','2024-08-12','Regular'),
('Sahil_Khan','sahil.khan@gmail.com','Delhi','North','2024-01-05','Regular'),
('Fatima_Shaikh','fatima.shaikh@gmail.com','Mumbai','West','2024-02-15','Regular'),
('Rajesh_Nair','rajesh.nair@gmail.com','Bangalore','South','2024-03-08','Regular'),
('Asha_Ghosh','asha.ghosh@gmail.com','Kolkata','East','2024-04-22','Regular'),
('Mohan_Lal','mohan.lal@gmail.com','Delhi','North','2024-05-30','Regular'),
('Sunita_Devi','sunita.devi@gmail.com','Patna','East','2024-06-05','Regular'),
('Vinod_Sharma','vinod.sharma@gmail.com','Jaipur','North','2024-07-14','Regular'),
('Bhavna_Patel','bhavna.patel@gmail.com','Surat','West','2024-07-25','Regular'),
('Naveen_Gowda','naveen.gowda@gmail.com','Mysore','South','2024-08-02','Regular'),
('Shalini_Khanna','shalini.khanna@gmail.com','Noida','North','2024-08-18','Regular');

-- SELLERS (20 rows)
INSERT INTO sellers (seller_name, rating, total_products, established_date, user_id) VALUES
('TechZone Electronics',4.8,120,'2020-05-15',1),
('FashionFirst India',4.6,85,'2019-08-20',21),
('HomeDecor Plus',4.5,60,'2021-02-10',41),
('BooksWorld India',4.9,200,'2018-11-01',61),
('GadgetGuru Store',4.7,95,'2020-03-25',2),
('StyleHub Fashion',4.4,75,'2021-06-18',22),
('KitchenKing Supplies',4.6,50,'2019-09-12',42),
('ReadMore Books',4.8,180,'2018-07-08',62),
('SmartTech Solutions',4.5,110,'2020-11-30',3),
('TrendyWear Clothing',4.3,65,'2022-01-15',23),
('FurnitureMart Online',4.7,40,'2019-04-22',43),
('PageTurner Books',4.6,150,'2018-03-18',63),
('ElectroMart India',4.9,130,'2017-12-05',4),
('DesignerDen Fashion',4.5,90,'2021-09-10',24),
('HomeEssentials Store',4.4,55,'2020-07-20',44),
('AcademicBooks Hub',4.7,220,'2017-05-28',64),
('MobileZone India',4.8,100,'2019-01-14',5),
('EthnicWear Palace',4.6,80,'2020-10-08',25),
('ApplianceKing India',4.5,45,'2021-03-22',45),
('UrbanReads Books',4.8,160,'2018-09-15',65);

-- CATEGORIES (12 rows)
INSERT INTO categories (category_name, subcategory) VALUES
('Electronics','Smartphones'),('Electronics','Laptops'),('Electronics','Tablets'),
('Electronics','Accessories'),('Fashion','Men Clothing'),('Fashion','Women Clothing'),
('Fashion','Footwear'),('Home','Kitchen Appliances'),('Home','Furniture'),
('Home','Home Decor'),('Books','Academic'),('Books','Fiction');

-- PRODUCTS (50 rows - realistic INR pricing)
INSERT INTO products (product_name, category_id, seller_id, price, rating, stock, created_date) VALUES
('Samsung Galaxy S24 Ultra 256GB',1,1,109999.00,4.7,45,'2024-02-01'),
('Apple iPhone 15 128GB',1,17,79999.00,4.8,30,'2024-01-15'),
('OnePlus 12 256GB',1,5,64999.00,4.6,60,'2024-03-01'),
('Realme 12 Pro Plus 5G 256GB',1,13,27999.00,4.3,80,'2024-04-01'),
('Redmi Note 13 Pro 5G 128GB',1,5,19999.00,4.4,120,'2024-04-15'),
('Apple MacBook Air M2 8GB',2,1,114900.00,4.9,20,'2023-10-01'),
('Dell XPS 15 Core i7 16GB',2,9,149990.00,4.7,15,'2023-11-01'),
('HP Pavilion 15 Core i5 8GB',2,13,54999.00,4.4,35,'2024-01-10'),
('Lenovo IdeaPad Slim 5 Ryzen 5',2,9,48999.00,4.3,40,'2024-02-15'),
('ASUS VivoBook 15 Core i3',2,5,35990.00,4.2,50,'2024-03-10'),
('Apple iPad Air 5th Gen 64GB',3,1,59900.00,4.8,25,'2023-09-01'),
('Samsung Galaxy Tab S9 128GB',3,13,74999.00,4.6,18,'2024-01-05'),
('Redmi Pad Pro WiFi 128GB',3,17,22999.00,4.3,55,'2024-04-01'),
('Sony WH-1000XM5 Headphones',4,1,26990.00,4.8,70,'2023-08-01'),
('JBL Flip 6 Bluetooth Speaker',4,13,9999.00,4.5,90,'2023-10-15'),
('Anker PowerBank 20000mAh',4,9,2499.00,4.4,150,'2024-01-01'),
('boAt Rockerz 450 Headphones',4,17,1299.00,4.2,200,'2024-02-01'),
('Logitech MX Master 3S Mouse',4,5,9495.00,4.7,60,'2024-03-15'),
('Raymond Slim Fit Formal Shirt',5,6,1299.00,4.4,200,'2024-01-05'),
('Allen Solly Slim Fit Chinos',5,10,2499.00,4.3,150,'2024-02-01'),
('Levis 511 Slim Fit Jeans',5,14,3299.00,4.5,120,'2024-02-15'),
('Peter England Formal Suit',5,6,6999.00,4.4,80,'2024-03-01'),
('US Polo Assn Polo T-Shirt',5,2,1499.00,4.3,250,'2024-03-15'),
('Biba Anarkali Kurta Set',6,18,2499.00,4.6,100,'2024-01-10'),
('W for Woman Straight Kurta',6,2,1799.00,4.4,150,'2024-02-05'),
('Banarasi Silk Saree with Blouse',6,18,4999.00,4.7,60,'2024-02-20'),
('FabIndia Cotton Salwar Suit',6,6,3499.00,4.5,90,'2024-03-05'),
('Nike Air Max 270 Men Shoes',7,10,8995.00,4.6,80,'2024-01-20'),
('Adidas Ultraboost 22 Men',7,14,12995.00,4.7,55,'2024-02-10'),
('Metro Shoes Formal Derby Men',7,2,2499.00,4.3,100,'2024-03-01'),
('Bata Ladies Block Heels',7,6,1799.00,4.2,120,'2024-03-20'),
('Instant Pot Duo 7-in-1',8,3,8999.00,4.7,40,'2024-01-08'),
('Prestige SS Pressure Cooker 5L',8,7,2499.00,4.5,100,'2024-01-25'),
('Philips Air Fryer HD9200 2.75L',8,15,6499.00,4.6,60,'2024-02-08'),
('IFB 30L Convection Microwave',8,19,14999.00,4.4,30,'2024-02-25'),
('Lifelong Mixer Grinder 500W',8,7,2799.00,4.3,80,'2024-03-12'),
('IKEA LACK Coffee Table',9,11,4999.00,4.3,20,'2024-01-12'),
('Solid Wood Study Desk',9,3,8499.00,4.5,15,'2024-02-12'),
('Nilkamal Plastic Chair Set of 4',9,11,3499.00,4.2,25,'2024-03-08'),
('Wakefit Memory Foam Mattress Queen',9,15,14999.00,4.7,10,'2024-03-25'),
('Asian Paints Royale Atmos 20L',10,3,5499.00,4.4,50,'2024-01-18'),
('Bombay Dyeing Cotton Bed Sheet',10,7,1299.00,4.3,150,'2024-02-18'),
('WallMantra Motivational Wall Art',10,11,799.00,4.1,200,'2024-03-18'),
('NCERT Mathematics Class 12',11,4,399.00,4.8,300,'2024-01-02'),
('Data Structures Made Easy',11,8,499.00,4.7,200,'2024-01-20'),
('CA Foundation Study Material',11,12,1299.00,4.6,150,'2024-02-02'),
('GATE 2025 Computer Science',11,16,699.00,4.5,180,'2024-02-20'),
('The God of Small Things',12,20,299.00,4.8,250,'2024-01-05'),
('Malgudi Days RK Narayan',12,4,199.00,4.7,300,'2024-01-22'),
('The Palace of Illusions',12,8,349.00,4.6,220,'2024-02-08');

-- ORDERS (155 rows - ~60% COD, ~20% UPI, ~20% Cards/Wallet)
INSERT INTO orders (user_id, order_date, total_amount, payment_method, order_status, region) VALUES
(1,'2026-03-01',109999.00,'Credit Card','Delivered','North'),
(2,'2026-03-02',27999.00,'COD','Delivered','North'),
(3,'2026-03-03',2499.00,'UPI','Delivered','North'),
(4,'2026-03-04',19999.00,'COD','Delivered','North'),
(5,'2026-03-05',79999.00,'Debit Card','Delivered','North'),
(6,'2026-03-06',1299.00,'COD','Delivered','North'),
(7,'2026-03-07',114900.00,'Credit Card','Delivered','North'),
(8,'2026-03-08',6999.00,'COD','Delivered','North'),
(9,'2026-03-09',3498.00,'COD','Delivered','North'),
(10,'2026-03-10',54999.00,'UPI','Delivered','North'),
(21,'2026-03-01',64999.00,'UPI','Delivered','South'),
(22,'2026-03-02',26990.00,'Credit Card','Delivered','South'),
(23,'2026-03-03',1799.00,'COD','Delivered','South'),
(24,'2026-03-04',22999.00,'COD','Delivered','South'),
(25,'2026-03-05',9999.00,'UPI','Delivered','South'),
(26,'2026-03-06',2598.00,'COD','Delivered','South'),
(27,'2026-03-07',74999.00,'Credit Card','Delivered','South'),
(28,'2026-03-08',4999.00,'COD','Delivered','South'),
(29,'2026-03-09',14999.00,'COD','Cancelled','South'),
(30,'2026-03-10',12995.00,'UPI','Delivered','South'),
(41,'2026-03-01',109999.00,'COD','Delivered','West'),
(42,'2026-03-02',8999.00,'COD','Delivered','West'),
(43,'2026-03-03',5499.00,'UPI','Delivered','West'),
(44,'2026-03-04',3499.00,'COD','Delivered','West'),
(45,'2026-03-05',79999.00,'Debit Card','Delivered','West'),
(46,'2026-03-06',799.00,'COD','Delivered','West'),
(47,'2026-03-07',2499.00,'COD','Delivered','West'),
(48,'2026-03-08',14999.00,'COD','Delivered','West'),
(49,'2026-03-09',8499.00,'COD','Delivered','West'),
(50,'2026-03-10',59900.00,'Credit Card','Delivered','West'),
(61,'2026-03-01',399.00,'COD','Delivered','East'),
(62,'2026-03-02',199.00,'COD','Delivered','East'),
(63,'2026-03-03',499.00,'UPI','Delivered','East'),
(64,'2026-03-04',1299.00,'COD','Delivered','East'),
(65,'2026-03-05',699.00,'COD','Delivered','East'),
(66,'2026-03-06',349.00,'COD','Delivered','East'),
(67,'2026-03-07',299.00,'COD','Delivered','East'),
(68,'2026-03-08',499.00,'COD','Delivered','East'),
(69,'2026-03-09',199.00,'COD','Delivered','East'),
(70,'2026-03-10',1299.00,'UPI','Delivered','East'),
(11,'2026-04-01',48999.00,'COD','Delivered','North'),
(12,'2026-04-02',35990.00,'COD','Delivered','North'),
(13,'2026-04-03',1499.00,'COD','Delivered','North'),
(14,'2026-04-04',3299.00,'COD','Delivered','North'),
(15,'2026-04-05',6999.00,'UPI','Delivered','North'),
(16,'2026-04-06',2598.00,'COD','Delivered','North'),
(17,'2026-04-07',1299.00,'COD','Delivered','North'),
(18,'2026-04-08',9495.00,'Wallet','Delivered','North'),
(19,'2026-04-09',26990.00,'Credit Card','Delivered','North'),
(20,'2026-04-10',2499.00,'COD','Delivered','North'),
(31,'2026-04-01',8995.00,'UPI','Delivered','South'),
(32,'2026-04-02',12995.00,'Credit Card','Delivered','South'),
(33,'2026-04-03',2499.00,'COD','Delivered','South'),
(34,'2026-04-04',1799.00,'COD','Delivered','South'),
(35,'2026-04-05',4999.00,'COD','Delivered','South'),
(36,'2026-04-06',6499.00,'COD','Delivered','South'),
(37,'2026-04-07',14999.00,'COD','Delivered','South'),
(38,'2026-04-08',3499.00,'COD','Delivered','South'),
(39,'2026-04-09',2799.00,'COD','Delivered','South'),
(40,'2026-04-10',1299.00,'COD','Delivered','South'),
(51,'2026-04-01',6499.00,'COD','Returned','West'),
(52,'2026-04-02',2499.00,'COD','Delivered','West'),
(53,'2026-04-03',8995.00,'UPI','Delivered','West'),
(54,'2026-04-04',1299.00,'COD','Delivered','West'),
(55,'2026-04-05',14999.00,'Debit Card','Delivered','West'),
(56,'2026-04-06',1799.00,'COD','Delivered','West'),
(57,'2026-04-07',3499.00,'COD','Delivered','West'),
(58,'2026-04-08',2499.00,'COD','Delivered','West'),
(59,'2026-04-09',4999.00,'COD','Delivered','West'),
(60,'2026-04-10',799.00,'COD','Delivered','West'),
(71,'2026-04-01',499.00,'COD','Delivered','East'),
(72,'2026-04-02',1299.00,'COD','Delivered','East'),
(73,'2026-04-03',699.00,'COD','Delivered','East'),
(74,'2026-04-04',299.00,'COD','Delivered','East'),
(75,'2026-04-05',349.00,'COD','Delivered','East'),
(76,'2026-04-06',199.00,'COD','Delivered','East'),
(77,'2026-04-07',1299.00,'UPI','Delivered','East'),
(78,'2026-04-08',499.00,'COD','Delivered','East'),
(79,'2026-04-09',399.00,'COD','Delivered','East'),
(80,'2026-04-10',699.00,'COD','Delivered','East'),
(1,'2026-05-01',79999.00,'Credit Card','Delivered','North'),
(5,'2026-05-02',64999.00,'UPI','Delivered','North'),
(7,'2026-05-03',149990.00,'Credit Card','Delivered','North'),
(21,'2026-05-04',109999.00,'Debit Card','Delivered','South'),
(28,'2026-05-05',59900.00,'Credit Card','Delivered','South'),
(34,'2026-05-06',26990.00,'UPI','Delivered','South'),
(41,'2026-05-07',114900.00,'Credit Card','Shipped','West'),
(49,'2026-05-08',74999.00,'Debit Card','Delivered','West'),
(61,'2026-05-09',2499.00,'COD','Delivered','East'),
(75,'2026-05-10',3299.00,'COD','Delivered','East'),
(2,'2026-06-01',19999.00,'COD','Delivered','North'),
(10,'2026-06-02',27999.00,'COD','Delivered','North'),
(15,'2026-06-03',9999.00,'UPI','Delivered','North'),
(22,'2026-06-04',22999.00,'COD','Delivered','South'),
(30,'2026-06-05',8995.00,'UPI','Delivered','South'),
(35,'2026-06-06',6499.00,'COD','Delivered','South'),
(42,'2026-06-07',8999.00,'COD','Delivered','West'),
(50,'2026-06-08',2499.00,'COD','Delivered','West'),
(55,'2026-06-09',4999.00,'COD','Delivered','West'),
(62,'2026-06-10',499.00,'COD','Delivered','East'),
(68,'2026-06-11',1299.00,'COD','Delivered','East'),
(73,'2026-06-12',699.00,'COD','Delivered','East'),
(3,'2026-07-01',48999.00,'COD','Delivered','North'),
(6,'2026-07-02',1299.00,'COD','Delivered','North'),
(11,'2026-07-03',35990.00,'UPI','Delivered','North'),
(23,'2026-07-04',12995.00,'COD','Delivered','South'),
(27,'2026-07-05',9495.00,'UPI','Delivered','South'),
(36,'2026-07-06',2499.00,'COD','Delivered','South'),
(43,'2026-07-07',3499.00,'COD','Delivered','West'),
(52,'2026-07-08',14999.00,'COD','Delivered','West'),
(57,'2026-07-09',5499.00,'COD','Delivered','West'),
(63,'2026-07-10',399.00,'COD','Delivered','East'),
(69,'2026-07-11',199.00,'COD','Delivered','East'),
(76,'2026-07-12',299.00,'COD','Delivered','East'),
(1,'2026-08-01',26990.00,'Credit Card','Delivered','North'),
(4,'2026-08-02',6999.00,'COD','Delivered','North'),
(8,'2026-08-03',3299.00,'COD','Delivered','North'),
(21,'2026-08-04',1299.00,'COD','Delivered','South'),
(25,'2026-08-05',8999.00,'COD','Delivered','South'),
(33,'2026-08-06',4999.00,'COD','Delivered','South'),
(41,'2026-08-07',2499.00,'COD','Delivered','West'),
(46,'2026-08-08',799.00,'COD','Delivered','West'),
(54,'2026-08-09',1799.00,'COD','Delivered','West'),
(61,'2026-08-10',699.00,'COD','Delivered','East'),
(67,'2026-08-11',349.00,'COD','Delivered','East'),
(72,'2026-08-12',1299.00,'UPI','Delivered','East'),
(81,'2026-08-13',19999.00,'COD','Shipped','North'),
(82,'2026-08-14',9999.00,'UPI','Delivered','West'),
(83,'2026-08-15',2499.00,'COD','Delivered','South'),
(84,'2026-08-16',699.00,'COD','Delivered','East'),
(85,'2026-08-17',1299.00,'COD','Delivered','North'),
(86,'2026-08-18',64999.00,'Debit Card','Delivered','South'),
(87,'2026-08-19',3499.00,'COD','Delivered','West'),
(88,'2026-08-20',499.00,'COD','Delivered','East'),
(89,'2026-08-21',79999.00,'Credit Card','Confirmed','North'),
(90,'2026-08-22',14999.00,'COD','Pending','West'),
(91,'2026-08-22',26990.00,'UPI','Delivered','South'),
(92,'2026-08-23',8995.00,'Wallet','Delivered','East'),
(93,'2026-08-23',35990.00,'COD','Shipped','North'),
(94,'2026-08-24',2499.00,'COD','Delivered','West'),
(95,'2026-08-24',12995.00,'Credit Card','Delivered','South');

-- ORDER_ITEMS (50 rows)
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
(1,1,1,109999.00),(2,4,1,27999.00),(3,20,1,2499.00),(4,5,1,19999.00),(5,2,1,79999.00),
(6,17,1,1299.00),(7,6,1,114900.00),(8,22,1,6999.00),(9,25,2,1799.00),(10,8,1,54999.00),
(11,3,1,64999.00),(12,14,1,26990.00),(13,25,1,1799.00),(14,13,1,22999.00),(15,15,1,9999.00),
(16,19,2,1299.00),(17,12,1,74999.00),(18,24,1,4999.00),(19,35,1,14999.00),(20,29,1,12995.00),
(21,1,1,109999.00),(22,32,1,8999.00),(23,40,1,5499.00),(24,37,1,3499.00),(25,2,1,79999.00),
(26,42,1,799.00),(27,21,1,2499.00),(28,35,1,14999.00),(29,38,1,8499.00),(30,11,1,59900.00),
(31,44,1,399.00),(32,50,1,199.00),(33,45,1,499.00),(34,46,1,1299.00),(35,47,1,699.00),
(36,48,1,349.00),(37,49,1,299.00),(38,45,1,499.00),(39,50,1,199.00),(40,47,2,699.00),
(41,9,1,48999.00),(42,10,1,35990.00),(43,23,1,1499.00),(44,21,1,3299.00),(45,22,1,6999.00),
(46,19,2,1299.00),(47,17,1,1299.00),(48,18,1,9495.00),(49,14,1,26990.00),(50,27,1,2499.00);

-- REVIEWS (50 rows)
INSERT INTO reviews (product_id, user_id, rating, review_text, review_date) VALUES
(1,1,5,'Excellent camera and performance! Worth every rupee.','2026-03-15'),
(2,5,5,'iPhone quality is unmatched. Face ID is super fast.','2026-03-20'),
(3,21,4,'Great phone for the price. OxygenOS is smooth.','2026-03-18'),
(4,22,4,'Good value for money. Camera could be better.','2026-03-22'),
(5,2,4,'Excellent budget phone. Battery life is amazing.','2026-03-25'),
(6,7,5,'M2 chip is blazing fast. Battery lasts all day.','2026-04-05'),
(7,10,5,'Best laptop I have owned. Display is gorgeous.','2026-04-10'),
(8,11,4,'Good performance for college use. Slightly heavy.','2026-04-15'),
(9,12,4,'Ryzen 5 is powerful. Good value for money.','2026-04-18'),
(10,13,3,'Average performance. Heats up under load.','2026-04-20'),
(11,30,5,'iPad is perfect for design work. Pencil support is great.','2026-04-22'),
(12,24,4,'Samsung tablet with great display. Android experience.','2026-04-25'),
(13,14,4,'Good budget tablet. Perfect for students.','2026-04-28'),
(14,1,5,'Sony noise cancellation is best in class!','2026-05-02'),
(15,23,4,'JBL speaker sounds amazing outdoors.','2026-05-05'),
(16,9,4,'Anker power bank charges my phone 4 times. Great!','2026-05-08'),
(17,4,3,'Decent headphones for the price. Bass is ok.','2026-05-10'),
(18,15,5,'MX Master 3S is the best productivity mouse ever.','2026-05-12'),
(19,6,4,'Good formal shirt. Fabric quality is nice.','2026-05-15'),
(20,16,4,'Comfortable trousers. Fit is slim and stylish.','2026-05-18'),
(21,17,5,'Levis quality is always top notch.','2026-05-20'),
(22,8,4,'Nice formal suit at this price. Stitching is good.','2026-05-22'),
(23,18,4,'Polo shirts are very comfortable.','2026-05-25'),
(24,22,5,'Biba kurta quality is fantastic. Loved the design.','2026-05-28'),
(25,3,4,'Good value kurta. Accurate sizing.','2026-06-01'),
(26,23,5,'Beautiful Banarasi saree. Very authentic.','2026-06-03'),
(27,24,5,'FabIndia cotton quality is always reliable.','2026-06-05'),
(28,25,4,'Nike Air Max is very comfortable for daily wear.','2026-06-08'),
(29,26,5,'Adidas Ultraboost comfort is unreal!','2026-06-10'),
(30,27,3,'Metro shoes are ok but sole could be better.','2026-06-12'),
(31,28,3,'Heels look nice but not very comfortable.','2026-06-15'),
(32,29,5,'Instant Pot changed my cooking life!','2026-06-18'),
(33,30,4,'Prestige cooker is very durable.','2026-06-20'),
(34,31,5,'Philips Air Fryer makes crispy snacks with less oil.','2026-06-22'),
(35,32,4,'IFB microwave is spacious and heats evenly.','2026-06-25'),
(36,33,4,'Lifelong mixer is solid for daily use.','2026-06-28'),
(37,41,4,'IKEA coffee table looks stylish. Easy to assemble.','2026-07-01'),
(38,42,4,'Study desk has good finish and sturdy build.','2026-07-03'),
(39,43,3,'Nilkamal chairs are functional but basic.','2026-07-05'),
(40,44,5,'Wakefit mattress has transformed my sleep quality!','2026-07-08'),
(41,45,4,'Asian Paints is good quality and long lasting.','2026-07-10'),
(42,46,4,'Bombay Dyeing sheets are very soft and comfortable.','2026-07-12'),
(43,47,3,'Wall art looks ok but printing could be sharper.','2026-07-15'),
(44,61,5,'NCERT books are the best for board exam prep.','2026-07-18'),
(45,62,5,'Narasimha Karumanchi explains DSA brilliantly.','2026-07-20'),
(46,63,4,'Good study material for CA Foundation.','2026-07-22'),
(47,64,4,'GATE book covers all topics well.','2026-07-25'),
(48,65,5,'God of Small Things is a literary masterpiece.','2026-07-28'),
(49,66,5,'Malgudi Days is timeless Indian literature.','2026-08-01'),
(50,67,4,'Palace of Illusions retells Mahabharata beautifully.','2026-08-03');

-- RETURNS (20 rows)
INSERT INTO returns (order_id, product_id, return_date, reason, status) VALUES
(29,35,'2026-03-15','Product not as described','Completed'),
(51,34,'2026-04-08','Defective product','Completed'),
(19,35,'2026-03-16','Wrong item delivered','Completed'),
(9,25,'2026-03-15','Size not fitting','Completed'),
(74,49,'2026-04-10','Better price available elsewhere','Rejected'),
(16,19,'2026-04-12','Changed mind','Approved'),
(46,42,'2026-03-12','Product damaged during delivery','Completed'),
(26,19,'2026-03-10','Quality not as expected','Completed'),
(76,50,'2026-04-12','Duplicate order placed','Completed'),
(36,47,'2026-04-18','Product expired','Approved'),
(3,20,'2026-03-09','Fabric defect','Completed'),
(39,50,'2026-04-15','Wrong book edition delivered','Completed'),
(67,49,'2026-04-14','Book pages torn','Completed'),
(13,25,'2026-03-10','Colour different from website','Approved'),
(23,1,'2026-03-09','Mobile overheating issue','Rejected'),
(48,18,'2026-04-14','Mouse left click not working','Completed'),
(28,24,'2026-03-14','Saree colour faded after first wash','Completed'),
(43,37,'2026-03-11','Furniture piece missing','Completed'),
(60,42,'2026-04-16','Sheet tore after first use','Approved'),
(35,37,'2026-04-11','Table surface scratched in transit','Completed');
"""

# ─────────────────────────────────────────────────────────────────────────────
# FILE 3: QUERIES.SQL
# ─────────────────────────────────────────────────────────────────────────────
QUERIES_SQL = """\
-- =============================================================================
-- Flipkart Analytics Hub - 15 Advanced Analytical SQL Queries
-- =============================================================================
USE flipkart_analytics;

-- QUERY 1: Top 10 Customers by Total Spending
-- Identifies highest-value customers by summing all delivered orders.
SELECT
    u.user_id, u.username, u.city, u.region, u.user_type,
    COUNT(o.order_id)            AS total_orders,
    ROUND(SUM(o.total_amount),2) AS total_spending,
    ROUND(AVG(o.total_amount),2) AS avg_order_value,
    MAX(o.order_date)            AS last_order_date
FROM users u
JOIN orders o ON u.user_id = o.user_id
WHERE o.order_status = 'Delivered'
GROUP BY u.user_id, u.username, u.city, u.region, u.user_type
ORDER BY total_spending DESC LIMIT 10;

-- QUERY 2: Best-Selling Products by Category
-- Uses RANK() window function with PARTITION BY for in-category ranking.
SELECT
    c.category_name, c.subcategory, p.product_name,
    SUM(oi.quantity)                           AS units_sold,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_revenue,
    RANK() OVER (PARTITION BY c.category_name ORDER BY SUM(oi.quantity) DESC) AS category_rank
FROM products p
JOIN categories  c  ON p.category_id = c.category_id
JOIN order_items oi ON p.product_id  = oi.product_id
JOIN orders      o  ON oi.order_id   = o.order_id
WHERE o.order_status IN ('Delivered','Shipped')
GROUP BY c.category_name, c.subcategory, p.product_id, p.product_name
ORDER BY c.category_name, category_rank;

-- QUERY 3: Payment Method Preferences (with Percentages)
-- COD dominance (~60%) typical in Indian e-commerce.
SELECT
    payment_method,
    COUNT(*)                                                              AS order_count,
    ROUND(SUM(total_amount),2)                                            AS total_revenue,
    ROUND(COUNT(*)*100.0/SUM(COUNT(*)) OVER (),2)                         AS order_pct,
    ROUND(SUM(total_amount)*100.0/SUM(SUM(total_amount)) OVER (),2)       AS revenue_pct,
    ROUND(AVG(total_amount),2)                                            AS avg_order_value
FROM orders GROUP BY payment_method ORDER BY order_count DESC;

-- QUERY 4: Regional Sales Performance
SELECT
    o.region,
    COUNT(DISTINCT o.order_id)                                               AS total_orders,
    COUNT(DISTINCT o.user_id)                                                AS unique_customers,
    ROUND(SUM(o.total_amount),2)                                             AS total_revenue,
    ROUND(AVG(o.total_amount),2)                                             AS avg_order_value,
    ROUND(SUM(o.total_amount)*100.0/SUM(SUM(o.total_amount)) OVER (),2)     AS revenue_share_pct
FROM orders o
WHERE o.order_status NOT IN ('Cancelled','Returned')
GROUP BY o.region ORDER BY total_revenue DESC;

-- QUERY 5: Top Sellers by Rating and Revenue (Composite Score)
SELECT
    s.seller_id, s.seller_name, s.rating AS seller_rating, s.total_products,
    COUNT(DISTINCT oi.order_id)                  AS total_orders_fulfilled,
    ROUND(SUM(oi.quantity*oi.unit_price),2)       AS gross_revenue,
    ROUND(AVG(oi.unit_price),2)                   AS avg_selling_price,
    ROUND((s.rating/5.0)*0.4 +
          (SUM(oi.quantity*oi.unit_price)/MAX(SUM(oi.quantity*oi.unit_price)) OVER ())*0.6,4)
                                                  AS composite_score
FROM sellers s
JOIN products p     ON s.seller_id  = p.seller_id
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o       ON oi.order_id  = o.order_id
WHERE o.order_status IN ('Delivered','Shipped')
GROUP BY s.seller_id, s.seller_name, s.rating, s.total_products
ORDER BY composite_score DESC;

-- QUERY 6: Product Return Analysis and Return Rates
-- Flags products with >15% return rate as HIGH RISK.
SELECT
    p.product_id, p.product_name, c.category_name,
    COUNT(DISTINCT oi.order_id)  AS total_orders,
    COUNT(DISTINCT r.return_id)  AS total_returns,
    ROUND(COUNT(DISTINCT r.return_id)*100.0/NULLIF(COUNT(DISTINCT oi.order_id),0),2) AS return_rate_pct,
    GROUP_CONCAT(DISTINCT r.reason ORDER BY r.return_id SEPARATOR ' | ') AS return_reasons,
    CASE
        WHEN COUNT(DISTINCT r.return_id)*100.0/NULLIF(COUNT(DISTINCT oi.order_id),0) > 15
             THEN 'HIGH RISK - Review Needed'
        WHEN COUNT(DISTINCT r.return_id)*100.0/NULLIF(COUNT(DISTINCT oi.order_id),0) > 5
             THEN 'MODERATE - Monitor'
        ELSE 'HEALTHY'
    END AS return_health_flag
FROM products p
JOIN categories  c   ON p.category_id = c.category_id
JOIN order_items oi  ON p.product_id  = oi.product_id
LEFT JOIN returns r  ON oi.order_id   = r.order_id AND oi.product_id = r.product_id
GROUP BY p.product_id, p.product_name, c.category_name
HAVING total_orders > 0 ORDER BY return_rate_pct DESC;

-- QUERY 7: Customer Lifetime Value - RFM Analysis
-- NTILE(5) segments customers into Champion, Loyal, Potential, At Risk, Lost.
WITH rfm_raw AS (
    SELECT u.user_id, u.username, u.city, u.user_type,
           DATEDIFF(CURDATE(), MAX(o.order_date)) AS recency_days,
           COUNT(o.order_id)                       AS frequency,
           ROUND(SUM(o.total_amount),2)            AS monetary
    FROM users u JOIN orders o ON u.user_id = o.user_id
    WHERE o.order_status = 'Delivered'
    GROUP BY u.user_id, u.username, u.city, u.user_type
),
rfm_scores AS (
    SELECT *, NTILE(5) OVER (ORDER BY recency_days ASC)  AS r_score,
              NTILE(5) OVER (ORDER BY frequency DESC)     AS f_score,
              NTILE(5) OVER (ORDER BY monetary DESC)      AS m_score
    FROM rfm_raw
)
SELECT user_id, username, city, user_type, recency_days, frequency, monetary,
       r_score, f_score, m_score,
       ROUND((r_score+f_score+m_score)/3.0,2) AS rfm_avg_score,
       CASE WHEN (r_score+f_score+m_score) >= 13 THEN 'Champion'
            WHEN (r_score+f_score+m_score) >= 10 THEN 'Loyal Customer'
            WHEN (r_score+f_score+m_score) >= 7  THEN 'Potential Loyalist'
            WHEN r_score <= 2                     THEN 'At Risk'
            ELSE 'Lost Customer' END AS customer_segment
FROM rfm_scores ORDER BY rfm_avg_score DESC;

-- QUERY 8: Monthly Revenue Trends
-- LAG() for MoM growth; cumulative SUM OVER UNBOUNDED PRECEDING.
WITH monthly AS (
    SELECT DATE_FORMAT(order_date,'%Y-%m') AS order_month,
           COUNT(order_id)                 AS orders_placed,
           ROUND(SUM(total_amount),2)      AS monthly_revenue,
           COUNT(DISTINCT user_id)         AS unique_customers
    FROM orders WHERE order_status NOT IN ('Cancelled','Returned')
    GROUP BY DATE_FORMAT(order_date,'%Y-%m')
)
SELECT order_month, orders_placed, monthly_revenue, unique_customers,
       LAG(monthly_revenue) OVER (ORDER BY order_month) AS prev_month_revenue,
       ROUND((monthly_revenue - LAG(monthly_revenue) OVER (ORDER BY order_month))*100.0
             /NULLIF(LAG(monthly_revenue) OVER (ORDER BY order_month),0),2) AS mom_growth_pct,
       ROUND(SUM(monthly_revenue) OVER (ORDER BY order_month ROWS UNBOUNDED PRECEDING),2) AS cumulative_revenue
FROM monthly ORDER BY order_month;

-- QUERY 9: Churn Analysis - Customers with No Purchase in 60 Days
SELECT u.user_id, u.username, u.email, u.city, u.region, u.user_type,
       MAX(o.order_date)                      AS last_purchase_date,
       DATEDIFF(CURDATE(),MAX(o.order_date))  AS days_since_last_purchase,
       COUNT(o.order_id)                      AS lifetime_orders,
       ROUND(SUM(o.total_amount),2)           AS lifetime_value,
       CASE WHEN DATEDIFF(CURDATE(),MAX(o.order_date)) BETWEEN 60 AND 90   THEN 'Early Churn Risk'
            WHEN DATEDIFF(CURDATE(),MAX(o.order_date)) BETWEEN 91 AND 180  THEN 'Churning'
            ELSE 'Churned' END AS churn_status
FROM users u JOIN orders o ON u.user_id = o.user_id
GROUP BY u.user_id, u.username, u.email, u.city, u.region, u.user_type
HAVING days_since_last_purchase >= 60
ORDER BY days_since_last_purchase DESC;

-- QUERY 10: Category Performance Metrics
SELECT c.category_name, c.subcategory,
       COUNT(DISTINCT p.product_id)               AS product_count,
       SUM(oi.quantity)                           AS units_sold,
       ROUND(SUM(oi.quantity*oi.unit_price),2)    AS gross_revenue,
       ROUND(AVG(p.price),2)                      AS avg_product_price,
       ROUND(AVG(p.rating),2)                     AS avg_product_rating,
       COUNT(DISTINCT r.return_id)                AS total_returns,
       ROUND(COUNT(DISTINCT r.return_id)*100.0/NULLIF(SUM(oi.quantity),0),2) AS return_rate_pct
FROM categories c
JOIN products p     ON c.category_id = p.category_id
JOIN order_items oi ON p.product_id  = oi.product_id
JOIN orders o       ON oi.order_id   = o.order_id
LEFT JOIN returns r ON o.order_id    = r.order_id AND p.product_id = r.product_id
WHERE o.order_status NOT IN ('Cancelled')
GROUP BY c.category_name, c.subcategory ORDER BY gross_revenue DESC;

-- QUERY 11: Festival Season Sales Patterns
-- Tags months: Diwali, Big Billion Days, Republic Day Sale, Holi, etc.
SELECT DATE_FORMAT(o.order_date,'%Y-%m') AS sale_month,
       MONTHNAME(o.order_date) AS month_name,
       COUNT(o.order_id) AS total_orders, ROUND(SUM(o.total_amount),2) AS total_revenue,
       COUNT(DISTINCT o.user_id) AS active_customers, ROUND(AVG(o.total_amount),2) AS avg_order_value,
       CASE MONTH(o.order_date)
           WHEN 1  THEN 'Republic Day Sale'
           WHEN 2  THEN 'Valentine Sale'
           WHEN 3  THEN 'Holi Sale'
           WHEN 8  THEN 'Independence Day Sale'
           WHEN 10 THEN 'Navratri / Big Billion Days'
           WHEN 11 THEN 'Diwali / Dhanteras'
           WHEN 12 THEN 'End of Season Sale'
           ELSE         'Regular Month'
       END AS festival_tag
FROM orders o WHERE o.order_status NOT IN ('Cancelled','Returned')
GROUP BY sale_month, month_name, MONTH(o.order_date) ORDER BY sale_month;

-- QUERY 12: Payment Method Distribution by Region
-- PARTITION BY region gives within-group percentage.
SELECT region, payment_method, COUNT(*) AS order_count,
       ROUND(SUM(total_amount),2) AS revenue,
       ROUND(COUNT(*)*100.0/SUM(COUNT(*)) OVER (PARTITION BY region),2) AS pct_within_region
FROM orders GROUP BY region, payment_method ORDER BY region, order_count DESC;

-- QUERY 13: Seller Reliability Score (Weighted 0-100)
WITH seller_stats AS (
    SELECT s.seller_id, s.seller_name, s.rating AS platform_rating,
           COUNT(DISTINCT o.order_id) AS total_orders,
           COUNT(DISTINCT CASE WHEN o.order_status='Cancelled' THEN o.order_id END) AS cancelled_orders,
           COUNT(DISTINCT CASE WHEN o.order_status='Returned'  THEN o.order_id END) AS returned_orders,
           COUNT(DISTINCT rv.review_id) AS review_count,
           ROUND(AVG(rv.rating),2) AS avg_review_rating
    FROM sellers s
    JOIN products p      ON s.seller_id  = p.seller_id
    JOIN order_items oi  ON p.product_id = oi.product_id
    JOIN orders o        ON oi.order_id  = o.order_id
    LEFT JOIN reviews rv ON p.product_id = rv.product_id
    GROUP BY s.seller_id, s.seller_name, s.rating
)
SELECT seller_id, seller_name, platform_rating, total_orders,
       cancelled_orders, returned_orders, review_count,
       COALESCE(avg_review_rating,0) AS avg_review_rating,
       ROUND(cancelled_orders*100.0/NULLIF(total_orders,0),2) AS cancel_rate_pct,
       ROUND(returned_orders *100.0/NULLIF(total_orders,0),2) AS return_rate_pct,
       ROUND((COALESCE(avg_review_rating,3)/5.0*40) +
             ((1-cancelled_orders/NULLIF(total_orders,1))*30) +
             ((1-returned_orders /NULLIF(total_orders,1))*20) +
             (platform_rating/5.0*10), 2) AS reliability_score
FROM seller_stats ORDER BY reliability_score DESC;

-- QUERY 14: Customer Acquisition Cost Analysis
-- FIRST_VALUE() + chained CTEs to classify conversion speed.
WITH first_orders AS (
    SELECT user_id, MIN(order_date) AS first_order_date,
           FIRST_VALUE(total_amount) OVER (PARTITION BY user_id ORDER BY order_date) AS first_order_value
    FROM orders WHERE order_status='Delivered' GROUP BY user_id, order_date, total_amount
),
customer_summary AS (
    SELECT u.user_id, u.username, u.user_type, u.signup_date,
           f.first_order_date, f.first_order_value,
           DATEDIFF(f.first_order_date, u.signup_date) AS days_to_first_purchase,
           COUNT(o.order_id) AS total_orders, ROUND(SUM(o.total_amount),2) AS total_clv
    FROM users u JOIN first_orders f ON u.user_id=f.user_id
    JOIN orders o ON u.user_id=o.user_id WHERE o.order_status='Delivered'
    GROUP BY u.user_id, u.username, u.user_type, u.signup_date, f.first_order_date, f.first_order_value
)
SELECT user_id, username, user_type, signup_date, first_order_date,
       days_to_first_purchase, first_order_value, total_orders, total_clv,
       ROUND(total_clv/NULLIF(total_orders,0),2) AS avg_order_value,
       CASE WHEN days_to_first_purchase <= 7  THEN 'Instant Converter'
            WHEN days_to_first_purchase <= 30 THEN 'Quick Converter'
            WHEN days_to_first_purchase <= 90 THEN 'Slow Converter'
            ELSE 'Long-term Nurture' END AS acquisition_type
FROM customer_summary ORDER BY total_clv DESC;

-- QUERY 15: Inventory Health Check
-- FIELD() for priority-based sort; stock velocity = units sold / 24 weeks.
WITH product_sales AS (
    SELECT p.product_id, p.product_name, p.price, p.stock AS current_stock, p.rating,
           c.category_name, s.seller_name,
           COALESCE(SUM(oi.quantity),0)   AS total_units_sold,
           COUNT(DISTINCT oi.order_id)    AS total_orders
    FROM products p
    JOIN categories c    ON p.category_id = c.category_id
    JOIN sellers s       ON p.seller_id   = s.seller_id
    LEFT JOIN order_items oi ON p.product_id = oi.product_id
    LEFT JOIN orders o   ON oi.order_id=o.order_id AND o.order_status IN ('Delivered','Shipped')
    GROUP BY p.product_id,p.product_name,p.price,p.stock,p.rating,c.category_name,s.seller_name
)
SELECT product_id, product_name, category_name, seller_name, price,
       current_stock, total_units_sold, total_orders, rating,
       ROUND(current_stock/NULLIF(total_units_sold/24.0,0),1) AS estimated_weeks_of_stock,
       CASE WHEN current_stock=0                             THEN 'OUT OF STOCK'
            WHEN current_stock<=10 AND total_units_sold>5   THEN 'CRITICAL - Reorder Now'
            WHEN current_stock<=30 AND total_units_sold>10  THEN 'LOW STOCK - Monitor'
            WHEN current_stock>100 AND total_units_sold<2   THEN 'OVERSTOCKED - Review'
            ELSE 'HEALTHY' END AS stock_health,
       ROUND(current_stock*price,2) AS inventory_value_inr
FROM product_sales
ORDER BY FIELD(stock_health,'OUT OF STOCK','CRITICAL - Reorder Now','LOW STOCK - Monitor','OVERSTOCKED - Review','HEALTHY'),
         total_units_sold DESC;
"""

# ─────────────────────────────────────────────────────────────────────────────
# FILE 4: README.MD
# ─────────────────────────────────────────────────────────────────────────────
README_MD = """\
# Flipkart Analytics Hub - SQL Portfolio Project

[![SQL](https://img.shields.io/badge/SQL-MySQL%208.0-blue?style=flat-square&logo=mysql)](https://www.mysql.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen?style=flat-square)]()
[![Queries](https://img.shields.io/badge/Analytical%20Queries-15-orange?style=flat-square)]()

> A complete, production-ready SQL analytics project modelled on an Indian e-commerce marketplace.  
> 8-table schema · 155+ realistic orders · 15 advanced analytical queries

---

## Project Overview

| Metric | Value |
|--------|-------|
| Users | 100 across Delhi, Mumbai, Bangalore, Kolkata, Chennai, Hyderabad |
| Sellers | 20 rated 4.0–4.9 |
| Products | 50 across Electronics, Fashion, Home, Books |
| Orders | 155+ (March–August 2026) |
| Payment Pattern | ~60% COD · ~20% UPI · ~20% Cards/Wallet |
| Regions | North · South · East · West |
| Price Range | Rs 199 – Rs 1,49,990 |

---

## Database Schema (8 Tables)

| Table | PK | Key Foreign Keys | Notable Columns |
|-------|----|-----------------|-----------------|
| users | user_id | — | region ENUM, user_type ENUM |
| sellers | seller_id | user_id → users | rating DECIMAL |
| categories | category_id | — | category_name, subcategory |
| products | product_id | category_id, seller_id | price, stock, rating |
| orders | order_id | user_id | payment_method ENUM, order_status ENUM |
| order_items | order_item_id | order_id, product_id | quantity, unit_price |
| reviews | review_id | product_id, user_id | rating CHECK(1-5) |
| returns | return_id | order_id, product_id | reason, status ENUM |

---

## Setup Instructions

```bash
# Import in order:
mysql -u root -p < schema.sql
mysql -u root -p < sample_data.sql

# Run queries one by one:
mysql -u root -p flipkart_analytics < queries.sql
```

---

## 15 Analytical Queries

| # | Query | Key Concept |
|---|-------|-------------|
| 1 | Top 10 Customers by Spending | GROUP BY, ORDER BY |
| 2 | Best-Selling Products by Category | RANK() OVER PARTITION BY |
| 3 | Payment Method Preferences | SUM() OVER(), % calculation |
| 4 | Regional Sales Performance | Window SUM OVER() |
| 5 | Top Sellers by Rating + Revenue | Composite scoring |
| 6 | Product Return Analysis | LEFT JOIN, NULLIF, GROUP_CONCAT |
| 7 | Customer Lifetime Value (RFM) | CTE + NTILE(5) |
| 8 | Monthly Revenue Trends | LAG(), cumulative SUM OVER() |
| 9 | Churn Analysis (60-day) | DATEDIFF(), HAVING |
| 10 | Category Performance Metrics | Multi-table JOINs |
| 11 | Festival Season Patterns | DATE_FORMAT(), CASE WHEN |
| 12 | Payment Method by Region | PARTITION BY region |
| 13 | Seller Reliability Score | CTE + weighted formula |
| 14 | Customer Acquisition Analysis | FIRST_VALUE(), chained CTEs |
| 15 | Inventory Health Check | FIELD() custom sort |

---

## SQL Concepts Demonstrated

```
DDL           CREATE TABLE with ENUM, CHECK, FK constraints
DML           Bulk INSERT with realistic Indian e-commerce data
Window Funcs  RANK, NTILE, LAG, FIRST_VALUE, SUM OVER, PARTITION BY
CTEs          WITH clauses for multi-step analytical logic
Joins         INNER JOIN, LEFT JOIN up to 5 tables
Aggregation   SUM, COUNT, AVG, MAX, MIN with GROUP BY / HAVING
Conditional   CASE WHEN, COALESCE, NULLIF, FIELD
Date Funcs    DATE_FORMAT, DATEDIFF, MONTHNAME, CURDATE
String Funcs  GROUP_CONCAT with ORDER BY and SEPARATOR
Business KPIs RFM scoring, CLV, churn rate, reliability score, inventory velocity
```

---

## Portfolio Tips

**Resume line:**
> "Designed and analysed an 8-table MySQL database with 15 BI queries for an Indian e-commerce platform, implementing RFM segmentation, churn detection, inventory health scoring, and regional revenue analytics using window functions and CTEs."

**Extend this project:**
- Connect to Power BI / Tableau for a live dashboard
- Use Python + matplotlib to visualise query results
- Add stored procedures to automate monthly RFM refresh
- Demonstrate EXPLAIN ANALYZE for query optimisation

---

## Project Structure

```
flipkart-analytics-hub/
├── schema.sql           # 8-table schema with all constraints
├── sample_data.sql      # Realistic Indian e-commerce data
├── queries.sql          # 15 advanced analytical queries
├── README.md            # This file
└── generate_project.py  # Python script that created these files
```

---

MIT License -- use freely for your portfolio. Star the repo if it helped!
"""


# =============================================================================
# MAIN - Write all 4 files
# =============================================================================
def write_file(filename: str, content: str) -> None:
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    size_kb = os.path.getsize(path) / 1024
    print(f"  [OK]  {filename:<22}  ({size_kb:.1f} KB)  -->  {path}")


def main() -> None:
    print()
    print("=" * 64)
    print("  Flipkart Analytics Hub  --  SQL Project Generator")
    print("=" * 64)
    print(f"  Output: {OUTPUT_DIR}")
    print()
    write_file("schema.sql",      SCHEMA_SQL)
    write_file("sample_data.sql", SAMPLE_DATA_SQL)
    write_file("queries.sql",     QUERIES_SQL)
    write_file("README.md",       README_MD)
    print()
    print("=" * 64)
    print("  All 4 files generated successfully!")
    print("=" * 64)
    print()
    print("  Next steps:")
    print("  1. Open MySQL Workbench")
    print("  2. source schema.sql")
    print("  3. source sample_data.sql")
    print("  4. Explore queries.sql")
    print("  5. Push to GitHub!")
    print()


if __name__ == "__main__":
    main()
