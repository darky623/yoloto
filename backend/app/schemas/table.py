from pydantic import BaseModel
from decimal import Decimal
from typing import List, Optional
from .game import RoundPlayerResponse


class TableResponse(BaseModel):
    id: int
    name: str
    bet_amount: Decimal
    min_players: int
    max_players: int
    status: str
    current_players: int = 0
    prize_pool: Decimal = Decimal("0.00")

    class Config:
        from_attributes = True


class TableDetail(BaseModel):
    id: int
    name: str
    bet_amount: Decimal
    min_players: int
    max_players: int
    status: str
    current_players: int
    prize_pool: Decimal
    players: List[RoundPlayerResponse] = []
    countdown_seconds: Optional[int] = None
    current_round_id: Optional[int] = None

    class Config:
        from_attributes = True

