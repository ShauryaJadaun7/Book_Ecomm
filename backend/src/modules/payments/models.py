import enum
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.core.database import Base

class TransactionStatus(str, enum.Enum):
    """
    Strict state-machine boundaries tracking Razorpay webhook lifecycles.
    """
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


class Transaction(Base):
    __tablename__ = "transactions"

    # Core Transaction Identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # 🎫 Subscription Plan Attributes
    plan_name = Column(String(100), nullable=False)  # e.g., "Premium_Monthly", "Elite_Semester"
    amount_paise = Column(Integer, nullable=False)    # Integer format maps naturally to Razorpay API structures (e.g., 29900 paise = ₹299.00)
    
    # 💳 Razorpay Gateway Handshake Fields
    razorpay_order_id = Column(String(255), nullable=False, unique=True, index=True)
    razorpay_payment_id = Column(String(255), nullable=True, unique=True, index=True)
    razorpay_signature = Column(String(500), nullable=True)
    
    # Lifecycle Tracking Status
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False, index=True)
    
    # Auditing Timestamps
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=text("CURRENT_TIMESTAMP"), 
        onupdate=text("CURRENT_TIMESTAMP")
    )

    # ORM Relationships
    user = relationship("User", backref="transactions")
    