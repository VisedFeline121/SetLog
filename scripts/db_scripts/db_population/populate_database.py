"""
SetLogs Database Seeding Script

This script populates the database with realistic test data including:
- 5 users with hashed passwords
- 50+ exercises with proper categorization
- 5 workout programs with structured entries
- 6-12 months of workout sessions and sets (10k-50k sets)

Usage:
    python scripts/seed_database.py
    make seed  # (after adding to Makefile)
"""

import json
import os
import random
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import after path setup (needs to be after sys.path modification)
from models import (  # noqa: E402
    Exercise,
    Program,
    ProgramEntry,
    Session,
    Set,
    User,
    UserProgram,
)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database connection
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://user:password@localhost:5432/setlogs"
)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def load_json_data(filename):
    """Load JSON data from the data directory."""
    data_path = Path(__file__).parent / "data" / filename
    with open(data_path, "r") as f:
        return json.load(f)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def create_users(session):
    """Create users from JSON data."""
    print("Creating users...")
    users_data = load_json_data("users.json")

    users = []
    for user_data in users_data:
        user = User(
            id=uuid.uuid4(),  # Explicitly generate UUID
            email=user_data["email"],
            password_hash=hash_password(user_data["password"]),
        )
        session.add(user)
        users.append(user)

    session.commit()
    print(f"Created {len(users)} users")
    return users


def create_exercises(session, users):
    """Create exercises from JSON data."""
    print("Creating exercises...")
    exercises_data = load_json_data("exercises.json")

    exercises = []
    for exercise_data in exercises_data:
        # Assign random creator from users
        created_by = random.choice(users)

        exercise = Exercise(
            id=uuid.uuid4(),  # Explicitly generate UUID
            slug=exercise_data["slug"],
            name=exercise_data["name"],
            description=exercise_data["description"],
            target_muscles=exercise_data["target_muscles"],
            created_by=created_by.id,
        )
        session.add(exercise)
        exercises.append(exercise)

    session.commit()
    print(f"Created {len(exercises)} exercises")
    return exercises


def create_programs(session, users, exercises):
    """Create programs and program entries from JSON data."""
    print("Creating programs...")
    programs_data = load_json_data("programs.json")

    # Create exercise lookup by slug
    exercise_lookup = {ex.slug: ex for ex in exercises}

    programs = []
    for program_data in programs_data:
        # Assign random owner from users
        owner = random.choice(users)

        program = Program(
            id=uuid.uuid4(),  # Explicitly generate UUID
            name=program_data["name"],
            description=program_data["description"],
            owner_id=owner.id,
        )
        session.add(program)
        session.flush()  # Get the program ID

        # Create program entries
        for entry_data in program_data["entries"]:
            exercise = exercise_lookup[entry_data["exercise_slug"]]
            program_entry = ProgramEntry(
                id=uuid.uuid4(),  # Explicitly generate UUID
                program_id=program.id,
                exercise_id=exercise.id,
                day_of_week=entry_data["day_of_week"],
                position=entry_data["position"],
            )
            session.add(program_entry)

        programs.append(program)

    session.commit()
    print(f"Created {len(programs)} programs")
    return programs


def create_user_programs(session, users, programs):
    """Create user program assignments."""
    print("Creating user program assignments...")

    user_programs = []
    for user in users:
        # Each user gets 1-3 random program assignments
        num_assignments = random.randint(1, 3)
        assigned_programs = random.sample(programs, min(num_assignments, len(programs)))

        for program in assigned_programs:
            start_date = (
                datetime.now() - timedelta(days=random.randint(30, 365))
            ).strftime("%Y-%m-%d")
            user_program = UserProgram(
                id=uuid.uuid4(),  # Explicitly generate UUID
                user_id=user.id,
                program_id=program.id,
                start_date=start_date,
                active=random.choice([True, False]),
            )
            session.add(user_program)
            user_programs.append(user_program)

    session.commit()
    print(f"Created {len(user_programs)} user program assignments")
    return user_programs


