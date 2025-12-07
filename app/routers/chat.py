"""
Enhanced Real-time Chat System.

Provides WebSocket-based real-time chat functionality with support for
customer service, property inquiries, and multi-tenant conversations.
"""

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException, status, Query
from sqlmodel import Session, select, and_, or_
from typing import List, Optional, Dict, Any
import json
import uuid
from datetime import datetime, timedelta

from app.core.database import get_session, engine
from app.core.websocket_manager import ws_manager
from app.core.redis import publish_message
from app.core.logger import logger
from app.models.chat_message import ChatMessage
from app.models.user import User
from app.models.booking import Booking
from app.models.property import Property
from app.schemas.chat import ChatMessageCreate, ChatMessageOut, ChatRoomOut
from app.utils.dependencies import get_active_user, get_current_user_optional
from app.utils.enums import UserRole

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatService:
    """Enhanced chat service with business logic."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_room_id(self, user_id: uuid.UUID, context_type: str, context_id: Optional[uuid.UUID] = None) -> str:
        """Create a standardized room ID."""
        if context_type == "support":
            return f"support_{user_id}"
        elif context_type == "property" and context_id:
            return f"property_{context_id}_{user_id}"
        elif context_type == "booking" and context_id:
            return f"booking_{context_id}"
        else:
            return f"general_{user_id}"
    
    def get_available_staff(self) -> List[User]:
        """Get available staff members for customer support."""
        return self.session.exec(
            select(User).where(
                and_(
                    User.role.in_([UserRole.STAFF, UserRole.ADMIN]),
                    User.is_active == True
                )
            )
        ).all()
    
    def assign_staff_to_room(self, room: str) -> Optional[User]:
        """Assign a staff member to a chat room."""
        available_staff = self.get_available_staff()
        if available_staff:
            # Simple round-robin assignment (can be enhanced)
            return available_staff[0]
        return None
    
    def save_message(self, room: str, sender_id: Optional[uuid.UUID], content: str, message_type: str = "text") -> ChatMessage:
        """Save a chat message to the database."""
        message = ChatMessage(
            room=room,
            sender_id=sender_id,
            content=content
        )
        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)
        return message
    
    def get_room_history(self, room: str, limit: int = 50, offset: int = 0) -> List[ChatMessage]:
        """Get chat history for a room."""
        return self.session.exec(
            select(ChatMessage)
            .where(ChatMessage.room == room)
            .order_by(ChatMessage.created_at.desc())
            .offset(offset)
            .limit(limit)
        ).all()
    
    def get_user_rooms(self, user_id: uuid.UUID) -> List[str]:
        """Get all chat rooms for a user."""
        messages = self.session.exec(
            select(ChatMessage.room)
            .where(ChatMessage.sender_id == user_id)
            .distinct()
        ).all()
        return list(messages)


@router.websocket("/ws/{room}")
async def websocket_endpoint(
    websocket: WebSocket, 
    room: str,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time chat.
    
    Supports different room types:
    - support_{user_id}: Customer support chat
    - property_{property_id}_{user_id}: Property inquiry chat
    - booking_{booking_id}: Booking-related chat
    """
    await ws_manager.connect(websocket, room)
    
    try:
        # Send welcome message
        welcome_data = {
            "type": "system",
            "message": "Connected to chat room",
            "room": room,
            "timestamp": datetime.utcnow().isoformat()
        }
        await websocket.send_text(json.dumps(welcome_data))
        
        # Auto-assign staff for support rooms
        if room.startswith("support_"):
            with Session(engine) as session:
                chat_service = ChatService(session)
                staff = chat_service.assign_staff_to_room(room)
                if staff:
                    staff_join_data = {
                        "type": "staff_joined",
                        "message": f"{staff.full_name} has joined the chat",
                        "staff_id": str(staff.id),
                        "staff_name": staff.full_name,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    await ws_manager.broadcast(room, json.dumps(staff_join_data))
        
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Validate message data
            if "content" not in message_data:
                continue
            
            # Save message to database
            with Session(engine) as session:
                chat_service = ChatService(session)
                message = chat_service.save_message(
                    room=room,
                    sender_id=uuid.UUID(message_data["sender_id"]) if message_data.get("sender_id") else None,
                    content=message_data["content"]
                )
                
                # Prepare broadcast data
                broadcast_data = {
                    "id": str(message.id),
                    "type": "message",
                    "sender_id": str(message.sender_id) if message.sender_id else None,
                    "content": message.content,
                    "timestamp": message.created_at.isoformat(),
                    "room": room
                }
            
            # Broadcast message to room
            await ws_manager.broadcast(room, json.dumps(broadcast_data))
            publish_message(f"chat:{room}", json.dumps(broadcast_data))
            
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, room)
        
        # Notify room about user disconnect
        disconnect_data = {
            "type": "user_disconnected",
            "message": "A user has left the chat",
            "timestamp": datetime.utcnow().isoformat()
        }
        await ws_manager.broadcast(room, json.dumps(disconnect_data))
        logger.info(f"WS disconnected from room: {room}")


