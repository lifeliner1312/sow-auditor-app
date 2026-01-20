"""
Gmail SMTP Connection Checker
Tests your Gmail SMTP credentials and diagnoses connection issues
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import sys

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

def test_env_file():
    """Test 1: Check if .env file exists and has required variables"""
    print_header("TEST 1: Checking .env File")

    if not os.path.exists('.env'):
        print_error(".env file not found in current directory!")
        print_info("Current directory: " + os.getcwd())
        print_warning("Create a .env file with your Gmail credentials")
        return False

    print_success(".env file found")

    # Load environment variables
    load_dotenv()

    # Check required variables
    required_vars = ['SMTP_SERVER', 'SMTP_PORT', 'SMTP_EMAIL', 'SMTP_PASSWORD']
    missing_vars = []

    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            print_error(f"{var} is missing or empty")
        else:
            if var == 'SMTP_PASSWORD':
                # Mask password
                masked = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '*' * len(value)
                print_success(f"{var} = {masked} (length: {len(value)} characters)")
            else:
                print_success(f"{var} = {value}")

    if missing_vars:
        print_error(f"Missing variables: {', '.join(missing_vars)}")
        return False

    return True

def test_smtp_connection():
    """Test 2: Test basic SMTP connection to Gmail"""
    print_header("TEST 2: Testing SMTP Connection to Gmail")

    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', 587))

    print_info(f"Connecting to {smtp_server}:{smtp_port}...")

    try:
        # Create SMTP session
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        print_success(f"Connected to {smtp_server}:{smtp_port}")

        # Get server response
        response = server.ehlo()
        print_success(f"Server responded: {response[1].decode()[:50]}...")

        server.quit()
        return True

    except smtplib.SMTPConnectError as e:
        print_error(f"Connection failed: {str(e)}")
        print_warning("Check if port 587 is blocked by firewall")
        return False
    except Exception as e:
        print_error(f"Connection error: {str(e)}")
        return False

def test_starttls():
    """Test 3: Test STARTTLS (encryption)"""
    print_header("TEST 3: Testing STARTTLS Encryption")

    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', 587))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        server.ehlo()

        print_info("Starting TLS encryption...")
        server.starttls()
        print_success("TLS encryption started successfully")

        server.ehlo()
        print_success("Re-identified after STARTTLS")

        server.quit()
        return True

    except Exception as e:
        print_error(f"STARTTLS failed: {str(e)}")
        print_warning("Gmail requires TLS encryption")
        return False

def test_authentication():
    """Test 4: Test authentication with credentials"""
    print_header("TEST 4: Testing Authentication")

    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_email = os.getenv('SMTP_EMAIL')
    smtp_password = os.getenv('SMTP_PASSWORD')

    print_info(f"Authenticating as: {smtp_email}")
    print_info(f"Password length: {len(smtp_password)} characters")

    try:
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        server.ehlo()
        server.starttls()
        server.ehlo()

        print_info("Attempting login...")
        server.login(smtp_email, smtp_password)
        print_success("✨ Authentication successful! Your credentials are correct.")

        server.quit()
        return True

    except smtplib.SMTPAuthenticationError as e:
        print_error(f"Authentication FAILED: {str(e)}")
        print_warning("\nPossible causes:")
        print_warning("1. App Password is incorrect or expired")
        print_warning("2. You're using regular password instead of App Password")
        print_warning("3. 2-Factor Authentication is not enabled")
        print_warning("4. Wrong email address")
        print_warning("5. Spaces in the App Password (remove them)")
        print_info("\nGenerate new App Password: https://myaccount.google.com/apppasswords")
        return False

    except Exception as e:
        print_error(f"Login error: {str(e)}")
        return False

def test_send_test_email():
    """Test 5: Send actual test email"""
    print_header("TEST 5: Sending Test Email")

    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_email = os.getenv('SMTP_EMAIL')
    smtp_password = os.getenv('SMTP_PASSWORD')

    recipient = input(f"\nEnter recipient email (or press Enter to send to yourself): ").strip()
    if not recipient:
        recipient = smtp_email

    print_info(f"Sending test email to: {recipient}")

    try:
        # Create message
        message = MIMEMultipart()
        message['From'] = smtp_email
        message['To'] = recipient
        message['Subject'] = "✅ Gmail SMTP Test - Connection Successful!"

        body = f"""
This is a test email from the Gmail SMTP Connection Checker.

✅ Your Gmail SMTP configuration is working correctly!

