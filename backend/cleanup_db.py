import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def cleanup():
    engine = create_async_engine('postgresql+asyncpg://postgres:anshu%402006@127.0.0.1:5432/cip')
    async with engine.connect() as conn:
        await conn.execute(text('DROP TABLE IF EXISTS constituencies CASCADE'))
        await conn.execute(text('DELETE FROM alembic_version'))
        await conn.commit()
        print('Cleaned up')
    await engine.dispose()

asyncio.run(cleanup())