@router.websocket("/support")
async def ws_support(websocket: WebSocket, room: str = Query("lobby")):
    """Legacy support endpoint."""
    await ws_manager.connect(websocket, room)
    try:
        await ws_manager.broadcast(room, "🟢 A user joined the chat")
        while True:
            text = await websocket.receive_text()
            await ws_manager.broadcast(room, text)
            publish_message(f"chat:{room}", text)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, room)
        await ws_manager.broadcast(room, "🔴 A user left")
        logger.info("WS disconnected")


@router.get("/history/{room}")
def get_chat_history(
    room: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
    limit: int = Query(50, description="Maximum number of messages"),
    offset: int = Query(0, description="Number of messages to skip")
):
    """
    Get chat history for a room.
    
    Users can only access rooms they are authorized for:
    - Customers: their own support/property/booking rooms
    - Staff/Admin: all rooms
    """
    # Authorization check
    if current_user.role == UserRole.CUSTOMER:
        user_id_str = str(current_user.id)
        if not (room.endswith(f"_{user_id_str}") or room.startswith(f"support_{user_id_str}")):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own chat rooms"
            )
    
    chat_service = ChatService(session)
    messages = chat_service.get_room_history(room, limit, offset)
    
    return {"messages": [
        {
            "id": str(msg.id),
            "sender_id": str(msg.sender_id) if msg.sender_id else None,
            "content": msg.content,
            "created_at": msg.created_at.isoformat()
        }
        for msg in reversed(messages)
    ]}


@router.get("/rooms")
def get_user_chat_rooms(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user)
):
    """Get all chat rooms for the current user."""
    if current_user.role in [UserRole.STAFF, UserRole.ADMIN]:
        # Staff can see all active rooms
        rooms_query = select(ChatMessage.room).distinct()
    else:
        # Customers see only their rooms
        rooms_query = select(ChatMessage.room).where(
            ChatMessage.sender_id == current_user.id
        ).distinct()
    
    room_names = session.exec(rooms_query).all()
    
    rooms = []
    for room_name in room_names:
        # Get last message
        last_message = session.exec(
            select(ChatMessage)
            .where(ChatMessage.room == room_name)
            .order_by(ChatMessage.created_at.desc())
            .limit(1)
        ).first()
        
        # Determine room type and context
        room_type = "general"
        context_id = None
        
        if room_name.startswith("support_"):
            room_type = "support"
        elif room_name.startswith("property_"):
            room_type = "property"
            parts = room_name.split("_")
            if len(parts) >= 2:
                try:
                    context_id = uuid.UUID(parts[1])
                except ValueError:
                    pass
        elif room_name.startswith("booking_"):
            room_type = "booking"
            parts = room_name.split("_")
            if len(parts) >= 2:
                try:
                    context_id = uuid.UUID(parts[1])
                except ValueError:
                    pass
        
        rooms.append({
            "room": room_name,
            "room_type": room_type,
            "context_id": str(context_id) if context_id else None,
            "last_message": last_message.content if last_message else None,
            "last_message_at": last_message.created_at.isoformat() if last_message else None,
            "unread_count": 0  # Simplified
        })
    
    return {"rooms": sorted(rooms, key=lambda x: x["last_message_at"] or "", reverse=True)}


@router.post("/rooms/support")
def create_support_room(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user)
):
    """Create a customer support chat room."""
    chat_service = ChatService(session)
    room = chat_service.create_room_id(current_user.id, "support")
    
    # Create initial system message
    welcome_message = chat_service.save_message(
        room=room,
        sender_id=None,
        content="Welcome to customer support. How can we help you today?"
    )
    
    return {
        "room": room,
        "message": "Support chat room created",
        "welcome_message": welcome_message.content
    }
