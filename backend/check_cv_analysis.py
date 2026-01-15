#!/usr/bin/env python3
"""Check what data is stored in CV analysis"""
import asyncio
import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.modules.ai.models import CVAnalysis

async def main():
    # Create engine
    DATABASE_URL = "postgresql+asyncpg://luonghailam:12070123a@localhost:5432/datn"
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        result = await session.execute(select(CVAnalysis).limit(1))
        analysis = result.scalar_one_or_none()
        
        if not analysis:
            print("❌ Không có CV analysis nào trong DB")
            return
        
        print("✅ CV Analysis Data Available:")
        print(f"   CV ID: {analysis.cv_id}")
        print(f"   Status: {analysis.status}")
        print(f"   AI Score: {analysis.ai_score}")
        print(f"\n📝 AI Summary (first 200 chars):")
        if analysis.ai_summary:
            print(f"   {analysis.ai_summary[:200]}...")
            print(f"   Total length: {len(analysis.ai_summary)} chars")
        else:
            print("   None")
        
        print(f"\n🔧 Extracted Skills:")
        if analysis.extracted_skills:
            print(f"   Count: {len(analysis.extracted_skills)}")
            print(f"   Skills: {analysis.extracted_skills[:10]}")
        else:
            print("   None")
        
        print(f"\n💡 AI Feedback:")
        if analysis.ai_feedback:
            print(f"   {json.dumps(analysis.ai_feedback, indent=2)[:300]}...")
        else:
            print("   None")
        
        print("\n" + "="*60)
        print("🤔 Question: Có thể dùng ai_summary thay cho raw CV text?")
        print("="*60)
        print("\nAnswer: KHÔNGnên dùng ai_summary vì:")
        print("  1. ai_summary là TÓM TẮT ngắn, không có đủ chi tiết")
        print("  2. Interview questions cần FULL CONTEXT từ CV")
        print("  3. Ollama LLM cần raw text để generate câu hỏi chi tiết")
        print("\n✅ Nhưng có thể OPTIMIZE bằng cách:")
        print("  - Store extracted_text field khi upload CV")
        print("  - Reuse text đã extract thay vì extract lại")

if __name__ == "__main__":
    asyncio.run(main())
