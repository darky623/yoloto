from sqlalchemy import Column, Integer, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class RoundPlayer(Base):
    __tablename__ = "round_players"

    id = Column(Integer, primary_key=True, index=True)
    round_id = Column(Integer, ForeignKey("game_rounds.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    dice_result = Column(Integer, nullable=True)
    bet_amount = Column(Numeric(10, 2), nullable=False)
    won_amount = Column(Numeric(10, 2), default=0, nullable=False)
    is_winner = Column(Boolean, default=False, nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

