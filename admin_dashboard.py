"""
Admin Dashboard - Complete Statistics and User Management
"""

import streamlit as st
from utils.database import Database
import pandas as pd
import os
from PIL import Image
from datetime import datetime

def render_admin_dashboard():
    """Render complete admin dashboard with user management"""
    
    db = Database()
    stats = db.get_admin_stats()
    
    if not stats:
        st.error("❌ Error loading statistics")
        return
    
    # Header
    st.markdown('<h1 class="main-header">👨‍💼 Admin Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header">Toonify Analytics & User Management</h2>', unsafe_allow_html=True)
    
    # Logout Button
    col1, col2, col3 = st.columns([5, 1, 1])
    with col3:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_data = None
            st.session_state.page = "login"
            st.rerun()
    
    st.markdown("---")
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 1.5rem; border-radius: 15px; text-align: center; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
            <h3 style="margin: 0; font-size: 2.5rem;">👥 {stats['total_users']}</h3>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem;">Total Users</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
                    padding: 1.5rem; border-radius: 15px; text-align: center; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
            <h3 style="margin: 0; font-size: 2.5rem;">💰 ₹{stats['total_revenue']}</h3>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem;">Total Revenue</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    padding: 1.5rem; border-radius: 15px; text-align: center; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
            <h3 style="margin: 0; font-size: 2.5rem;">📊 {stats['total_transactions']}</h3>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem;">Transactions</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 1.5rem; border-radius: 15px; text-align: center; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
            <h3 style="margin: 0; font-size: 2.5rem;">🎨 {stats['total_images']}</h3>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem;">Images Processed</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Clickable User Details Section
    st.markdown("### 👥 User Details (Click to View)")
    
    # Get all users
    all_users = db.get_all_users()
    
    if all_users:
        # Create a list of user data for the dataframe
        user_data = []
        for user in all_users:
            user_data.append({
                'ID': user[0],
                'Name': user[1],
                'Email': user[2],
                'Gender': user[3],
                'Age': user[4],
                'City': user[5],
                'Join Date': user[7]
            })
        
        df_users = pd.DataFrame(user_data)
        
        # Display user table with click functionality
        selected_user = st.selectbox(
            "Select a user to view details",
            df_users['Name'].tolist(),
            index=0
        )
        
        # Get selected user data
        selected_user_data = df_users[df_users['Name'] == selected_user].iloc[0]
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### 👤 User Profile")
            st.markdown(f"""
            <div style="background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <p style="color: #000; margin: 0.5rem 0;">
                    <strong>Name:</strong> {selected_user_data['Name']}
                </p>
                <p style="color: #000; margin: 0.5rem 0;">
                    <strong>Email:</strong> {selected_user_data['Email']}
                </p>
                <p style="color: #000; margin: 0.5rem 0;">
                    <strong>Gender:</strong> {selected_user_data['Gender']}
                </p>
                <p style="color: #000; margin: 0.5rem 0;">
                    <strong>Age:</strong> {selected_user_data['Age']}
                </p>
                <p style="color: #000; margin: 0.5rem 0;">
                    <strong>City:</strong> {selected_user_data['City']}
                </p>
                <p style="color: #000; margin: 0.5rem 0;">
                    <strong>Join Date:</strong> {selected_user_data['Join Date']}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Get user's edited images
            user_email = selected_user_data['Email']
            user_images = db.get_user_image_history(user_email)
            
            if user_images:
                st.markdown(f"### 🖼️ Edited Images ({len(user_images)})")
                
                # Display first 4 images
                cols = st.columns(min(4, len(user_images)))
                for idx, img_data in enumerate(user_images[:4]):
                    effect_name, image_path, amount, transaction_id, created_at = img_data
                    
                    with cols[idx % 4]:
                        try:
                            if os.path.exists(image_path):
                                img = Image.open(image_path)
                                st.image(img, use_column_width=True)
                                st.caption(f"{effect_name} - ₹{amount}")
                            else:
                                st.info(f"Image not found: {effect_name}")
                        except:
                            st.info("Image preview unavailable")
                
                # Show summary
                total_spent = sum([img[2] for img in user_images])
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
                            padding: 1rem; border-radius: 10px; margin-top: 1rem; text-align: center;">
                    <p style="color: white; font-size: 1.2rem; margin: 0;">
                        Total Spent: ₹{total_spent} | Images: {len(user_images)}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("📷 This user hasn't edited any images yet.")
    else:
        st.info("No users found in the database.")
    
    st.markdown("---")
    
    # Revenue Analytics
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 💰 Revenue by Effect")
        
        if stats['revenue_by_effect']:
            revenue_data = []
            for effect, count, revenue in stats['revenue_by_effect']:
                revenue_data.append({
                    'Effect': effect,
                    'Transactions': count,
                    'Revenue': f"₹{revenue:.2f}"
                })
            
            df = pd.DataFrame(revenue_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No revenue data yet")
    
    
    
    st.markdown("---")
    
    # Recent Transactions
    st.markdown("### 📋 Recent Transactions")
    
    if stats['recent_transactions']:
        transactions = []
        for txn in stats['recent_transactions']:
            transactions.append({
                'Transaction ID': txn[0],
                'User Email': txn[1],
                'Effect': txn[2],
                'Amount': f"₹{txn[3]}",
                'Date': txn[4]
            })
        
        df = pd.DataFrame(transactions)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No transactions yet")
    
    st.markdown("---")
    
    # Quick Stats
    st.markdown("### 🎯 Platform Statistics")
    
    avg_transaction = stats['total_revenue'] / stats['total_transactions'] if stats['total_transactions'] > 0 else 0
    avg_images_per_user = stats['total_images'] / stats['total_users'] if stats['total_users'] > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Average Transaction", f"₹{avg_transaction:.2f}")
    with col2:
        st.metric("Images per User", f"{avg_images_per_user:.1f}")
    with col3:
        st.metric("Conversion Rate", "85%")
    
    st.markdown("---")
    
    # Footer
   # st.markdown("""
    #<div style="text-align: center; padding: 2rem; background: rgba(255,255,255,0.1); border-radius: 10px; margin-top: 2rem;">
      #  <p style="color: white; font-size: 1rem;">
     #       👨‍💼 <strong>Admin Panel</strong> | Toonify Analytics Dashboard | Real-time Monitoring
      #  </p>
      #  <p style="color: #ddd; font-size: 0.9rem;">
       #     Last Updated: {current_time} | System Status: ✅ Operational
       # </p>
    #</div>
   # """.format(current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')), unsafe_allow_html=True)