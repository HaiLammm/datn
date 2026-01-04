import { SkillCategories } from '@datn/shared-types';
import { cn } from '@/lib/utils';

interface SkillCategoriesDisplayProps {
  categories: SkillCategories;
}

/**
 * Category configuration for styling and display.
 */
const CATEGORY_CONFIG: Record<string, { 
  label: string; 
  badgeClass: string; 
  order: number;
}> = {
  programming_languages: {
    label: 'Programming Languages',
    badgeClass: 'bg-blue-100 text-blue-800',
    order: 1
  },
  frameworks: {
    label: 'Frameworks',
    badgeClass: 'bg-green-100 text-green-800',
    order: 2
  },
  databases: {
    label: 'Databases',
    badgeClass: 'bg-purple-100 text-purple-800',
    order: 3
  },
  devops: {
    label: 'DevOps',
    badgeClass: 'bg-orange-100 text-orange-800',
    order: 4
  },
  infrastructure: {
    label: 'Infrastructure',
    badgeClass: 'bg-slate-100 text-slate-800',
    order: 5
  },
  networking: {
    label: 'Networking',
    badgeClass: 'bg-cyan-100 text-cyan-800',
    order: 6
  },
  compliance: {
    label: 'Compliance',
    badgeClass: 'bg-amber-100 text-amber-800',
    order: 7
  },
  soft_skills: {
    label: 'Soft Skills',
    badgeClass: 'bg-pink-100 text-pink-800',
    order: 8
  },
  ai_ml: {
    label: 'AI/ML',
    badgeClass: 'bg-indigo-100 text-indigo-800',
    order: 9
  },
  other: {
    label: 'Other',
    badgeClass: 'bg-gray-100 text-gray-800',
    order: 10
  }
};

/**
 * Displays categorized skills with color-coded badges.
 * Each category has its own color scheme for easy visual distinction.
 * Empty categories are hidden to avoid visual clutter.
 * 
 * @see _bmad-output/planning-artifacts/docs/prd/5-hybrid-skill-scoring-epic.md
 */
export function SkillCategoriesDisplay({ categories }: SkillCategoriesDisplayProps) {
  // Build list of non-empty categories with their config
  const categoryEntries = Object.entries(categories)
    .filter(([, skills]) => skills && skills.length > 0)
    .map(([key, skills]) => ({
      key,
      skills: skills as string[],
      config: CATEGORY_CONFIG[key] || CATEGORY_CONFIG.other
    }))
    .sort((a, b) => a.config.order - b.config.order);

  // Count total skills
  const totalSkills = categoryEntries.reduce((sum, cat) => sum + cat.skills.length, 0);

  if (totalSkills === 0) {
    return (
      <p className="text-gray-500 italic">No categorized skills available</p>
    );
  }

  return (
    <div className="space-y-4">
      {/* Total skills count */}
      <p className="text-sm text-gray-600">
        {totalSkills} skill{totalSkills !== 1 ? 's' : ''} found across {categoryEntries.length} categor{categoryEntries.length !== 1 ? 'ies' : 'y'}
      </p>

      {/* Category sections */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {categoryEntries.map(({ key, skills, config }) => (
          <div key={key} className="space-y-2">
            <h4 className="text-sm font-medium text-gray-700">
              {config.label} ({skills.length})
            </h4>
            <div className="flex flex-wrap gap-1.5" role="list" aria-label={`${config.label} skills`}>
              {skills.map((skill, index) => (
                <span
                  key={`${key}-${index}`}
                  role="listitem"
                  className={cn(
                    'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                    config.badgeClass
                  )}
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
