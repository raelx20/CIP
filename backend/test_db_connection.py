import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    import nest_asyncio
    nest_asyncio.apply()

from sqlalchemy import text

from app.database.connection import engine


async def test_database_connection() -> None:
    try:
        async with engine.connect() as connection:
            result = await connection.execute(text("SELECT 1"))
            value = result.scalar_one()

            print("DATABASE CONNECTED")
            print(f"SELECT 1 RESULT: {value}")

    except Exception as exc:
        print("DATABASE CONNECTION FAILED")
        print(f"ERROR TYPE: {type(exc).__name__}")
        print(f"ERROR: {exc}")
        raise

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_database_connection())