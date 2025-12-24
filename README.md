# 🎨 AI-Based Image Transformation Tool

Convert real-world images into stunning cartoon and anime-style artwork using advanced deep learning models.



## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Demo](#demo)
- [Technologies](#technologies)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [Security](#security)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## 🌟 Overview

This web-based AI image transformation system leverages computer vision and deep learning to convert photographs into cartoon and anime-style images. Built with Python and Streamlit, it provides an intuitive interface for users to explore various artistic styles powered by AnimeGAN models.

### Key Capabilities

- **Cartoon Conversion**: Transform images using OpenCV-based filters
- **Anime Style Transfer**: Apply multiple anime aesthetics using pre-trained AnimeGAN models
- **User Management**: Secure authentication and personalized image history
- **Admin Dashboard**: Monitor system usage and manage users
- **Payment Integration**: Premium feature access control

---

## ✨ Features

### Image Transformation
- **Cartoon Effect**: Edge detection and bilateral filtering for cartoon-style images
- **Anime Styles**: Four distinct anime aesthetics
  - 🎭 **Ghibli**: Studio Ghibli-inspired watercolor style
  - 🌸 **Hayao**: Classic Miyazaki animation style
  - 🎨 **Paprika**: Vibrant and surreal artistic style
  - 🌅 **Shinkai**: Makoto Shinkai's signature lighting and atmosphere

### User Features
- Secure registration and login system
- Password encryption using SHA-256 hashing
- Session-based authentication
- Personal image history and gallery
- Image upload and download capabilities

### Admin Features
- User management dashboard
- Usage analytics and monitoring
- System access control
- Database administration

### Payment System
- Payment record tracking
- Premium feature access control
- Transaction history management

---

## 🎥 Demo

> Add screenshots or GIFs of your application here

```
[Before Image] --> [Processing] --> [After Image]
```

---

## 🛠️ Technologies

### Core Technologies
| Technology | Purpose |
|------------|---------|
| **Python 3.8+** | Primary programming language |
| **Streamlit** | Web application framework |
| **OpenCV** | Image processing and computer vision |
| **ONNX Runtime** | Deep learning model inference |
| **SQLite3** | Database management |

### Libraries & Dependencies
- **NumPy**: Numerical computing
- **Pillow (PIL)**: Image manipulation
- **Hashlib**: Secure password hashing
- **AnimeGAN Models**: Pre-trained ONNX models for anime style transfer

---

## 📥 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/AI-Based-Image-Transformation-Tool.git
cd AI-Based-Image-Transformation-Tool
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Download Models
Ensure all ONNX models are present in the `anime_models/` directory:
- Ghibli.onnx
- Hayao.onnx
- Paprika.onnx
- Shinkai.onnx

### Step 5: Run Setup (Optional)
```bash
python setup.py
```

---

## 🚀 Usage

### Starting the Application
```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

### Basic Workflow

1. **Register/Login**: Create an account or log in with existing credentials
2. **Upload Image**: Select an image from your device (JPEG, PNG)
3. **Choose Style**: Select either cartoon effect or one of the anime styles
4. **Process**: Click the transform button to apply the effect
5. **Download**: Save your transformed image to your device

### Admin Access
```bash
streamlit run admin_dashboard.py
```
Default admin credentials should be configured during setup.

---

## 📂 Project Structure

```
AI-Based-Image-Transformation-Tool/
│
├── app.py                          # Main application entry point
├── admin_dashboard.py              # Admin panel interface
├── setup.py                        # Initial setup script
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
│
├── anime_models/                   # Pre-trained ONNX models
│   ├── Ghibli.onnx
│   ├── Hayao.onnx
│   ├── Paprika.onnx
│   └── Shinkai.onnx
│
├── assets/                         # Static assets
│   ├── picc.jpg
│   └── backgrounds/
│
├── utils/                          # Utility modules
│   ├── auth.py                     # Authentication logic
│   ├── database.py                 # Database operations
│   ├── validators.py               # Input validation
│   ├── image_processor.py          # Cartoon processing
│   ├── animegan_processor.py       # AnimeGAN processing
│   ├── cartoon.py                  # Cartoon filters
│   ├── ghibli.py                   # Ghibli style handler
│   └── Shinkai.py                  # Shinkai style handler
│
└── payment_system/                 # Payment module
    ├── payment_engine.py           # Payment logic
    └── payment_db.py               # Payment database
```

---

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Image History Table
```sql
CREATE TABLE image_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    original_image BLOB,
    transformed_image BLOB,
    style TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Payments Table
```sql
CREATE TABLE payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount DECIMAL(10,2),
    status TEXT,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## 🔐 Security

This application implements multiple security measures:

- **Password Hashing**: SHA-256 encryption for all passwords
- **Session Management**: Secure session-based authentication
- **Input Validation**: Sanitization of user inputs to prevent injection attacks
- **Role-Based Access**: Separate permissions for users and administrators
- **SQL Injection Prevention**: Parameterized queries for database operations

---

## 🚀 Future Enhancements

- [ ] Additional anime and cartoon styles
- [ ] GAN-based super-resolution for higher quality outputs
- [ ] Batch processing capabilities
- [ ] Cloud deployment (AWS/GCP/Azure)
- [ ] Mobile application (React Native/Flutter)
- [ ] User profile customization
- [ ] Real payment gateway integration (Stripe/PayPal)
- [ ] Social sharing features
- [ ] API endpoint for third-party integration
- [ ] Advanced image editing tools

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Contribution Guidelines
- Follow PEP 8 style guide for Python code
- Add comments and docstrings for new functions
- Update documentation for new features
- Write unit tests for critical functionality

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Note**: This project is developed for educational and academic purposes. The AnimeGAN models used are subject to their respective licenses.

---

## 🙏 Acknowledgments

- **Developer**: Prem Kumar R (November Batch – 2025)
- **AnimeGAN**: Original model developers for anime style transfer
- **OpenCV Community**: For computer vision tools and resources
- **Streamlit Team**: For the excellent web framework
- Special thanks to mentors and instructors for guidance and support



<div align="center">
Made with ❤️ by Prem Kumar R
</div>