// src/types/job.ts

// 1. Định nghĩa JSONB cho Skill
export type ExtractedSkills = {
  must_have: string[];
  nice_to_have: string[];
};

// 2. Định nghĩa cho bảng Jobs
export interface Job {
  id: number;
  title: string;
  company_name: string;
  location: string;

  salary_min: number;
  salary_max: number | null;
  extracted_skills: ExtractedSkills;

  requirements_raw: string;

  created_at: string;
  upodated_at: string;
}

// 3. Định nghĩa kết quả Gợi ý (Job Matches)
export interface JobMatch extends Job {
  match_score: number; // 0.0 - 1.0 (AI chấm)
  reason: string; // "Phù hợp vì bạn biết Python..."
}
