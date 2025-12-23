import json
from pathlib import Path
from typing import Dict, List, Set

class SkillSuggester:
    def __init__(self, relationships_file: Path = None):
        self.skill_relationships: Dict[str, List[str]] = {}
        if relationships_file:
            self._load_relationships(relationships_file)
        else:
            # Default to the expected location if not provided
            default_path = Path(__file__).parent / "skill_relationships.json"
            self._load_relationships(default_path)

    def _load_relationships(self, file_path: Path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.skill_relationships = json.load(f)
        except FileNotFoundError:
            print(f"Skill relationships file not found: {file_path}")
            self.skill_relationships = {} # Ensure it's an empty dict
        except json.JSONDecodeError:
            print(f"Error decoding JSON from skill relationships file: {file_path}")
            self.skill_relationships = {} # Ensure it's an empty dict

    def get_suggestions(self, cv_skills: List[str], max_suggestions: int = 5) -> List[str]:
        cv_skills_lower = {skill.lower() for skill in cv_skills}
        potential_suggestions: Set[str] = set()

        for cv_skill in cv_skills_lower:
            # Check for direct matches in the relationship keys
            if cv_skill in self.skill_relationships:
                for related_skill in self.skill_relationships[cv_skill]:
                    if related_skill.lower() not in cv_skills_lower:
                        potential_suggestions.add(related_skill)
            
            # Check if cv_skill is a related skill to another key
            for primary_skill, related_list in self.skill_relationships.items():
                if cv_skill in {r.lower() for r in related_list}:
                    # If the CV has a related skill, suggest the primary skill itself
                    if primary_skill.lower() not in cv_skills_lower:
                        potential_suggestions.add(primary_skill)
                    # Also suggest other related skills from this primary skill
                    for other_related in related_list:
                        if other_related.lower() not in cv_skills_lower:
                            potential_suggestions.add(other_related)

        # Remove skills that are already in the CV
        filtered_suggestions = [
            s for s in potential_suggestions if s.lower() not in cv_skills_lower
        ]

        # For consistent results (e.g., in tests), sort before slicing
        sorted_suggestions = sorted(list(set(filtered_suggestions)))

        return sorted_suggestions[:max_suggestions]

# Module-level instance for convenient access
skill_suggester = SkillSuggester()
