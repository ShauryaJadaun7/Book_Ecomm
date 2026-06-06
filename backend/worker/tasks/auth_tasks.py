import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from worker.celery_app import celery_worker
from src.core.config import settings  # Access centralized settings matrix

@celery_worker.task(name="tasks.send_otp_email", max_retries=3, default_retry_delay=10)
def send_otp_email_task(email: str, otp: str) -> str:
    """
    Asynchronous Background Task: Spawns an explicit STARTTLS cryptographic 
    socket connection over Resend to deliver immediate authentication OTP codes.
    """
    try:
        print(f"📡 [RESEND SMTP CONNECTING] Transporting OTP challenge token to: {email}")

        # 1. Initialize the multipart email structural envelope
        message = MIMEMultipart("alternative")
        message["Subject"] = f"🔑 Your Verification Code: {otp}"
        
        # 🎯 BRAND ENHANCEMENT: Mask the sender using your verified Resend custom company domain email address
        # ye from me resend ka default email add kiya he , pehle jo tha vo placholder tha
        # esko baad me setting se replace karange , abhi to isko MERGE karna
        
        message["From"] = "LocalShelf Onboarding <onboarding@resend.dev>"
        message["To"] = email

        # 2. Compile clean, minimalist HTML body (Updated timeline window text copy to 15 mins)
        html_content = f"""
        <html>
          <body style="font-family: 'Inter', sans-serif; background-color: #FAF9F6; color: #1a1a1a; padding: 30px;">
            <div style="max-width: 500px; margin: 0 auto; background: #ffffff; padding: 40px; border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.03); border: 1px solid #E6DFD3;">
              <h2 style="color: #2C4A3E; margin-top: 0; font-size: 24px; text-align: center;">Verify Your Account</h2>
              <p style="font-size: 15px; line-height: 1.6; color: #4A4A4A; text-align: center;">
                Use the following secure one-time passcode to complete your authentication process on BookMyBook. This code expires in 15 minutes.
              </p>
              <div style="background-color: #E8ECE9; padding: 15px 0; border-radius: 12px; text-align: center; margin: 25px 0; letter-spacing: 6px;">
                <span style="font-size: 32px; font-weight: bold; color: #2C4A3E; font-family: 'Courier New', monospace;">{otp}</span>
              </div>
              <p style="font-size: 13px; color: #8A8A8A; text-align: center; margin-bottom: 0;">
                If you did not request this code, please ignore this email or reach out to your campus cluster support admin.
              </p>
            </div>
          </body>
        </html>
        """
        message.attach(MIMEText(html_content, "html"))

        # 3. Establish link, apply TLS cryptography layer, log in, and transmit
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
            server.starttls()  # Securely upgrades the pipeline connection to TLS
            server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(message["From"], email, message.as_string())

        print(f"✅ [RESEND SMTP SUCCESS] Verification code cleanly delivered to {email}")
        return f"OTP notification dispatched downstream to {email} via Resend."

    except Exception as exc:
        print(f"❌ [RESEND SMTP FAIL] Transmission exception generated for {email}: {str(exc)}")
        raise send_otp_email_task.retry(exc=exc)