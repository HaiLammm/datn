#!/usr/bin/env python3
"""
Test script to check conversation and message sending
"""
import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
import uuid

# Add backend to path
sys.path.insert(0, '/home/luonghailam/Projects/datn/backend')

from app.modules.messages.models import Conversation, Message
from app.core.config import settings

async def test_conversation():
    # Create async engine
    engine = create_async_engine(str(settings.DATABASE_URL), echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    conversation_id = uuid.UUID('7c68ae22-5399-42cd-bab3-117958a48aff')
    
    async with async_session() as session:
        # Check if conversation exists
        result = await session.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalars().first()
        
        if not conversation:
            print(f"❌ Conversation {conversation_id} NOT FOUND")
            
            # List all conversations
            all_convs = await session.execute(select(Conversation))
            convs = all_convs.scalars().all()
            print(f"\n📋 Available conversations ({len(convs)}):")
            for conv in convs:
                print(f"  - {conv.id} (Recruiter: {conv.recruiter_id}, Candidate: {conv.candidate_id})")
        else:
            print(f"✅ Conversation {conversation_id} EXISTS")
            print(f"   Recruiter ID: {conversation.recruiter_id}")
            print(f"   Candidate ID: {conversation.candidate_id}")
            print(f"   Created: {conversation.created_at}")
            print(f"   Updated: {conversation.updated_at}")
            
            # Count messages
            msg_result = await session.execute(
                select(Message).where(Message.conversation_id == conversation_id)
            )
            messages = msg_result.scalars().all()
            print(f"   Messages: {len(messages)}")
            
    await engine.dispose()

if __name__ == '__main__':
    asyncio.run(test_conversation())
