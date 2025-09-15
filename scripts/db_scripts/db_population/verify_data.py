"""
Quick verification script for seeded data
"""

import os
import sys
from pathlib import Path

from sqlalchemy import create_engine, text

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def main():
    DATABASE_URL = os.getenv(
        "DATABASE_URL", "postgresql://user:password@localhost:5432/setlogs"
    )
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        print("SetLogs Database Verification")
        print("=" * 50)

        # Row counts
        tables = [
            "users",
            "exercises",
            "programs",
            "program_entries",
            "user_programs",
            "sessions",
            "sets",
        ]
        print("\nRow Counts:")
        for table in tables:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            print(f"  {table:15}: {count:,}")

        # Sample data
        print("\nSample Users:")
        result = conn.execute(text("SELECT email FROM users ORDER BY RANDOM() LIMIT 3"))
        for row in result:
            print(f"  - {row[0]}")

        print("\nSample Exercises:")
        result = conn.execute(
            text("SELECT name FROM exercises ORDER BY RANDOM() LIMIT 5")
        )
        for row in result:
            print(f"  - {row[0]}")

        # Workout stats
        print("\nWorkout Statistics:")
        result = conn.execute(
            text(
                """
            SELECT 
                COUNT(DISTINCT s.user_id) as active_users,
                COUNT(s.id) as total_sessions,
                COUNT(st.id) as total_sets
            FROM sessions s
            LEFT JOIN sets st ON s.id = st.session_id
        """
            )
        )
        stats = result.fetchone()
        print(f"  Active users: {stats[0]}")
        print(f"  Total sessions: {stats[1]:,}")
        print(f"  Total sets: {stats[2]:,}")

        # Date range (since dates are stored as text)
        result = conn.execute(
            text("SELECT MIN(started_at), MAX(started_at) FROM sessions")
        )
        date_range = result.fetchone()
        print(f"  Date range: {date_range[0]} to {date_range[1]}")

        # Sample workout
        print("\nSample Workout Session:")
        result = conn.execute(
            text(
                """
            SELECT 
                u.email,
                e.name,
                st.reps,
                st.weight_kg,
                st.rpe
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            JOIN sets st ON s.id = st.session_id
            JOIN exercises e ON st.exercise_id = e.id
            WHERE s.id = (SELECT id FROM sessions ORDER BY RANDOM() LIMIT 1)
            ORDER BY st.set_index
            LIMIT 5
        """
            )
        )
        for row in result:
            rpe_str = f" (RPE: {row[4]})" if row[4] else ""
            print(f"  {row[1]}: {row[2]} reps @ {row[3]}kg{rpe_str}")

        print("\nVerification complete!")


if __name__ == "__main__":
    main()
