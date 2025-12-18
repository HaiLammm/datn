"use client";

import { useState, useEffect, useCallback } from "react";
import { Input } from "@/components/ui/input";

interface MinScoreFilterProps {
  value: number;
  onChange: (value: number) => void;
}

export function MinScoreFilter({ value, onChange }: MinScoreFilterProps) {
  const [localValue, setLocalValue] = useState(value);

  // Sync local value with prop
  useEffect(() => {
    setLocalValue(value);
  }, [value]);

  // Debounced onChange
  useEffect(() => {
    const timer = setTimeout(() => {
      if (localValue !== value) {
        onChange(localValue);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [localValue, value, onChange]);

  const handleSliderChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const newValue = parseInt(e.target.value, 10);
      setLocalValue(newValue);
    },
    []
  );

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const inputValue = e.target.value;
      if (inputValue === "") {
        setLocalValue(0);
        return;
      }
      const newValue = parseInt(inputValue, 10);
      if (!isNaN(newValue) && newValue >= 0 && newValue <= 100) {
        setLocalValue(newValue);
      }
    },
    []
  );

  return (
    <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
      <label htmlFor="min-score-input" className="text-sm font-medium text-gray-700 whitespace-nowrap">
        Điểm tối thiểu:
      </label>
      <div className="flex items-center gap-3 w-full sm:w-auto">
        <input
          type="range"
          min="0"
          max="100"
          value={localValue}
          onChange={handleSliderChange}
          className="flex-1 sm:w-40 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
          aria-label="Minimum score slider"
          aria-valuemin={0}
          aria-valuemax={100}
          aria-valuenow={localValue}
        />
        <div className="flex items-center gap-1">
          <Input
            id="min-score-input"
            type="number"
            min="0"
            max="100"
            value={localValue}
            onChange={handleInputChange}
            className="w-16 text-center"
            aria-label="Minimum score input"
          />
          <span className="text-sm text-muted-foreground">%</span>
        </div>
      </div>
    </div>
  );
}
