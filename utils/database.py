"""
Database Module - Updated with User Management and Image History
"""

import sqlite3
import hashlib
import os
from datetime import datetime
import json

class Database:
    def __init__(self, db_path="data/toonify.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                gender TEXT,
                age INTEGER,
                mobile TEXT,
                city TEXT,
                is_admin INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT UNIQUE NOT NULL,
                transaction_id TEXT UNIQUE NOT NULL,
                user_email TEXT NOT NULL,
                effect_name TEXT NOT NULL,
                amount REAL NOT NULL,
                payment_method TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_email) REFERENCES users(email)
            )
        ''')
        
        # Image history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS image_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL,
                effect_name TEXT NOT NULL,
                original_path TEXT,
                cartoonized_path TEXT NOT NULL,
                amount REAL NOT NULL,
                transaction_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_email) REFERENCES users(email)
            )
        ''')
        
        # Create default admin if doesn't exist
        cursor.execute("SELECT * FROM users WHERE email = ?", ("admin@toonify.com",))
        if not cursor.fetchone():
            admin_password = self.hash_password("Admin@123")
            cursor.execute('''
                INSERT INTO users (name, email, password, gender, age, mobile, city, is_admin)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', ("Admin", "admin@toonify.com", admin_password, "Other", 30, "0000000000", "Admin City", 1))
        
        conn.commit()
        conn.close()
    
    def create_user(self, name, email, password, gender, age, mobile, city):
        """Create new user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            hashed_password = self.hash_password(password)
            
            cursor.execute('''
                INSERT INTO users (name, email, password, gender, age, mobile, city)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, email, hashed_password, gender, age, mobile, city))
            
            conn.commit()
            conn.close()
            return True, "Account created successfully!"
            
        except sqlite3.IntegrityError:
            return False, "Email already exists"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def authenticate_user(self, email, password):
        """Authenticate user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            hashed_password = self.hash_password(password)
            
            cursor.execute('''
                SELECT id, name, email, gender, age, mobile, city, is_admin, created_at
                FROM users WHERE email = ? AND password = ? AND is_admin = 0
            ''', (email, hashed_password))
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                return True, {
                    'id': user[0],
                    'name': user[1],
                    'email': user[2],
                    'gender': user[3],
                    'age': user[4],
                    'mobile': user[5],
                    'city': user[6],
                    'is_admin': user[7],
                    'created_at': user[8]
                }
            return False, "Invalid credentials"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def authenticate_admin(self, email, password):
        """Authenticate admin"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            hashed_password = self.hash_password(password)
            
            cursor.execute('''
                SELECT id, name, email, gender, age, mobile, city, is_admin, created_at
                FROM users WHERE email = ? AND password = ? AND is_admin = 1
            ''', (email, hashed_password))
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                return True, {
                    'id': user[0],
                    'name': user[1],
                    'email': user[2],
                    'gender': user[3],
                    'age': user[4],
                    'mobile': user[5],
                    'city': user[6],
                    'is_admin': user[7],
                    'created_at': user[8]
                }
            return False, "Invalid admin credentials"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def update_password(self, email, current_password, new_password):
        """Update user password"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            current_hash = self.hash_password(current_password)
            
            cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", 
                         (email, current_hash))
            
            if not cursor.fetchone():
                conn.close()
                return False, "Current password is incorrect"
            
            new_hash = self.hash_password(new_password)
            cursor.execute("UPDATE users SET password = ? WHERE email = ?", 
                         (new_hash, email))
            
            conn.commit()
            conn.close()
            return True, "Password updated successfully"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def save_transaction(self, order_id, transaction_id, user_email, effect_name, amount, payment_method):
        """Save transaction"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO transactions (order_id, transaction_id, user_email, effect_name, amount, payment_method)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (order_id, transaction_id, user_email, effect_name, amount, payment_method))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Transaction save error: {e}")
            return False
    
    def save_image_history(self, user_email, effect_name, original_path, cartoonized_path, amount, transaction_id):
        """Save image processing history"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO image_history (user_email, effect_name, original_path, cartoonized_path, amount, transaction_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_email, effect_name, original_path, cartoonized_path, amount, transaction_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Image history save error: {e}")
            return False
    
    def get_user_image_history(self, user_email):
        """Get user's image processing history"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT effect_name, cartoonized_path, amount, transaction_id, created_at
                FROM image_history
                WHERE user_email = ?
                ORDER BY created_at DESC
            ''', (user_email,))
            
            history = cursor.fetchall()
            conn.close()
            return history
            
        except Exception as e:
            print(f"Error fetching history: {e}")
            return []
    
    def get_all_users(self):
        """Get all users (excluding admin)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, email, gender, age, mobile, city, created_at
                FROM users
                WHERE is_admin = 0
                ORDER BY created_at DESC
            ''')
            
            users = cursor.fetchall()
            conn.close()
            return users
            
        except Exception as e:
            print(f"Error fetching users: {e}")
            return []
    
    def get_user_by_id(self, user_id):
        """Get user details by ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, email, gender, age, mobile, city, created_at
                FROM users
                WHERE id = ? AND is_admin = 0
            ''', (user_id,))
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                return {
                    'id': user[0],
                    'name': user[1],
                    'email': user[2],
                    'gender': user[3],
                    'age': user[4],
                    'mobile': user[5],
                    'city': user[6],
                    'created_at': user[7]
                }
            return None
            
        except Exception as e:
            print(f"Error fetching user: {e}")
            return None
        
    def clear_transactions(self):
        """Delete all rows from transactions table (table stays)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions")
            conn.commit()
            conn.close()
            return True, "All transaction data deleted successfully"
        except Exception as e:
            return False, str(e)

    def clear_image_history(self):
        """Delete all rows from image_history table (table stays)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM image_history")
            conn.commit()
            conn.close()
            return True, "Image history cleared successfully"
        except Exception as e:
            return False, str(e)

    
    def get_admin_stats(self):
        """Get admin dashboard statistics"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Total users (excluding admin)
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = 0")
            total_users = cursor.fetchone()[0]
            
            # Total revenue
            cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions")
            total_revenue = cursor.fetchone()[0]
            
            # Total transactions
            cursor.execute("SELECT COUNT(*) FROM transactions")
            total_transactions = cursor.fetchone()[0]
            
            # Total images
            cursor.execute("SELECT COUNT(*) FROM image_history")
            total_images = cursor.fetchone()[0]
            
            # Revenue by effect
            cursor.execute('''
                SELECT effect_name, COUNT(*), SUM(amount)
                FROM transactions
                GROUP BY effect_name
                ORDER BY SUM(amount) DESC
            ''')
            revenue_by_effect = cursor.fetchall()
            
            # Monthly revenue
            cursor.execute('''
                SELECT strftime('%Y-%m', created_at) as month, SUM(amount)
                FROM transactions
                GROUP BY month
                ORDER BY month DESC
                LIMIT 6
            ''')
            monthly_revenue = cursor.fetchall()
            
            # Recent transactions
            cursor.execute('''
                SELECT transaction_id, user_email, effect_name, amount, created_at
                FROM transactions
                ORDER BY created_at DESC
                LIMIT 10
            ''')
            recent_transactions = cursor.fetchall()
            
            conn.close()
            
            return {
                'total_users': total_users,
                'total_revenue': round(total_revenue, 2),
                'total_transactions': total_transactions,
                'total_images': total_images,
                'revenue_by_effect': revenue_by_effect,
                'monthly_revenue': monthly_revenue,
                'recent_transactions': recent_transactions
            }
            
        except Exception as e:
            print(f"Error fetching stats: {e}")
            return None

