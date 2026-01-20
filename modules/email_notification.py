"""
Email Notification Module - FIXED VERSION
Sends audit reports via email with PDF attachments using SMTP

✅ FIX: Added proper EHLO handshakes (same as working gmail_smtp_checker.py)
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class EmailNotifier:
    """Handle email notifications for SOW audit reports"""

    def __init__(self):
        """Initialize email configuration from environment variables"""
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_email = os.getenv('SMTP_EMAIL', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')

        # Validate configuration
        if not self.smtp_email or not self.smtp_password:
            print("⚠️ Warning: SMTP credentials not configured in .env file")

    def send_email_with_attachment(self, recipient_email, subject, pdf_path,
                                   compliance_score, project_name, analysis):
        """
        Send email with PDF attachment via SMTP

        Args:
            recipient_email: Email address to send to
            subject: Email subject line
            pdf_path: Path to PDF report file
            compliance_score: Overall compliance score
            project_name: Name of the project
            analysis: Analysis results dictionary

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate SMTP configuration
            if not self.smtp_email or not self.smtp_password:
                raise Exception(
                    "SMTP credentials not configured.\n\n"
                    "Please add to .env file:\n"
                    "SMTP_SERVER=smtp.gmail.com\n"
                    "SMTP_PORT=587\n"
                    "SMTP_EMAIL=your-email@gmail.com\n"
                    "SMTP_PASSWORD=your-app-password"
                )

            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.smtp_email
            msg['To'] = recipient_email
            msg['Subject'] = subject

            # Calculate metrics
            total_pillars = len(analysis.get('pillars', []))
            met_pillars = sum(1 for p in analysis['pillars'] if p.get('status') == 'Met')
            critical_issues = sum(1 for p in analysis['pillars'] 
                                if p.get('risk_level', p.get('risklevel')) == 'Critical')
            high_issues = sum(1 for p in analysis['pillars'] 
                            if p.get('risk_level', p.get('risklevel')) == 'High')

            # Create email body
            body = f"""
Dear Stakeholder,

Please find attached the SOW (Statement of Work) Audit Report for {project_name}.

═══════════════════════════════════════════════════════════════
📊 AUDIT SUMMARY
═══════════════════════════════════════════════════════════════

Project Name: {project_name}
Overall Compliance: {compliance_score}%
Audit Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p IST')}

═══════════════════════════════════════════════════════════════
📈 KEY METRICS
═══════════════════════════════════════════════════════════════

Total Pillars Reviewed: {total_pillars}
Pillars Met: {met_pillars}
Partial Compliance: {sum(1 for p in analysis['pillars'] if p.get('status') == 'Partial')}
Not Met: {sum(1 for p in analysis['pillars'] if p.get('status') == 'Not Met')}
Critical Issues: {critical_issues}
High Risk Items: {high_issues}

═══════════════════════════════════════════════════════════════
🎯 COMPLIANCE STATUS
═══════════════════════════════════════════════════════════════
"""

            # Add pillar status
            for idx, pillar in enumerate(analysis.get('pillars', []), 1):
                status_icon = "✅" if pillar.get('status') == 'Met' else "⚠️" if pillar.get('status') == 'Partial' else "❌"
                risk = pillar.get('risk_level', pillar.get('risklevel', 'Low'))
                body += f"\n{status_icon} {pillar.get('name', 'Unknown')} - {pillar.get('status', 'Unknown')} ({risk} Risk)"

            body += f"""

═══════════════════════════════════════════════════════════════

📎 The detailed PDF audit report is attached to this email.

For any questions or clarifications, please reply to this email.

Best regards,
SOW Auditor v2.0
Automated Divestment Audit System

═══════════════════════════════════════════════════════════════
⚙️ Generated by SOW Auditor v2.0 | Powered by Deepseek AI
═══════════════════════════════════════════════════════════════
"""

            # Attach body
            msg.attach(MIMEText(body, 'plain'))

            # Attach PDF
            if os.path.exists(pdf_path):
                with open(pdf_path, 'rb') as f:
                    pdf_attachment = MIMEApplication(f.read(), _subtype='pdf')
                    pdf_attachment.add_header(
                        'Content-Disposition',
                        'attachment',
                        filename=os.path.basename(pdf_path)
                    )
                    msg.attach(pdf_attachment)
            else:
                raise Exception(f"PDF file not found: {pdf_path}")

            # ✨✨✨ FIX: Proper SMTP connection sequence (same as working checker) ✨✨✨
            print(f"📧 Connecting to {self.smtp_server}:{self.smtp_port}...")

            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10)

            # ✅ FIX 1: Initial EHLO handshake (MISSING in your old code!)
            server.ehlo()

            print("🔐 Starting TLS encryption...")
            server.starttls()

            # ✅ FIX 2: Re-identify after STARTTLS (MISSING in your old code!)
            server.ehlo()

            print(f"🔐 Authenticating as {self.smtp_email}...")
            server.login(self.smtp_email, self.smtp_password)

            print(f"📤 Sending email to {recipient_email}...")
            server.send_message(msg)

            print("✅ Email sent successfully!")
            server.quit()

            return True

        except smtplib.SMTPAuthenticationError as e:
            raise Exception(
                f"SMTP Authentication Failed: {str(e)}\n\n"
                "For Gmail, you need an App Password:\n"
                "1. Go to https://myaccount.google.com/security\n"
                "2. Enable 2-Step Verification\n"
                "3. Go to App Passwords\n"
                "4. Generate new password for 'Mail'\n"
                "5. Use that password in SMTP_PASSWORD in .env"
            )
        except smtplib.SMTPException as e:
            raise Exception(f"SMTP Error: {str(e)}")
        except Exception as e:
            raise Exception(f"Email sending failed: {str(e)}")

    def send_notification(self, analysis, compliance_score, pdf_path):
        """
        Legacy method - kept for backwards compatibility
        Now requires recipient_email parameter
        """
        raise Exception(
            "Please use send_email_with_attachment() method instead.\n"
            "This method now requires recipient email address."
        )
