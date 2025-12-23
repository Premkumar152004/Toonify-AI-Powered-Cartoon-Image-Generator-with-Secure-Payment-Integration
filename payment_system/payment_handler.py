"""
Payment Handler Module - COMPLETE FIXED VERSION
- Fixed database saving issue
- Simplified validation
"""

import random
import string
from datetime import datetime
import os
import json

class PaymentHandler:
    """Handles all payment-related operations"""
    
    def __init__(self):
        # UNIQUE PRICING PER STYLE (NO GST)
        self.style_prices = {
            # AI Anime Styles (Premium)
            'Hayao': 129.00,
            'Shinkai': 149.00,
            'Paprika': 139.00,
            'Ghibli Style': 159.00,
            
            # OpenCV Effects (Standard)
            'Classic Cartoon': 79.00,
            'Sketch': 59.00,
            'Pencil Color': 69.00,
            'Oil Painting': 89.00
        }
        
        self.payment_methods = {
            'upi': ['PhonePe', 'Google Pay', 'Paytm', 'BHIM UPI'],
            'netbanking': ['SBI', 'HDFC', 'ICICI', 'Axis Bank', 'PNB', 'BOB'],
            'card': ['Credit Card', 'Debit Card']
        }
        self.transactions_dir = "data/transactions"
        os.makedirs(self.transactions_dir, exist_ok=True)
    
    def generate_order_id(self):
        """Generate unique order ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"TOON{timestamp}{random_str}"
    
    def generate_transaction_id(self):
        """Generate unique transaction ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = ''.join(random.choices(string.digits, k=8))
        return f"TXN{timestamp}{random_str}"
    
    def calculate_total_by_effect(self, effect_name):
        """Calculate total amount based on effect type - NO GST"""
        # Get price for the effect, default to 99 if not found
        base_price = self.style_prices.get(effect_name, 99.00)
        
        return {
            'effect_name': effect_name,
            'base_price': round(base_price, 2),
            'total': round(base_price, 2)  # No GST
        }
    
    def validate_upi_id(self, upi_id):
        """Validate UPI ID format - accept any @ format for demo"""
        if not upi_id or '@' not in upi_id:
            return False, "Invalid UPI ID format. Use: username@bank"
        
        return True, "Valid UPI ID"
    
    def process_payment(self, payment_method, payment_details, user_email, amount_details, effect_name):
        """Process payment and save to database"""
        try:
            from utils.database import Database
            
            order_id = self.generate_order_id()
            transaction_id = self.generate_transaction_id()
            
            # Save to database
            db = Database()
            success = db.save_transaction(
                order_id, transaction_id, user_email, 
                effect_name, amount_details['total'], payment_method
            )
            
            if success:
                # Also save to JSON file for admin stats
                transaction_data = {
                    'order_id': order_id,
                    'transaction_id': transaction_id,
                    'user_email': user_email,
                    'effect_name': effect_name,
                    'amount': amount_details['total'],
                    'payment_method': payment_method,
                    'timestamp': datetime.now().isoformat()
                }
                
                self.save_transaction(transaction_data)
                
                return True, {
                    'order_id': order_id,
                    'transaction_id': transaction_id,
                    'message': 'Payment successful!'
                }
            else:
                return False, "Failed to save transaction to database"
        
        except Exception as e:
            print(f"Payment processing error: {e}")
            return False, f"Payment error: {str(e)}"
    
    def save_transaction(self, transaction_data):
        """Save transaction details"""
        try:
            transaction_file = f"{self.transactions_dir}/transactions.json"
            
            # Load existing transactions
            if os.path.exists(transaction_file):
                with open(transaction_file, 'r') as f:
                    transactions = json.load(f)
            else:
                transactions = []
            
            # Add new transaction
            transactions.append(transaction_data)
            
            # Save updated transactions
            with open(transaction_file, 'w') as f:
                json.dump(transactions, f, indent=4)
            
            return True
        except Exception as e:
            print(f"Error saving transaction: {str(e)}")
            return False