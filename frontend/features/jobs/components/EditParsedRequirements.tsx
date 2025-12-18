"use client";

import { useState } from "react";
import { ParsedJDRequirements } from "@datn/shared-types";
import { updateParsedRequirementsAction } from "@/features/jobs/actions";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Loader2, X, Plus } from "lucide-react";

interface EditParsedRequirementsProps {
  jdId: string;
  currentRequirements: ParsedJDRequirements;
  onSave: () => void;
  onCancel: () => void;
}

export function EditParsedRequirements({
  jdId,
  currentRequirements,
  onSave,
  onCancel,
}: EditParsedRequirementsProps) {
  const [requiredSkills, setRequiredSkills] = useState<string[]>(
    currentRequirements.required_skills || []
  );
  const [niceToHaveSkills, setNiceToHaveSkills] = useState<string[]>(
    currentRequirements.nice_to_have_skills || []
  );
  const [minExperienceYears, setMinExperienceYears] = useState<string>(
    currentRequirements.min_experience_years?.toString() || ""
  );
  const [newRequiredSkill, setNewRequiredSkill] = useState("");
  const [newNiceToHaveSkill, setNewNiceToHaveSkill] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const addSkill = (
    skill: string,
    list: string[],
    setList: React.Dispatch<React.SetStateAction<string[]>>,
    clearInput: () => void
  ) => {
    const trimmed = skill.trim();
    if (trimmed && !list.includes(trimmed)) {
      setList([...list, trimmed]);
      clearInput();
    }
  };

  const removeSkill = (
    skillToRemove: string,
    list: string[],
    setList: React.Dispatch<React.SetStateAction<string[]>>
  ) => {
    setList(list.filter((s) => s !== skillToRemove));
  };

  const handleAddRequiredSkill = () => {
    addSkill(newRequiredSkill, requiredSkills, setRequiredSkills, () =>
      setNewRequiredSkill("")
    );
  };

  const handleAddNiceToHaveSkill = () => {
    addSkill(newNiceToHaveSkill, niceToHaveSkills, setNiceToHaveSkills, () =>
      setNewNiceToHaveSkill("")
    );
  };

  const handleKeyDown = (
    e: React.KeyboardEvent,
    addHandler: () => void
  ) => {
    if (e.key === "Enter") {
      e.preventDefault();
      addHandler();
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    setError(null);

    try {
      const data: Partial<ParsedJDRequirements> = {
        required_skills: requiredSkills,
        nice_to_have_skills: niceToHaveSkills,
        min_experience_years: minExperienceYears
          ? parseInt(minExperienceYears, 10)
          : null,
      };

      const result = await updateParsedRequirementsAction(jdId, data);

      if (result.success) {
        onSave();
      } else {
        setError(result.message);
      }
    } catch (err) {
      setError("Đã xảy ra lỗi khi lưu thay đổi.");
      console.error("Save error:", err);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center gap-2">
        ✏️ Chỉnh sửa yêu cầu
      </h3>

      <div className="space-y-6">
        {/* Required Skills */}
        <div className="space-y-2">
          <Label>Kỹ năng yêu cầu</Label>
          <div
            className="flex flex-wrap gap-2 mb-2"
            role="list"
            aria-label="Kỹ năng yêu cầu"
          >
            {requiredSkills.map((skill) => (
              <span
                key={skill}
                role="listitem"
                className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800"
              >
                {skill}
                <button
                  type="button"
                  onClick={() =>
                    removeSkill(skill, requiredSkills, setRequiredSkills)
                  }
                  className="hover:bg-blue-200 rounded-full p-0.5"
                  aria-label={`Xóa ${skill}`}
                >
                  <X className="h-3 w-3" />
                </button>
              </span>
            ))}
          </div>
          <div className="flex gap-2">
            <Input
              value={newRequiredSkill}
              onChange={(e) => setNewRequiredSkill(e.target.value)}
              onKeyDown={(e) => handleKeyDown(e, handleAddRequiredSkill)}
              placeholder="Thêm kỹ năng..."
              aria-label="Thêm kỹ năng yêu cầu mới"
            />
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={handleAddRequiredSkill}
              disabled={!newRequiredSkill.trim()}
            >
              <Plus className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Nice-to-have Skills */}
        <div className="space-y-2">
          <Label>Kỹ năng ưu tiên</Label>
          <div
            className="flex flex-wrap gap-2 mb-2"
            role="list"
            aria-label="Kỹ năng ưu tiên"
          >
            {niceToHaveSkills.map((skill) => (
              <span
                key={skill}
                role="listitem"
                className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm bg-purple-100 text-purple-800"
              >
                {skill}
                <button
                  type="button"
                  onClick={() =>
                    removeSkill(skill, niceToHaveSkills, setNiceToHaveSkills)
                  }
                  className="hover:bg-purple-200 rounded-full p-0.5"
                  aria-label={`Xóa ${skill}`}
                >
                  <X className="h-3 w-3" />
                </button>
              </span>
            ))}
          </div>
          <div className="flex gap-2">
            <Input
              value={newNiceToHaveSkill}
              onChange={(e) => setNewNiceToHaveSkill(e.target.value)}
              onKeyDown={(e) => handleKeyDown(e, handleAddNiceToHaveSkill)}
              placeholder="Thêm kỹ năng..."
              aria-label="Thêm kỹ năng ưu tiên mới"
            />
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={handleAddNiceToHaveSkill}
              disabled={!newNiceToHaveSkill.trim()}
            >
              <Plus className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Min Experience Years */}
        <div className="space-y-2">
          <Label htmlFor="edit-min-exp">Kinh nghiệm tối thiểu (năm)</Label>
          <Input
            id="edit-min-exp"
            type="number"
            min="0"
            value={minExperienceYears}
            onChange={(e) => setMinExperienceYears(e.target.value)}
            placeholder="VD: 3"
            className="max-w-32"
          />
        </div>

        {/* Error message */}
        {error && (
          <p role="alert" className="text-red-500 text-sm">
            {error}
          </p>
        )}

        {/* Actions */}
        <div className="flex gap-3 pt-2">
          <Button onClick={handleSave} disabled={isSaving}>
            {isSaving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {isSaving ? "Đang lưu..." : "Lưu thay đổi"}
          </Button>
          <Button variant="outline" onClick={onCancel} disabled={isSaving}>
            Hủy
          </Button>
        </div>
      </div>
    </div>
  );
}
