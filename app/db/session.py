from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from app.core.config import settings

class DatabaseSessionManager:
    def __init__(self):
        self._engine = None
        self._sessionmaker = None

    def init(self, db_url: str):
        # convert to string and handle URL encoding
        db_url_str = str(db_url)

        # Configure SSL for asyncpg with Neon database
        connect_args = {}
        if "neon.tech" in db_url_str:
            connect_args = {
                "ssl": "require",
                "server_settings": {
                    "jit": "off"
                }
            }

        self._engine = create_async_engine(
            db_url_str,
            poolclass=QueuePool,
            pool_size=20,
            max_overflow=10,
            pool_pre_ping=True,
            echo=settings.DB_ECHO,
            connect_args=connect_args,
        )
        self._sessionmaker = sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False
        )

    async def close(self):
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._sessionmaker = None

    async def get_db(self):
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")
        
        async with self._sessionmaker() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()

    async def get_db_no_ctx(self):
        """For use in scripts and tests where context manager isn't appropriate"""
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")
        return self._sessionmaker()

session_manager = DatabaseSessionManager()

async def get_db():
    async for session in session_manager.get_db():
        yield session
