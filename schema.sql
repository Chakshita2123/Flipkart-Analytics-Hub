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
