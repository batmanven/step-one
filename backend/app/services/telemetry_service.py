from fastapi import WebSocket
from typing import Dict, Set
import json
import asyncio


class TelemetryService:
    """Real-time telemetry service using WebSocket"""
    
    def __init__(self):
        """Initialize telemetry service"""
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Connect a client to a session's telemetry stream"""
        await websocket.accept()
        
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        
        self.active_connections[session_id].add(websocket)
        
        # Send initial connection message
        await websocket.send_json({
            "type": "connected",
            "session_id": session_id,
            "message": "Connected to telemetry stream"
        })
    
    def disconnect(self, websocket: WebSocket, session_id: str):
        """Disconnect a client from telemetry stream"""
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            
            # Clean up empty session sets
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
    
    async def broadcast_to_session(self, session_id: str, message: dict):
        """Broadcast a message to all clients connected to a session"""
        if session_id not in self.active_connections:
            return
        
        disconnected = set()
        
        for connection in self.active_connections[session_id]:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection, session_id)
    
    async def broadcast_processing_update(
        self,
        session_id: str,
        stage: str,
        status: str,
        progress: float = 0.0,
        message: str = ""
    ):
        """Broadcast processing stage update"""
        await self.broadcast_to_session(session_id, {
            "type": "processing_update",
            "session_id": session_id,
            "stage": stage,
            "status": status,
            "progress": progress,
            "message": message,
            "timestamp": asyncio.get_event_loop().time()
        })
    
    async def broadcast_asset_update(
        self,
        session_id: str,
        asset_id: str,
        stage: str,
        status: str
    ):
        """Broadcast asset processing update"""
        await self.broadcast_to_session(session_id, {
            "type": "asset_update",
            "session_id": session_id,
            "asset_id": asset_id,
            "stage": stage,
            "status": status,
            "timestamp": asyncio.get_event_loop().time()
        })
    
    async def broadcast_output_generated(
        self,
        session_id: str,
        output_type: str,
        output_id: str
    ):
        """Broadcast output generation completion"""
        await self.broadcast_to_session(session_id, {
            "type": "output_generated",
            "session_id": session_id,
            "output_type": output_type,
            "output_id": output_id,
            "timestamp": asyncio.get_event_loop().time()
        })
    
    async def broadcast_error(
        self,
        session_id: str,
        error: str,
        stage: str = ""
    ):
        """Broadcast error message"""
        await self.broadcast_to_session(session_id, {
            "type": "error",
            "session_id": session_id,
            "stage": stage,
            "error": error,
            "timestamp": asyncio.get_event_loop().time()
        })
    
    def get_active_sessions(self) -> list[str]:
        """Get list of sessions with active connections"""
        return list(self.active_connections.keys())
    
    def get_connection_count(self, session_id: str) -> int:
        """Get number of active connections for a session"""
        return len(self.active_connections.get(session_id, set()))


# Singleton instance
telemetry_service = TelemetryService()
