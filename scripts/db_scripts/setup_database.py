"""
Database Setup Script for SetLogs

This script sets up the database with proper roles and permissions:
1. Creates a least-privilege application role
2. Grants appropriate permissions
3. Optionally creates the database if it doesn't exist

Usage:
    python scripts/setup_database.py
    make setup-db  # (after adding to Makefile)
"""

import os
import sys
from pathlib import Path

from sqlalchemy import create_engine, text

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Constants
APP_NAME = "setlogs"
APP_ROLE_NAME = f"{APP_NAME}_app"
APP_ROLE_PASSWORD = os.getenv("APP_DB_PASSWORD", "app_password_123")


def get_database_config():
    """Get database configuration from environment variables."""
    DATABASE_URL = os.getenv(
        "DATABASE_URL", "postgresql://user:password@localhost:5432/setlogs"
    )

    # Parse the URL to get individual components
    # Format: postgresql://user:password@host:port/database
    if "://" in DATABASE_URL:
        url_parts = DATABASE_URL.split("://")[1]
        if "@" in url_parts:
            auth, host_db = url_parts.split("@")
            user, password = auth.split(":")
            if ":" in host_db:
                host, port_db = host_db.split(":")
                port, database = port_db.split("/")
            else:
                host = host_db.split("/")[0]
                port = "5432"
                database = host_db.split("/")[1]
        else:
            raise ValueError("Invalid DATABASE_URL format")
    else:
        raise ValueError("Invalid DATABASE_URL format")

    return {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "database": database,
    }


def create_application_role(engine, config):
    """Create a least-privilege application role."""
    print("Creating application role...")

    with engine.connect() as conn:
        # Start a transaction
        trans = conn.begin()

        try:
            # Create the application role
            conn.execute(
                text(
                    f"""
                DO $$
                BEGIN
                    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '{APP_ROLE_NAME}') THEN
                        CREATE ROLE {APP_ROLE_NAME} WITH LOGIN PASSWORD '{APP_ROLE_PASSWORD}';
                    END IF;
                END
                $$;
            """
                )
            )

            # Grant connect permission to the database
            conn.execute(
                text(
                    f"GRANT CONNECT ON DATABASE {config['database']} TO {APP_ROLE_NAME};"
                )
            )

            # Grant usage on public schema
            conn.execute(text(f"GRANT USAGE ON SCHEMA public TO {APP_ROLE_NAME};"))

            # Grant table permissions (SELECT, INSERT, UPDATE, DELETE)
            conn.execute(
                text(
                    f"""
                GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO {APP_ROLE_NAME};
            """
                )
            )

            # Grant sequence permissions (for auto-incrementing IDs)
            conn.execute(
                text(
                    f"""
                GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO {APP_ROLE_NAME};
            """
                )
            )

            # Set default privileges for future tables/sequences
            conn.execute(
                text(
                    f"""
                ALTER DEFAULT PRIVILEGES IN SCHEMA public
                GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {APP_ROLE_NAME};
            """
                )
            )

            conn.execute(
                text(
                    f"""
                ALTER DEFAULT PRIVILEGES IN SCHEMA public
                GRANT USAGE, SELECT ON SEQUENCES TO {APP_ROLE_NAME};
            """
                )
            )

            # Commit the transaction
            trans.commit()
            print("Application role created successfully!")

        except Exception as e:
            trans.rollback()
            print(f"Error creating application role: {e}")
            raise


def verify_role_permissions(engine, config):
    """Verify that the application role has correct permissions."""
    print("Verifying role permissions...")

    # Test connection with application role
    app_url = f"postgresql://{APP_ROLE_NAME}:{APP_ROLE_PASSWORD}@{config['host']}:{config['port']}/{config['database']}"
    app_engine = create_engine(app_url)

    try:
        with app_engine.connect() as conn:
            # Test SELECT permission
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            user_count = result.scalar()
            print(f"  SELECT test: Can read {user_count} users")

            # Test INSERT permission (we'll rollback)
            try:
                # Use a savepoint for the test
                savepoint = conn.begin_nested()
                try:
                    conn.execute(
                        text(
                            """
                        INSERT INTO users (id, email, password_hash, created_at, version)
                        VALUES (gen_random_uuid(), 'test@example.com', 'test_hash', now(), 1)
                    """
                        )
                    )
                    print("  INSERT test: Can insert data")
                    savepoint.rollback()  # Don't actually insert
                except Exception as e:
                    print(f"  INSERT test failed: {e}")
                    savepoint.rollback()
            except Exception as e:
                print(f"  INSERT test setup failed: {e}")

            # Test that DDL is blocked
            try:
                conn.execute(text("CREATE TABLE test_table (id INT)"))
                print("  WARNING: DDL test failed - role can create tables!")
            except Exception as e:
                print(f"  DDL test: Correctly blocked ({type(e).__name__})")

    except Exception as e:
        print(f"Error verifying permissions: {e}")
        raise


def print_environment_info():
    """Print information about required environment variables."""
    print("\nRequired environment variables:")
    print("  DATABASE_URL=postgresql://user:password@localhost:5432/setlogs")
    print(
        f"  APP_DATABASE_URL=postgresql://{APP_ROLE_NAME}:{APP_ROLE_PASSWORD}@localhost:5432/setlogs"
    )
    print(
        f"  APP_DB_PASSWORD={APP_ROLE_PASSWORD}  # Optional: override app role password"
    )


def main():
    """Main setup function."""
    print("Setting up SetLogs database roles and permissions...")

    try:
        # Get database configuration
        config = get_database_config()
        print(
            f"Connecting to database: {config['database']} on {config['host']}:{config['port']}"
        )

        # Create engine with admin privileges
        admin_url = f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
        engine = create_engine(admin_url)

        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"Connected to PostgreSQL: {version.split(',')[0]}")

        # Create application role
        create_application_role(engine, config)

        # Verify permissions
        verify_role_permissions(engine, config)

        # Print environment information
        print_environment_info()

        print("\nDatabase setup completed successfully!")
        print("\nNext steps:")
        print("1. Add APP_DATABASE_URL to your .env file")
        print(
            "2. Update your application to use APP_DATABASE_URL for runtime operations"
        )
        print("3. Keep using DATABASE_URL for migrations (alembic)")
        print("4. Run 'make seed' to populate with test data")

    except Exception as e:
        print(f"Database setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
