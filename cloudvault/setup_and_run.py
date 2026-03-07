#!/usr/bin/env python3
"""
CloudVault Setup Script
Run this to set up and start the Django server.
"""
import subprocess
import sys
import os

def run(cmd, check=True):
    print(f"  → {cmd}")
    result = subprocess.run(cmd, shell=True, check=check)
    return result.returncode == 0

print("\n╔══════════════════════════════════════╗")
print("║         CloudVault Setup             ║")
print("╚══════════════════════════════════════╝\n")

# Check Python
print("📦 Installing dependencies...")
run("pip install django pillow")

print("\n🗄️  Setting up database...")
os.chdir(os.path.dirname(os.path.abspath(__file__)))
run("python manage.py migrate")

print("\n✅ Setup complete!")
print("\n🚀 Starting CloudVault server...")
print("   Open http://127.0.0.1:8000 in your browser\n")
run("python manage.py runserver")
