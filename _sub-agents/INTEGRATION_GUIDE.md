# Integration Guide - Tích hợp AI Agents vào FastAPI Backend

Hướng dẫn này mô tả chi tiết cách tích hợp 3 AI sub-agents vào backend FastAPI hiện tại của hệ thống AI Recruitment Platform.

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Database Schema](#database-schema)
3. [FastAPI Integration](#fastapi-integration)
4. [Service Layer](#service-layer)
5. [API Endpoints](#api-endpoints)
6. [Error Handling](#error-handling)
7. [Performance Optimization](#performance-optimization)
8. [Testing Integration](#testing-integration)

---

## Architecture Overview

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                       Frontend (React)                        │
└───────────────────────────┬──────────────────────────────────┘
                            │ HTTPS
┌───────────────────────────▼──────────────────────────────────┐
│                    FastAPI Backend                            │
│  ┌────────────────────────────────────────────────────────┐  │
│  │               API Layer (Routers)                      │  │
│  └───────────┬────────────────────────────────────────────┘  │
│              │                                                │
│  ┌───────────▼────────────────────────────────────────────┐  │
│  │           Service Layer (Business Logic)               │  │
│  │  ┌──────────────┐  ┌────────────────┐  ┌───────────┐ │  │
│  │  │ Question     │  │ Conversation   │  │ Evaluation│ │  │
│  │  │ Service      │  │ Service        │  │ Service   │ │  │
│  │  └──────┬───────┘  └────────┬───────┘  └─────┬─────┘ │  │
│  └─────────┼──────────────────┼─────────────────┼────────┘  │
│            │                  │                 │            │
│  ┌─────────▼──────────────────▼─────────────────▼─────────┐ │
│  │         AI Agents Layer (Ollama Integration)           │ │
│  │  ┌───────────┐  ┌────────────┐  ┌──────────────────┐  │ │
│  │  │Question   │  │Conversation│  │Performance       │  │ │
│  │  │Generator  │  │Agent       │  │Evaluator         │  │ │
│  │  └─────┬─────┘  └──────┬─────┘  └────────┬─────────┘  │ │
│  └────────┼────────────────┼──────────────────┼────────────┘ │
│           │                │                  │               │
│  ┌────────▼────────────────▼──────────────────▼────────────┐ │
│  │         Database Layer (SQLAlchemy + PostgreSQL)        │ │
│  └─────────────────────────────────────────────────────────┘ │
└───────────────────────────┬──────────────────────────────────┘
                            │
                  ┌─────────▼─────────┐
                  │   Ollama Server   │
                  │   (localhost)     │
                  └───────────────────┘
```

### Design Principles

1. **Separation of Concerns**: API → Service → Agent → Database
2. **Async Operations**: Sử dụng async/await cho all I/O operations
3. **Database as Context Store**: Interview context lưu trong DB, không lưu trong agent memory
4. **Stateless Agents**: Mỗi agent call là independent, nhận context từ DB
5. **Error Recovery**: Retry logic + fallback strategies

---

## Database Schema

### New Tables for Epic 8

```sql
-- Interview Sessions
CREATE TABLE interview_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_posting_id UUID REFERENCES job_postings(id),
    candidate_id UUID REFERENCES candidates(id),
    status VARCHAR(20) NOT NULL, -- 'pending', 'in_progress', 'completed', 'cancelled'
    scheduled_at TIMESTAMP WITH TIME ZONE,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_minutes INT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Generated Interview Questions
CREATE TABLE interview_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    interview_session_id UUID REFERENCES interview_sessions(id) ON DELETE CASCADE,
    question_id VARCHAR(50) NOT NULL, -- từ AI agent (Q1, Q2, ...)
    category VARCHAR(20) NOT NULL, -- 'technical', 'behavioral', 'situational'
    difficulty VARCHAR(20) NOT NULL, -- 'junior', 'middle', 'senior'
    question_text TEXT NOT NULL,
    key_points JSONB, -- array of strings
    ideal_answer_outline TEXT,
    evaluation_criteria JSONB, -- array of strings
    order_index INT NOT NULL,
    is_selected BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Interview Conversation Turns
CREATE TABLE interview_turns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    interview_session_id UUID REFERENCES interview_sessions(id) ON DELETE CASCADE,
    question_id UUID REFERENCES interview_questions(id),
    turn_number INT NOT NULL,
    ai_message TEXT NOT NULL,
    candidate_message TEXT NOT NULL,
    answer_quality JSONB, -- {technical_accuracy, communication_clarity, depth_of_knowledge, overall_score}
    key_observations JSONB, -- array of strings
    strengths JSONB, -- array of strings
    gaps JSONB, -- array of strings
    action_type VARCHAR(20), -- 'continue', 'follow_up', 'next_question', 'end_interview'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Interview Evaluations (Final Report)
CREATE TABLE interview_evaluations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    interview_session_id UUID REFERENCES interview_sessions(id) ON DELETE CASCADE,
    final_score DECIMAL(3,1) NOT NULL,
    grade VARCHAR(20) NOT NULL, -- 'excellent', 'good', 'average', 'poor'
    hiring_recommendation VARCHAR(20) NOT NULL, -- 'strong_hire', 'hire', 'consider', 'no_hire'
    dimension_scores JSONB NOT NULL, -- full dimension scores structure
    detailed_analysis JSONB NOT NULL, -- strengths, weaknesses, notable moments, red flags
    recommendations JSONB NOT NULL, -- hiring decision, reasoning, suggestions
    metadata JSONB, -- total questions, duration, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agent Call Logs (for monitoring and debugging)
CREATE TABLE agent_call_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_type VARCHAR(50) NOT NULL, -- 'question_generator', 'conversation', 'evaluator'
    interview_session_id UUID REFERENCES interview_sessions(id),
    input_data JSONB,
    output_data JSONB,
    status VARCHAR(20) NOT NULL, -- 'success', 'error'
    error_message TEXT,
    latency_ms INT,
    model_used VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Indexes

```sql
CREATE INDEX idx_interview_sessions_candidate ON interview_sessions(candidate_id);
CREATE INDEX idx_interview_sessions_job_posting ON interview_sessions(job_posting_id);
CREATE INDEX idx_interview_sessions_status ON interview_sessions(status);
CREATE INDEX idx_interview_questions_session ON interview_questions(interview_session_id);
CREATE INDEX idx_interview_turns_session ON interview_turns(interview_session_id);
CREATE INDEX idx_interview_turns_turn_number ON interview_turns(interview_session_id, turn_number);
CREATE INDEX idx_agent_call_logs_session ON agent_call_logs(interview_session_id);
CREATE INDEX idx_agent_call_logs_created_at ON agent_call_logs(created_at);
```

---

## FastAPI Integration

### 1. Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │           └── interviews.py        # NEW
│   ├── services/
│   │   ├── question_service.py          # NEW
│   │   ├── conversation_service.py      # NEW
│   │   └── evaluation_service.py        # NEW
│   ├── models/
│   │   └── interview.py                 # NEW SQLAlchemy models
│   ├── schemas/
│   │   └── interview.py                 # NEW Pydantic schemas
│   ├── core/
│   │   └── config.py                    # UPDATE: add agent configs
│   └── main.py
├── _sub-agents/                          # Agent implementation
│   ├── agents/
│   ├── configs/
│   └── prompts/
└── requirements.txt
```

### 2. Configuration (app/core/config.py)

```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # ... existing settings ...
    
    # Ollama Settings
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_TIMEOUT: int = 30
    
    # Agent Settings
    QUESTION_AGENT_CONFIG: str = "_sub-agents/configs/question_generator_config.json"
    CONVERSATION_AGENT_CONFIG: str = "_sub-agents/configs/conversation_agent_config.json"
    EVALUATOR_AGENT_CONFIG: str = "_sub-agents/configs/performance_evaluator_config.json"
    
    # Performance Settings
    AGENT_MAX_RETRIES: int = 2
    AGENT_ENABLE_LOGGING: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 3. SQLAlchemy Models (app/models/interview.py)

```python
from sqlalchemy import Column, String, Integer, Boolean, Text, TIMESTAMP, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import uuid
from datetime import datetime

class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_posting_id = Column(UUID(as_uuid=True), ForeignKey("job_postings.id"))
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"))
    status = Column(String(20), nullable=False, default="pending")
    scheduled_at = Column(TIMESTAMP(timezone=True))
    started_at = Column(TIMESTAMP(timezone=True))
    completed_at = Column(TIMESTAMP(timezone=True))
    duration_minutes = Column(Integer)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    questions = relationship("InterviewQuestion", back_populates="session", cascade="all, delete-orphan")
    turns = relationship("InterviewTurn", back_populates="session", cascade="all, delete-orphan")
    evaluation = relationship("InterviewEvaluation", back_populates="session", uselist=False)

class InterviewQuestion(Base):
    __tablename__ = "interview_questions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    interview_session_id = Column(UUID(as_uuid=True), ForeignKey("interview_sessions.id", ondelete="CASCADE"))
    question_id = Column(String(50), nullable=False)
    category = Column(String(20), nullable=False)
    difficulty = Column(String(20), nullable=False)
    question_text = Column(Text, nullable=False)
    key_points = Column(JSONB)
    ideal_answer_outline = Column(Text)
    evaluation_criteria = Column(JSONB)
    order_index = Column(Integer, nullable=False)
    is_selected = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    
    # Relationships
    session = relationship("InterviewSession", back_populates="questions")
    turns = relationship("InterviewTurn", back_populates="question")

class InterviewTurn(Base):
    __tablename__ = "interview_turns"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    interview_session_id = Column(UUID(as_uuid=True), ForeignKey("interview_sessions.id", ondelete="CASCADE"))
    question_id = Column(UUID(as_uuid=True), ForeignKey("interview_questions.id"))
    turn_number = Column(Integer, nullable=False)
    ai_message = Column(Text, nullable=False)
    candidate_message = Column(Text, nullable=False)
    answer_quality = Column(JSONB)
    key_observations = Column(JSONB)
    strengths = Column(JSONB)
    gaps = Column(JSONB)
    action_type = Column(String(20))
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    
    # Relationships
    session = relationship("InterviewSession", back_populates="turns")
    question = relationship("InterviewQuestion", back_populates="turns")

class InterviewEvaluation(Base):
    __tablename__ = "interview_evaluations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    interview_session_id = Column(UUID(as_uuid=True), ForeignKey("interview_sessions.id", ondelete="CASCADE"))
    final_score = Column(Numeric(3, 1), nullable=False)
    grade = Column(String(20), nullable=False)
    hiring_recommendation = Column(String(20), nullable=False)
    dimension_scores = Column(JSONB, nullable=False)
    detailed_analysis = Column(JSONB, nullable=False)
    recommendations = Column(JSONB, nullable=False)
    metadata = Column(JSONB)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    session = relationship("InterviewSession", back_populates="evaluation")

class AgentCallLog(Base):
    __tablename__ = "agent_call_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_type = Column(String(50), nullable=False)
    interview_session_id = Column(UUID(as_uuid=True), ForeignKey("interview_sessions.id"))
    input_data = Column(JSONB)
    output_data = Column(JSONB)
    status = Column(String(20), nullable=False)
    error_message = Column(Text)
    latency_ms = Column(Integer)
    model_used = Column(String(100))
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
```

---

## Service Layer

Xem tiếp ở phần 2 của Integration Guide...

### 4. Service Layer - Question Service (app/services/question_service.py)

```python
import sys
sys.path.append('..')

from _sub_agents.agents.question_generator import QuestionGeneratorAgent
from app.models.interview import InterviewSession, InterviewQuestion, AgentCallLog
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import time
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class QuestionService:
    """Service for generating interview questions using AI agent"""
    
    def __init__(self):
        self.agent = QuestionGeneratorAgent(settings.QUESTION_AGENT_CONFIG)
    
    async def generate_questions(
        self,
        db: AsyncSession,
        session_id: str,
        job_description: str,
        cv_content: str,
        position_level: str,
        num_questions: int = 10,
        focus_areas: List[str] = None
    ) -> List[InterviewQuestion]:
        """
        Generate interview questions and save to database
        
        Returns:
            List of created InterviewQuestion objects
        """
        start_time = time.time()
        
        try:
            # Call AI agent
            result = self.agent.generate_questions(
                job_description=job_description,
                cv_content=cv_content,
                position_level=position_level,
                num_questions=num_questions,
                focus_areas=focus_areas or []
            )
            
            if result["status"] != "success":
                raise Exception(f"Agent error: {result.get('error')}")
            
            # Save questions to database
            questions = []
            for idx, q_data in enumerate(result["questions"]):
                question = InterviewQuestion(
                    interview_session_id=session_id,
                    question_id=q_data["question_id"],
                    category=q_data["category"],
                    difficulty=q_data["difficulty"],
                    question_text=q_data["question_text"],
                    key_points=q_data.get("key_points"),
                    ideal_answer_outline=q_data.get("ideal_answer_outline"),
                    evaluation_criteria=q_data.get("evaluation_criteria"),
                    order_index=idx,
                    is_selected=True
                )
                db.add(question)
                questions.append(question)
            
            # Log agent call
            latency_ms = int((time.time() - start_time) * 1000)
            log = AgentCallLog(
                agent_type="question_generator",
                interview_session_id=session_id,
                input_data={
                    "position_level": position_level,
                    "num_questions": num_questions
                },
                output_data=result.get("metadata"),
                status="success",
                latency_ms=latency_ms,
                model_used=self.agent.model
            )
            db.add(log)
            
            await db.commit()
            
            logger.info(f"Generated {len(questions)} questions in {latency_ms}ms")
            return questions
            
        except Exception as e:
            logger.error(f"Error generating questions: {e}")
            
            # Log error
            latency_ms = int((time.time() - start_time) * 1000)
            log = AgentCallLog(
                agent_type="question_generator",
                interview_session_id=session_id,
                status="error",
                error_message=str(e),
                latency_ms=latency_ms
            )
            db.add(log)
            await db.commit()
            
            raise
```

Tiếp tục trong message tiếp theo...
