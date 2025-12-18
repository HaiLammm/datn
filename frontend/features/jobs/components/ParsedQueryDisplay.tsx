"use client";

import { useState } from "react";
import { ParsedQueryResponse } from "@datn/shared-types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ChevronDown, ChevronUp, Sparkles } from "lucide-react";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";

export interface ParsedQueryDisplayProps {
  parsedQuery: ParsedQueryResponse;
}

export function ParsedQueryDisplay({ parsedQuery }: ParsedQueryDisplayProps) {
  const [isOpen, setIsOpen] = useState(false);

  const hasSkills = parsedQuery.extracted_skills.length > 0;
  const hasExperience = parsedQuery.experience_keywords.length > 0;

  if (!hasSkills && !hasExperience) {
    return null;
  }

  return (
    <div className="rounded-lg border bg-muted/30 p-4">
      <div className="flex items-center gap-2 mb-3">
        <Sparkles className="h-4 w-4 text-primary" aria-hidden="true" />
        <span className="text-sm font-medium">
          He thong da phan tich query cua ban:
        </span>
      </div>

      <div className="space-y-3">
        {hasSkills && (
          <div>
            <span className="text-sm text-muted-foreground mr-2">
              Ky nang tim kiem:
            </span>
            <div className="inline-flex flex-wrap gap-1 mt-1">
              {parsedQuery.extracted_skills.map((skill, index) => (
                <Badge
                  key={`skill-${index}`}
                  variant="secondary"
                  className="bg-primary/10 text-primary"
                >
                  {skill}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {hasExperience && (
          <div>
            <span className="text-sm text-muted-foreground mr-2">
              Kinh nghiem:
            </span>
            <div className="inline-flex flex-wrap gap-1 mt-1">
              {parsedQuery.experience_keywords.map((keyword, index) => (
                <Badge
                  key={`exp-${index}`}
                  variant="outline"
                  className="bg-blue-50 text-blue-700 border-blue-200"
                >
                  {keyword}
                </Badge>
              ))}
            </div>
          </div>
        )}

        <Collapsible open={isOpen} onOpenChange={setIsOpen}>
          <CollapsibleTrigger asChild>
            <Button
              variant="ghost"
              size="sm"
              className="h-7 text-xs text-muted-foreground hover:text-foreground p-0"
            >
              {isOpen ? (
                <>
                  <ChevronUp className="h-3 w-3 mr-1" />
                  An query goc
                </>
              ) : (
                <>
                  <ChevronDown className="h-3 w-3 mr-1" />
                  Xem query goc
                </>
              )}
            </Button>
          </CollapsibleTrigger>
          <CollapsibleContent className="mt-2">
            <div className="rounded bg-muted p-2 text-sm text-muted-foreground italic">
              &quot;{parsedQuery.raw_query}&quot;
            </div>
          </CollapsibleContent>
        </Collapsible>
      </div>
    </div>
  );
}
