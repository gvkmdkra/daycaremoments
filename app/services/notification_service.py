"""
Notification Service - Email, SMS, and Voice Call notifications
Handles automated notifications for enrollment, daily updates, etc.
"""

import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

class NotificationService:
    def __init__(self):
        # Email configuration
        self.email_host = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
        self.email_port = int(os.getenv('EMAIL_PORT', 465))
        self.email_user = os.getenv('EMAIL_HOST_USER')
        self.email_password = os.getenv('EMAIL_HOST_PASSWORD')
        self.email_from = os.getenv('EMAIL_FROM_ADDRESS', 'noreply@daycaremoments.com')

        # Twilio configuration
        self.twilio_enabled = os.getenv('TWILIO_ENABLED', 'true').lower() == 'true'
        self.twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')

        self.twilio_client = None
        if self.twilio_enabled and self.twilio_account_sid and self.twilio_auth_token:
            try:
                from twilio.rest import Client
                self.twilio_client = Client(self.twilio_account_sid, self.twilio_auth_token)
            except ImportError:
                print("Twilio not installed. Install with: pip install twilio")
            except Exception as e:
                print(f"Twilio initialization error: {e}")

    def send_enrollment_email(self, parent_email, parent_name, child_name, temp_password):
        """Send enrollment welcome email to parent"""
        try:
            subject = f"Welcome to DaycareMoments - {child_name} Enrolled!"

            html_body = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                              color: white; padding: 30px; text-align: center; border-radius: 10px; }}
                    .content {{ background: #f9f9f9; padding: 30px; margin-top: 20px; border-radius: 10px; }}
                    .credentials {{ background: white; padding: 20px; border-left: 4px solid #667eea; margin: 20px 0; }}
                    .button {{ display: inline-block; background: #667eea; color: white;
                             padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ text-align: center; color: #999; margin-top: 30px; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>👶 DaycareMoments</h1>
                        <h2>Welcome to Our Family!</h2>
                    </div>

                    <div class="content">
                        <p>Dear {parent_name},</p>

                        <p>Congratulations! <strong>{child_name}</strong> has been successfully enrolled in our daycare.</p>

                        <p>Your parent account has been created. You can now:</p>
                        <ul>
                            <li>📸 View your child's daily photos</li>
                            <li>🤖 Read AI-generated activity descriptions</li>
                            <li>📥 Download and share special moments</li>
                            <li>📊 Track your child's activities</li>
                        </ul>

                        <div class="credentials">
                            <h3>🔐 Your Login Credentials</h3>
                            <p><strong>Email:</strong> {parent_email}</p>
                            <p><strong>Temporary Password:</strong> {temp_password}</p>
                            <p><em>⚠️ Please change your password after first login for security.</em></p>
                        </div>

                        <a href="http://localhost:8501" class="button">🚀 Login to Parent Portal</a>

                        <h3>📱 What's Next?</h3>
                        <ol>
                            <li>Click the button above to login</li>
                            <li>Change your password in settings</li>
                            <li>Start viewing your child's daily moments!</li>
                        </ol>

                        <p>Our staff will begin uploading photos of {child_name}'s activities throughout the day.</p>

                        <p>If you have any questions, please don't hesitate to contact us.</p>

                        <p>Best regards,<br>
                        <strong>The DaycareMoments Team</strong></p>
                    </div>

                    <div class="footer">
                        <p>© 2025 DaycareMoments | AI-Powered Daycare Management</p>
                        <p>Made with ❤️ for parents and daycares</p>
                    </div>
                </div>
            </body>
            </html>
            """

            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_from
            msg['To'] = parent_email

            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)

            with smtplib.SMTP_SSL(self.email_host, self.email_port) as server:
                server.login(self.email_user, self.email_password)
                server.send_message(msg)

            return True, "Email sent successfully"
        except Exception as e:
            return False, f"Email error: {str(e)}"

    def send_enrollment_sms(self, parent_phone, child_name, portal_url="http://localhost:8501"):
        """Send SMS notification to parent"""
        if not self.twilio_client:
            return False, "Twilio not configured"

        try:
            message_body = f"""🎉 Welcome to DaycareMoments!

{child_name} has been enrolled. Your parent account is ready!

Login now: {portal_url}

Check your email for credentials.

-DaycareMoments Team"""

            message = self.twilio_client.messages.create(
                body=message_body,
                from_=self.twilio_phone_number,
                to=parent_phone
            )

            return True, f"SMS sent: {message.sid}"
        except Exception as e:
            return False, f"SMS error: {str(e)}"

    def make_enrollment_call(self, parent_phone, child_name, parent_name):
        """Make automated voice call to parent"""
        if not self.twilio_client:
            return False, "Twilio not configured"

        try:
            # TwiML for voice message
            twiml_url = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">
        Hello {parent_name}! This is DaycareMoments calling.

        We're excited to inform you that {child_name} has been successfully enrolled in our daycare.

        Your parent account has been created. Please check your email for login credentials and access the parent portal to view your child's daily moments.

        Welcome to the DaycareMoments family! If you have any questions, please contact our staff.

        Thank you, and have a wonderful day!
    </Say>
</Response>"""

            # For demo, we'll use a simple greeting
            # In production, you'd host the TwiML on a server
            call = self.twilio_client.calls.create(
                twiml=f'<Response><Say voice="alice">Hello {parent_name}! This is DaycareMoments. {child_name} has been successfully enrolled. Please check your email for login credentials. Welcome to DaycareMoments family!</Say></Response>',
                to=parent_phone,
                from_=self.twilio_phone_number
            )

            return True, f"Call initiated: {call.sid}"
        except Exception as e:
            return False, f"Call error: {str(e)}"

    def send_complete_enrollment_notification(self, parent_email, parent_name, parent_phone,
                                             child_name, temp_password):
        """
        Send all notifications: Email, SMS, and Voice Call
        Returns a dict with status of each notification type
        """
        results = {
            'email': {'sent': False, 'message': ''},
            'sms': {'sent': False, 'message': ''},
            'call': {'sent': False, 'message': ''}
        }

        # Send Email
        email_success, email_msg = self.send_enrollment_email(
            parent_email, parent_name, child_name, temp_password
        )
        results['email'] = {'sent': email_success, 'message': email_msg}

        # Send SMS (if phone number provided)
        if parent_phone:
            sms_success, sms_msg = self.send_enrollment_sms(parent_phone, child_name)
            results['sms'] = {'sent': sms_success, 'message': sms_msg}

            # Make Voice Call (if phone number provided)
            call_success, call_msg = self.make_enrollment_call(parent_phone, child_name, parent_name)
            results['call'] = {'sent': call_success, 'message': call_msg}

        return results


# Singleton instance
_notification_service = None

def get_notification_service():
    """Get singleton notification service instance"""
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service
