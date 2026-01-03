from sqlalchemy import Column, Integer, Numeric, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    round_id = Column(Integer, ForeignKey("game_rounds.id"), nullable=True, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    type = Column(String(20), nullable=False)  # bet, win, refund
    balance_after = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

