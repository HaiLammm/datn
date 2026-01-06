"use client";

import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { useState, useEffect } from "react";
import { SkillAutocomplete } from "./SkillAutocomplete";

interface SalaryJobTypeFiltersProps {
    minSalary?: number;
    maxSalary?: number;
    jobTypes: string[];
    skills: string[];
    benefits: string[];
    onApply: (filters: { minSalary?: number; maxSalary?: number; jobTypes: string[]; skills: string[]; benefits: string[] }) => void;
    onClear: () => void;
}

const JOB_TYPES = [
    { id: "full-time", label: "Full-time" },
    { id: "part-time", label: "Part-time" },
    { id: "contract", label: "Contract" },
    { id: "internship", label: "Internship" },
    { id: "freelance", label: "Freelance" },
];

const BENEFITS = [
    { id: "insurance", label: "Bảo hiểm" },
    { id: "training", label: "Đào tạo" },
    { id: "laptop", label: "Cấp Laptop" },
    { id: "bonus", label: "Thưởng" },
    { id: "travel", label: "Du lịch" },
    { id: "leave", label: "Nghỉ phép" },
];

export function SalaryJobTypeFilters({
    minSalary: initialMin,
    maxSalary: initialMax,
    jobTypes: initialTypes,
    skills: initialSkills,
    benefits: initialBenefits,
    onApply,
    onClear,
}: SalaryJobTypeFiltersProps) {
    const [minSalary, setMinSalary] = useState<string>(initialMin?.toString() || "");
    const [maxSalary, setMaxSalary] = useState<string>(initialMax?.toString() || "");
    const [selectedTypes, setSelectedTypes] = useState<string[]>(initialTypes || []);
    const [selectedSkills, setSelectedSkills] = useState<string[]>(initialSkills || []);
    const [selectedBenefits, setSelectedBenefits] = useState<string[]>(initialBenefits || []);

    // Update local state when props change (e.g. from URL)
    useEffect(() => {
        setMinSalary(initialMin?.toString() || "");
        setMaxSalary(initialMax?.toString() || "");
        setSelectedTypes(initialTypes || []);
        setSelectedSkills(initialSkills || []);
        setSelectedBenefits(initialBenefits || []);
    }, [initialMin, initialMax, initialTypes, initialSkills, initialBenefits]);

    const handleApply = () => {
        const min = minSalary ? parseInt(minSalary) : undefined;
        const max = maxSalary ? parseInt(maxSalary) : undefined;
        onApply({ minSalary: min, maxSalary: max, jobTypes: selectedTypes, skills: selectedSkills, benefits: selectedBenefits });
    };

    const handleTypeChange = (type: string, checked: boolean) => {
        if (checked) {
            setSelectedTypes([...selectedTypes, type]);
        } else {
            setSelectedTypes(selectedTypes.filter((t) => t !== type));
        }
    };

    const handleClear = () => {
        setMinSalary("");
        setMaxSalary("");
        setSelectedTypes([]);
        setSelectedSkills([]);
        setSelectedBenefits([]);
        onClear();
    };

    const handleBenefitChange = (benefit: string, checked: boolean) => {
        if (checked) {
            setSelectedBenefits([...selectedBenefits, benefit]);
        } else {
            setSelectedBenefits(selectedBenefits.filter((b) => b !== benefit));
        }
    };

    return (
        <div className="space-y-6 p-4 border rounded-lg bg-white shadow-sm">
            {/* Salary Range */}
            <div>
                <h3 className="font-medium mb-3 text-sm">Mức lương</h3>
                <div className="flex gap-2 items-center">
                    <Input
                        type="number"
                        placeholder="Min"
                        value={minSalary}
                        onChange={(e) => setMinSalary(e.target.value)}
                        className="w-full text-sm"
                    />
                    <span className="text-muted-foreground">-</span>
                    <Input
                        type="number"
                        placeholder="Max"
                        value={maxSalary}
                        onChange={(e) => setMaxSalary(e.target.value)}
                        className="w-full text-sm"
                    />
                </div>
            </div>

            {/* Job Types */}
            <div>
                <h3 className="font-medium mb-3 text-sm">Loại công việc</h3>
                <div className="space-y-2">
                    {JOB_TYPES.map((type) => (
                        <div key={type.id} className="flex items-center space-x-2">
                            <Checkbox
                                id={type.id}
                                checked={selectedTypes.includes(type.id)}
                                onCheckedChange={(checked) => handleTypeChange(type.id, checked as boolean)}
                            />
                            <Label htmlFor={type.id} className="text-sm font-normal cursor-pointer">{type.label}</Label>
                        </div>
                    ))}
                </div>
            </div>

            {/* Benefits */}
            <div>
                <h3 className="font-medium mb-3 text-sm">Phúc lợi</h3>
                <div className="space-y-2">
                    {BENEFITS.map((benefit) => (
                        <div key={benefit.id} className="flex items-center space-x-2">
                            <Checkbox
                                id={`benefit-${benefit.id}`}
                                checked={selectedBenefits.includes(benefit.id)}
                                onCheckedChange={(checked) => handleBenefitChange(benefit.id, checked as boolean)}
                            />
                            <Label htmlFor={`benefit-${benefit.id}`} className="text-sm font-normal cursor-pointer">{benefit.label}</Label>
                        </div>
                    ))}
                </div>
            </div>

            {/* Skills */}
            <div>
                <SkillAutocomplete
                    selectedSkills={selectedSkills}
                    onSkillsChange={setSelectedSkills}
                />
            </div>

            {/* Actions */}
            <div className="flex gap-2 pt-2">
                <Button onClick={handleApply} className="flex-1" size="sm">Áp dụng</Button>
                <Button variant="outline" onClick={handleClear} size="sm">Xóa lọc</Button>
            </div>
        </div>
    );
}
