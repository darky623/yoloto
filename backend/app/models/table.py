from sqlalchemy import Column, Integer, String, Numeric, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Table(Base):
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    bet_amount = Column(Numeric(10, 2), nullable=False)
    min_players = Column(Integer, default=2, nullable=False)
    max_players = Column(Integer, default=6, nullable=False)
    status = Column(String(20), default="waiting", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

