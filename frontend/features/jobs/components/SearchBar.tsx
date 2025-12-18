"use client";

import { useState, useCallback, FormEvent, KeyboardEvent } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Search, X, Loader2 } from "lucide-react";

export interface SearchBarProps {
  onSearch: (query: string) => void;
  loading?: boolean;
  placeholder?: string;
  initialValue?: string;
}

export function SearchBar({
  onSearch,
  loading = false,
  placeholder = "Nhap mo ta ung vien ban can tim...",
  initialValue = "",
}: SearchBarProps) {
  const [query, setQuery] = useState(initialValue);

  const handleSubmit = useCallback(
    (e: FormEvent<HTMLFormElement>) => {
      e.preventDefault();
      const trimmedQuery = query.trim();
      if (trimmedQuery.length >= 2) {
        onSearch(trimmedQuery);
      }
    },
    [query, onSearch]
  );

  const handleClear = useCallback(() => {
    setQuery("");
  }, []);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLInputElement>) => {
      if (e.key === "Escape") {
        handleClear();
      }
    },
    [handleClear]
  );

  return (
    <form
      role="search"
      aria-label="Tim kiem ung vien"
      onSubmit={handleSubmit}
      className="flex gap-2 w-full"
    >
      <div className="relative flex-1">
        <Search
          className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground"
          aria-hidden="true"
        />
        <Input
          type="search"
          role="searchbox"
          aria-label="Tim kiem ung vien"
          placeholder={placeholder}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
          className="pl-9 pr-9"
        />
        {query && !loading && (
          <Button
            type="button"
            variant="ghost"
            size="icon"
            onClick={handleClear}
            className="absolute right-1 top-1/2 -translate-y-1/2 h-7 w-7"
            aria-label="Xoa query"
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>
      <Button
        type="submit"
        disabled={loading || query.trim().length < 2}
        aria-label="Tim kiem"
        className="min-w-[100px]"
      >
        {loading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Dang tim...
          </>
        ) : (
          <>
            <Search className="mr-2 h-4 w-4" />
            Tim kiem
          </>
        )}
      </Button>
    </form>
  );
}
