"""
Diagnostic Script - Check .env Configuration
Run this to diagnose email credential issues
"""

import os
from dotenv import load_dotenv

print("="*70)
print("🔍 SOW AUDITOR - EMAIL CONFIGURATION DIAGNOSTIC")
print("="*70)

# Load .env file
print("\n1. Loading .env file...")
load_dotenv()
print("   ✅ load_dotenv() executed")

# Check if .env file exists
env_path = os.path.join(os.getcwd(), '.env')
if os.path.exists(env_path):
    print(f"   ✅ .env file found at: {env_path}")
else:
    print(f"   ❌ .env file NOT FOUND at: {env_path}")
    print("   ⚠️  YOU NEED TO CREATE .env FILE!")

# Check environment variables
print("\n2. Checking environment variables...")

smtp_server = os.getenv('SMTP_SERVER')
smtp_port = os.getenv('SMTP_PORT')
smtp_email = os.getenv('SMTP_EMAIL')
smtp_password = os.getenv('SMTP_PASSWORD')
deepseek_key = os.getenv('DEEPSEEK_API_KEY')

print(f"   SMTP_SERVER: {smtp_server if smtp_server else '❌ NOT SET'}")
print(f"   SMTP_PORT: {smtp_port if smtp_port else '❌ NOT SET'}")
print(f"   SMTP_EMAIL: {smtp_email if smtp_email else '❌ NOT SET'}")
print(f"   SMTP_PASSWORD: {'✅ SET (' + smtp_password[:4] + '****' + ')' if smtp_password else '❌ NOT SET'}")
print(f"   DEEPSEEK_API_KEY: {'✅ SET (' + deepseek_key[:10] + '...' + ')' if deepseek_key else '❌ NOT SET'}")

# Diagnosis
print("\n3. Diagnosis:")
print("="*70)

if not smtp_email or not smtp_password:
    print("❌ PROBLEM FOUND: Email credentials not configured!")
    print("\n📋 SOLUTION:")
    print("   Create .env file in project root with this content:")
    print("\n" + "-"*70)
    print("""# Deepseek AI API Configuration
DEEPSEEK_API_KEY=sk-26fa459920364a71bdc5fe9df0709762

# Email Configuration (Gmail SMTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=ashishtech1312@gmail.com
SMTP_PASSWORD=fvxwxqjeQItnb2md

# Application Settings
APP_NAME=SOW Auditor
APP_VERSION=2.0""")
    print("-"*70)
    print("\n💡 Save this as: .env (with dot at start, no .txt)")
    print(f"   Location: {os.getcwd()}\\.env")
else:
    print("✅ All email credentials are properly configured!")
    print("   Email should work correctly.")

print("\n" + "="*70)
print("Press Enter to exit...")
input()
