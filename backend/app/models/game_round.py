from sqlalchemy import Column, Integer, Numeric, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class GameRound(Base):
    __tablename__ = "game_rounds"

    id = Column(Integer, primary_key=True, index=True)
    table_id = Column(Integer, ForeignKey("tables.id"), nullable=False, index=True)
    round_number = Column(Integer, nullable=False)
    prize_pool = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), default="waiting", nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

