"""
Base model class for all SetLogs models.

This module provides the common base class that all models inherit from,
including common fields and functionality.
"""

import uuid

from sqlalchemy import Column, DateTime, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base


class BaseModel:
    """
    Base class for all SetLogs models.

    Provides common fields and functionality that all models inherit.
    Uses PostgreSQL-specific features like UUID primary keys and TIMESTAMPTZ.
    """

    # Primary key field that all models inherit
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=func.gen_random_uuid(),
        comment="Unique identifier for the record",
    )

    # Common fields that all models inherit
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        comment="Timestamp when the record was created",
    )

    # Version field for optimistic locking (where needed)
    version = Column(
        Integer,
        nullable=False,
        default=1,
        comment="Version number for optimistic locking",
    )


# Create the declarative base with our custom Base class
Base = declarative_base(cls=BaseModel)


def generate_uuid():
    """Generate a new UUID for primary keys."""
    return str(uuid.uuid4())
