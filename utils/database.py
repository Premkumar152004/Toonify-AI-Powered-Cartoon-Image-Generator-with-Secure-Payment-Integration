"""
Database operations using SQLite.
Handles user creation, authentication, and password updates.
"""

import sqlite3
import hashlib
from datetime import datetime
import os


class Database:
    def __init__(self, db_path="data/users.db"):
        """Initialize database and ensure folder exists."""
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.create_tables()

    # --------------------- INTERNAL UTILS ---------------------

    def connect(self):
        """Create and return a new database connection."""
        return sqlite3.connect(self.db_path)

    def hash_password(self, password: str) -> str:
        """Return SHA-256 hashed password."""
        return hashlib.sha256(password.encode()).hexdigest()

    # --------------------- TABLE CREATION ---------------------

    def create_tables(self):
        """Create users table if it does not exist."""
        try:
            conn = self.connect()
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    gender TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    mobile TEXT NOT NULL,
                    city TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"[ERROR] Failed to create tables: {e}")

    # --------------------- USER CREATION ---------------------

    def create_user(self, name, email, password, gender, age, mobile, city):
        """Register a new user account."""
        try:
            conn = self.connect()
            cursor = conn.cursor()

            # Check if email exists
            cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                conn.close()
                return False, "Email already registered"

            hashed_pwd = self.hash_password(password)

            cursor.execute("""
                INSERT INTO users (name, email, password, gender, age, mobile, city)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, email, hashed_pwd, gender, age, mobile, city))

            conn.commit()
            conn.close()
            return True, "Account created successfully!"

        except Exception as e:
            return False, f"Error: {str(e)}"

    # --------------------- USER LOGIN ---------------------

    def authenticate_user(self, email, password):
        """Authenticate login and return user data if valid."""
        try:
            conn = self.connect()
            cursor = conn.cursor()

            hashed_pwd = self.hash_password(password)

            cursor.execute("""
                SELECT id, name, email, gender, age, mobile, city, created_at
                FROM users
                WHERE email = ? AND password = ?
            """, (email, hashed_pwd))

            user = cursor.fetchone()
            conn.close()

            if user:
                return True, {
                    "id": user[0],
                    "name": user[1],
                    "email": user[2],
                    "gender": user[3],
                    "age": user[4],
                    "mobile": user[5],
                    "city": user[6],
                    "created_at": user[7]
                }

            return False, "Invalid email or password"

        except Exception as e:
            return False, f"Error: {str(e)}"

    # --------------------- PASSWORD UPDATE ---------------------

    def update_password(self, email, current_password, new_password):
        """Update the password after verifying current password."""
        try:
            conn = self.connect()
            cursor = conn.cursor()

            hashed_current = self.hash_password(current_password)

            # Verify current password exists
            cursor.execute("""
                SELECT id FROM users 
                WHERE email = ? AND password = ?
            """, (email, hashed_current))

            if not cursor.fetchone():
                conn.close()
                return False, "Current password is incorrect"

            hashed_new = self.hash_password(new_password)

            cursor.execute("""
                UPDATE users SET password = ?
                WHERE email = ?
            """, (hashed_new, email))

            conn.commit()
            conn.close()
            return True, "Password updated successfully!"

        except Exception as e:
            return False, f"Error: {str(e)}"
