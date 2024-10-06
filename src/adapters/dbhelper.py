from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import clear_mappers

from adapters.mappings import get_mapper_registry
from configs.settings import PGSettings


def get_engine_async():
    return create_async_engine(
        PGSettings().db_connection_async(),
        isolation_level="REPEATABLE READ",
        # echo=True
    )


def get_engine_sync():
    return create_engine(
        PGSettings().db_connection_sync(),
        isolation_level="REPEATABLE READ",
        # echo=True
    )


def start_db_sync():
    mapper_registry = get_mapper_registry()
    engine = get_engine_sync()
    mapper_registry.metadata.create_all(engine)


async def start_db_async():
    mapper_registry = get_mapper_registry()
    engine = get_engine_async()
    async with engine.begin() as conn:
        await conn.run_sync(mapper_registry.metadata.create_all)


def clear_all_mappers():
    clear_mappers()


async def drop_db_async():
    engine = get_engine_async()
    mapper_registry = get_mapper_registry()
    async with engine.begin() as conn:
        await conn.run_sync(mapper_registry.metadata.drop_all)
    clear_all_mappers()
