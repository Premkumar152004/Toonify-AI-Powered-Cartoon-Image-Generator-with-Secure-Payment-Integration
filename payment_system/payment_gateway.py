import streamlit as st
import time
from payment_system.payment_handler import PaymentHandler

def render_payment_gateway(image_path, user_email, effect_name):
    """Main payment gateway interface"""
    if st.session_state.get('payment_success'):
        success_data = st.session_state.get('success_data', {})
        # Reset if it's a different image or effect
        if (success_data.get('image_path') != image_path or 
            success_data.get('effect_name') != effect_name):
            clear_payment_session()
    payment_handler = PaymentHandler()
    amount_details = payment_handler.calculate_total_by_effect(effect_name)

    st.markdown('<h1 class="main-header">💳 Secure Payment Gateway</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header">Complete your payment to download the image</h2>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Order Summary
        st.markdown(f"""
        <div style="background: white; padding: 2rem; border-radius: 20px;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.1); margin-bottom: 1.5rem; border: 2px solid #667eea;">
            <h2 style="text-align: center; color: #667eea; margin-bottom: 1rem;">
                📋 Order Summary
            </h2>
            <div style="border-top: 2px solid #E0E0E0; padding-top: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin: 1rem 0;">
                    <span style="color: #000000; font-size: 1.1rem; font-weight: 500;">
                        Product:
                    </span>
                    <span style="color: #667eea; font-size: 1.1rem; font-weight: 600;">
                        Toonify - {effect_name} Effect
                    </span>
                </div>
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            padding: 1.5rem; border-radius: 15px; margin: 1.5rem 0; text-align: center;">
                    <p style="color: white; font-size: 1rem; margin: 0; opacity: 0.9;">
                        Total Amount
                    </p>
                    <p style="color: white; font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;">
                        ₹{amount_details['total']}
                    </p>
                    <p style="color: rgba(255,255,255,0.8); font-size: 0.9rem; margin: 0;">
                        One-time payment | No hidden charges
                    </p>
                </div>
                <div style="display: flex; align-items: center; justify-content: center; gap: 0.5rem; margin-top: 1rem;">
                    <span style="color: #28a745; font-size: 1rem;">✓</span>
                    <span style="color: #28a745; font-size: 0.9rem;">Secure payment</span>
                    <span style="color: #28a745; font-size: 1rem; margin-left: 1rem;">✓</span>
                    <span style="color: #28a745; font-size: 0.9rem;">Instant delivery</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Check if we need to show success page
        if st.session_state.get('payment_success'):
            success_data = st.session_state.get('success_data', {})
            # Double-check it's for the current image
            if (success_data.get('image_path') == image_path and 
                success_data.get('effect_name') == effect_name):
                return show_payment_success_page(
                    st.session_state.success_data['image_path'],
                    st.session_state.success_data['effect_name'],
                    st.session_state.success_data['transaction_id'],
                    st.session_state.success_data['amount']
            )
            else:
                clear_payment_session()

        # Payment method selection
        st.markdown("""
        <h3 style="text-align: center; color: #333; margin-bottom: 1.5rem;">
            💰 Select Payment Method
        </h3>
        """, unsafe_allow_html=True)

        col_upi, col_netbank, col_card = st.columns(3)

        with col_upi:
            button_style = "primary" if st.session_state.get('payment_method') == "upi" else "secondary"
            if st.button("💳 UPI", use_container_width=True, key="select_upi", type=button_style):
                st.session_state.payment_method = "upi"
                st.rerun()

        with col_netbank:
            button_style = "primary" if st.session_state.get('payment_method') == "netbanking" else "secondary"
            if st.button("🏦 Net Banking", use_container_width=True, key="select_netbank", type=button_style):
                st.session_state.payment_method = "netbanking"
                st.rerun()

        with col_card:
            button_style = "primary" if st.session_state.get('payment_method') == "card" else "secondary"
            if st.button("💳 Card", use_container_width=True, key="select_card", type=button_style):
                st.session_state.payment_method = "card"
                st.rerun()

        st.markdown("---")

        if "payment_method" not in st.session_state:
            st.session_state.payment_method = "upi"

        # Render selected payment UI
        if st.session_state.payment_method == "upi":
            render_upi_payment(payment_handler, amount_details, user_email, image_path, effect_name)
        elif st.session_state.payment_method == "netbanking":
            render_netbanking_payment(payment_handler, amount_details, user_email, image_path, effect_name)
        elif st.session_state.payment_method == "card":
            render_card_payment(payment_handler, amount_details, user_email, image_path, effect_name)

        # ❌ Cancel payment
        col_cancel1, col_cancel2, col_cancel3 = st.columns([1, 2, 1])
        with col_cancel2:
            if st.button("❌ Cancel Payment", use_container_width=True, type="secondary"):
                clear_payment_session()
                st.rerun()

    return False


def render_upi_payment(payment_handler, amount_details, user_email, image_path, effect_name):
    """UPI Payment - Simplified without OTP"""
    
    st.markdown("""
    <h3 style="text-align: center; color: #333; margin-bottom: 1rem;">
        📱 UPI Payment
    </h3>
    """, unsafe_allow_html=True)
    
    with st.form("upi_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            upi_app = st.selectbox("Select UPI App", payment_handler.payment_methods['upi'])
        
        with col2:
            st.markdown("""
            <div style="margin-top: 1.7rem;">
                <p style="color: #666; font-size: 0.9rem; margin: 0;">
                    Demo: any valid format accepted
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        upi_id = st.text_input(
            "Enter UPI ID", 
            placeholder="username@paytm / 9876543210@ybl",
            help="Enter any UPI ID format for demo"
        )
        
        # Show amount prominently
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
                    padding: 1.5rem; border-radius: 15px; margin: 1.5rem 0; text-align: center;">
            <p style="color: white; font-size: 1rem; margin: 0; opacity: 0.9;">
                Amount to Pay
            </p>
            <p style="color: white; font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;">
                ₹{amount_details['total']}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        submitted = st.form_submit_button("Pay Now", use_container_width=True, type="primary")
        
        if submitted:
            if not upi_id or '@' not in upi_id:
                st.error("❌ Please enter a UPI ID (any format with @ is accepted)")
            else:
                # Process payment directly (no OTP)
                try:
                    with st.spinner("🔄 Processing payment..."):
                        time.sleep(1.5)
                        
                        payment_details = {'upi_id': upi_id, 'upi_app': upi_app}
                        success, result = payment_handler.process_payment(
                            'upi', payment_details, user_email, amount_details, effect_name
                        )
                        
                        if success:
                            # Save to database
                            from utils.database import Database
                            db = Database()
                            db.save_image_history(user_email, effect_name, "", image_path, amount_details['total'], result['transaction_id'])
                            
                            # Store success data and rerun
                            st.session_state.payment_success = True
                            st.session_state.success_data = {
                                'image_path': image_path,
                                'effect_name': effect_name,
                                'transaction_id': result['transaction_id'],
                                'amount': amount_details['total']
                            }
                            st.rerun()
                        else:
                            st.error(f"❌ Payment failed: {result}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")


def render_netbanking_payment(payment_handler, amount_details, user_email, image_path, effect_name):
    """Net Banking Payment - Simplified without OTP"""
    
    st.markdown("""
    <h3 style="text-align: center; color: #333; margin-bottom: 1rem;">
        🏦 Net Banking
    </h3>
    """, unsafe_allow_html=True)
    
    with st.form("netbank_form"):
        bank = st.selectbox("Select Bank", payment_handler.payment_methods['netbanking'])
        
        customer_id = st.text_input(
            "Customer ID / Username", 
            placeholder="Enter your bank username",
            help="Enter any value for demo"
        )
        
        # Show amount prominently
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
                    padding: 1.5rem; border-radius: 15px; margin: 1.5rem 0; text-align: center;">
            <p style="color: white; font-size: 1rem; margin: 0; opacity: 0.9;">
                Amount to Pay
            </p>
            <p style="color: white; font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;">
                ₹{amount_details['total']}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        submitted = st.form_submit_button("Pay Now", use_container_width=True, type="primary")
        
        if submitted:
            if not customer_id:
                st.error("❌ Please enter a Customer ID")
            else:
                # Process payment directly (no OTP)
                try:
                    with st.spinner("🔄 Processing payment..."):
                        time.sleep(1.5)
                        
                        payment_details = {'bank': bank, 'customer_id': customer_id}
                        success, result = payment_handler.process_payment(
                            'netbanking', payment_details, user_email, amount_details, effect_name
                        )
                        
                        if success:
                            # Save to database
                            from utils.database import Database
                            db = Database()
                            db.save_image_history(user_email, effect_name, "", image_path, amount_details['total'], result['transaction_id'])
                            
                            # Store success data and rerun
                            st.session_state.payment_success = True
                            st.session_state.success_data = {
                                'image_path': image_path,
                                'effect_name': effect_name,
                                'transaction_id': result['transaction_id'],
                                'amount': amount_details['total']
                            }
                            st.rerun()
                        else:
                            st.error(f"❌ Payment failed: {result}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")


def render_card_payment(payment_handler, amount_details, user_email, image_path, effect_name):
    """Card Payment - With JavaScript for real-time formatting"""
    
    st.markdown("""
    <h3 style="text-align: center; color: #333; margin-bottom: 1rem;">
        💳 Credit/Debit Card
    </h3>
    """, unsafe_allow_html=True)
    
    # JavaScript for real-time card formatting
    st.markdown("""
    <script>
    function formatCardNumber(input) {
        // Remove all non-digits
        let value = input.value.replace(/\D/g, '');
        
        // Add space after every 4 digits
        let formatted = '';
        for (let i = 0; i < value.length; i++) {
            if (i > 0 && i % 4 === 0) {
                formatted += ' ';
            }
            formatted += value[i];
        }
        
        // Update the input value
        input.value = formatted.substring(0, 19);
    }
    
    // Apply formatting when page loads
    document.addEventListener('DOMContentLoaded', function() {
        const cardInput = document.querySelector('input[placeholder*="card"]');
        if (cardInput) {
            cardInput.addEventListener('input', function() {
                formatCardNumber(this);
            });
        }
    });
    </script>
    
    <style>
    .card-number-input {
        letter-spacing: 3px !important;
        font-family: monospace !important;
        font-size: 1.2rem !important;
    }
    .card-format-hint {
        color: #666;
        font-size: 0.9rem;
        margin-top: -10px;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.form("card_form"):
        # Card number input with JavaScript formatting
        card_number = st.text_input(
            "Card Number",
            placeholder="1234 5678 9012 3456",
            max_chars=19,
            key="card_number",
            help="Spaces added automatically as you type"
        )
        
        st.markdown('<div class="card-format-hint">Format: 1234 5678 9012 3456</div>', unsafe_allow_html=True)
        
        card_name = st.text_input("Cardholder Name", placeholder="JOHN DOE")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            expiry = st.text_input("Expiry (MM/YY)", placeholder="12/25", max_chars=5)
        with col2:
            cvv = st.text_input("CVV", type="password", max_chars=4, placeholder="123")
        
        # Show amount prominently
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
                    padding: 1.5rem; border-radius: 15px; margin: 1.5rem 0; text-align: center;">
            <p style="color: white; font-size: 1rem; margin: 0; opacity: 0.9;">
                Amount to Pay
            </p>
            <p style="color: white; font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;">
                ₹{amount_details['total']}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        submitted = st.form_submit_button("Pay Now", use_container_width=True, type="primary")
        
        if submitted:
            # Get the raw card number (without spaces)
            raw_card = card_number.replace(' ', '') if card_number else ''
            
            # Simplified validation - accept any input for demo
            if not raw_card or len(raw_card) < 8:
                st.error("❌ Please enter a card number (minimum 8 digits)")
            elif not card_name or len(card_name) < 2:
                st.error("❌ Please enter cardholder name")
            elif not expiry:
                st.error("❌ Please enter expiry date")
            elif not cvv:
                st.error("❌ Please enter CVV")
            else:
                # Process payment directly (no OTP)
                try:
                    with st.spinner("🔄 Processing payment..."):
                        time.sleep(1.5)
                        
                        payment_details = {
                            'card_number': raw_card,
                            'card_name': card_name,
                            'expiry': expiry,
                            'cvv': cvv
                        }
                        success, result = payment_handler.process_payment(
                            'card', payment_details, user_email, amount_details, effect_name
                        )
                        
                        if success:
                            # Save to database
                            from utils.database import Database
                            db = Database()
                            success_save = db.save_image_history(
                                user_email, effect_name, "", image_path, 
                                amount_details['total'], result['transaction_id']
                            )
                            
                            if success_save:
                                # Store success data and rerun
                                st.session_state.payment_success = True
                                st.session_state.success_data = {
                                    'image_path': image_path,
                                    'effect_name': effect_name,
                                    'transaction_id': result['transaction_id'],
                                    'amount': amount_details['total']
                                }
                                st.rerun()
                            else:
                                st.error("❌ Failed to save transaction history. Please contact support.")
                        else:
                            st.error(f"❌ Payment failed: {result}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")


def show_payment_success_page(image_path, effect_name, transaction_id, amount):
    """Show payment success page (outside form context)"""
    
    try:
        # Read the file
        with open(image_path, 'rb') as file:
            file_data = file.read()
        
        # Generate filename
        file_name = f"toonify_{effect_name}_{transaction_id[-8:]}.png"
        
        # Show success message
        st.markdown(f"""
        <div style="background: white; padding: 2.5rem; border-radius: 20px; text-align: center; 
                    box-shadow: 0 8px 32px rgba(0,0,0,0.1); margin: 1.5rem 0; border: 3px solid #28a745;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">✅</div>
            <h2 style="color: #28a745; margin-bottom: 1rem; font-size: 2.2rem;">
                Payment Successful!
            </h2>
            <div style="background: #d4edda; padding: 1.5rem; border-radius: 15px; margin: 1.5rem 0;">
                <p style="color: #155724; font-size: 1.2rem; margin: 0.5rem 0;">
                    Transaction Completed
                </p>
                <p style="color: #000000; font-size: 2.5rem; font-weight: bold; margin: 1rem 0;">
                    ₹{amount}
                </p>
                <p style="color: #155724; font-size: 1rem; margin: 0.5rem 0;">
                    {effect_name} Effect
                </p>
            </div>
            <p style="color: #000000; font-size: 1.1rem; margin: 1rem 0;">
                <strong>Transaction ID:</strong> {transaction_id}
            </p>
            <p style="color: #28a745; font-size: 1.2rem; font-weight: bold; margin: 1.5rem 0;">
                ✓ Your image is ready to download
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.balloons()
        
        # Download button (outside form, so it's allowed)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.download_button(
                label="📥 Download Your Image",
                data=file_data,
                file_name=file_name,
                mime="image/png",
                use_container_width=True,
                type="primary",
                key=f"download_{transaction_id}"
            )
        
        # Auto-redirect message
        st.info("🔄 Redirecting to dashboard in 5 seconds...")
        
        # Add JavaScript for auto-redirect
        redirect_js = """
        <script>
        // Redirect after 5 seconds
        setTimeout(() => {
            window.location.href = window.location.origin;
        }, 5000);
        </script>
        """
        
        st.markdown(redirect_js, unsafe_allow_html=True)
        
        # Manual back button
        if st.button("🏠 Go to Dashboard", use_container_width=True, type="secondary"):
            clear_payment_session()
            st.session_state.show_payment = False
            st.rerun()
        
        return True
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        
        # Show back button if error occurs
        if st.button("🔙 Go Back", use_container_width=True):
            st.session_state.payment_success = False
            st.rerun()
        
        return False


def clear_payment_session():
    """Clear all payment session states"""
    keys = ['payment_method', 'payment_success', 'success_data']
    for key in keys:
        if key in st.session_state:
            del st.session_state[key]