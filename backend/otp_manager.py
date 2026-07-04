import random
import smtplib
from email.mime.text import MIMEText
from dotenv import dotenv_values

config = dotenv_values(".env")

class OTPManager:
    def __init__(self):
        
        self.otp_store = {}

    def generate_otp(self, user_id):
        otp = str(random.randint(100000, 999999))
        self.otp_store[user_id] = otp
        return otp

    def validate_otp(self, user_id, otp):
        return self.otp_store.get(user_id) == otp

    def send_email(self, to_email, otp):
        from_email = config.get("EMAIL_FROM")
        email_password = config.get("EMAIL_PASSWORD")
        smtp_user = config.get("SMTP_USER")
        smtp_server = config.get("SMTP_SERVER")
        smtp_port = int(config.get("SMTP_PORT", 587))

        msg = MIMEText(f"Your OTP for complaint submission is: {otp}")
        msg['Subject'] = 'Your Complaint OTP Verification'
        msg['From'] = from_email
        msg['To'] = to_email

        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            
            server.login(smtp_user, email_password)
            server.sendmail(from_email, [to_email], msg.as_string())
