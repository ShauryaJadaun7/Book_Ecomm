import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from worker.celery_app import celery_worker

# ---------------- New IMPORTS for EMAIL FEATURES ----------------
from src.core.config import settings
import asyncio
from src.core.database import AsyncSessionLocal
from src.modules.users.models import User
from sqlalchemy import select

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
                Use the following secure one-time passcode to complete your authentication process on LocalShelf. This code expires in 15 minutes.
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

# MERGE NOTE:
# 2 New Feature jesa add kiya he 
#   1) Welcoming email
#   2) Profile reminders
# Same hi tha code to mene bas copy past kardiya 😂 
# Tu ek baar dekh lena ,  koi problen na ho , aur kuch change karna hoto dekh lena
# Aur delay timer rakhe hue he testing ke liye 60 sec ka baad me change kar lege jo rakhne ho vo practically 

@celery_worker.task(name="tasks.send_welcome_email", max_retries=3, default_retry_delay=10)
def send_welcome_email_task(email: str, name: str) -> str:
    """
    Sends an aesthetic welcome email to the user once their profile is completed.
    """
    try:
        print(f"📡 [RESEND SMTP CONNECTING] Sending Welcome Email to: {email}")
        message = MIMEMultipart("alternative")
        message["Subject"] = "Welcome to the LocalShelf Community! 📚"
        message["From"] = "LocalShelf Onboarding <onboarding@resend.dev>"
        message["To"] = email

        html_content = f"""
        <html>
          <body style="font-family: 'Inter', sans-serif; background-color: #FAF9F6; color: #1a1a1a; padding: 30px;">
            <div style="max-width: 500px; margin: 0 auto; background: #ffffff; padding: 40px; border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.03); border: 1px solid #E6DFD3;">
              <h2 style="color: #2C4A3E; margin-top: 0; font-size: 24px; text-align: center;">Welcome, {name}!</h2>
              <p style="font-size: 15px; line-height: 1.6; color: #4A4A4A; text-align: center;">
                Your campus profile is now complete. You are officially ready to start scanning, uploading, and trading books with students in your immediate area!
              </p>
              <div style="text-align: center; margin: 25px 0;">
                <a href="http://localhost:5173/dashboard" style="background-color: #2C4A3E; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold;">Go to Dashboard</a>
              </div>
            </div>
          </body>
        </html>
        """
        message.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(message["From"], email, message.as_string())

        print(f"✅ [RESEND SMTP SUCCESS] Welcome email delivered to {email}")
        return "Welcome email sent successfully."

    except Exception as exc:
        raise send_welcome_email_task.retry(exc=exc)


@celery_worker.task(name="tasks.check_profile_and_remind", max_retries=3, default_retry_delay=10)
def check_profile_and_remind_task(user_id: str, email: str, name: str) -> str:
    """
    Checks if the user's profile is complete. If not, sends a reminder email.
    """
    async def _check_and_send():
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).filter(User.id == user_id))
            user = result.scalar_one_or_none()
            
            # If the user exists and their area is STILL null, send the reminder!
            if user and not user.area:
                print(f"📡 [RESEND SMTP CONNECTING] Sending Profile Reminder to: {email}")
                message = MIMEMultipart("alternative")
                message["Subject"] = "Action Required: Complete Your LocalShelf Profile 📍"
                message["From"] = "LocalShelf Onboarding <onboarding@resend.dev>"
                message["To"] = email

                html_content = f"""
                <html>
                  <body style="font-family: 'Inter', sans-serif; background-color: #FAF9F6; color: #1a1a1a; padding: 30px;">
                    <div style="max-width: 500px; margin: 0 auto; background: #ffffff; padding: 40px; border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.03); border: 1px solid #E6DFD3;">
                      <h2 style="color: #2C4A3E; margin-top: 0; font-size: 24px; text-align: center;">Hi {name},</h2>
                      <p style="font-size: 15px; line-height: 1.6; color: #4A4A4A; text-align: center;">
                        We noticed you haven't completed your profile yet. To start trading books, you must set your campus location and pincode so we can match you with local students!
                      </p>
                      <div style="text-align: center; margin: 25px 0;">
                        <a href="http://localhost:5173/dashboard/profile" style="background-color: #EAB308; color: #1a1a1a; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold;">Complete Profile Now</a>
                      </div>
                    </div>
                  </body>
                </html>
                """
                message.attach(MIMEText(html_content, "html"))

                with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
                    server.starttls()
                    server.login(settings.smtp_user, settings.smtp_password)
                    server.sendmail(message["From"], email, message.as_string())

                print(f"✅ [RESEND SMTP SUCCESS] Reminder email delivered to {email}")
                return "Reminder email sent."
            
            print(f"⏩ [CELERY SKIP] User {email} already completed profile. Skipping reminder.")
            return "Profile already complete."

    try:
        # Run the async database check within the sync Celery worker context
        return asyncio.run(_check_and_send())
    except Exception as exc:
        raise check_profile_and_remind_task.retry(exc=exc)