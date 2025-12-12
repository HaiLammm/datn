interface SkillCloudProps {
  skills: string[];
}

export function SkillCloud({ skills }: SkillCloudProps) {
  if (skills.length === 0) {
    return (
      <p className="text-gray-500 italic">No skills extracted</p>
    );
  }

  return (
    <div className="flex flex-wrap gap-2">
      {skills.map((skill, index) => (
        <span
          key={index}
          className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800"
        >
          {skill}
        </span>
      ))}
    </div>
  );
}