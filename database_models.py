"""
Database models for distributed ticket verification system.
Replaces CSV-based storage with PostgreSQL for multi-device support.
"""

import os
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    from psycopg2.pool import ThreadedConnectionPool
except ImportError:
    print("PostgreSQL dependencies not installed. Run: pip install psycopg2-binary")
    psycopg2 = None

logger = logging.getLogger(__name__)


@dataclass
class Ticket:
    """Ticket model for database storage"""
    id: str
    email: str
    event_name: str
    encrypted_data: str
    qr_code_data: str
    status: str = 'generated'
    created_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None
    device_id: Optional[str] = None
    version: int = 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert ticket to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'event_name': self.event_name,
            'encrypted_data': self.encrypted_data,
            'qr_code_data': self.qr_code_data,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'verified_by': self.verified_by,
            'device_id': self.device_id,
            'version': self.version
        }


@dataclass
class StaffDevice:
    """Staff device model for multi-device management"""
    id: str
    device_name: str
    staff_email: str
    last_active: Optional[datetime] = None
    is_active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert staff device to dictionary"""
        return {
            'id': self.id,
            'device_name': self.device_name,
            'staff_email': self.staff_email,
            'last_active': self.last_active.isoformat() if self.last_active else None,
            'is_active': self.is_active
        }


@dataclass
class VerificationLog:
    """Verification log model for audit trail"""
    id: str
    ticket_id: str
    staff_email: str
    device_id: str
    action: str  # 'verified', 'attempted', 'failed'
    timestamp: Optional[datetime] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert verification log to dictionary"""
        return {
            'id': self.id,
            'ticket_id': self.ticket_id,
            'staff_email': self.staff_email,
            'device_id': self.device_id,
            'action': self.action,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent
        }


