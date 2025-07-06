from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
import os
import sys
from dotenv import load_dotenv

# Add your project directory to the path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Load environment variables
load_dotenv()

# Import Base before any models to avoid circular import
from app.db.base import Base

# Import models for Alembic's autogenerate to detect schema
from app.models.db_models import *

# Alembic Config object
config = context.config

# Configure logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for Alembic's autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode using sync engine."""
    # Use sync PostgreSQL driver (psycopg2)
    sync_url = os.getenv("DATABASE_URL").replace("postgresql+asyncpg", "postgresql+psycopg2")

    connectable = create_engine(
        sync_url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True
        )

        with context.begin_transaction():
            context.run_migrations()


# Decide mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

