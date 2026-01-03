from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.table import Table
from app.models.game_round import GameRound
from app.models.round_player import RoundPlayer
from app.models.user import User
from app.utils.security import decode_access_token
from app.services.table_manager import table_manager
from app.schemas.game import RoundPlayerResponse, GameResult
import json
from typing import Dict, Set
import asyncio


router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}  # table_id -> set of websockets
    
    async def connect(self, websocket: WebSocket, table_id: int):
        await websocket.accept()
        if table_id not in self.active_connections:
            self.active_connections[table_id] = set()
        self.active_connections[table_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, table_id: int):
        if table_id in self.active_connections:
            self.active_connections[table_id].discard(websocket)
            if not self.active_connections[table_id]:
                del self.active_connections[table_id]
    
    async def broadcast_to_table(self, table_id: int, message: dict):
        if table_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[table_id]:
                try:
                    await connection.send_json(message)
                except:
                    disconnected.add(connection)
            
            for conn in disconnected:
                self.disconnect(conn, table_id)


manager = ConnectionManager()


async def get_user_from_token(token: str, db: AsyncSession) -> User:
    """Получить пользователя из токена"""
    payload = decode_access_token(token)
    if not payload:
        return None
    
    username = payload.get("sub")
    if not username:
        return None
    
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


@router.websocket("/ws/{table_id}")
async def websocket_endpoint(websocket: WebSocket, table_id: int):
    """WebSocket endpoint для получения обновлений стола в реальном времени"""
    await manager.connect(websocket, table_id)
    
    # Установить callback для table_manager
    async def broadcast_callback(message):
        await manager.broadcast_to_table(table_id, message)
    
    table_manager.set_broadcast_callback(table_id, broadcast_callback)
    
    # Получить токен из query параметров
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008, reason="No token provided")
        return
    
    # Получить пользователя
    from app.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        user = await get_user_from_token(token, db)
        if not user:
            await websocket.close(code=1008, reason="Invalid token")
            return
        
            # Отправить начальное состояние
            state = await table_manager.get_table_state(db, table_id)
            if state and state["table"]:
                # Собрать информацию об игроках
                players = []
                if state["round"]:
                    for round_player, username in state["players_data"]:
                        players.append({
                            "player_id": round_player.user_id,
                            "username": username,
                            "dice": round_player.dice_result,
                            "is_winner": round_player.is_winner
                        })
                
                await websocket.send_json({
                    "type": "table_state",
                    "data": {
                        "table_id": table_id,
                        "status": state["table"].status,
                        "players_count": state["players_count"],
                        "prize_pool": float(state["round"].prize_pool) if state["round"] else 0.0,
                        "players": players,
                        "countdown_seconds": table_manager.table_countdowns.get(table_id)
                    }
                })
        
        # Запустить задачу для отправки обновлений
        async def send_updates():
            last_countdown = None
            last_players_count = None
            last_status = None
            
            while True:
                try:
                    await asyncio.sleep(1)
                    async with AsyncSessionLocal() as update_db:
                        state = await table_manager.get_table_state(update_db, table_id)
                        
                        if not state or not state["table"]:
                            continue
                        
                        table = state["table"]
                        current_round = state["round"]
                        
                        # Отправлять обновления таймера
                        countdown = table_manager.table_countdowns.get(table_id)
                        if countdown is not None and countdown != last_countdown:
                            if last_countdown is None:
                                await manager.broadcast_to_table(table_id, {
                                    "type": "countdown_started",
                                    "data": {"seconds": countdown}
                                })
                            else:
                                await manager.broadcast_to_table(table_id, {
                                    "type": "countdown_update",
                                    "data": {"seconds_left": countdown}
                                })
                            last_countdown = countdown
                        
                        # Отправлять обновления статуса
                        if table.status != last_status:
                            if table.status == "rolling":
                                await manager.broadcast_to_table(table_id, {
                                    "type": "game_rolling",
                                    "data": {"round_id": current_round.id if current_round else None}
                                })
                            last_status = table.status
                        
                        # Отправлять обновления количества игроков
                        if state["players_count"] != last_players_count:
                            last_players_count = state["players_count"]
                
                except Exception as e:
                    print(f"Error in send_updates: {e}")
                    break
        
        update_task = asyncio.create_task(send_updates())
        
        try:
            while True:
                data = await websocket.receive_text()
                try:
                    message = json.loads(data)
                    message_type = message.get("type")
                    
                    if message_type == "join_table":
                        async with AsyncSessionLocal() as action_db:
                            result = await table_manager.join_table(action_db, table_id, user)
                            await manager.broadcast_to_table(table_id, {
                                "type": "player_joined",
                                "data": {
                                    "player_id": user.id,
                                    "username": user.username,
                                    "players_count": result["players_count"],
                                    "prize_pool": result["prize_pool"]
                                }
                            })
                    
                    elif message_type == "leave_table":
                        async with AsyncSessionLocal() as action_db:
                            state = await table_manager.get_table_state(action_db, table_id)
                            current_round = state["round"] if state else None
                            result = await table_manager.leave_table(action_db, table_id, user)
                            await manager.broadcast_to_table(table_id, {
                                "type": "player_left",
                                "data": {
                                    "player_id": user.id,
                                    "username": user.username,
                                    "players_count": result["players_count"],
                                    "prize_pool": float(current_round.prize_pool) if current_round else 0.0
                                }
                            })
                
                except json.JSONDecodeError:
                    await websocket.send_json({
                        "type": "error",
                        "data": {"message": "Invalid JSON"}
                    })
                except ValueError as e:
                    await websocket.send_json({
                        "type": "error",
                        "data": {"message": str(e)}
                    })
        
        except WebSocketDisconnect:
            manager.disconnect(websocket, table_id)
            update_task.cancel()
        except Exception as e:
            print(f"WebSocket error: {e}")
            manager.disconnect(websocket, table_id)
            update_task.cancel()

