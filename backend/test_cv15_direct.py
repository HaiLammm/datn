#!/usr/bin/env python3
"""
Direct test with CV 15.pdf to diagnose the issue
"""
import asyncio
import sys
sys.path.insert(0, '/home/luonghailam/Projects/datn/backend')

from app.modules.ai.service import AIService

async def test_cv15():
    service = AIService()
    
    # Read the extracted CV text
    with open('/home/luonghailam/Projects/datn/backend/cv15_extracted_text.txt', 'r') as f:
        cv_content = f.read()
    
    print("="*70)
    print("🔍 Testing CV 15.pdf Analysis")
    print("="*70)
    print(f"CV Content Length: {len(cv_content)} chars")
    print()
    
    # Test section splitting
    print("📑 Step 1: Section Splitting")
    print("-"*70)
    sections = service.robust_section_split(cv_content)
    print(f"Sections found: {list(sections.keys())}")
    for name, content in sections.items():
        print(f"  - {name}: {len(content)} chars")
    print()
    
    # Test smart truncation
    print("🔧 Step 2: Smart Truncation")
    print("-"*70)
    priority_sections = ['experience', 'skills', 'education']
    smart_content = service._build_smart_truncated_content(
        sections=sections,
        priority_sections=priority_sections,
        max_length=5000
    )
    print(f"Smart content length: {len(smart_content)} chars")
    print()
    
    # Count date patterns in smart content
    import re
    date_pattern = r'(\d{2}/\d{4})\s+to\s+(\d{2}/\d{4})'
    dates = re.findall(date_pattern, smart_content)
    print(f"Date ranges found: {len(dates)}")
    for i, (start, end) in enumerate(dates, 1):
        print(f"  {i}. {start} to {end}")
    print()
    
    # Test LLM analysis
    print("🤖 Step 3: LLM Analysis")
    print("-"*70)
    print("Sending to LLM... (this may take 60-120 seconds)")
    
    result = await service._perform_ai_analysis(cv_content)
    
    print()
    print("="*70)
    print("📊 Analysis Results")
    print("="*70)
    print(f"Overall Score: {result.get('score')}")
    print(f"Summary: {result.get('summary')[:150]}...")
    print()
    
    print("Criteria Scores:")
    criteria = result.get('criteria', {})
    for key, value in criteria.items():
        print(f"  - {key}: {value}")
    print()
    
    print("Experience Breakdown:")
    exp = result.get('experience_breakdown', {})
    print(f"  Total Years: {exp.get('total_years')}")
    print(f"  Key Roles: {exp.get('key_roles')}")
    print(f"  Industries: {exp.get('industries')}")
    print()
    
    print("Quality Indicators:")
    print(f"  Projects: {exp.get('num_projects', 0)}")
    print(f"  Awards: {exp.get('num_awards', 0)}")
    print(f"  Certifications: {exp.get('num_certifications', 0)}")
    print(f"  Leadership: {exp.get('has_leadership', False)}")
    print(f"  Description Quality: {exp.get('description_quality', 'N/A')}")
    print()
    
    if exp.get('quality_adjusted_score'):
        qs = exp['quality_adjusted_score']
        print("Quality-Adjusted Score:")
        print(f"  Final Score: {qs['final_score']}")
        print(f"  Base Score: {qs['base_score']} (from {exp.get('total_years')} years)")
        print(f"  Quality Bonus: +{qs['quality_bonus']}")
        print(f"  Quality Penalty: {qs['quality_penalty']}")
        print(f"  Explanation: {qs['explanation']}")
        
        if qs['bonus_details']:
            print(f"  Bonuses: {', '.join(qs['bonus_details'])}")
        if qs['penalty_details']:
            print(f"  Penalties: {', '.join(qs['penalty_details'])}")
    
    print()
    print("="*70)
    print("✅ Analysis complete!")
    print("="*70)
    
    # Expected vs Actual comparison
    print()
    print("📌 Expected vs Actual:")
    print(f"  Expected years: ~19 years (4 positions from 1996-2015)")
    print(f"  Actual extracted: {exp.get('total_years')} years")
    print(f"  Expected leadership: TRUE (Director, Team Leader, CIO)")
    print(f"  Actual detected: {exp.get('has_leadership', False)}")
    
    difference = abs(19 - exp.get('total_years', 0))
    if difference <= 2:
        print(f"  ✅ Year calculation is ACCURATE (within ±2 years)")
    elif difference <= 5:
        print(f"  ⚠️  Year calculation is ACCEPTABLE (within ±5 years)")
    else:
        print(f"  ❌ Year calculation is INACCURATE (off by {difference} years)")

if __name__ == "__main__":
    asyncio.run(test_cv15())
