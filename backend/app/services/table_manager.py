from typing import Dict, Set, Optional, Callable
from asyncio import Lock
from app.models.table import Table
from app.models.game_round import GameRound
from app.models.round_player import RoundPlayer
from app.models.user import User
from app.models.transaction import Transaction
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from decimal import Decimal
import random
import asyncio
from datetime import datetime


class TableManager:
    def __init__(self):
        self.table_locks: Dict[int, Lock] = {}
        self.table_tasks: Dict[int, asyncio.Task] = {}
        self.table_countdowns: Dict[int, int] = {}
        self.table_rounds: Dict[int, int] = {}  # table_id -> round_id
        self.broadcast_callbacks: Dict[int, Callable] = {}  # table_id -> callback
    
    def set_broadcast_callback(self, table_id: int, callback: Callable):
        """Установить callback для отправки сообщений через WebSocket"""
        self.broadcast_callbacks[table_id] = callback
    
    async def _broadcast(self, table_id: int, message: dict):
        """Отправить сообщение всем подключенным клиентам стола"""
        if table_id in self.broadcast_callbacks:
            await self.broadcast_callbacks[table_id](message)
    
    def get_lock(self, table_id: int) -> Lock:
        if table_id not in self.table_locks:
            self.table_locks[table_id] = Lock()
        return self.table_locks[table_id]
    
    async def get_table_state(self, db: AsyncSession, table_id: int) -> dict:
        """Получить текущее состояние стола"""
        result = await db.execute(select(Table).where(Table.id == table_id))
        table = result.scalar_one_or_none()
        if not table:
            return None
        
        # Получить текущий раунд
        current_round_id = self.table_rounds.get(table_id)
        if current_round_id:
            result = await db.execute(
                select(GameRound).where(GameRound.id == current_round_id)
            )
            current_round = result.scalar_one_or_none()
        else:
            current_round = None
        
        # Подсчитать игроков
        if current_round:
            result = await db.execute(
                select(func.count(RoundPlayer.id)).where(
                    RoundPlayer.round_id == current_round.id
                )
            )
            players_count = result.scalar() or 0
            
            # Получить игроков
            result = await db.execute(
                select(RoundPlayer, User.username)
                .join(User, RoundPlayer.user_id == User.id)
                .where(RoundPlayer.round_id == current_round.id)
            )
            players_data = result.all()
        else:
            players_count = 0
            players_data = []
        
        return {
            "table": table,
            "round": current_round,
            "players_count": players_count,
            "players_data": players_data,
        }
    
    async def join_table(
        self, db: AsyncSession, table_id: int, user: User
    ) -> dict:
        """Присоединиться к столу"""
        async with self.get_lock(table_id):
            state = await self.get_table_state(db, table_id)
            if not state or not state["table"]:
                raise ValueError("Table not found")
            
            table = state["table"]
            
            # Проверки
            if table.status not in ["waiting", "countdown"]:
                raise ValueError("Cannot join table in current status")
            
            if state["players_count"] >= table.max_players:
                raise ValueError("Table is full")
            
            if user.balance < table.bet_amount:
                raise ValueError("Insufficient balance")
            
            # Проверить, не участвует ли уже в другом раунде
            if state["round"]:
                result = await db.execute(
                    select(RoundPlayer).where(
                        RoundPlayer.round_id == state["round"].id,
                        RoundPlayer.user_id == user.id
                    )
                )
                existing = result.scalar_one_or_none()
                if existing:
                    raise ValueError("Already joined this round")
            
            # Создать или получить текущий раунд
            if not state["round"]:
                # Создать новый раунд
                round_number = self.table_rounds.get(table_id, 0) + 1
                new_round = GameRound(
                    table_id=table_id,
                    round_number=round_number,
                    prize_pool=Decimal("0.00"),
                    status="waiting"
                )
                db.add(new_round)
                await db.flush()
                await db.refresh(new_round)
                self.table_rounds[table_id] = new_round.id
                current_round = new_round
            else:
                current_round = state["round"]
            
            # Создать запись игрока
            round_player = RoundPlayer(
                round_id=current_round.id,
                user_id=user.id,
                bet_amount=table.bet_amount
            )
            db.add(round_player)
            
            # Списать средства
            user.balance -= table.bet_amount
            transaction = Transaction(
                user_id=user.id,
                round_id=current_round.id,
                amount=-table.bet_amount,
                type="bet",
                balance_after=user.balance
            )
            db.add(transaction)
            
            # Обновить призовой фонд
            current_round.prize_pool += table.bet_amount
            
            await db.commit()
            await db.refresh(current_round)
            await db.refresh(user)
            
            # Запустить таймер, если нужно
            if state["players_count"] + 1 >= table.min_players and table.status == "waiting":
                table.status = "countdown"
                self.table_countdowns[table_id] = 60
                if table_id not in self.table_tasks or self.table_tasks[table_id].done():
                    self.table_tasks[table_id] = asyncio.create_task(
                        self._game_loop(db, table_id)
                    )
            
            return {
                "round_id": current_round.id,
                "prize_pool": float(current_round.prize_pool),
                "players_count": state["players_count"] + 1
            }
    
    async def leave_table(
        self, db: AsyncSession, table_id: int, user: User
    ) -> dict:
        """Покинуть стол (только до начала игры)"""
        async with self.get_lock(table_id):
            state = await self.get_table_state(db, table_id)
            if not state or not state["round"]:
                raise ValueError("Not in a round")
            
            current_round = state["round"]
            
            # Найти игрока
            result = await db.execute(
                select(RoundPlayer).where(
                    RoundPlayer.round_id == current_round.id,
                    RoundPlayer.user_id == user.id
                )
            )
            round_player = result.scalar_one_or_none()
            if not round_player:
                raise ValueError("Not in this round")
            
            # Можно выйти только до начала игры
            if current_round.status not in ["waiting", "countdown"]:
                raise ValueError("Cannot leave after game started")
            
            # Вернуть средства
            user.balance += round_player.bet_amount
            transaction = Transaction(
                user_id=user.id,
                round_id=current_round.id,
                amount=round_player.bet_amount,
                type="refund",
                balance_after=user.balance
            )
            db.add(transaction)
            
            # Обновить призовой фонд
            current_round.prize_pool -= round_player.bet_amount
            
            # Удалить игрока
            await db.delete(round_player)
            
            await db.commit()
            await db.refresh(user)
            await db.refresh(current_round)
            
            # Если остался один игрок, остановить таймер
            result = await db.execute(
                select(func.count(RoundPlayer.id)).where(
                    RoundPlayer.round_id == current_round.id
                )
            )
            remaining_players = result.scalar() or 0
            
            if remaining_players < 2:
                table = state["table"]
                table.status = "waiting"
                if table_id in self.table_countdowns:
                    del self.table_countdowns[table_id]
            
            return {"players_count": remaining_players}
    
    async def _game_loop(self, db: AsyncSession, table_id: int):
        """Игровой цикл для стола"""
        try:
            while True:
                state = await self.get_table_state(db, table_id)
                if not state or not state["round"]:
                    await asyncio.sleep(1)
                    continue
                
                table = state["table"]
                current_round = state["round"]
                
                # Фаза countdown
                if current_round.status == "countdown":
                    countdown = self.table_countdowns.get(table_id, 60)
                    while countdown > 0:
                        await asyncio.sleep(1)
                        countdown -= 1
                        self.table_countdowns[table_id] = countdown
                        
                        # Проверить, не остановился ли таймер
                        state = await self.get_table_state(db, table_id)
                        if not state or state["table"].status != "countdown":
                            return
                    
                    # Таймер истек, начинаем игру
                    current_round.status = "rolling"
                    current_round.started_at = datetime.utcnow()
                    table.status = "rolling"
                    await db.commit()
                    
                    # Анимация 3-5 секунд
                    await asyncio.sleep(4)
                    
                    # Генерация результатов
                    result = await db.execute(
                        select(RoundPlayer, User.username)
                        .join(User, RoundPlayer.user_id == User.id)
                        .where(RoundPlayer.round_id == current_round.id)
                    )
                    players = result.all()
                    
                    # Генерируем числа для каждого игрока
                    for round_player, username in players:
                        round_player.dice_result = random.randint(1, 20)
                    
                    await db.commit()
                    
                    # Определяем победителей
                    if players:
                        max_dice = max(p[0].dice_result for p in players)
                        winners = [p for p in players if p[0].dice_result == max_dice]
                    else:
                        winners = []
                    
                    # Начисляем выигрыш
                    if winners:
                        win_amount = current_round.prize_pool / len(winners)
                        for round_player, username in winners:
                            round_player.is_winner = True
                            round_player.won_amount = win_amount
                            
                            # Обновляем баланс
                            result = await db.execute(
                                select(User).where(User.id == round_player.user_id)
                            )
                            winner_user = result.scalar_one()
                            winner_user.balance += win_amount
                            
                            transaction = Transaction(
                                user_id=winner_user.id,
                                round_id=current_round.id,
                                amount=win_amount,
                                type="win",
                                balance_after=winner_user.balance
                            )
                            db.add(transaction)
                    
                    current_round.status = "finished"
                    current_round.finished_at = datetime.utcnow()
                    table.status = "finished"
                    await db.commit()
                    
                    # Отправить результаты через WebSocket
                    results_data = []
                    for round_player, username in players:
                        results_data.append({
                            "player_id": round_player.user_id,
                            "username": username,
                            "dice": round_player.dice_result,
                            "is_winner": round_player.is_winner
                        })
                    
                    winners_data = [r for r in results_data if r["is_winner"]]
                    
                    await self._broadcast(table_id, {
                        "type": "game_result",
                        "data": {
                            "round_id": current_round.id,
                            "results": results_data,
                            "winners": winners_data
                        }
                    })
                    
                    # Показываем результат 5 секунд
                    await asyncio.sleep(5)
                    
                    # Сброс для нового раунда
                    table.status = "waiting"
                    if table_id in self.table_countdowns:
                        del self.table_countdowns[table_id]
                    if table_id in self.table_rounds:
                        del self.table_rounds[table_id]
                    await db.commit()
                    
                else:
                    await asyncio.sleep(1)
        
        except Exception as e:
            print(f"Error in game loop for table {table_id}: {e}")
            import traceback
            traceback.print_exc()


# Глобальный менеджер столов
table_manager = TableManager()

