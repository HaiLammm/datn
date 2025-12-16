#!/usr/bin/env python3
"""
Test quality-adjusted experience scoring directly
"""
import asyncio
from app.modules.ai.service import AIService

async def test_quality_scoring():
    service = AIService()
    
    # Test case 1: Junior with many projects
    print("="*60)
    print("TEST 1: Junior (3 years) with 8 projects and 2 awards")
    print("="*60)
    result1 = service._calculate_quality_adjusted_experience_score(
        total_years=3,
        num_projects=8,
        num_awards=2,
        num_certifications=0,
        has_leadership=False,
        job_description_quality="good"
    )
    print(f"Final Score: {result1['final_score']}")
    print(f"Base Score: {result1['base_score']}")
    print(f"Quality Bonus: {result1['quality_bonus']}")
    print(f"Quality Penalty: {result1['quality_penalty']}")
    print(f"Explanation: {result1['explanation']}")
    if result1['bonus_details']:
        print(f"Bonuses: {', '.join(result1['bonus_details'])}")
    
    # Test case 2: Senior with few projects
    print("\n" + "="*60)
    print("TEST 2: Senior (10 years) with 3 projects, no awards")
    print("="*60)
    result2 = service._calculate_quality_adjusted_experience_score(
        total_years=10,
        num_projects=3,
        num_awards=0,
        num_certifications=0,
        has_leadership=False,
        job_description_quality="medium"
    )
    print(f"Final Score: {result2['final_score']}")
    print(f"Base Score: {result2['base_score']}")
    print(f"Quality Bonus: {result2['quality_bonus']}")
    print(f"Quality Penalty: {result2['quality_penalty']}")
    print(f"Explanation: {result2['explanation']}")
    if result2['penalty_details']:
        print(f"Penalties: {', '.join(result2['penalty_details'])}")
    
    # Test case 3: Senior with many achievements
    print("\n" + "="*60)
    print("TEST 3: Senior (10 years) with 12 projects, 3 awards, leadership")
    print("="*60)
    result3 = service._calculate_quality_adjusted_experience_score(
        total_years=10,
        num_projects=12,
        num_awards=3,
        num_certifications=5,
        has_leadership=True,
        job_description_quality="good"
    )
    print(f"Final Score: {result3['final_score']}")
    print(f"Base Score: {result3['base_score']}")
    print(f"Quality Bonus: {result3['quality_bonus']}")
    print(f"Quality Penalty: {result3['quality_penalty']}")
    print(f"Explanation: {result3['explanation']}")
    if result3['bonus_details']:
        print(f"Bonuses: {', '.join(result3['bonus_details'])}")
    
    # Test case 4: Very senior but poor quality
    print("\n" + "="*60)
    print("TEST 4: Very Senior (15 years) with 2 projects, no awards")
    print("="*60)
    result4 = service._calculate_quality_adjusted_experience_score(
        total_years=15,
        num_projects=2,
        num_awards=0,
        num_certifications=0,
        has_leadership=False,
        job_description_quality="poor"
    )
    print(f"Final Score: {result4['final_score']}")
    print(f"Base Score: {result4['base_score']}")
    print(f"Quality Bonus: {result4['quality_bonus']}")
    print(f"Quality Penalty: {result4['quality_penalty']}")
    print(f"Explanation: {result4['explanation']}")
    if result4['penalty_details']:
        print(f"Penalties: {', '.join(result4['penalty_details'])}")
    
    print("\n" + "="*60)
    print("✅ Quality scoring tests completed!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_quality_scoring())
