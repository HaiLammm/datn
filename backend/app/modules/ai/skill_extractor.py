"""
Skill Extractor - Rule-based skill extraction from text.

This module provides a SkillExtractor class that extracts and normalizes
IT skills from text content (e.g., CV, job descriptions) using the
skill taxonomy defined in skill_taxonomy.py.

Features:
- Case-insensitive skill matching
- Skill normalization to canonical names
- Categorization of extracted skills
- Singleton pattern for efficient reuse
- Special character handling (C++, C#, .NET, etc.)
"""

import re
import logging
from typing import Dict, List, Optional, Set, Tuple

from .skill_taxonomy import (
    SKILL_TAXONOMY,
    get_skill_aliases,
    get_skill_to_category,
)


logger = logging.getLogger(__name__)


class SkillExtractor:
    """
    Rule-based skill extractor using predefined IT skill taxonomy.
    
    This class extracts skills from text and normalizes them to canonical
    names. It uses a singleton pattern to avoid rebuilding lookup tables
    on each instantiation.
    
    Attributes:
        _alias_to_canonical: Mapping from aliases to canonical names.
        _canonical_to_category: Mapping from canonical names to categories.
        _all_patterns: Precompiled regex patterns for skill matching.
        
    Example:
        >>> extractor = SkillExtractor()
        >>> result = extractor.extract_skills("Python developer with React experience")
        >>> print(result)
        {'programming_languages': ['python'], 'frameworks': ['react'], ...}
    """
    
    _instance: Optional["SkillExtractor"] = None
    
    def __new__(cls) -> "SkillExtractor":
        """Create or return singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        """Initialize lookup tables and regex patterns."""
        logger.debug("Initializing SkillExtractor...")
        
        # Build lookup tables from taxonomy
        self._alias_to_canonical: Dict[str, str] = get_skill_aliases()
        self._canonical_to_category: Dict[str, str] = get_skill_to_category()
        
        # Build regex patterns for all skills and aliases
        self._build_patterns()
        
        logger.debug(
            f"SkillExtractor initialized with {len(self._alias_to_canonical)} "
            f"skill aliases across {len(self._canonical_to_category)} canonical skills"
        )
    
    def _build_patterns(self) -> None:
        """
        Build regex patterns for skill matching.
        
        Special handling for:
        - C++, C#: Need to escape special regex characters
        - .NET: Dot needs escaping
        - Multi-word skills: "machine learning", "problem solving"
        """
        self._skill_patterns: Dict[str, List[re.Pattern]] = {}
        
        for alias, canonical in self._alias_to_canonical.items():
            # Skip if pattern already exists for this canonical skill
            # (we want to match any alias)
            pattern = self._create_pattern(alias)
            if pattern:
                # Store pattern with its canonical mapping
                if canonical not in self._skill_patterns:
                    self._skill_patterns[canonical] = []
                self._skill_patterns[canonical].append(pattern)
        
        # Flatten to list of (pattern, canonical) for matching
        self._all_patterns: List[Tuple[re.Pattern, str]] = []
        for canonical, patterns in self._skill_patterns.items():
            for pattern in patterns:
                self._all_patterns.append((pattern, canonical))
    
    def _create_pattern(self, skill: str) -> Optional[re.Pattern]:
        """
        Create a regex pattern for matching a skill.
        
        Args:
            skill: The skill name/alias to create a pattern for.
            
        Returns:
            Compiled regex pattern or None if invalid.
        """
        if not skill or not skill.strip():
            return None
        
        # Escape special regex characters but handle special cases
        escaped = re.escape(skill)
        
        # Special cases for common programming patterns
        # These need word boundary handling that works with special chars
        
        # For skills like "c++", "c#" - don't require word boundary after
        if skill.lower() in ["c++", "c#"]:
            # Match the skill followed by non-alphanumeric or end of string
            pattern = rf"(?<![a-zA-Z]){escaped}(?![a-zA-Z0-9])"
        elif skill.lower().startswith("."):
            # For .NET and similar, don't require word boundary before
            pattern = rf"{escaped}\b"
        else:
            # Standard word boundary matching
            # Use lookarounds that also handle markdown formatting chars like _ and *
            # This allows matching skills surrounded by underscores or asterisks
            pattern = rf"(?<![a-zA-Z0-9]){escaped}(?![a-zA-Z0-9])"
        
        try:
            return re.compile(pattern, re.IGNORECASE)
        except re.error as e:
            logger.warning(f"Failed to compile pattern for skill '{skill}': {e}")
            return None
    
    def normalize_skill(self, skill: str) -> Optional[str]:
        """
        Normalize a skill name to its canonical form.
        
        Args:
            skill: The skill name to normalize (case-insensitive).
            
        Returns:
            The canonical skill name, or None if not recognized.
            
        Example:
            >>> extractor = SkillExtractor()
            >>> extractor.normalize_skill("ReactJS")
            'react'
            >>> extractor.normalize_skill("PYTHON")
            'python'
            >>> extractor.normalize_skill("UnknownSkill")
            None
        """
        if not skill:
            return None
        
        normalized = skill.lower().strip()
        result = self._alias_to_canonical.get(normalized)
        
        if result:
            logger.debug(f"Normalized skill: '{skill}' -> '{result}'")
        else:
            logger.debug(f"Unknown skill: '{skill}'")
        
        return result
    
    def get_skill_category(self, skill: str) -> Optional[str]:
        """
        Get the category for a given skill.
        
        Args:
            skill: The skill name (canonical or alias).
            
        Returns:
            The category name, or None if skill not found.
            
        Example:
            >>> extractor = SkillExtractor()
            >>> extractor.get_skill_category("python")
            'programming_languages'
            >>> extractor.get_skill_category("ReactJS")
            'frameworks'
        """
        # First normalize the skill
        canonical = self.normalize_skill(skill)
        if not canonical:
            return None
        
        return self._canonical_to_category.get(canonical)
    
    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """
        Extract and categorize skills from text.
        
        This method scans the input text for known skills from the taxonomy,
        normalizes them to canonical names, and organizes them by category.
        
        Args:
            text: The text to extract skills from (e.g., CV content).
            
        Returns:
            Dict mapping category names to lists of unique canonical skill names.
            Categories with no skills found will have empty lists.
            
        Example:
            >>> extractor = SkillExtractor()
            >>> text = '''
            ...     Skills: Python, JavaScript, React, PostgreSQL
            ...     Experience with Docker and AWS
            ... '''
            >>> result = extractor.extract_skills(text)
            >>> result['programming_languages']
            ['python', 'javascript']
            >>> result['frameworks']
            ['react']
            >>> result['devops']
            ['docker', 'aws']
        """
        if not text:
            logger.debug("Empty text provided to extract_skills")
            return self._empty_result()
        
        logger.debug(f"Extracting skills from text ({len(text)} chars)")
        
        # Track found skills by category (using sets to handle duplicates)
        found_skills: Dict[str, Set[str]] = {
            category: set() for category in SKILL_TAXONOMY.keys()
        }
        
        # Search for each skill pattern in the text
        for pattern, canonical in self._all_patterns:
            if pattern.search(text):
                category = self._canonical_to_category.get(canonical)
                if category:
                    found_skills[category].add(canonical)
                    logger.debug(f"Found skill: {canonical} ({category})")
        
        # Convert sets to sorted lists for consistent output
        result: Dict[str, List[str]] = {
            category: sorted(list(skills))
            for category, skills in found_skills.items()
        }
        
        # Log summary
        total_skills = sum(len(skills) for skills in result.values())
        logger.debug(f"Extracted {total_skills} unique skills from text")
        
        return result
    
    def extract_skills_flat(self, text: str) -> List[str]:
        """
        Extract skills from text as a flat list.
        
        This is a convenience method that returns all extracted skills
        as a single list without category organization.
        
        Args:
            text: The text to extract skills from.
            
        Returns:
            Sorted list of unique canonical skill names.
            
        Example:
            >>> extractor = SkillExtractor()
            >>> extractor.extract_skills_flat("Python and React developer")
            ['python', 'react']
        """
        categorized = self.extract_skills(text)
        all_skills: Set[str] = set()
        for skills in categorized.values():
            all_skills.update(skills)
        return sorted(list(all_skills))
    
    def _empty_result(self) -> Dict[str, List[str]]:
        """Return an empty result dict with all categories."""
        return {category: [] for category in SKILL_TAXONOMY.keys()}
    
    @classmethod
    def reset_instance(cls) -> None:
        """
        Reset the singleton instance.
        
        This is primarily useful for testing to ensure a fresh instance.
        """
        cls._instance = None


# Create a module-level instance for convenient access
skill_extractor = SkillExtractor()
