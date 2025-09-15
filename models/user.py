"""
User model for authentication and user management.

This module defines the User model which represents user accounts in the system.
Users own exercises, programs, and sessions.
"""

from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, generate_uuid


class User(Base):
    """
    User account model.

    Represents a user account in the SetLogs system. Users can create exercises,
    programs, and log workout sessions. Each user has a unique email address
    and encrypted password.

    Attributes:
        id: Primary key (UUID)
        email: User's email address (unique)
        password_hash: Encrypted password
        created_at: Timestamp when account was created (inherited from Base)
    """

    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=generate_uuid,
        comment="Unique identifier for the user",
    )

    email = Column(
        String(255),
        nullable=False,
        unique=True,
        comment="User's email address (unique)",
    )

    password_hash = Column(Text, nullable=False, comment="Encrypted password hash")

    # Relationships
    # Exercises created by this user
    exercises = relationship(
        "Exercise", back_populates="created_by_user", cascade="all, delete-orphan"
    )

    # Programs created by this user
    programs = relationship(
        "Program", back_populates="owner", cascade="all, delete-orphan"
    )

    # Workout sessions performed by this user
    sessions = relationship(
        "Session", back_populates="user", cascade="all, delete-orphan"
    )

    # Program assignments for this user
    user_programs = relationship(
        "UserProgram", back_populates="user", cascade="all, delete-orphan"
    )

    # Cached report data for this user
    report_cache = relationship(
        "ReportCache", back_populates="user", cascade="all, delete-orphan"
    )

    # Idempotency keys for this user's requests
    idempotency_keys = relationship(
        "IdempotencyKey", back_populates="user", cascade="all, delete-orphan"
    )

    # Audit trail for this user's actions
    audit_events = relationship(
        "AuditEvent", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
