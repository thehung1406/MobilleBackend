from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect
from app.core.logger import logger

class WebSocketManager:
    def __init__(self):
        self.rooms: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room: str):
        await websocket.accept()
        self.rooms.setdefault(room, set()).add(websocket)
        logger.info(f"WS connected -> room={room}, count={len(self.rooms[room])}")

    def disconnect(self, websocket: WebSocket, room: str):
        self.rooms.get(room, set()).discard(websocket)
        logger.info(f"WS disconnected -> room={room}")

    async def broadcast(self, room: str, message: str):
        for ws in list(self.rooms.get(room, set())):
            try:
                await ws.send_text(message)
            except Exception:
                self.disconnect(ws, room)

ws_manager = WebSocketManager()