def generate_realistic_workout_data(session, users, exercises, programs, user_programs):
    """Generate 6-12 months of realistic workout sessions and sets."""
    print("Generating workout sessions and sets...")

    sessions_created = 0
    sets_created = 0

    # Generate sessions for the last 6-12 months
    start_date = datetime.now() - timedelta(days=365)
    end_date = datetime.now()

    for user in users:
        # Each user works out 2-5 times per week
        workout_frequency = random.uniform(2.5, 4.5)
        total_days = (end_date - start_date).days
        num_workouts = int(total_days * workout_frequency / 7)

        # Get user's active programs
        user_active_programs = [
            up for up in user_programs if up.user_id == user.id and up.active
        ]

        for _ in range(num_workouts):
            # Random workout date
            workout_date = start_date + timedelta(days=random.randint(0, total_days))
            workout_date = workout_date.replace(
                hour=random.randint(6, 20), minute=random.randint(0, 59)
            )

            # Determine if this is a program workout or free-form
            use_program = random.choice([True, False]) and user_active_programs

            if use_program and user_active_programs:
                # Program-based workout
                user_program = random.choice(user_active_programs)
                program = next(p for p in programs if p.id == user_program.program_id)

                # Calculate program week and day
                program_start = datetime.strptime(user_program.start_date, "%Y-%m-%d")
                weeks_since_start = (workout_date - program_start).days // 7
                day_of_week = workout_date.weekday()

                # Get exercises for this day
                day_exercises = [
                    pe for pe in program.entries if pe.day_of_week == day_of_week
                ]

                if not day_exercises:
                    continue  # Skip if no exercises for this day

                session_obj = Session(
                    id=uuid.uuid4(),  # Explicitly generate UUID
                    user_id=user.id,
                    user_program_id=user_program.id,
                    prog_week_index=weeks_since_start,
                    prog_day_of_week=day_of_week,
                    started_at=workout_date.strftime("%Y-%m-%d %H:%M:%S"),
                    ended_at=(
                        workout_date + timedelta(hours=random.uniform(0.5, 2.0))
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                )
            else:
                # Free-form workout
                session_obj = Session(
                    id=uuid.uuid4(),  # Explicitly generate UUID
                    user_id=user.id,
                    started_at=workout_date.strftime("%Y-%m-%d %H:%M:%S"),
                    ended_at=(
                        workout_date + timedelta(hours=random.uniform(0.5, 2.0))
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                )

            session.add(session_obj)
            session.flush()  # Get session ID

            # Generate sets for this session
            if use_program and user_active_programs and day_exercises:
                # Program-based sets
                for program_entry in day_exercises:
                    exercise = next(
                        ex for ex in exercises if ex.id == program_entry.exercise_id
                    )
                    num_sets = random.randint(3, 6)

                    for set_num in range(1, num_sets + 1):
                        weight = generate_realistic_weight(exercise.slug, user.id)
                        reps = generate_realistic_reps(exercise.slug, set_num, num_sets)
                        rpe = random.choice(
                            [
                                None,
                                f"{random.randint(6, 10)}.0",
                                f"{random.randint(6, 9)}.5",
                            ]
                        )

                        set_obj = Set(
                            id=uuid.uuid4(),  # Explicitly generate UUID
                            session_id=session_obj.id,
                            exercise_id=exercise.id,
                            set_index=set_num,
                            reps=reps,
                            weight_kg=str(weight),
                            rpe=rpe,
                        )
                        session.add(set_obj)
                        sets_created += 1
            else:
                # Free-form sets - random exercises
                num_exercises = random.randint(3, 8)
                selected_exercises = random.sample(
                    exercises, min(num_exercises, len(exercises))
                )

                for exercise in selected_exercises:
                    num_sets = random.randint(2, 5)

                    for set_num in range(1, num_sets + 1):
                        weight = generate_realistic_weight(exercise.slug, user.id)
                        reps = generate_realistic_reps(exercise.slug, set_num, num_sets)
                        rpe = random.choice(
                            [
                                None,
                                f"{random.randint(6, 10)}.0",
                                f"{random.randint(6, 9)}.5",
                            ]
                        )

                        set_obj = Set(
                            id=uuid.uuid4(),  # Explicitly generate UUID
                            session_id=session_obj.id,
                            exercise_id=exercise.id,
                            set_index=set_num,
                            reps=reps,
                            weight_kg=str(weight),
                            rpe=rpe,
                        )
                        session.add(set_obj)
                        sets_created += 1

            sessions_created += 1

            # Commit in batches to avoid memory issues
            if sessions_created % 100 == 0:
                session.commit()
                print(f"Created {sessions_created} sessions, {sets_created} sets...")

    session.commit()
    print(f"Generated {sessions_created} sessions and {sets_created} sets")


def generate_realistic_weight(exercise_slug, user_id):
    """Generate realistic weight based on exercise type and user."""
    # Base weights for different exercise categories (in kg)
    base_weights = {
        # Compound movements
        "squat": 80,
        "deadlift": 100,
        "barbell-bench-press": 70,
        "overhead-press": 40,
        "barbell-row": 60,
        "front-squat": 60,
        "romanian-deadlift": 80,
        # Accessory movements
        "incline-bench-press": 50,
        "dumbbell-bench-press": 25,
        "dumbbell-row": 20,
        "lateral-raises": 8,
        "bicep-curls": 12,
        "tricep-dips": 0,  # Bodyweight
        "pull-ups": 0,
        "dips": 0,
        "push-ups": 0,  # Bodyweight
        # Isolation movements
        "leg-press": 100,
        "leg-curls": 20,
        "leg-extensions": 15,
        "calf-raises": 30,
        "shoulder-press": 25,
        "hammer-curls": 10,
        "tricep-pushdowns": 15,
        "skull-crushers": 12,
        # Bodyweight movements
        "plank": 0,
        "mountain-climbers": 0,
        "burpees": 0,
        "box-jumps": 0,
        "jumping-jacks": 0,
        "high-knees": 0,
        "jumping-squats": 0,
    }

    base_weight = base_weights.get(exercise_slug, 20)  # Default 20kg

    if base_weight == 0:  # Bodyweight exercise
        return 0

    # Add some variation based on user (simulate different strength levels)
    # Convert UUID to int for modulo operation
    user_hash = hash(str(user_id)) % 3  # 0, 1, or 2
    user_variation = user_hash * 0.2  # 0%, 20%, or 40% variation
    weight_multiplier = 0.6 + user_variation  # 60% to 100% of base

    # Add some random variation
    random_variation = random.uniform(0.8, 1.2)

    final_weight = base_weight * weight_multiplier * random_variation
    return round(final_weight, 1)


def generate_realistic_reps(exercise_slug, set_num, total_sets):
    """Generate realistic rep counts based on exercise and set position."""
    # Base rep ranges for different exercise types
    if exercise_slug in [
        "squat",
        "deadlift",
        "barbell-bench-press",
        "overhead-press",
        "barbell-row",
    ]:
        # Compound movements - lower reps
        base_reps = random.randint(3, 8)
    elif exercise_slug in [
        "bicep-curls",
        "tricep-dips",
        "lateral-raises",
        "calf-raises",
    ]:
        # Isolation movements - higher reps
        base_reps = random.randint(8, 15)
    elif exercise_slug in ["plank", "mountain-climbers", "burpees"]:
        # Cardio/endurance - time-based (convert to reps)
        base_reps = random.randint(10, 30)
    else:
        # Default range
        base_reps = random.randint(5, 12)

    # Later sets typically have fewer reps (fatigue)
    if set_num > total_sets // 2:
        base_reps = max(1, base_reps - random.randint(1, 3))

    return max(1, base_reps)


def main():
    """Main seeding function."""
    print("Starting SetLogs database seeding...")

    # Create database session
    db_session = SessionLocal()

    try:
        # Create all data
        users = create_users(db_session)
        exercises = create_exercises(db_session, users)
        programs = create_programs(db_session, users, exercises)
        user_programs = create_user_programs(db_session, users, programs)
        generate_realistic_workout_data(
            db_session, users, exercises, programs, user_programs
        )

        print("Database seeding completed successfully!")
        print("Summary:")
        print(f"   - Users: {len(users)}")
        print(f"   - Exercises: {len(exercises)}")
        print(f"   - Programs: {len(programs)}")
        print(f"   - User Programs: {len(user_programs)}")

        # Get final counts
        session_count = db_session.query(Session).count()
        set_count = db_session.query(Set).count()
        print(f"   - Sessions: {session_count}")
        print(f"   - Sets: {set_count}")

    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        db_session.rollback()
        raise
    finally:
        db_session.close()


if __name__ == "__main__":
    main()
