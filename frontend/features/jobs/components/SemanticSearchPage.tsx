"use client";

import { useState, useCallback } from "react";
import { SearchResultResponse, ParsedQueryResponse } from "@datn/shared-types";
import { SearchBar } from "./SearchBar";
import { ParsedQueryDisplay } from "./ParsedQueryDisplay";
import { SearchResultList } from "./SearchResultList";
import { searchCandidatesAction } from "@/features/jobs/actions";

export function SemanticSearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResultResponse[]>([]);
  const [total, setTotal] = useState(0);
  const [parsedQuery, setParsedQuery] = useState<ParsedQueryResponse | null>(
    null
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [limit, setLimit] = useState(20);
  const [offset, setOffset] = useState(0);
  const [minScore, setMinScore] = useState(0);

  const executeSearch = useCallback(
    async (
      searchQuery: string,
      searchLimit: number,
      searchOffset: number,
      searchMinScore: number
    ) => {
      if (searchQuery.trim().length < 2) {
        setError("Query phai co it nhat 2 ky tu");
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const result = await searchCandidatesAction({
          query: searchQuery,
          limit: searchLimit,
          offset: searchOffset,
          min_score: searchMinScore,
        });

        if (result) {
          setResults(result.items);
          setTotal(result.total);
          setParsedQuery(result.parsed_query);
        } else {
          setError("Tim kiem that bai. Vui long thu lai.");
        }
      } catch (err) {
        console.error("Search error:", err);
        setError("Co loi xay ra. Vui long thu lai.");
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const handleSearch = useCallback(
    (searchQuery: string) => {
      setQuery(searchQuery);
      setOffset(0); // Reset to first page on new search
      executeSearch(searchQuery, limit, 0, minScore);
    },
    [limit, minScore, executeSearch]
  );

  const handlePageChange = useCallback(
    (newOffset: number) => {
      setOffset(newOffset);
      if (query) {
        executeSearch(query, limit, newOffset, minScore);
      }
    },
    [query, limit, minScore, executeSearch]
  );

  const handlePageSizeChange = useCallback(
    (newLimit: number) => {
      setLimit(newLimit);
      setOffset(0); // Reset to first page when changing page size
      if (query) {
        executeSearch(query, newLimit, 0, minScore);
      }
    },
    [query, minScore, executeSearch]
  );

  const handleMinScoreChange = useCallback(
    (newMinScore: number) => {
      setMinScore(newMinScore);
      setOffset(0); // Reset to first page when changing filter
      if (query) {
        executeSearch(query, limit, 0, newMinScore);
      }
    },
    [query, limit, executeSearch]
  );

  const handleRetry = useCallback(() => {
    if (query) {
      executeSearch(query, limit, offset, minScore);
    }
  }, [query, limit, offset, minScore, executeSearch]);

  const hasSearched = query.length > 0 || results.length > 0 || error !== null;

  return (
    <div className="space-y-6">
      {/* Search Bar */}
      <SearchBar onSearch={handleSearch} loading={loading} />

      {/* Parsed Query Display */}
      {parsedQuery && !loading && <ParsedQueryDisplay parsedQuery={parsedQuery} />}

      {/* Results */}
      {hasSearched && (
        <SearchResultList
          results={results}
          total={total}
          loading={loading}
          error={error}
          limit={limit}
          offset={offset}
          minScore={minScore}
          onPageChange={handlePageChange}
          onPageSizeChange={handlePageSizeChange}
          onMinScoreChange={handleMinScoreChange}
          onRetry={handleRetry}
        />
      )}
    </div>
  );
}
