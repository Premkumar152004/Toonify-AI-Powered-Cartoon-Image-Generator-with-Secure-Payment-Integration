"""
Automated setup script for Toonify project
Run this after creating all the necessary files
"""
import os
import sys
import subprocess


def create_directories():
    """Create necessary directories"""
    directories = [
        'data',
        'data/user_images',
        'utils',
        'pages',
        '.streamlit',
        'assets'
    ]
    
    print("Creating directories...")
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created: {directory}")
    
    # Create __init__.py files
    init_files = ['utils/__init__.py', 'pages/__init__.py']
    for init_file in init_files:
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write("# Auto-generated __init__.py\n")
            print(f"✓ Created: {init_file}")


def check_python_version():
    """Check if Python version is compatible"""
    print("\nChecking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
    return True


def check_files():
    """Check if all required files exist"""
    print("\nChecking required files...")
    required_files = [
        'requirements.txt',
        'app.py',
        'utils/validators.py',
        'utils/database.py',
        'utils/auth.py',
        'utils/image_processor.py',
        '.streamlit/config.toml'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ Found: {file}")
        else:
            print(f"❌ Missing: {file}")
            missing_files.append(file)
    
    if missing_files:
        print("\n⚠️  Please create the missing files before running setup")
        return False
    return True


def install_dependencies():
    """Install Python dependencies"""
    print("\nInstalling dependencies...")
    print("This may take a few minutes...\n")
    
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("\n✓ All dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("\n❌ Error installing dependencies")
        return False


def verify_installation():
    """Verify that key packages are installed"""
    print("\nVerifying installation...")
    packages = ['streamlit', 'cv2', 'pandas', 'numpy', 'PIL', 'bcrypt']
    
    all_installed = True
    for package in packages:
        try:
            if package == 'cv2':
                __import__('cv2')
            elif package == 'PIL':
                __import__('PIL')
            else:
                __import__(package)
            print(f"✓ {package} installed")
        except ImportError:
            print(f"❌ {package} not found")
            all_installed = False
    
    return all_installed


def main():
    """Main setup function"""
    print("=" * 60)
    print("🎨 Toonify Project Setup")
    print("=" * 60)
    
    # Step 1: Check Python version
    if not check_python_version():
        return
    
    # Step 2: Create directories
    create_directories()
    
    # Step 3: Check files
    if not check_files():
        return
    
    # Step 4: Ask user if they want to install dependencies
    print("\n" + "=" * 60)
    response = input("Install dependencies from requirements.txt? (y/n): ")
    
    if response.lower() == 'y':
        if install_dependencies():
            verify_installation()
    else:
        print("Skipping dependency installation")
    
    # Final instructions
    print("\n" + "=" * 60)
    print("✅ Setup Complete!")
    print("=" * 60)
    print("\nTo run the application:")
    print("  1. Activate virtual environment (if using one)")
    print("  2. Run: streamlit run app.py")
    print("\nThe application will start at: http://localhost:8501")
    print("\nFor detailed instructions, see README.md")
    print("=" * 60)


if __name__ == "__main__":
    main()