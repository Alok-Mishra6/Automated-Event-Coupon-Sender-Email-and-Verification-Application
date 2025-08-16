"""
Real-time WebSocket service for distributed ticket verification.
Enables instant synchronization across multiple devices and staff members.
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from flask import request
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    print("Redis not available. Install with: pip install redis")
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class RealtimeService:
    """Real-time service for multi-device ticket verification synchronization"""
    
    def __init__(self, app=None, redis_url: str = None):
        self.app = app
        self.socketio = None
        self.redis_client = None
        self.connected_devices = {}  # device_id -> {staff_email, device_name, room}
        self.active_rooms = {}  # event_name -> set of device_ids
        
        # Initialize Redis if available
        if REDIS_AVAILABLE and redis_url:
            try:
                self.redis_client = redis.from_url(redis_url or os.getenv('REDIS_URL', 'redis://localhost:6379'))
                self.redis_client.ping()  # Test connection
                logger.info("Redis connection established")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}")
                self.redis_client = None
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize SocketIO with Flask app"""
        self.app = app
        self.socketio = SocketIO(
            app,
            cors_allowed_origins="*",
            async_mode='threading',
            logger=True,
            engineio_logger=True
        )
        
        # Register event handlers
        self._register_handlers()
        logger.info("Real-time service initialized")
    
    def _register_handlers(self):
        """Register WebSocket event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            client_id = request.sid
            logger.info(f"Client connected: {client_id}")
            emit('connected', {'status': 'Connected to verification system'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            client_id = request.sid
            
            # Remove from connected devices
            device_info = self.connected_devices.pop(client_id, None)
            if device_info:
                event_room = device_info.get('room')
                if event_room and event_room in self.active_rooms:
                    self.active_rooms[event_room].discard(client_id)
                    
                    # Broadcast device disconnection
                    self.socketio.emit('device_disconnected', {
                        'device_id': client_id,
                        'staff_email': device_info.get('staff_email'),
                        'device_name': device_info.get('device_name'),
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }, room=event_room)
            
            logger.info(f"Client disconnected: {client_id}")
        
        @self.socketio.on('join_event')
        def handle_join_event(data):
            """Handle device joining an event room"""
            client_id = request.sid
            event_name = data.get('event_name')
            staff_email = data.get('staff_email')
            device_name = data.get('device_name', f'Device-{client_id[:8]}')
            
            if not event_name or not staff_email:
                emit('error', {'message': 'Event name and staff email required'})
                return
            
            # Join the event room
            room_name = f"event_{event_name}"
            join_room(room_name)
            
            # Store device information
            self.connected_devices[client_id] = {
                'staff_email': staff_email,
                'device_name': device_name,
                'room': room_name,
                'event_name': event_name,
                'joined_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Add to active rooms
            if room_name not in self.active_rooms:
                self.active_rooms[room_name] = set()
            self.active_rooms[room_name].add(client_id)
            
            # Broadcast device connection to other devices in the room
            self.socketio.emit('device_connected', {
                'device_id': client_id,
                'staff_email': staff_email,
                'device_name': device_name,
                'event_name': event_name,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }, room=room_name, include_self=False)
            
            # Send current active devices to the new device
            active_devices = []
            for device_id in self.active_rooms[room_name]:
                if device_id != client_id and device_id in self.connected_devices:
                    device_info = self.connected_devices[device_id]
                    active_devices.append({
                        'device_id': device_id,
                        'staff_email': device_info['staff_email'],
                        'device_name': device_info['device_name'],
                        'joined_at': device_info['joined_at']
                    })
            
            emit('joined_event', {
                'event_name': event_name,
                'room': room_name,
                'active_devices': active_devices,
                'device_count': len(self.active_rooms[room_name])
            })
            
            logger.info(f"Device {device_name} ({staff_email}) joined event {event_name}")
        
        @self.socketio.on('leave_event')
        def handle_leave_event():
            """Handle device leaving an event room"""
            client_id = request.sid
            device_info = self.connected_devices.get(client_id)
            
            if device_info:
                room_name = device_info['room']
                leave_room(room_name)
                
                # Remove from active rooms
                if room_name in self.active_rooms:
                    self.active_rooms[room_name].discard(client_id)
                
                # Broadcast device leaving
                self.socketio.emit('device_left', {
                    'device_id': client_id,
                    'staff_email': device_info['staff_email'],
                    'device_name': device_info['device_name'],
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }, room=room_name)
                
                emit('left_event', {'status': 'Left event room'})
                logger.info(f"Device {device_info['device_name']} left event {device_info['event_name']}")
        
        @self.socketio.on('verify_ticket')
        def handle_verify_ticket(data):
            """Handle real-time ticket verification"""
            client_id = request.sid
            device_info = self.connected_devices.get(client_id)
            
            if not device_info:
                emit('error', {'message': 'Device not registered for any event'})
                return
            
            ticket_id = data.get('ticket_id')
            if not ticket_id:
                emit('error', {'message': 'Ticket ID required'})
                return
            
            # Broadcast verification attempt to all devices in the room
            room_name = device_info['room']
            verification_data = {
                'ticket_id': ticket_id,
                'staff_email': device_info['staff_email'],
                'device_name': device_info['device_name'],
                'device_id': client_id,
                'action': 'verifying',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            self.socketio.emit('ticket_verification_started', verification_data, room=room_name)
            logger.info(f"Ticket verification started: {ticket_id} by {device_info['staff_email']}")
        
        @self.socketio.on('request_stats')
        def handle_request_stats():
            """Handle request for real-time statistics"""
            client_id = request.sid
            device_info = self.connected_devices.get(client_id)
            
            if device_info:
                room_name = device_info['room']
                device_count = len(self.active_rooms.get(room_name, set()))
                
                emit('stats_update', {
                    'active_devices': device_count,
                    'event_name': device_info['event_name'],
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
    
    def broadcast_ticket_verified(self, ticket_data: Dict[str, Any], event_name: str):
        """Broadcast ticket verification to all devices in event room"""
        if not self.socketio:
            return
        
        room_name = f"event_{event_name}"
        
        broadcast_data = {
            'ticket_id': ticket_data.get('ticket_id'),
            'email': ticket_data.get('email'),
            'verified_by': ticket_data.get('verified_by'),
            'verified_at': ticket_data.get('verified_at'),
            'device_id': ticket_data.get('device_id'),
            'action': 'verified',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        self.socketio.emit('ticket_verified', broadcast_data, room=room_name)
        
        # Store in Redis for persistence if available
        if self.redis_client:
            try:
                key = f"verification:{event_name}:{ticket_data.get('ticket_id')}"
                self.redis_client.setex(key, 3600, json.dumps(broadcast_data))  # 1 hour TTL
            except Exception as e:
                logger.warning(f"Failed to store verification in Redis: {e}")
        
        logger.info(f"Broadcasted ticket verification: {ticket_data.get('ticket_id')}")
    
    def broadcast_ticket_failed(self, ticket_id: str, error_data: Dict[str, Any], 
                               event_name: str, staff_email: str, device_id: str):
        """Broadcast failed ticket verification"""
        if not self.socketio:
            return
        
        room_name = f"event_{event_name}"
        
        broadcast_data = {
            'ticket_id': ticket_id,
            'error': error_data.get('error'),
            'error_code': error_data.get('error_code'),
            'staff_email': staff_email,
            'device_id': device_id,
            'action': 'failed',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        self.socketio.emit('ticket_verification_failed', broadcast_data, room=room_name)
        logger.info(f"Broadcasted ticket verification failure: {ticket_id}")
    
    def broadcast_stats_update(self, stats_data: Dict[str, Any], event_name: str):
        """Broadcast statistics update to all devices"""
        if not self.socketio:
            return
        
        room_name = f"event_{event_name}"
        
        broadcast_data = {
            'stats': stats_data,
            'event_name': event_name,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        self.socketio.emit('stats_updated', broadcast_data, room=room_name)
        logger.info(f"Broadcasted stats update for event: {event_name}")
    
    def broadcast_device_activity(self, activity_data: Dict[str, Any], event_name: str):
        """Broadcast device activity to all devices in room"""
        if not self.socketio:
            return
        
        room_name = f"event_{event_name}"
        
        broadcast_data = {
            'activity': activity_data,
            'event_name': event_name,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        self.socketio.emit('device_activity', broadcast_data, room=room_name)
        logger.info(f"Broadcasted device activity for event: {event_name}")
    
    def get_active_devices_for_event(self, event_name: str) -> List[Dict[str, Any]]:
        """Get list of active devices for an event"""
        room_name = f"event_{event_name}"
        active_devices = []
        
        if room_name in self.active_rooms:
            for device_id in self.active_rooms[room_name]:
                if device_id in self.connected_devices:
                    device_info = self.connected_devices[device_id]
                    active_devices.append({
                        'device_id': device_id,
                        'staff_email': device_info['staff_email'],
                        'device_name': device_info['device_name'],
                        'joined_at': device_info['joined_at']
                    })
        
        return active_devices
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get overall system statistics"""
        total_devices = len(self.connected_devices)
        active_events = len(self.active_rooms)
        
        event_stats = {}
        for room_name, devices in self.active_rooms.items():
            if room_name.startswith('event_'):
                event_name = room_name[6:]  # Remove 'event_' prefix
                event_stats[event_name] = len(devices)
        
        return {
            'total_connected_devices': total_devices,
            'active_events': active_events,
            'event_device_counts': event_stats,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def disconnect_device(self, device_id: str, reason: str = "Admin disconnect"):
        """Administratively disconnect a device"""
        if not self.socketio:
            return False
        
        if device_id in self.connected_devices:
            device_info = self.connected_devices[device_id]
            
            # Notify the device
            self.socketio.emit('force_disconnect', {
                'reason': reason,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }, room=device_id)
            
            # Disconnect the device
            self.socketio.disconnect(device_id)
            
            logger.info(f"Administratively disconnected device: {device_id} - {reason}")
            return True
        
        return False
    
    def send_alert_to_event(self, event_name: str, alert_data: Dict[str, Any]):
        """Send alert to all devices in an event"""
        if not self.socketio:
            return
        
        room_name = f"event_{event_name}"
        
        alert_message = {
            'alert': alert_data,
            'event_name': event_name,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        self.socketio.emit('system_alert', alert_message, room=room_name)
        logger.info(f"Sent alert to event {event_name}: {alert_data.get('message', 'No message')}")


# Global instance
realtime_service = RealtimeService()


def init_realtime_service(app, redis_url: str = None):
    """Initialize the real-time service with Flask app"""
    realtime_service.init_app(app)
    return realtime_service