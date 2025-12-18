import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import { CandidateCard } from "./CandidateCard";
import { RankedCandidateResponse } from "@datn/shared-types";

// Mock next/link
jest.mock("next/link", () => {
  const MockLink = ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  );
  MockLink.displayName = "MockLink";
  return MockLink;
});

const mockCandidate: RankedCandidateResponse = {
  cv_id: "123e4567-e89b-12d3-a456-426614174000",
  user_id: 1,
  match_score: 85,
  breakdown: {
    matched_skills: ["Python", "FastAPI"],
    missing_skills: ["Kubernetes"],
    extra_skills: ["Docker"],
    skill_score: 55,
    experience_score: 30,
    experience_years: 4,
  },
  cv_summary: "Senior developer with Python experience",
  filename: "john_doe_cv.pdf",
};

describe("CandidateCard", () => {
  it("renders candidate info correctly", () => {
    render(<CandidateCard candidate={mockCandidate} rank={1} />);
    
    expect(screen.getByText("#1")).toBeInTheDocument();
    expect(screen.getByText("john_doe_cv.pdf")).toBeInTheDocument();
    expect(screen.getByText("85%")).toBeInTheDocument();
  });

  it("renders rank number correctly", () => {
    render(<CandidateCard candidate={mockCandidate} rank={5} />);
    
    expect(screen.getByText("#5")).toBeInTheDocument();
  });

  it("shows CV summary when available", () => {
    render(<CandidateCard candidate={mockCandidate} rank={1} />);
    
    expect(screen.getByText("Senior developer with Python experience")).toBeInTheDocument();
  });

  it("links to correct CV page", () => {
    render(<CandidateCard candidate={mockCandidate} rank={1} />);
    
    const link = screen.getByRole("link", { name: /xem cv/i });
    expect(link).toHaveAttribute("href", "/cvs/123e4567-e89b-12d3-a456-426614174000");
  });

  it("displays fallback name when filename is null", () => {
    const candidateWithoutFilename = {
      ...mockCandidate,
      filename: null,
    };
    render(<CandidateCard candidate={candidateWithoutFilename} rank={1} />);
    
    expect(screen.getByText("CV #123e4567")).toBeInTheDocument();
  });

  it("hides summary when cv_summary is null", () => {
    const candidateWithoutSummary = {
      ...mockCandidate,
      cv_summary: null,
    };
    render(<CandidateCard candidate={candidateWithoutSummary} rank={1} />);
    
    expect(screen.queryByText("Senior developer with Python experience")).not.toBeInTheDocument();
  });

  it("has correct accessibility label", () => {
    render(<CandidateCard candidate={mockCandidate} rank={1} />);
    
    const article = screen.getByRole("article");
    expect(article).toHaveAttribute("aria-label", "Candidate rank 1: john_doe_cv.pdf");
  });

  it("displays match score with correct color for high score", () => {
    render(<CandidateCard candidate={mockCandidate} rank={1} />);
    
    const scoreBadge = screen.getByRole("img", { name: /match score: 85%/i });
    expect(scoreBadge).toHaveClass("bg-green-500");
  });

  it("displays match score with yellow color for medium score", () => {
    const mediumScoreCandidate = {
      ...mockCandidate,
      match_score: 60,
    };
    render(<CandidateCard candidate={mediumScoreCandidate} rank={1} />);
    
    const scoreBadge = screen.getByRole("img", { name: /match score: 60%/i });
    expect(scoreBadge).toHaveClass("bg-yellow-500");
  });

  it("displays match score with red color for low score", () => {
    const lowScoreCandidate = {
      ...mockCandidate,
      match_score: 30,
    };
    render(<CandidateCard candidate={lowScoreCandidate} rank={1} />);
    
    const scoreBadge = screen.getByRole("img", { name: /match score: 30%/i });
    expect(scoreBadge).toHaveClass("bg-red-500");
  });
});
