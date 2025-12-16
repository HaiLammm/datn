#!/usr/bin/env python3
"""
Direct test of LLM analysis with quality indicators
"""
import asyncio
import sys
sys.path.insert(0, '/home/luonghailam/Projects/datn/backend')

from app.modules.ai.service import AIService

async def test_llm_analysis():
    service = AIService()
    
    # Simple test CV content
    test_cv = """
[EXPERIENCE]
Software Engineer 01/2020 to 12/2023 Tech Company
- Led development of 5 major projects
- Received Best Employee Award 2022
- Managed team of 3 developers

[SKILLS]
Python, JavaScript, React, SQL

[EDUCATION]
Bachelor of Computer Science 2019
    """.strip()
    
    print("="*60)
    print("Testing LLM Analysis with Quality Indicators")
    print("="*60)
    print(f"\nTest CV Content:\n{test_cv}\n")
    
    # Perform analysis
    result = await service._perform_ai_analysis(test_cv)
    
    print("\n" + "="*60)
    print("LLM Analysis Result:")
    print("="*60)
    print(f"Overall Score: {result.get('score')}")
    print(f"Criteria: {result.get('criteria')}")
    print(f"\nExperience Breakdown:")
    exp = result.get('experience_breakdown', {})
    for key, value in exp.items():
        print(f"  {key}: {value}")
    
    print("\n" + "="*60)
    print("✅ Test completed!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_llm_analysis())
