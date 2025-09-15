"""
Exercise model for workout exercise definitions.

This module defines the Exercise model which represents exercise definitions
that users can create and reference in their workout sessions.
"""

from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import relationship

from .base import Base, generate_uuid


class Exercise(Base):
    """
    Exercise definition model.

    Represents a logical exercise definition (e.g., "Bench Press", "Squat").
    Users create exercises to define the movements they perform in their workouts.
    Each exercise has a name, optional description, and target muscle groups.

    Attributes:
        id: Primary key (UUID)
        slug: URL-friendly unique identifier
        name: Exercise name (e.g., "Bench Press")
        description: Optional exercise description
        target_muscles: Array of target muscle groups
        created_by: Foreign key to User who created this exercise
        created_at: Timestamp when exercise was created (inherited from Base)
    """

    __tablename__ = "exercises"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=generate_uuid,
        comment="Unique identifier for the exercise",
    )

    slug = Column(
        String(255),
        nullable=False,
        unique=True,
        comment="URL-friendly unique identifier for the exercise",
    )

    name = Column(
        String(255), nullable=False, comment="Exercise name (e.g., 'Bench Press')"
    )

    description = Column(Text, nullable=True, comment="Optional exercise description")

    target_muscles: "Column[list[str]]" = Column(
        ARRAY(String),
        nullable=False,
        default=[],
        comment="Array of target muscle groups (e.g., ['chest', 'triceps'])",
    )

    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="User who created this exercise",
    )

    # Relationships
    # User who created this exercise
    created_by_user = relationship("User", back_populates="exercises")

    # Sets performed for this exercise
    sets = relationship("Set", back_populates="exercise", cascade="all, delete-orphan")

    # Program entries that include this exercise
    program_entries = relationship(
        "ProgramEntry", back_populates="exercise", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Exercise(id={self.id}, name='{self.name}', slug='{self.slug}')>"
