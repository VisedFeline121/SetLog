"""
Session models for workout tracking.

This module defines the Session, Set, and UserProgram models which represent
workout sessions, individual sets performed, and user program assignments.
"""

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, generate_uuid


class UserProgram(Base):
    """
    User program assignment model.

    Represents a user's assignment to a program, including the start date
    and whether the assignment is currently active. This allows users to
    follow structured workout programs.

    Attributes:
        id: Primary key (UUID)
        user_id: Foreign key to User
        program_id: Foreign key to Program
        start_date: Date when the user started this program
        active: Whether this assignment is currently active
        created_at: Timestamp when assignment was created (inherited from Base)
    """

    __tablename__ = "user_programs"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=generate_uuid,
        comment="Unique identifier for the user program assignment",
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="User assigned to this program",
    )

    program_id = Column(
        UUID(as_uuid=True),
        ForeignKey("programs.id", ondelete="CASCADE"),
        nullable=False,
        comment="Program being assigned",
    )

    start_date = Column(
        String(10),  # YYYY-MM-DD format
        nullable=False,
        comment="Date when the user started this program (YYYY-MM-DD)",
    )

    active = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether this assignment is currently active",
    )

    # Relationships
    # User assigned to this program
    user = relationship("User", back_populates="user_programs")

    # Program being assigned
    program = relationship("Program", back_populates="user_programs")

    # Sessions performed as part of this program assignment
    sessions = relationship("Session", back_populates="user_program")

    def __repr__(self):
        return f"<UserProgram(id={self.id}, user_id={self.user_id}, program_id={self.program_id}, active={self.active})>"


class Session(Base):
    """
    Workout session model.

    Represents a workout session performed by a user. Sessions can be
    standalone or part of a program assignment. They track the date/time
    and program context when applicable.

    Attributes:
        id: Primary key (UUID)
        user_id: Foreign key to User
        user_program_id: Optional foreign key to UserProgram
        prog_week_index: Week index within the program (if part of program)
        prog_day_of_week: Day of week within the program (if part of program)
        started_at: Timestamp when session started
        ended_at: Optional timestamp when session ended
        created_at: Timestamp when session was created (inherited from Base)
    """

    __tablename__ = "sessions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=generate_uuid,
        comment="Unique identifier for the session",
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="User who performed this session",
    )

    user_program_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user_programs.id", ondelete="SET NULL"),
        nullable=True,
        comment="Program assignment this session belongs to (if any)",
    )

    prog_week_index = Column(
        Integer,
        nullable=True,
        comment="Week index within the program (if part of program)",
    )

    prog_day_of_week = Column(
        Integer,
        nullable=True,
        comment="Day of week within the program (if part of program)",
    )

    started_at = Column(
        String(19),  # YYYY-MM-DD HH:MM:SS format
        nullable=False,
        comment="Timestamp when session started (YYYY-MM-DD HH:MM:SS)",
    )

    ended_at = Column(
        String(19),  # YYYY-MM-DD HH:MM:SS format
        nullable=True,
        comment="Timestamp when session ended (YYYY-MM-DD HH:MM:SS)",
    )

    # Relationships
    # User who performed this session
    user = relationship("User", back_populates="sessions")

    # Program assignment this session belongs to
    user_program = relationship("UserProgram", back_populates="sessions")

    # Sets performed in this session
    sets = relationship("Set", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Session(id={self.id}, user_id={self.user_id}, started_at='{self.started_at}')>"


class Set(Base):
    """
    Individual set model.

    Represents a single set performed during a workout session. This is the
    atomic unit of workout logging, containing the exercise, reps, weight,
    and RPE (Rate of Perceived Exertion).

    Attributes:
        id: Primary key (UUID)
        session_id: Foreign key to Session
        exercise_id: Foreign key to Exercise
        set_index: Order within the session/exercise (1-based)
        reps: Number of repetitions performed
        weight_kg: Weight used in kilograms
        rpe: Rate of Perceived Exertion (1-10 scale, optional)
        created_at: Timestamp when set was logged (inherited from Base)
    """

    __tablename__ = "sets"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=generate_uuid,
        comment="Unique identifier for the set",
    )

    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        comment="Session this set belongs to",
    )

    exercise_id = Column(
        UUID(as_uuid=True),
        ForeignKey("exercises.id", ondelete="RESTRICT"),
        nullable=False,
        comment="Exercise performed in this set",
    )

    set_index = Column(
        Integer, nullable=False, comment="Order within the session/exercise (1-based)"
    )

    reps = Column(Integer, nullable=False, comment="Number of repetitions performed")

    weight_kg = Column(
        String(10),  # Store as string to handle decimal precision
        nullable=False,
        comment="Weight used in kilograms",
    )

    rpe = Column(
        String(4),  # Store as string to handle decimal precision (e.g., "8.5")
        nullable=True,
        comment="Rate of Perceived Exertion (1-10 scale, optional)",
    )

    # Relationships
    # Session this set belongs to
    session = relationship("Session", back_populates="sets")

    # Exercise performed in this set
    exercise = relationship("Exercise", back_populates="sets")

    # Constraints
    __table_args__ = (
        UniqueConstraint(
            "session_id",
            "exercise_id",
            "set_index",
            name="uq_set_session_exercise_index",
        ),
        CheckConstraint("reps > 0", name="ck_set_reps_positive"),
        CheckConstraint("weight_kg::numeric >= 0", name="ck_set_weight_non_negative"),
        CheckConstraint(
            "rpe IS NULL OR (rpe::numeric BETWEEN 1 AND 10)", name="ck_set_rpe_range"
        ),
    )

    def __repr__(self):
        return f"<Set(id={self.id}, session_id={self.session_id}, exercise_id={self.exercise_id}, reps={self.reps}, weight={self.weight_kg}kg)>"
