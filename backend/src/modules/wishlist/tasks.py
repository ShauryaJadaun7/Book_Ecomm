import asyncio
from celery import shared_task
from sqlalchemy.future import select
from sqlalchemy import text
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from celery import shared_task
from src.core.config import settings

from src.core.database import sessionmanager  # 🧠 Async session maker optimized for tasks
from src.modules.users.models import User

@shared_task(name="wishlist.check_wishlist_matches")
def check_wishlist_matches_task(book_id: str, book_title: str, uploader_id: str):
    """
    Coordinator Task: Discovers matching local wishlists via PostGIS + pg_trgm 
    and fans them out into independent notification instances.
    """
    # Force the asynchronous execution loop to execute cleanly within a synchronous Celery worker thread
    return asyncio.run(_async_check_wishlist_matches(book_id, book_title, uploader_id))


async def _async_check_wishlist_matches(book_id: str, book_title: str, uploader_id: str):
    async with sessionmanager.session() as db:
        # 1. Fetch the exact spatial coordinates of the uploader profile
        uploader = await db.get(User, uuid.UUID(uploader_id))
        if not uploader:
            return f"Uploader {uploader_id} not found."

        # Convert uploader point geometry into a text representation for the raw SQL block
        uploader_loc_wkt = await db.scalar(select(func.ST_AsText(uploader.location)))

        # 2. Execute your optimized cross-index matching statement
        match_query = text("""
            SELECT w.user_id, u.email 
            FROM wishlist_items w
            JOIN users u ON w.user_id = u.id
            WHERE 
                similarity(w.desired_title, :title) >= 0.6
                AND ST_DWithin(u.location, ST_GeomFromText(:uploader_loc, 4326), 5000)
                AND w.user_id != :uploader_id;
        """)

        result = await db.execute(
            match_query, 
            {"title": book_title, "uploader_loc": uploader_loc_wkt, "uploader_id": uuid.UUID(uploader_id)}
        )
        matches = result.all()

        if not matches:
            return f"Scan complete for '{book_title}'. 0 local wishlist matches discovered."

        # 3. 🚀 THE FAN-OUT: Offload each notification safely as its own worker instance
        for row in matches:
            send_single_notification_task.delay(
                user_id=str(row.user_id),
                email=row.email,
                book_title=book_title,
                book_id=book_id
            )

        return f"Scan complete. Successfully dispatched {len(matches)} isolated alert sub-tasks."


@shared_task(name="wishlist.send_single_notification", max_retries=3, default_retry_delay=60)
def send_single_notification_task(user_id: str, email: str, book_title: str, book_id: str):
    """
    Worker Task: Executes individual delivery notification workflows via a secure SMTP handshake,
    injecting the dynamic book name into the core messaging subject envelope.
    """
    try:
        print(f"📡 [SMTP CONNECTING] Initializing mail stream connection for {email}...")

        # 1. Construct the email structural envelope
        message = MIMEMultipart("alternative")
        
        # 🎯 DYNAMIC SUBJECT LINE: Injected the actual book title directly into the notification header
        message["Subject"] = f"📚 Wishlist Alert: '{book_title}' is now available near you!"
        message["From"] = f"BookMyBook Alerts <{settings.SMTP_USER}>"
        message["To"] = email

        # 2. Render the HTML Layout Structure
        html_content = f"""
        <html>
          <body style="font-family: 'Inter', sans-serif; color: #1a1a1a; background-color: #FAF9F6; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: #ffffff; padding: 30px; border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
              <h2 style="color: #2C4A3E; margin-top: 0;">Hey Reader! 👋</h2>
              <p style="font-size: 16px; line-height: 1.6;">
                Great news! A book matching an item pinned to your campus alert registry has just been listed in your area:
              </p>
              <div style="background-color: #E8ECE9; padding: 20px; border-radius: 12px; margin: 20px 0; border-left: 5px solid #2C4A3E;">
                <span style="font-size: 14px; text-transform: uppercase; letter-spacing: 1px; color: #4A4A4A; display: block; margin-bottom: 4px;">Desired Book</span>
                <strong style="font-size: 20px; color: #2C4A3E; display: block;">{book_title}</strong>
              </div>
              <p style="font-size: 14px; line-height: 1.6; color: #4A4A4A;">
                Open the <strong>BookMyBook</strong> catalog right now to view full descriptions, verify the peer's hyper-local campus coordinates, and drop them a WhatsApp message to lock down your exchange before someone else grabs it!
              </p>
              <hr style="border: none; border-top: 1px solid #E6DFD3; margin: 25px 0;" />
              <small style="color: #8A8A8A; font-size: 12px;">This is an automated real-time campus notification alert dispatched asynchronously by your core backend system cluster.</small>
            </div>
          </body>
        </html>
        """
        
        message.attach(MIMEText(html_content, "html"))

        # 3. Secure TLS Encryption Handshake & Transmission Execution
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
            server.starttls() 
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, email, message.as_string())

        print(f"✅ [MAIL DELIVERED] Wishlist notification for '{book_title}' successfully pushed straight to inbox: {email}")
        return f"Notification confirmed delivered to user {user_id}"

    except Exception as exc:
        print(f"❌ [SMTP ERROR] Transmission dropped for {email} matching '{book_title}'. Scheduling worker retry...")
        raise send_single_notification_task.retry(exc=exc)