"""
Supporting models for caching, idempotency, and audit trails.

This module defines supporting models that provide infrastructure features
like report caching, request idempotency, and audit logging.
"""

from sqlalchemy import Column, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from .base import Base, generate_uuid


class ReportCache(Base):
    """
    Report cache model for storing precomputed report results.

    Caches expensive report calculations to improve performance.
    Reports are keyed by user and report type, with JSON payloads
    storing the computed results.

    Attributes:
        id: Primary key (UUID)
        user_id: Foreign key to User
        key: Cache key identifying the report type
        payload_json: JSON payload containing the cached report data
        created_at: Timestamp when cache entry was created (inherited from Base)
    """

    __tablename__ = "report_cache"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=generate_uuid,
        comment="Unique identifier for the cache entry",
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="User this cache entry belongs to",
    )

    key = Column(
        String(255), nullable=False, comment="Cache key identifying the report type"
    )

    payload_json = Column(
        JSONB, nullable=False, comment="JSON payload containing the cached report data"
    )

    # Relationships
    # User this cache entry belongs to
    user = relationship("User", back_populates="report_cache")

    # Constraints
    __table_args__ = (
        UniqueConstraint("user_id", "key", name="uq_report_cache_user_key"),
    )

    def __repr__(self):
        return f"<ReportCache(id={self.id}, user_id={self.user_id}, key='{self.key}')>"


class IdempotencyKey(Base):
    """
    Idempotency key model for preventing duplicate requests.

    Stores idempotency keys to ensure that duplicate requests are handled
    gracefully. Keys are scoped to users and endpoints, with request hashes
    to detect payload changes.

    Attributes:
        id: Primary key (UUID)
        user_id: Foreign key to User
        endpoint: API endpoint this key applies to
        key: The idempotency key value
        request_hash: Hash of the request payload
        created_at: Timestamp when key was created (inherited from Base)
    """

    __tablename__ = "idempotency_keys"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=generate_uuid,
        comment="Unique identifier for the idempotency key",
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="User this key belongs to",
    )

    endpoint = Column(
        String(255), nullable=False, comment="API endpoint this key applies to"
    )

    key = Column(String(255), nullable=False, comment="The idempotency key value")

    request_hash = Column(
        String(64),  # SHA-256 hash
        nullable=False,
        comment="Hash of the request payload",
    )

    # Relationships
    # User this key belongs to
    user = relationship("User", back_populates="idempotency_keys")

    # Constraints
    __table_args__ = (
        UniqueConstraint(
            "user_id", "endpoint", "key", name="uq_idempotency_key_user_endpoint"
        ),
    )

    def __repr__(self):
        return f"<IdempotencyKey(id={self.id}, user_id={self.user_id}, endpoint='{self.endpoint}', key='{self.key}')>"


class AuditEvent(Base):
    """
    Audit event model for tracking system actions.

    Provides an append-only log of user and system actions for traceability
    and debugging. Stores entity information and payload snapshots.

    Attributes:
        id: Primary key (UUID)
        user_id: Foreign key to User
        entity_type: Type of entity that was modified
        entity_id: ID of the entity that was modified
        payload_json: JSON payload containing the event details
        created_at: Timestamp when event was created (inherited from Base)
    """

    __tablename__ = "audit_events"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=generate_uuid,
        comment="Unique identifier for the audit event",
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="User who performed the action",
    )

    entity_type = Column(
        String(50),
        nullable=False,
        comment="Type of entity that was modified (e.g., 'exercise', 'session')",
    )

    entity_id = Column(
        UUID(as_uuid=True), nullable=False, comment="ID of the entity that was modified"
    )

    payload_json = Column(
        JSONB, nullable=False, comment="JSON payload containing the event details"
    )

    # Relationships
    # User who performed the action
    user = relationship("User", back_populates="audit_events")

    def __repr__(self):
        return f"<AuditEvent(id={self.id}, user_id={self.user_id}, entity_type='{self.entity_type}', entity_id={self.entity_id})>"
