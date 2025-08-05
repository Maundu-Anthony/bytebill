#!/usr/bin/env python3

"""
ByteBill Database Initialization Script
This script creates the MySQL database and initializes it with default data.
"""

import sys
import os
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import hashlib

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': ''  # No password for default MySQL installation
}

BYTEBILL_DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'bytebill_user',
    'password': 'bytebill_password',
    'database': 'bytebill_db'
}

def create_database_and_user():
    """Create ByteBill database and user"""
    try:
        # Connect as root
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print("Creating ByteBill database...")
        
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS bytebill_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        
        # Create user and grant privileges
        cursor.execute("CREATE USER IF NOT EXISTS 'bytebill_user'@'localhost' IDENTIFIED BY 'bytebill_password'")
        cursor.execute("GRANT ALL PRIVILEGES ON bytebill_db.* TO 'bytebill_user'@'localhost'")
        cursor.execute("FLUSH PRIVILEGES")
        
        print("Database and user created successfully!")
        
    except Error as e:
        print(f"Error creating database: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    
    return True

def create_tables():
    """Create all necessary tables"""
    try:
        connection = mysql.connector.connect(**BYTEBILL_DB_CONFIG)
        cursor = connection.cursor()
        
        print("Creating tables...")
        
        # Plans table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS plans (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                type ENUM('hourly', 'daily', 'weekly', 'monthly', 'unlimited') NOT NULL,
                duration INT NOT NULL COMMENT 'Duration in seconds',
                data_limit BIGINT NULL COMMENT 'Data limit in bytes, NULL for unlimited',
                price DECIMAL(10, 2) NOT NULL,
                description TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ip_address VARCHAR(45) NOT NULL,
                mac_address VARCHAR(17) NOT NULL UNIQUE,
                device_name VARCHAR(255),
                status ENUM('active', 'disconnected', 'expired', 'blocked') DEFAULT 'active',
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                total_sessions INT DEFAULT 0,
                total_data_used BIGINT DEFAULT 0 COMMENT 'Total data used in bytes',
                is_blocked BOOLEAN DEFAULT FALSE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_mac_address (mac_address),
                INDEX idx_ip_address (ip_address),
                INDEX idx_status (status)
            )
        """)
        
        # Vouchers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vouchers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                code VARCHAR(20) NOT NULL UNIQUE,
                plan_id INT NOT NULL,
                status ENUM('unused', 'used', 'expired', 'disabled') DEFAULT 'unused',
                created_by VARCHAR(100) NOT NULL,
                used_by_mac VARCHAR(17),
                used_at TIMESTAMP NULL,
                expires_at TIMESTAMP NOT NULL,
                batch_id VARCHAR(50),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (plan_id) REFERENCES plans(id) ON DELETE CASCADE,
                INDEX idx_code (code),
                INDEX idx_status (status),
                INDEX idx_expires_at (expires_at),
                INDEX idx_batch_id (batch_id)
            )
        """)
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id VARCHAR(100) NOT NULL UNIQUE,
                user_id INT NOT NULL,
                plan_id INT NOT NULL,
                voucher_id INT,
                status ENUM('active', 'expired', 'terminated', 'paused') DEFAULT 'active',
                payment_method ENUM('voucher', 'mpesa', 'free') NOT NULL,
                payment_reference VARCHAR(100),
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP NULL,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                duration_limit INT NOT NULL COMMENT 'Duration limit in seconds',
                time_used INT DEFAULT 0 COMMENT 'Time used in seconds',
                data_limit BIGINT COMMENT 'Data limit in bytes, NULL for unlimited',
                bytes_uploaded BIGINT DEFAULT 0,
                bytes_downloaded BIGINT DEFAULT 0,
                ip_address VARCHAR(45) NOT NULL,
                mac_address VARCHAR(17) NOT NULL,
                amount_paid DECIMAL(10, 2) DEFAULT 0.00,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (plan_id) REFERENCES plans(id) ON DELETE CASCADE,
                FOREIGN KEY (voucher_id) REFERENCES vouchers(id) ON DELETE SET NULL,
                INDEX idx_session_id (session_id),
                INDEX idx_user_id (user_id),
                INDEX idx_status (status),
                INDEX idx_mac_address (mac_address),
                INDEX idx_start_time (start_time)
            )
        """)
        
        # M-PESA transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mpesa_transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                checkout_request_id VARCHAR(100) UNIQUE,
                merchant_request_id VARCHAR(100),
                phone_number VARCHAR(15) NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                mpesa_receipt_number VARCHAR(100),
                transaction_date TIMESTAMP NULL,
                status ENUM('pending', 'completed', 'failed', 'cancelled') DEFAULT 'pending',
                result_code INT,
                result_desc TEXT,
                plan_id INT,
                session_id INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (plan_id) REFERENCES plans(id) ON DELETE SET NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE SET NULL,
                INDEX idx_checkout_request (checkout_request_id),
                INDEX idx_phone_number (phone_number),
                INDEX idx_status (status)
            )
        """)
        
        # System logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                level ENUM('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL') NOT NULL,
                message TEXT NOT NULL,
                module VARCHAR(100),
                user_id INT,
                ip_address VARCHAR(45),
                additional_data JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_level (level),
                INDEX idx_module (module),
                INDEX idx_created_at (created_at)
            )
        """)
        
        connection.commit()
        print("Tables created successfully!")
        
    except Error as e:
        print(f"Error creating tables: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    
    return True

def insert_default_data():
    """Insert default plans and admin user"""
    try:
        connection = mysql.connector.connect(**BYTEBILL_DB_CONFIG)
        cursor = connection.cursor()
        
        print("Inserting default data...")
        
        # Insert default plans
        plans = [
            ('1 Hour Basic', 'hourly', 3600, 524288000, 50.00, '1 hour internet access with 500MB data'),
            ('Daily Standard', 'daily', 86400, 1073741824, 150.00, '24 hours internet access with 1GB data'),
            ('Daily Premium', 'daily', 86400, 2147483648, 250.00, '24 hours internet access with 2GB data'),
            ('Weekly Basic', 'weekly', 604800, 5368709120, 500.00, '7 days internet access with 5GB data'),
            ('Weekly Premium', 'weekly', 604800, 10737418240, 800.00, '7 days internet access with 10GB data'),
            ('Monthly Unlimited', 'monthly', 2592000, None, 2000.00, '30 days unlimited internet access')
        ]
        
        for plan in plans:
            cursor.execute("""
                INSERT IGNORE INTO plans (name, type, duration, data_limit, price, description)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, plan)
        
        # Generate some sample vouchers for testing
        import random
        import string
        
        def generate_voucher_code():
            return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        
        # Get plan IDs
        cursor.execute("SELECT id FROM plans ORDER BY id LIMIT 3")
        plan_ids = [row[0] for row in cursor.fetchall()]
        
        # Generate vouchers for each plan
        for plan_id in plan_ids:
            for i in range(5):  # 5 vouchers per plan
                voucher_code = generate_voucher_code()
                expires_at = datetime.now() + timedelta(days=30)
                
                cursor.execute("""
                    INSERT INTO vouchers (code, plan_id, created_by, expires_at, batch_id)
                    VALUES (%s, %s, %s, %s, %s)
                """, (voucher_code, plan_id, 'system', expires_at, 'initial_batch'))
        
        connection.commit()
        print("Default data inserted successfully!")
        
        # Display sample vouchers
        cursor.execute("""
            SELECT v.code, p.name, p.price 
            FROM vouchers v 
            JOIN plans p ON v.plan_id = p.id 
            WHERE v.status = 'unused'
            ORDER BY p.id, v.created_at
            LIMIT 10
        """)
        
        print("\nSample vouchers created:")
        print("-" * 50)
        for code, plan_name, price in cursor.fetchall():
            print(f"Code: {code} | Plan: {plan_name} | Price: KSh {price}")
        
    except Error as e:
        print(f"Error inserting default data: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    
    return True

def main():
    """Main initialization function"""
    print("ByteBill Database Initialization")
    print("=" * 40)
    
    # Check if MySQL is running
    try:
        test_connection = mysql.connector.connect(**DB_CONFIG)
        test_connection.close()
        print("✓ MySQL connection successful")
    except Error as e:
        print(f"✗ MySQL connection failed: {e}")
        print("Please ensure MySQL is running and the root password is correct.")
        return False
    
    # Create database and user
    if not create_database_and_user():
        return False
    
    # Create tables
    if not create_tables():
        return False
    
    # Insert default data
    if not insert_default_data():
        return False
    
    print("\n" + "=" * 40)
    print("✓ ByteBill database initialization complete!")
    print("\nDatabase details:")
    print(f"  Host: {BYTEBILL_DB_CONFIG['host']}")
    print(f"  Database: {BYTEBILL_DB_CONFIG['database']}")
    print(f"  Username: {BYTEBILL_DB_CONFIG['user']}")
    print(f"  Password: {BYTEBILL_DB_CONFIG['password']}")
    
    print("\nNext steps:")
    print("1. Update backend/config.py with your MySQL credentials if different")
    print("2. Run: cd backend && pip install -r requirements.txt")
    print("3. Run: cd backend && python app.py")
    print("4. Access admin panel at: http://localhost:5000")
    
    return True

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("ByteBill Database Initialization Script")
        print("Usage: python init_database.py")
        print("\nThis script will:")
        print("- Create the 'bytebill' database")
        print("- Create the 'bytebill' MySQL user")
        print("- Create all necessary tables")
        print("- Insert default plans and sample vouchers")
        sys.exit(0)
    
    success = main()
    sys.exit(0 if success else 1)
