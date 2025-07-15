"""
Quick start script for LinkedIn Post Generator by Vacant Vectors
"""
import os
import subprocess
import sys

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def install_requirements():
    """Install required packages"""
    print("📦 Installing requirements...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def check_env_file():
    """Check if .env file exists"""
    if not os.path.exists('.env'):
        print("⚠️ .env file not found!")
        print("📝 Creating .env file from template...")
        
        if os.path.exists('.env.example'):
            # Copy .env.example to .env
            with open('.env.example', 'r') as src:
                with open('.env', 'w') as dst:
                    dst.write(src.read())
            print("✅ .env file created!")
            print("🔑 Please edit .env and add your GROQ_API_KEY")
            print("   Get your key from: https://console.groq.com/keys")
            return False
        else:
            print("❌ .env.example not found!")
            return False
    else:
        print("✅ .env file found")
        
        # Check if API key is set
        with open('.env', 'r') as f:
            content = f.read()
            if 'your_groq_api_key_here' in content or 'GROQ_API_KEY=' not in content:
                print("⚠️ Please add your GROQ_API_KEY to the .env file")
                return False
        print("✅ API key appears to be configured")
        return True

def run_tests():
    """Run functionality tests"""
    print("🧪 Running functionality tests...")
    try:
        subprocess.run([sys.executable, "test_functionality.py"], check=True)
        return True
    except subprocess.CalledProcessError:
        print("⚠️ Some tests failed, but the app might still work")
        return True
    except FileNotFoundError:
        print("⚠️ Test file not found, skipping tests")
        return True

def start_app():
    """Start the Streamlit app"""
    print("🚀 Starting the LinkedIn Post Generator...")
    print("📝 The app will open in your default web browser")
    print("🛑 Press Ctrl+C to stop the application")
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "main.py"])
    except KeyboardInterrupt:
        print("\n👋 Application stopped. Thanks for using Vacant Vectors LinkedIn Post Generator!")
    except FileNotFoundError:
        print("❌ Streamlit not found. Please install requirements first.")

def main():
    """Main quick start function"""
    print("🚀 Vacant Vectors LinkedIn Post Generator - Quick Start")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install requirements
    if not install_requirements():
        return
    
    # Check .env file
    env_ready = check_env_file()
    
    # Run tests
    run_tests()
    
    if env_ready:
        # Start the app
        start_app()
    else:
        print("\n📋 Next steps:")
        print("1. Edit the .env file and add your GROQ_API_KEY")
        print("2. Run this script again: python quickstart.py")
        print("   OR manually run: streamlit run main.py")

if __name__ == "__main__":
    main()
