from pydantic import BaseModel
from decimal import Decimal
from typing import List, Optional
from datetime import datetime


class RoundPlayerResponse(BaseModel):
    id: int
    user_id: int
    username: str
    dice_result: Optional[int] = None
    bet_amount: Decimal
    is_winner: bool = False

    class Config:
        from_attributes = True


class GameRoundResponse(BaseModel):
    id: int
    table_id: int
    round_number: int
    prize_pool: Decimal
    status: str
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class GameResult(BaseModel):
    round_id: int
    results: List[RoundPlayerResponse]
    winners: List[RoundPlayerResponse]

