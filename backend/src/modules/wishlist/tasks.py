import asyncio
from contextlib import asynccontextmanager
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from celery import shared_task
from sqlalchemy import text
from sqlalchemy.future import select

from src.core.config import settings
from src.core.database import get_db
from src.modules.users.models import User


@shared_task(name="wishlist.check_wishlist_matches")
def check_wishlist_matches_task(book_id: str, book_title: str, uploader_id: str):
    """
    Coordinator Task: Discovers matching local wishlists via PostGIS + pg_trgm 
    and fans them out into independent notification instances.
    """
    return asyncio.run(_async_check_wishlist_matches(book_id, book_title, uploader_id))


async def _async_check_wishlist_matches(book_id: str, book_title: str, uploader_id: str):
    async_db_context = asynccontextmanager(get_db)

    async with async_db_context() as db:
        uploader = await db.get(User, uuid.UUID(uploader_id))
        if not uploader:
            return f"Uploader {uploader_id} not found."

        # Fetch uploader point geometry into a text representation safely
        uploader_loc_wkt = await db.scalar(
            select(text("ST_AsText(location)")).select_from(User).filter(User.id == uploader.id)
        )
        
        if not uploader_loc_wkt:
            uploader_loc_wkt = "POINT(72.5714 23.0225)"

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

        # Trigger independent task workers for each matched user profile discovered
        from .tasks import send_single_notification_task
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
    Worker Task: Connects over Resend SMTP to deliver hyper-targeted wishlist match notifications.
    """
    try:
        print(f"📡 [RESEND SMTP CONNECTING] Transporting wishlist alert stream to: {email}")

        message = MIMEMultipart("alternative")
        message["Subject"] = f"📚 Wishlist Alert: '{book_title}' is now available near you!"
        
        # 🎯 BRAND ENHANCEMENT: Swap this with your verified Resend custom domain email address
        message["From"] = "BookMyBook Alerts <alerts@yourcompanyname.com>"
        message["To"] = email

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

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
            server.starttls() 
            server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(message["From"], email, message.as_string())

        print(f"✅ [RESEND SMTP SUCCESS] Wishlist notification alert pushed cleanly to inbox: {email}")
        return f"Notification confirmed delivered to user {user_id}"

    except Exception as exc:
        print(f"❌ [RESEND SMTP FAIL] Wishlist email delivery failure encountered for {email}: {str(exc)}")
        raise send_single_notification_task.retry(exc=exc)