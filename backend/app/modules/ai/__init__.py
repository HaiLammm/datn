# AI Analysis Module
"""
AI Analysis Module for CV processing and skill extraction.

This module provides:
- CV analysis using LLM (Ollama)
- RAG (Retrieval-Augmented Generation) integration
- Skill extraction and normalization
- Vector store for semantic search

Exports:
- SkillExtractor: Rule-based skill extraction class
- skill_extractor: Singleton instance of SkillExtractor
- SKILL_TAXONOMY: Comprehensive IT skill taxonomy
- HOT_SKILLS_2024: In-demand skills for 2024
"""

from .skill_taxonomy import (
    SKILL_TAXONOMY,
    HOT_SKILLS_2024,
    get_all_skills,
    get_skill_aliases,
    get_skill_to_category,
    is_hot_skill,
)

from .skill_extractor import (
    SkillExtractor,
    skill_extractor,
)

__all__ = [
    # Skill Taxonomy
    "SKILL_TAXONOMY",
    "HOT_SKILLS_2024",
    "get_all_skills",
    "get_skill_aliases",
    "get_skill_to_category",
    "is_hot_skill",
    # Skill Extractor
    "SkillExtractor",
    "skill_extractor",
]
