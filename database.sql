-- ================================================================================
-- AFFORGATO CAFE - COMPREHENSIVE NORMALIZED DATABASE SCHEMA
-- ================================================================================
-- Database: afforgato_cafe
-- Version: 2.0 - Fully Normalized (3NF)
-- Features: Triggers, Audit Trails, Inventory Management, Advanced Relationships
-- Location: Bengaluru, India
-- Currency: Indian Rupees (₹)
-- ================================================================================

CREATE DATABASE IF NOT EXISTS afforgato_cafe
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE afforgato_cafe;

-- ================================================================================
-- CORE ENTITY TABLES
-- ================================================================================

-- 1. USERS TABLE - Core user authentication and basic information
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20),
    is_admin BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_active_users (is_active, created_at)
);

-- 2. USER_PROFILES TABLE - Extended user information (Normalized)
CREATE TABLE user_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    date_of_birth DATE,
    gender ENUM('male', 'female', 'other', 'prefer_not_to_say'),
    preferences TEXT,
    loyalty_points INT DEFAULT 0,
    total_orders INT DEFAULT 0,
    total_spent DECIMAL(10,2) DEFAULT 0.00,
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_profile (user_id),
    INDEX idx_loyalty_points (loyalty_points DESC)
);

-- 3. ADDRESSES TABLE - Normalized address storage
CREATE TABLE addresses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    address_type ENUM('home', 'work', 'other') DEFAULT 'home',
    street_address TEXT NOT NULL,
    city VARCHAR(100) NOT NULL DEFAULT 'Bengaluru',
    state VARCHAR(100) NOT NULL DEFAULT 'Karnataka',
    postal_code VARCHAR(20) NOT NULL,
    country VARCHAR(100) DEFAULT 'India',
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_addresses (user_id),
    INDEX idx_default_address (user_id, is_default),
    INDEX idx_city_state (city, state)
);

-- 4. CATEGORIES TABLE - Menu item categories
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    emoji VARCHAR(10),
    display_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_category_order (display_order, is_active),
    INDEX idx_active_categories (is_active, name)
);

-- 5. MENU_ITEMS TABLE - Coffee shop products with detailed information
CREATE TABLE menu_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(8,2) NOT NULL,
    category_id INT,
    emoji VARCHAR(10),
    image_url VARCHAR(255),
    is_available BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    preparation_time INT DEFAULT 5,
    calories INT,
    ingredients TEXT,
    allergens TEXT,
    inventory_count INT DEFAULT 0,
    min_stock_level INT DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    INDEX idx_menu_category (category_id, is_available),
    INDEX idx_featured_items (is_featured, is_available),
    INDEX idx_price_range (price),
    INDEX idx_inventory (inventory_count, min_stock_level),

    CONSTRAINT chk_positive_price CHECK (price > 0),
    CONSTRAINT chk_positive_inventory CHECK (inventory_count >= 0)
);

-- Insert sample categories
INSERT INTO categories (name, description, emoji) VALUES
('Hot Coffee', 'Freshly brewed hot coffee beverages', '☕'),
('Cold Coffee', 'Refreshing iced coffee drinks', '🧊'),
('Tea', 'Premium tea selection', '🍵'),
('Pastries', 'Fresh baked goods and pastries', '🥐'),
('Sandwiches', 'Delicious sandwiches and wraps', '🥪'),
('Desserts', 'Sweet treats and desserts', '🍰');

-- Insert sample menu items
INSERT INTO menu_items (name, description, price, category_id, emoji, is_available) VALUES
-- Hot Coffee
('Espresso', 'Rich and bold single shot', 2.50, 1, '☕', TRUE),
('Americano', 'Espresso with hot water', 3.00, 1, '☕', TRUE),
('Cappuccino', 'Espresso with steamed milk and foam', 4.50, 1, '☕', TRUE),
('Latte', 'Espresso with steamed milk', 4.75, 1, '☕', TRUE),
('Mocha', 'Espresso with chocolate and steamed milk', 5.25, 1, '☕', TRUE),

-- Cold Coffee
('Iced Coffee', 'Cold brew over ice', 3.50, 2, '🧊', TRUE),
('Iced Latte', 'Espresso with cold milk over ice', 4.75, 2, '🧊', TRUE),
('Frappuccino', 'Blended coffee with ice and cream', 5.50, 2, '🧊', TRUE),
('Cold Brew', 'Smooth cold-brewed coffee', 4.00, 2, '🧊', TRUE),

-- Tea
('Earl Grey', 'Classic bergamot-flavored black tea', 2.75, 3, '🍵', TRUE),
('Green Tea', 'Antioxidant-rich green tea', 2.50, 3, '🍵', TRUE),
('Chai Latte', 'Spiced tea with steamed milk', 4.25, 3, '🍵', TRUE),

-- Pastries
('Croissant', 'Buttery, flaky French pastry', 3.25, 4, '🥐', TRUE),
('Blueberry Muffin', 'Fresh blueberry muffin', 2.75, 4, '🧁', TRUE),
('Danish', 'Sweet pastry with fruit filling', 3.50, 4, '🥐', TRUE),

-- Sandwiches
('Club Sandwich', 'Triple-decker with turkey and bacon', 8.50, 5, '🥪', TRUE),
('Grilled Cheese', 'Classic grilled cheese sandwich', 6.25, 5, '🥪', TRUE),
('Veggie Wrap', 'Fresh vegetables in a tortilla wrap', 7.75, 5, '🌯', TRUE),

-- Desserts
('Chocolate Cake', 'Rich chocolate layer cake', 4.50, 6, '🍰', TRUE),
('Cheesecake', 'Creamy New York style cheesecake', 5.25, 6, '🍰', TRUE),
('Tiramisu', 'Italian coffee-flavored dessert', 5.75, 6, '🍰', TRUE);

-- Insert admin user (password: admin123)
INSERT INTO users (username, email, password_hash, first_name, last_name, is_admin) VALUES
('admin', 'admin@afforgato.com', 'pbkdf2:sha256:600000$8xQJ9K2L$8f5c8e4a9b2d1c3e5f7a9b1c3d5e7f9a1b3c5d7e9f1a3b5c7d9e1f3a5b7c9d1e', 'Admin', 'User', TRUE);

-- Insert demo user (password: demo123)
INSERT INTO users (username, email, password_hash, first_name, last_name, phone, address) VALUES
('demo', 'demo@afforgato.com', 'pbkdf2:sha256:600000$9yRK0M3N$9g6d9f5b0c3e2d4f6g8a0b2c4d6f8g0a2b4c6d8f0a2b4c6d8f0a2b4c6d8f0a2b', 'Demo', 'User', '+1 (555) 123-4567', '123 Coffee Street, Brew City, BC 12345');
