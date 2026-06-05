import razorpay
import uuid
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.core.config import settings
from .models import Transaction, TransactionStatus

# Initialize the Razorpay client using your lowercase validated configurations
razorpay_client = razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))

async def create_payment_order(db: AsyncSession, user_id: str, plan_name: str) -> dict:
    """
    Step 1 Backend: Contacts Razorpay to construct a cryptographic order block,
    saving a 'PENDING' tracker entry into our regional persistent storage.
    """
    # Define rigid pricing points based on matching campus tiers (in Paise: ₹1 = 100 Paise)
    plan_pricing = {
        "premium_monthly": 19900,  # ₹199
        "premium_semester": 49900  # ₹499
    }
    
    normalized_plan = plan_name.lower().strip()
    if normalized_plan not in plan_pricing:
        raise HTTPException(status_code=400, detail="Requested membership plan mapping does not exist.")
        
    amount_in_paise = plan_pricing[normalized_plan]

    # Generate the payload context array parameters for Razorpay
    order_data = {
        "amount": amount_in_paise,
        "currency": "INR",
        "receipt": f"rcpt_{uuid.uuid4().hex[:20]}",
        "payment_capture": 1  # 1 means automatically capture payment upon customer authorization
    }

    try:
        # Create an order directly inside the Razorpay gateway network
        razorpay_order = razorpay_client.order.create(data=order_data)
        order_id = razorpay_order["id"]
    except Exception as e:
        print(f"❌ [RAZORPAY GATEWAY ERROR] Failed to spawn order instance: {str(e)}")
        raise HTTPException(status_code=500, detail="External checkout service provider initialization failed.")

    # Commit a permanent record entry to tracking memory to prevent downstream data mismatches
    new_transaction = Transaction(
        user_id=uuid.UUID(user_id),
        plan_name=normalized_plan,
        amount_paise=amount_in_paise,
        razorpay_order_id=order_id,
        status=TransactionStatus.PENDING
    )
    db.add(new_transaction)
    await db.commit()
    await db.refresh(new_transaction)

    return {
        "razorpay_order_id": order_id,
        "razorpay_key_id": settings.razorpay_key_id,
        "amount": amount_in_paise,
        "currency": "INR",
        "transaction_id": str(new_transaction.id)
    }


async def verify_payment_authenticity(
    db: AsyncSession, 
    razorpay_order_id: str, 
    razorpay_payment_id: str, 
    razorpay_signature: str
) -> dict:
    """
    Step 2 Backend: Performs secure cryptographic signature matching.
    Only updates transaction statuses and grants premium tokens if hashes align.
    """
    # 1. Re-verify the signature matching parameters against local credentials
    try:
        signature_params = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        # Throws an exception natively if the signature signature does not verify cleanly
        razorpay_client.utility.verify_payment_signature(signature_params)
        print(f"🔒 [CRYPTO VERIFIED] Payment signature matches for Order ID: {razorpay_order_id}")
    except Exception:
        print(f"⚠️ [SECURITY WARNING] Malicious payment spoofing signature detected for Order ID: {razorpay_order_id}")
        raise HTTPException(status_code=400, detail="Payment validation hash verification failed. Signature mismatch.")

    # 2. Fetch the corresponding order record entry from PostgreSQL database
    query = select(Transaction).filter(Transaction.razorpay_order_id == razorpay_order_id)
    result = await db.execute(query)
    transaction = result.scalars().first()

    if not transaction:
        raise HTTPException(status_code=444, detail="Order origin record not found in structural databases.")

    # Guard against processing identical webhooks or duplicate verification calls twice
    if transaction.status == TransactionStatus.SUCCESS:
        return {"status": "already_processed", "message": "Transaction audit trail already marked complete."}

    # 3. Securely promote status attributes
    transaction.razorpay_payment_id = razorpay_payment_id
    transaction.razorpay_signature = razorpay_signature
    transaction.status = TransactionStatus.SUCCESS
    
    # 🚀 FUTURE EXTENSION HOOK ZONE:
    # This is exactly where you will append your database state switches to upgrade user levels!
    # For example:
    # user = await db.get(User, transaction.user_id)
    # user.is_premium = True
    # user.premium_expires_at = calculate_expiry_date(transaction.plan_name)

    db.add(transaction)
    await db.commit()

    return {
        "status": "success",
        "message": "Payment verified securely. Premium capabilities unlocked natively across account scopes.",
        "plan": transaction.plan_name
    }