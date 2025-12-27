"""
Quick Setup Script
Installs dependencies and trains the model
"""

import subprocess
import sys
import os

def install_requirements():
    """Install Python dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def train_model():
    """Train the ML model"""
    print("\nTraining ML model...")
    try:
        subprocess.check_call([sys.executable, "train_model.py"])
        print("✅ Model trained successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to train model")
        return False

def main():
    print("=" * 60)
    print("AI-Based Fake News Detection System - Setup")
    print("=" * 60)
    
    # Install dependencies
    if not install_requirements():
        print("\nSetup failed. Please install dependencies manually:")
        print("pip install -r requirements.txt")
        return
    
    # Train model
    print("\n" + "=" * 60)
    response = input("Do you want to train the ML model now? (y/n): ")
    if response.lower() == 'y':
        train_model()
    else:
        print("\nYou can train the model later by running:")
        print("python train_model.py")
    
    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print("\nTo start the application, run:")
    print("python app.py")
    print("\nThen open: http://localhost:5000")

if __name__ == '__main__':
    main()

