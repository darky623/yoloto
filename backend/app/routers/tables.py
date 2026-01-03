from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.table import Table
from app.models.game_round import GameRound
from app.models.round_player import RoundPlayer
from app.models.user import User
from app.schemas.table import TableResponse, TableDetail
from app.schemas.game import RoundPlayerResponse
from app.utils.dependencies import get_current_user
from app.services.table_manager import table_manager
from typing import List

router = APIRouter(prefix="/api/tables", tags=["tables"])


@router.get("", response_model=List[TableResponse])
async def get_tables(db: AsyncSession = Depends(get_db)):
    """Получить список всех столов"""
    result = await db.execute(select(Table))
    tables = result.scalars().all()
    
    tables_response = []
    for table in tables:
        # Получить текущий раунд
        current_round_id = table_manager.table_rounds.get(table.id)
        if current_round_id:
            result = await db.execute(
                select(GameRound).where(GameRound.id == current_round_id)
            )
            current_round = result.scalar_one_or_none()
            if current_round:
                result = await db.execute(
                    select(func.count(RoundPlayer.id)).where(
                        RoundPlayer.round_id == current_round.id
                    )
                )
                players_count = result.scalar() or 0
                prize_pool = current_round.prize_pool
            else:
                players_count = 0
                prize_pool = 0
        else:
            players_count = 0
            prize_pool = 0
        
        tables_response.append(TableResponse(
            id=table.id,
            name=table.name,
            bet_amount=table.bet_amount,
            min_players=table.min_players,
            max_players=table.max_players,
            status=table.status,
            current_players=players_count,
            prize_pool=prize_pool
        ))
    
    return tables_response


@router.get("/{table_id}", response_model=TableDetail)
async def get_table(
    table_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить детальную информацию о столе"""
    state = await table_manager.get_table_state(db, table_id)
    if not state or not state["table"]:
        raise HTTPException(status_code=404, detail="Table not found")
    
    table = state["table"]
    current_round = state["round"]
    
    # Собрать информацию об игроках
    players = []
    if current_round:
        for round_player, username in state["players_data"]:
            players.append(RoundPlayerResponse(
                id=round_player.id,
                user_id=round_player.user_id,
                username=username,
                dice_result=round_player.dice_result,
                bet_amount=round_player.bet_amount,
                is_winner=round_player.is_winner
            ))
    
    countdown_seconds = table_manager.table_countdowns.get(table_id)
    
    return TableDetail(
        id=table.id,
        name=table.name,
        bet_amount=table.bet_amount,
        min_players=table.min_players,
        max_players=table.max_players,
        status=table.status,
        current_players=state["players_count"],
        prize_pool=current_round.prize_pool if current_round else 0,
        players=players,
        countdown_seconds=countdown_seconds,
        current_round_id=current_round.id if current_round else None
    )


@router.post("/{table_id}/join")
async def join_table(
    table_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Присоединиться к столу"""
    try:
        result = await table_manager.join_table(db, table_id, current_user)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{table_id}/leave")
async def leave_table(
    table_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Покинуть стол"""
    try:
        result = await table_manager.leave_table(db, table_id, current_user)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

