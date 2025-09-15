"""
Program models for workout program templates.

This module defines the Program and ProgramEntry models which represent
reusable workout program templates that users can create and follow.
"""

from sqlalchemy import Column, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, generate_uuid


class Program(Base):
    """
    Workout program template model.

    Represents a reusable template that groups exercises into a structured plan.
    Programs are created by users and can be assigned to other users or used
    as templates for creating workout sessions.

    Attributes:
        id: Primary key (UUID)
        owner_id: Foreign key to User who created this program
        name: Program name (e.g., "5/3/1 Strength")
        description: Optional program description
        created_at: Timestamp when program was created (inherited from Base)
    """

    __tablename__ = "programs"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=generate_uuid,
        comment="Unique identifier for the program",
    )

    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="User who created this program",
    )

    name = Column(
        String(255), nullable=False, comment="Program name (e.g., '5/3/1 Strength')"
    )

    description = Column(Text, nullable=True, comment="Optional program description")

    # Relationships
    # User who created this program
    owner = relationship("User", back_populates="programs")

    # Exercises included in this program
    entries = relationship(
        "ProgramEntry", back_populates="program", cascade="all, delete-orphan"
    )

    # User assignments to this program
    user_programs = relationship(
        "UserProgram", back_populates="program", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Program(id={self.id}, name='{self.name}')>"


class ProgramEntry(Base):
    """
    Program exercise entry model.

    Represents a specific exercise within a program, including its day
    and position within that day. Programs can have multiple exercises
    per day and span multiple days.

    Attributes:
        id: Primary key (UUID)
        program_id: Foreign key to Program
        exercise_id: Foreign key to Exercise
        day_of_week: Day of the week (0=Sunday, 1=Monday, etc.)
        position: Position within the day (1-based)
        created_at: Timestamp when entry was created (inherited from Base)
    """

    __tablename__ = "program_entries"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=generate_uuid,
        comment="Unique identifier for the program entry",
    )

    program_id = Column(
        UUID(as_uuid=True),
        ForeignKey("programs.id", ondelete="CASCADE"),
        nullable=False,
        comment="Program this entry belongs to",
    )

    exercise_id = Column(
        UUID(as_uuid=True),
        ForeignKey("exercises.id", ondelete="CASCADE"),
        nullable=False,
        comment="Exercise included in this program entry",
    )

    day_of_week = Column(
        Integer,
        nullable=False,
        comment="Day of the week (0=Sunday, 1=Monday, ..., 6=Saturday)",
    )

    position = Column(
        Integer, nullable=False, default=1, comment="Position within the day (1-based)"
    )

    # Relationships
    # Program this entry belongs to
    program = relationship("Program", back_populates="entries")

    # Exercise included in this program entry
    exercise = relationship("Exercise", back_populates="program_entries")

    # Constraints
    __table_args__ = (
        UniqueConstraint(
            "program_id",
            "day_of_week",
            "position",
            name="uq_program_entry_day_position",
        ),
    )

    def __repr__(self):
        return f"<ProgramEntry(id={self.id}, program_id={self.program_id}, day={self.day_of_week}, position={self.position})>"
