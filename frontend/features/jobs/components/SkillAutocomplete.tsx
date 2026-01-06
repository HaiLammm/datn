"use client";

import * as React from "react";
import { X } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { useDebounce } from "@/hooks/use-debounce";
import { getSkillSuggestionsAction, SkillSuggestion } from "../actions";
import { cn } from "@/lib/utils";

interface SkillAutocompleteProps {
    selectedSkills: string[];
    onSkillsChange: (skills: string[]) => void;
}

export function SkillAutocomplete({
    selectedSkills,
    onSkillsChange,
}: SkillAutocompleteProps) {
    const [inputValue, setInputValue] = React.useState("");
    const [suggestions, setSuggestions] = React.useState<SkillSuggestion[]>([]);
    const [isOpen, setIsOpen] = React.useState(false);
    const [loading, setLoading] = React.useState(false);

    const debouncedInput = useDebounce(inputValue, 300);

    React.useEffect(() => {
        const fetchSuggestions = async () => {
            if (debouncedInput.length < 1) {
                setSuggestions([]);
                return;
            }
            setLoading(true);
            const data = await getSkillSuggestionsAction(debouncedInput);
            setLoading(false);

            // Filter out already selected skills
            setSuggestions(data.filter(s => !selectedSkills.includes(s.skill)));
            setIsOpen(true);
        };

        fetchSuggestions();
    }, [debouncedInput, selectedSkills]);

    const handleSelect = (skill: string) => {
        if (!selectedSkills.includes(skill)) {
            onSkillsChange([...selectedSkills, skill]);
        }
        setInputValue("");
        setIsOpen(false);
    };

    const handleRemove = (skill: string) => {
        onSkillsChange(selectedSkills.filter((s) => s !== skill));
    };

    return (
        <div className="space-y-3">
            <h3 className="font-medium text-sm">Kỹ năng</h3>

            {/* Selected badges */}
            {selectedSkills.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-2">
                    {selectedSkills.map((skill) => (
                        <Badge key={skill} variant="secondary" className="px-2 py-1 flex items-center gap-1">
                            {skill}
                            <button
                                className="ml-1 ring-offset-background rounded-full outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 cursor-pointer"
                                onClick={() => handleRemove(skill)}
                                type="button"
                            >
                                <X className="h-3 w-3 text-muted-foreground hover:text-foreground" />
                            </button>
                        </Badge>
                    ))}
                </div>
            )}

            <div className="relative">
                <Input
                    placeholder="Nhập kỹ năng (vd: Java...)"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onFocus={() => inputValue.length > 0 && setIsOpen(true)}
                    onBlur={() => setTimeout(() => setIsOpen(false), 200)}
                    className="w-full text-sm"
                />

                {isOpen && suggestions.length > 0 && (
                    <div className="absolute top-full z-10 w-full mt-1 bg-white border rounded-md shadow-md max-h-60 overflow-y-auto">
                        {suggestions.map((suggestion) => (
                            <div
                                key={suggestion.skill}
                                className={cn(
                                    "flex items-center justify-between px-3 py-2 text-sm cursor-pointer hover:bg-accent hover:text-accent-foreground",
                                )}
                                onMouseDown={(e) => {
                                    e.preventDefault(); // Prevent blur which closes dropdown
                                    handleSelect(suggestion.skill);
                                }}
                            >
                                <span>{suggestion.skill}</span>
                                <span className="text-xs text-muted-foreground">({suggestion.count})</span>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
