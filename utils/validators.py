"""
Input validation functions
"""
import re

def validate_name(name):
    """Validate user name"""
    if not name or len(name.strip()) < 2:
        return False, "Name must be at least 2 characters"
    if not re.match(r'^[a-zA-Z\s]+$', name):
        return False, "Name can only contain letters and spaces"
    return True, "Valid"

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    return True, "Valid"

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    return True, "Valid"

def validate_mobile(mobile):
    """Validate mobile number"""
    if not re.match(r'^\d{10}$', mobile):
        return False, "Mobile number must be exactly 10 digits"
    return True, "Valid"

def validate_age(age):
    """Validate age"""
    if age < 13:
        return False, "You must be at least 13 years old"
    if age > 120:
        return False, "Please enter a valid age"
    return True, "Valid"

def validate_city(city):
    """Validate city name"""
    if not city or len(city.strip()) < 2:
        return False, "City name must be at least 2 characters"
    if not re.match(r'^[a-zA-Z\s]+$', city):
        return False, "City name can only contain letters and spaces"
    return True, "Valid"