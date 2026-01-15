#!/usr/bin/env python3
"""Verify the extracted_text optimization is working"""
import asyncio
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

async def main():
    DATABASE_URL = "postgresql+asyncpg://luonghailam:12070123a@localhost:5432/datn"
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Check if column exists
        result = await session.execute(text("""
            SELECT column_name, data_type, character_maximum_length 
            FROM information_schema.columns 
            WHERE table_name = 'cv_analyses' AND column_name = 'extracted_text'
        """))
        col = result.fetchone()
        
        if col:
            print("✅ extracted_text column EXISTS in cv_analyses")
            print(f"   Type: {col[1]}")
        else:
            print("❌ extracted_text column NOT FOUND")
            return
        
        # Check current data
        result = await session.execute(text("""
            SELECT 
                id, 
                cv_id, 
                status,
                CASE 
                    WHEN extracted_text IS NULL THEN 'NULL'
                    ELSE 'HAS DATA (' || LENGTH(extracted_text) || ' chars)'
                END as extracted_text_status
            FROM cv_analyses 
            LIMIT 5
        """))
        
        rows = result.fetchall()
        if rows:
            print(f"\n📊 Sample cv_analyses records ({len(rows)} shown):")
            for row in rows:
                print(f"   CV: {row[1]}, Status: {row[2]}, Text: {row[3]}")
        else:
            print("\n⚠️ No cv_analyses records found")
        
        print("\n" + "="*60)
        print("🎯 NEXT STEPS TO TEST OPTIMIZATION:")
        print("="*60)
        print("1. Upload a NEW CV at /cvs/upload")
        print("   → extracted_text will be saved automatically")
        print("")
        print("2. Create interview at /interviews/new")
        print("   → Should use cached text (check logs for '✅ Using cached')")
        print("")
        print("3. For EXISTING CVs (with NULL extracted_text):")
        print("   → They will extract fresh but slower")
        print("   → Re-upload to get cached version")

if __name__ == "__main__":
    asyncio.run(main())
