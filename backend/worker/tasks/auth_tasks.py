from worker.celery_app import celery_worker

@celery_worker.task(name="tasks.send_otp_email", max_retries=3, default_retry_delay=10)
def send_otp_email_task(email: str, otp: str) -> str:
    """
    Decoupled background task thread.
    Integrate production SMTP transports (AWS SES, SendGrid, Resend) securely here.
    """
    print(f"=========================================================")
    print(f"✉️ [DISPATCH] Pinging secure message relay to: {email}")
    print(f"🔒 [SECURITY] Authentication Challenge Passcode: {otp}")
    print(f"=========================================================")
    return f"Notification safely dispatched downstream to {email}."