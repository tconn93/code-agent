"""
WebSocket support for real-time job status updates.
"""
from fastapi import WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Set, List
import json
import asyncio
import logging
from sqlalchemy.orm import Session
from services.api.database import get_db
from services.api import models
from services.api.auth import decode_access_token

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self):
        # Map of user_id -> set of WebSocket connections
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # Map of project_id -> set of WebSocket connections
        self.project_subscriptions: Dict[int, Set[WebSocket]] = {}
        # Map of job_id -> set of WebSocket connections
        self.job_subscriptions: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """Accept WebSocket connection."""
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()

        self.active_connections[user_id].add(websocket)
        logger.info(f"WebSocket connected for user {user_id}")

    def disconnect(self, websocket: WebSocket, user_id: int):
        """Remove WebSocket connection."""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)

            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

        # Clean up subscriptions
        for project_id, connections in list(self.project_subscriptions.items()):
            connections.discard(websocket)
            if not connections:
                del self.project_subscriptions[project_id]

        for job_id, connections in list(self.job_subscriptions.items()):
            connections.discard(websocket)
            if not connections:
                del self.job_subscriptions[job_id]

        logger.info(f"WebSocket disconnected for user {user_id}")

    def subscribe_to_project(self, websocket: WebSocket, project_id: int):
        """Subscribe WebSocket to project updates."""
        if project_id not in self.project_subscriptions:
            self.project_subscriptions[project_id] = set()

        self.project_subscriptions[project_id].add(websocket)
        logger.debug(f"Subscribed to project {project_id}")

    def subscribe_to_job(self, websocket: WebSocket, job_id: int):
        """Subscribe WebSocket to job updates."""
        if job_id not in self.job_subscriptions:
            self.job_subscriptions[job_id] = set()

        self.job_subscriptions[job_id].add(websocket)
        logger.debug(f"Subscribed to job {job_id}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific WebSocket."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send message: {e}")

    async def broadcast_to_user(self, message: dict, user_id: int):
        """Broadcast message to all connections for a user."""
        if user_id in self.active_connections:
            disconnected = set()

            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Failed to send to user {user_id}: {e}")
                    disconnected.add(connection)

            # Clean up disconnected
            for connection in disconnected:
                self.active_connections[user_id].discard(connection)

    async def broadcast_to_project(self, message: dict, project_id: int):
        """Broadcast message to all subscribers of a project."""
        if project_id in self.project_subscriptions:
            disconnected = set()

            for connection in self.project_subscriptions[project_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Failed to send to project {project_id}: {e}")
                    disconnected.add(connection)

            # Clean up disconnected
            for connection in disconnected:
                self.project_subscriptions[project_id].discard(connection)

    async def broadcast_to_job(self, message: dict, job_id: int):
        """Broadcast message to all subscribers of a job."""
        if job_id in self.job_subscriptions:
            disconnected = set()

            for connection in self.job_subscriptions[job_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Failed to send to job {job_id}: {e}")
                    disconnected.add(connection)

            # Clean up disconnected
            for connection in disconnected:
                self.job_subscriptions[job_id].discard(connection)

    async def broadcast_job_update(self, job_id: int, status: str, result: dict = None):
        """
        Broadcast job status update to all relevant subscribers.

        This should be called whenever a job status changes.
        """
        message = {
            "type": "job_update",
            "job_id": job_id,
            "status": status,
            "timestamp": asyncio.get_event_loop().time()
        }

        if result:
            message["result"] = result

        # Send to job subscribers
        await self.broadcast_to_job(message, job_id)

        logger.info(f"Broadcasted job {job_id} update: {status}")


# Global connection manager
manager = ConnectionManager()


async def authenticate_websocket(websocket: WebSocket, token: str = None) -> int:
    """
    Authenticate WebSocket connection.

    Args:
        websocket: WebSocket connection
        token: JWT token

    Returns:
        user_id if authenticated

    Raises:
        WebSocketDisconnect: If authentication fails
    """
    if not token:
        await websocket.close(code=1008, reason="Missing authentication token")
        raise WebSocketDisconnect()

    # Decode token
    payload = decode_access_token(token)

    if not payload:
        await websocket.close(code=1008, reason="Invalid token")
        raise WebSocketDisconnect()

    user_id = payload.get("sub")

    if not user_id:
        await websocket.close(code=1008, reason="Invalid token payload")
        raise WebSocketDisconnect()

    return user_id


async def websocket_endpoint(websocket: WebSocket, token: str = None):
    """
    Main WebSocket endpoint.

    Usage:
        ws = new WebSocket('ws://localhost:8000/ws?token=YOUR_JWT_TOKEN')
    """
    # Authenticate
    try:
        user_id = await authenticate_websocket(websocket, token)
    except WebSocketDisconnect:
        return

    # Connect
    await manager.connect(websocket, user_id)

    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_json()

            # Handle different message types
            message_type = data.get("type")

            if message_type == "subscribe_project":
                project_id = data.get("project_id")
                if project_id:
                    manager.subscribe_to_project(websocket, project_id)
                    await manager.send_personal_message(
                        {"type": "subscribed", "project_id": project_id},
                        websocket
                    )

            elif message_type == "subscribe_job":
                job_id = data.get("job_id")
                if job_id:
                    manager.subscribe_to_job(websocket, job_id)
                    await manager.send_personal_message(
                        {"type": "subscribed", "job_id": job_id},
                        websocket
                    )

            elif message_type == "ping":
                await manager.send_personal_message(
                    {"type": "pong", "timestamp": asyncio.get_event_loop().time()},
                    websocket
                )

            else:
                await manager.send_personal_message(
                    {"type": "error", "message": f"Unknown message type: {message_type}"},
                    websocket
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, user_id)


# Helper function to broadcast job updates (called from worker)
def broadcast_job_update_sync(job_id: int, status: str, result: dict = None):
    """
    Synchronous wrapper for broadcasting job updates.

    This can be called from the worker (synchronous context).
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Create task in existing loop
            asyncio.create_task(manager.broadcast_job_update(job_id, status, result))
        else:
            # Run in new loop
            asyncio.run(manager.broadcast_job_update(job_id, status, result))
    except Exception as e:
        logger.error(f"Failed to broadcast job update: {e}")


class ServerSentEvents:
    """
    Server-Sent Events (SSE) fallback for browsers that don't support WebSockets.

    Usage:
        const eventSource = new EventSource('/sse/jobs/123?token=YOUR_TOKEN');
        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('Job update:', data);
        };
    """

    def __init__(self):
        # Map of job_id -> list of queues
        self.job_queues: Dict[int, List[asyncio.Queue]] = {}

    async def subscribe(self, job_id: int) -> asyncio.Queue:
        """Subscribe to job updates."""
        queue = asyncio.Queue()

        if job_id not in self.job_queues:
            self.job_queues[job_id] = []

        self.job_queues[job_id].append(queue)
        return queue

    def unsubscribe(self, job_id: int, queue: asyncio.Queue):
        """Unsubscribe from job updates."""
        if job_id in self.job_queues:
            try:
                self.job_queues[job_id].remove(queue)
                if not self.job_queues[job_id]:
                    del self.job_queues[job_id]
            except ValueError:
                pass

    async def publish(self, job_id: int, data: dict):
        """Publish update to all subscribers."""
        if job_id in self.job_queues:
            for queue in self.job_queues[job_id]:
                try:
                    await queue.put(data)
                except Exception as e:
                    logger.error(f"Failed to publish to queue: {e}")


# Global SSE manager
sse_manager = ServerSentEvents()
