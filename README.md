🎨 AI-Based Image Transformation Tool for Cartoon & Anime Effect Generation
📌 Project Title

AI-Based Image Transformation Tool for Cartoon & Anime Effect Generation

👨‍💻 Developed By

Prem Kumar R
November Batch – 2025

📖 Project Description

This project is a web-based AI image transformation system that converts real-world images into cartoon and anime-style images using computer vision and deep learning models.

The application supports:

Cartoon image generation

Anime-style image transformation using AnimeGAN

Multiple anime styles (Ghibli, Hayao, Paprika, Shinkai)

User authentication

Admin dashboard

Payment system integration

Image history management

The application is built using Python, Streamlit, OpenCV, and ONNX deep learning models.

🎯 Objectives

Convert real images into cartoon/anime effects

Implement AI-based image processing

Provide a user-friendly web interface

Secure user authentication and admin access

Store user data and image history

Demonstrate real-world AI application

🚀 Features
🖼️ Image Transformation

Cartoon image conversion

Anime image generation using AnimeGAN

Multiple anime styles:

Ghibli

Hayao

Paprika

Shinkai

👤 User Management

User registration & login

Secure password hashing

Session-based authentication

🛠️ Admin Dashboard

View registered users

Monitor image usage

Control system access

💳 Payment System

Payment database handling

Payment engine logic

Controlled access to premium features

📂 Data Handling

Image upload & processing

Image history storage

SQLite database integration

🧠 Technologies Used
Programming Language

Python

Frameworks & Libraries

Streamlit

OpenCV

NumPy

PIL (Pillow)

SQLite3

ONNX Runtime

Hashlib

AI Models

AnimeGAN (.onnx models)

Tools

Git & GitHub

VS Code

Python Virtual Environment

🏗️ Project Folder Structure (From ZIP)
AI-Based-Image-Transformation-Tool-for-Cartoon-Effect-Generation/
│
├── app.py                     # Main Streamlit application
├── admin_dashboard.py          # Admin panel
├── setup.py                    # Project setup
├── requirements.txt            # Dependencies
├── README.md                   # Documentation
│
├── anime_models/               # Deep learning models
│   ├── Ghibli.onnx
│   ├── Hayao.onnx
│   ├── Paprika.onnx
│   └── Shinkai.onnx
│
├── assets/
│   ├── picc.jpg
│   └── backgrounds/
│
├── utils/
│   ├── auth.py                 # Authentication logic
│   ├── database.py             # User & image database
│   ├── validators.py           # Input validation
│   ├── image_processor.py      # Cartoon image processing
│   ├── animegan_processor.py   # AnimeGAN image processing
│   ├── cartoon.py              # Cartoon filters
│   ├── ghibli.py               # Ghibli style handler
│   ├── Shinkai.py              # Shinkai style handler
│
├── payment_system/
│   ├── payment_engine.py       # Payment logic
│   └── payment_db.py           # Payment database
│
└── __pycache__/                # Compiled Python files

⚙️ Installation & Execution
1️⃣ Clone Repository
git clone https://github.com/your-username/AI-Based-Image-Transformation-Tool.git
cd AI-Based-Image-Transformation-Tool

2️⃣ Create Virtual Environment
python -m venv venv

3️⃣ Activate Virtual Environment

Windows

venv\Scripts\activate


Linux / Mac

source venv/bin/activate

4️⃣ Install Dependencies
pip install -r requirements.txt

5️⃣ Run the Application
streamlit run app.py

⚙️ How the System Works

User logs in or registers

Image is uploaded through Streamlit UI

User selects:

Cartoon effect OR

Anime style (Ghibli / Hayao / Paprika / Shinkai)

Image is processed using:

OpenCV filters (cartoon)

AnimeGAN ONNX models (anime)

Transformed image is displayed

Image and usage data are stored in database

🗄️ Database Details

SQLite database used

Stores:

User credentials

Image history

Payment records

Passwords stored using hashed encryption

🔐 Security Implementation

SHA-256 password hashing

Session-based login validation

Admin-only dashboard access

Input validation to prevent misuse

🎓 Learning Outcomes

Hands-on experience with AI image processing

Integration of deep learning models

Web application development using Streamlit

Database management using SQLite

Secure authentication implementation

Real-world AI project deployment

📈 Future Enhancements

More anime styles

GAN-based high-resolution models

Cloud deployment

Mobile app version

User profile dashboard

Real payment gateway integration

📜 License

This project is developed strictly for educational, academic, and internship purposes.
Free to use and modify for learning.

🙏 Acknowledgement

I would like to thank my mentors and institution for their guidance and support throughout the development of this project.