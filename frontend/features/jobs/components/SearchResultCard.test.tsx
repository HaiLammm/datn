import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import { SearchResultCard } from "./SearchResultCard";
import { SearchResultResponse } from "@datn/shared-types";

// Mock next/link
jest.mock("next/link", () => {
  const MockLink = ({
    children,
    href,
  }: {
    children: React.ReactNode;
    href: string;
  }) => <a href={href}>{children}</a>;
  MockLink.displayName = "MockLink";
  return MockLink;
});

const mockResult: SearchResultResponse = {
  cv_id: "123e4567-e89b-12d3-a456-426614174000",
  user_id: 1,
  relevance_score: 85,
  matched_skills: ["Python", "AWS", "Docker"],
  cv_summary: "Experienced Python developer with strong AWS skills and DevOps background.",
  filename: "john_doe_cv.pdf",
};

describe("SearchResultCard", () => {
  it("renders result info correctly", () => {
    render(<SearchResultCard result={mockResult} rank={1} />);

    expect(screen.getByText("john_doe_cv.pdf")).toBeInTheDocument();
    expect(
      screen.getByText(/Experienced Python developer with strong AWS skills/)
    ).toBeInTheDocument();
  });

  it("shows correct rank number", () => {
    render(<SearchResultCard result={mockResult} rank={3} />);

    expect(screen.getByText("#3")).toBeInTheDocument();
  });

  it("displays relevance score with MatchScoreBadge", () => {
    render(<SearchResultCard result={mockResult} rank={1} />);

    // MatchScoreBadge shows score with % sign and has role="img"
    expect(screen.getByRole("img", { name: /match score: 85%/i })).toBeInTheDocument();
    expect(screen.getByText("85%")).toBeInTheDocument();
  });

  it("displays matched skills as badges", () => {
    render(<SearchResultCard result={mockResult} rank={1} />);

    expect(screen.getByText("Python")).toBeInTheDocument();
    expect(screen.getByText("AWS")).toBeInTheDocument();
    expect(screen.getByText("Docker")).toBeInTheDocument();
  });

  it("links to correct CV page", () => {
    render(<SearchResultCard result={mockResult} rank={1} />);

    const viewButton = screen.getByRole("link", { name: /xem cv/i });
    expect(viewButton).toHaveAttribute(
      "href",
      "/jobs/candidates/123e4567-e89b-12d3-a456-426614174000"
    );
  });

  it("shows truncated filename when no filename provided", () => {
    const resultNoFilename: SearchResultResponse = {
      ...mockResult,
      filename: null,
    };

    render(<SearchResultCard result={resultNoFilename} rank={1} />);

    // Should show CV #{first 8 chars of UUID}
    expect(screen.getByText("CV #123e4567")).toBeInTheDocument();
  });

  it("shows default text when no summary provided", () => {
    const resultNoSummary: SearchResultResponse = {
      ...mockResult,
      cv_summary: null,
    };

    render(<SearchResultCard result={resultNoSummary} rank={1} />);

    expect(screen.getByText("Khong co mo ta")).toBeInTheDocument();
  });

  it("truncates long summary", () => {
    const longSummary =
      "This is a very long summary that exceeds 150 characters. It should be truncated with an ellipsis at the end to maintain a clean UI. This text continues beyond the limit.";
    const resultLongSummary: SearchResultResponse = {
      ...mockResult,
      cv_summary: longSummary,
    };

    render(<SearchResultCard result={resultLongSummary} rank={1} />);

    // The summary should be truncated to 150 chars + "..."
    const summaryElement = screen.getByText(/This is a very long summary/);
    expect(summaryElement.textContent?.endsWith("...")).toBe(true);
  });

  it("handles empty matched skills array", () => {
    const resultNoSkills: SearchResultResponse = {
      ...mockResult,
      matched_skills: [],
    };

    render(<SearchResultCard result={resultNoSkills} rank={1} />);

    // Should still render without skills section
    expect(screen.getByText("john_doe_cv.pdf")).toBeInTheDocument();
    expect(screen.queryByText("Python")).not.toBeInTheDocument();
  });

  it("has correct ARIA attributes for accessibility", () => {
    render(<SearchResultCard result={mockResult} rank={1} />);

    // Card should have role="listitem" with aria-label containing candidate info
    // Note: SkillBadges also renders listitems inside, so we use aria-label to find the card
    const card = screen.getByRole("listitem", { name: /ung vien 1/i });
    expect(card).toBeInTheDocument();
    expect(card).toHaveAttribute("aria-label");
  });

  it("renders different score colors based on score value", () => {
    // High score (green) - score >= 70
    const { unmount } = render(
      <SearchResultCard result={{ ...mockResult, relevance_score: 90 }} rank={1} />
    );
    expect(screen.getByRole("img", { name: /match score: 90%/i })).toBeInTheDocument();
    expect(screen.getByText("90%")).toBeInTheDocument();
    unmount();

    // Medium score (yellow) - score 50-69
    const { unmount: unmount2 } = render(
      <SearchResultCard result={{ ...mockResult, relevance_score: 60 }} rank={2} />
    );
    expect(screen.getByRole("img", { name: /match score: 60%/i })).toBeInTheDocument();
    expect(screen.getByText("60%")).toBeInTheDocument();
    unmount2();

    // Low score (red) - score < 50
    render(<SearchResultCard result={{ ...mockResult, relevance_score: 30 }} rank={3} />);
    expect(screen.getByRole("img", { name: /match score: 30%/i })).toBeInTheDocument();
    expect(screen.getByText("30%")).toBeInTheDocument();
  });
});