class DatabaseManager:
    """PostgreSQL database manager for distributed ticket system"""
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv('DATABASE_URL', 
            'postgresql://localhost:5432/event_tickets')
        self.connection_pool = None
        self.logger = logging.getLogger(__name__)
        
        if psycopg2 is None:
            raise ImportError("PostgreSQL dependencies not installed")
        
        self._initialize_connection_pool()
        self._create_tables()
    
    def _initialize_connection_pool(self):
        """Initialize connection pool for multi-device access"""
        try:
            self.connection_pool = ThreadedConnectionPool(
                minconn=1,
                maxconn=20,
                dsn=self.database_url
            )
            self.logger.info("Database connection pool initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize connection pool: {e}")
            raise
    
    def _get_connection(self):
        """Get connection from pool"""
        return self.connection_pool.getconn()
    
    def _return_connection(self, conn):
        """Return connection to pool"""
        self.connection_pool.putconn(conn)
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Create tickets table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tickets (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    email VARCHAR(255) NOT NULL,
                    event_name VARCHAR(255) NOT NULL,
                    encrypted_data TEXT NOT NULL,
                    qr_code_data TEXT NOT NULL,
                    status VARCHAR(50) DEFAULT 'generated',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    sent_at TIMESTAMP NULL,
                    verified_at TIMESTAMP NULL,
                    verified_by VARCHAR(255) NULL,
                    device_id VARCHAR(255) NULL,
                    version INTEGER DEFAULT 1,
                    UNIQUE(email, event_name)
                );
            """)
            
            # Create indexes for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_tickets_email ON tickets(email);
                CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);
                CREATE INDEX IF NOT EXISTS idx_tickets_event ON tickets(event_name);
            """)
            
            # Create staff_devices table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS staff_devices (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    device_name VARCHAR(255) NOT NULL,
                    staff_email VARCHAR(255) NOT NULL,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT true,
                    UNIQUE(device_name, staff_email)
                );
            """)
            
            # Create verification_logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS verification_logs (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    ticket_id UUID REFERENCES tickets(id),
                    staff_email VARCHAR(255) NOT NULL,
                    device_id VARCHAR(255) NOT NULL,
                    action VARCHAR(50) NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address INET,
                    user_agent TEXT
                );
            """)
            
            # Create index for logs
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_logs_ticket ON verification_logs(ticket_id);
                CREATE INDEX IF NOT EXISTS idx_logs_staff ON verification_logs(staff_email);
                CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON verification_logs(timestamp);
            """)
            
            conn.commit()
            self.logger.info("Database tables created successfully")
            
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Failed to create tables: {e}")
            raise
        finally:
            if conn:
                self._return_connection(conn)
    
    def save_ticket(self, ticket: Ticket) -> bool:
        """Save a ticket to database with conflict resolution"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO tickets (
                    id, email, event_name, encrypted_data, qr_code_data,
                    status, created_at, sent_at, verified_at, verified_by, device_id, version
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (email, event_name) 
                DO UPDATE SET
                    encrypted_data = EXCLUDED.encrypted_data,
                    qr_code_data = EXCLUDED.qr_code_data,
                    status = EXCLUDED.status,
                    version = tickets.version + 1
            """, (
                ticket.id, ticket.email, ticket.event_name, ticket.encrypted_data,
                ticket.qr_code_data, ticket.status, ticket.created_at, ticket.sent_at,
                ticket.verified_at, ticket.verified_by, ticket.device_id, ticket.version
            ))
            
            conn.commit()
            self.logger.info(f"Saved ticket {ticket.id} for {ticket.email}")
            return True
            
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Failed to save ticket: {e}")
            return False
        finally:
            if conn:
                self._return_connection(conn)
    
    def find_ticket_by_id(self, ticket_id: str) -> Optional[Ticket]:
        """Find ticket by ID"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("SELECT * FROM tickets WHERE id = %s", (ticket_id,))
            row = cursor.fetchone()
            
            if row:
                return Ticket(
                    id=str(row['id']),
                    email=row['email'],
                    event_name=row['event_name'],
                    encrypted_data=row['encrypted_data'],
                    qr_code_data=row['qr_code_data'],
                    status=row['status'],
                    created_at=row['created_at'],
                    sent_at=row['sent_at'],
                    verified_at=row['verified_at'],
                    verified_by=row['verified_by'],
                    device_id=row['device_id'],
                    version=row['version']
                )
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to find ticket {ticket_id}: {e}")
            return None
        finally:
            if conn:
                self._return_connection(conn)
    
    def verify_ticket_atomic(self, ticket_id: str, staff_email: str, 
                           device_id: str, ip_address: str = None) -> Dict[str, Any]:
        """Atomically verify a ticket with conflict resolution"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Start transaction
            cursor.execute("BEGIN")
            
            # Lock the ticket row for update
            cursor.execute("""
                SELECT * FROM tickets WHERE id = %s FOR UPDATE
            """, (ticket_id,))
            
            ticket_row = cursor.fetchone()
            if not ticket_row:
                conn.rollback()
                return {
                    'success': False,
                    'error': 'Ticket not found',
                    'error_code': 'NOT_FOUND'
                }
            
            # Check if already verified
            if ticket_row['status'] == 'used':
                conn.rollback()
                return {
                    'success': False,
                    'error': 'Ticket already verified',
                    'error_code': 'ALREADY_USED',
                    'verified_by': ticket_row['verified_by'],
                    'verified_at': ticket_row['verified_at'].isoformat() if ticket_row['verified_at'] else None
                }
            
            # Update ticket as verified
            now = datetime.now(timezone.utc)
            cursor.execute("""
                UPDATE tickets 
                SET status = 'used', 
                    verified_at = %s, 
                    verified_by = %s, 
                    device_id = %s,
                    version = version + 1
                WHERE id = %s
            """, (now, staff_email, device_id, ticket_id))
            
            # Log the verification
            cursor.execute("""
                INSERT INTO verification_logs 
                (ticket_id, staff_email, device_id, action, timestamp, ip_address)
                VALUES (%s, %s, %s, 'verified', %s, %s)
            """, (ticket_id, staff_email, device_id, now, ip_address))
            
            # Commit transaction
            conn.commit()
            
            self.logger.info(f"Ticket {ticket_id} verified by {staff_email} on {device_id}")
            
            return {
                'success': True,
                'ticket_id': ticket_id,
                'email': ticket_row['email'],
                'event_name': ticket_row['event_name'],
                'verified_by': staff_email,
                'verified_at': now.isoformat(),
                'device_id': device_id
            }
            
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Failed to verify ticket {ticket_id}: {e}")
            return {
                'success': False,
                'error': f'Database error: {str(e)}',
                'error_code': 'DATABASE_ERROR'
            }
        finally:
            if conn:
                self._return_connection(conn)
    
    def get_all_tickets(self, event_name: str = None) -> List[Ticket]:
        """Get all tickets, optionally filtered by event"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            if event_name:
                cursor.execute("SELECT * FROM tickets WHERE event_name = %s ORDER BY created_at", 
                             (event_name,))
            else:
                cursor.execute("SELECT * FROM tickets ORDER BY created_at")
            
            tickets = []
            for row in cursor.fetchall():
                tickets.append(Ticket(
                    id=str(row['id']),
                    email=row['email'],
                    event_name=row['event_name'],
                    encrypted_data=row['encrypted_data'],
                    qr_code_data=row['qr_code_data'],
                    status=row['status'],
                    created_at=row['created_at'],
                    sent_at=row['sent_at'],
                    verified_at=row['verified_at'],
                    verified_by=row['verified_by'],
                    device_id=row['device_id'],
                    version=row['version']
                ))
            
            return tickets
            
        except Exception as e:
            self.logger.error(f"Failed to get tickets: {e}")
            return []
        finally:
            if conn:
                self._return_connection(conn)
    
    def register_device(self, device_name: str, staff_email: str) -> str:
        """Register a new staff device"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            device_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO staff_devices (id, device_name, staff_email, last_active, is_active)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (device_name, staff_email)
                DO UPDATE SET last_active = CURRENT_TIMESTAMP, is_active = true
                RETURNING id
            """, (device_id, device_name, staff_email, datetime.now(timezone.utc), True))
            
            result = cursor.fetchone()
            conn.commit()
            
            device_id = str(result[0]) if result else device_id
            self.logger.info(f"Registered device {device_name} for {staff_email}")
            return device_id
            
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Failed to register device: {e}")
            return None
        finally:
            if conn:
                self._return_connection(conn)
    
    def get_active_devices(self) -> List[StaffDevice]:
        """Get all active staff devices"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT * FROM staff_devices 
                WHERE is_active = true 
                ORDER BY last_active DESC
            """)
            
            devices = []
            for row in cursor.fetchall():
                devices.append(StaffDevice(
                    id=str(row['id']),
                    device_name=row['device_name'],
                    staff_email=row['staff_email'],
                    last_active=row['last_active'],
                    is_active=row['is_active']
                ))
            
            return devices
            
        except Exception as e:
            self.logger.error(f"Failed to get active devices: {e}")
            return []
        finally:
            if conn:
                self._return_connection(conn)
    
    def get_verification_stats(self, event_name: str = None) -> Dict[str, Any]:
        """Get verification statistics"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Base query
            base_query = "SELECT status, COUNT(*) as count FROM tickets"
            params = []
            
            if event_name:
                base_query += " WHERE event_name = %s"
                params.append(event_name)
            
            base_query += " GROUP BY status"
            
            cursor.execute(base_query, params)
            status_counts = {row['status']: row['count'] for row in cursor.fetchall()}
            
            # Get recent verification activity
            recent_query = """
                SELECT vl.*, t.email, t.event_name 
                FROM verification_logs vl
                JOIN tickets t ON vl.ticket_id = t.id
            """
            
            if event_name:
                recent_query += " WHERE t.event_name = %s"
            
            recent_query += " ORDER BY vl.timestamp DESC LIMIT 10"
            
            cursor.execute(recent_query, params)
            recent_activity = [dict(row) for row in cursor.fetchall()]
            
            return {
                'status_counts': status_counts,
                'recent_activity': recent_activity,
                'total_tickets': sum(status_counts.values())
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get verification stats: {e}")
            return {'status_counts': {}, 'recent_activity': [], 'total_tickets': 0}
        finally:
            if conn:
                self._return_connection(conn)
    
    def close(self):
        """Close all database connections"""
        if self.connection_pool:
            self.connection_pool.closeall()
            self.logger.info("Database connections closed")