Configuration Details:
- SMTP Server: {smtp_server}
- SMTP Port: {smtp_port}
- Email: {smtp_email}
- Encryption: TLS (STARTTLS)

If you received this email, your SOW Auditor app should be able to send emails successfully.

---
Sent from Gmail SMTP Connection Checker
"""

        message.attach(MIMEText(body, 'plain'))

        # Connect and send
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(smtp_email, smtp_password)

        print_info("Sending email...")
        server.send_message(message)
        server.quit()

        print_success(f"✨ Test email sent successfully to {recipient}!")
        print_info("Check your inbox (and spam folder)")
        return True

    except Exception as e:
        print_error(f"Failed to send email: {str(e)}")
        return False

def show_diagnostics():
    """Show diagnostic information"""
    print_header("DIAGNOSTIC INFORMATION")

    print_info("Python version: " + sys.version.split()[0])
    print_info("Current directory: " + os.getcwd())
    print_info("Operating System: " + sys.platform)

    # Check if .env exists
    env_exists = os.path.exists('.env')
    if env_exists:
        print_success(".env file exists")
        print_info(f".env file path: {os.path.abspath('.env')}")
    else:
        print_error(".env file not found")

    # Check environment variables
    load_dotenv()
    smtp_email = os.getenv('SMTP_EMAIL')
    smtp_password = os.getenv('SMTP_PASSWORD')

    if smtp_password:
        print_info(f"Password format check:")
        has_spaces = ' ' in smtp_password
        if has_spaces:
            print_error("  ❌ Password contains SPACES - remove them!")
        else:
            print_success("  ✅ No spaces in password")

        print_info(f"  Length: {len(smtp_password)} characters")

        if len(smtp_password) == 16:
            print_success("  ✅ Correct length for Gmail App Password")
        else:
            print_warning(f"  ⚠️  Gmail App Passwords are usually 16 characters")

def main():
    """Main execution"""
    print_header("📧 Gmail SMTP Connection Checker")
    print_info("This tool will test your Gmail SMTP configuration step by step\n")

    # Run all tests
    test_results = []

    # Test 1: .env file
    result1 = test_env_file()
    test_results.append(("ENV File", result1))

    if not result1:
        print_error("\n❌ Cannot proceed without .env file")
        print_info("\nCreate a .env file with:")
        print("""
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
""")
        show_diagnostics()
        return

    # Test 2: SMTP connection
    result2 = test_smtp_connection()
    test_results.append(("SMTP Connection", result2))

    if not result2:
        print_error("\n❌ Cannot connect to Gmail SMTP server")
        print_warning("Check your internet connection and firewall settings")
        show_diagnostics()
        return

    # Test 3: STARTTLS
    result3 = test_starttls()
    test_results.append(("STARTTLS", result3))

    if not result3:
        print_error("\n❌ TLS encryption failed")
        show_diagnostics()
        return

    # Test 4: Authentication
    result4 = test_authentication()
    test_results.append(("Authentication", result4))

    if not result4:
        print_error("\n❌ Authentication failed - THIS IS YOUR PROBLEM!")
        print_warning("\n📋 SOLUTION STEPS:")
        print("1. Go to: https://myaccount.google.com/apppasswords")
        print("2. Sign in to your Gmail account")
        print("3. Generate NEW App Password:")
        print("   - Select app: Mail")
        print("   - Select device: Other (Custom name)")
        print("   - Name it: SOW Auditor")
        print("   - Click Generate")
        print("4. Copy the 16-character password (REMOVE SPACES!)")
        print("5. Update SMTP_PASSWORD in your .env file")
        print("6. Run this checker again")
        show_diagnostics()
        return

    # Test 5: Send test email
    print_success("\n✨ All authentication tests passed!")

    send_test = input("\nDo you want to send a test email? (y/n): ").strip().lower()
    if send_test == 'y':
        result5 = test_send_test_email()
        test_results.append(("Send Test Email", result5))

    # Summary
    print_header("TEST SUMMARY")

    for test_name, result in test_results:
        if result:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")

    all_passed = all(result for _, result in test_results if result is not None)

    if all_passed:
        print_success("\n✨ ALL TESTS PASSED! Your Gmail SMTP is configured correctly.")
        print_info("Your SOW Auditor app should now be able to send emails.")
    else:
        print_error("\n❌ Some tests failed. Fix the issues above and try again.")

    print_info("\nChecker completed.\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nChecker interrupted by user.")
    except Exception as e:
        print_error(f"\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
