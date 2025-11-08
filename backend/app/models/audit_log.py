"""
Audit-Log-Modell für Datenbank-persistentes Logging
Zusätzlich zu File-basiertem Logging
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.sql import func

from app.core.database import Base


class AuditLog(Base):
    """
    Audit-Log für alle sicherheitsrelevanten Aktionen

    Gem. Art. 32 DSGVO - Protokollierung von Zugriffen
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Wer
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    username = Column(String(100), nullable=True)  # Denormalisiert für History

    # Was
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=True, index=True)
    resource_id = Column(String(100), nullable=True, index=True)

    # Wann
    timestamp = Column(DateTime, server_default=func.now(), nullable=False, index=True)

    # Von wo
    ip_address = Column(String(45), nullable=True)  # IPv4/IPv6
    user_agent = Column(String(500), nullable=True)

    # Ergebnis
    success = Column(Boolean, nullable=False, default=True)
    error_message = Column(Text, nullable=True)

    # Zusätzliche Daten (JSON)
    additional_data = Column(JSON, nullable=True)

    # HTTP-Request-Details (optional)
    http_method = Column(String(10), nullable=True)
    http_path = Column(String(500), nullable=True)
    http_status = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<AuditLog(id={self.id}, user={self.username}, action={self.action}, time={self.timestamp})>"
