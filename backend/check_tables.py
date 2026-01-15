import asyncio
from app.core.database import engine
from sqlalchemy import text

async def check():
    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename")
        )
        print('📊 All tables in database:')
        tables = [row[0] for row in result]
        for table in tables:
            print(f'  - {table}')
        
        print(f'\n📈 Total: {len(tables)} tables')
        
        # Check specifically for cv_analyses
        if 'cv_analyses' in tables:
            print('\n✅ cv_analyses table EXISTS')
        else:
            print('\n❌ cv_analyses table MISSING!')

asyncio.run(check())
