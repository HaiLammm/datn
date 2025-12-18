import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import { MatchScoreBadge } from "./MatchScoreBadge";

describe("MatchScoreBadge", () => {
  it("renders the score correctly", () => {
    render(<MatchScoreBadge score={85} />);
    
    expect(screen.getByText("85%")).toBeInTheDocument();
  });

  it("renders correct color for score >= 70 (green)", () => {
    render(<MatchScoreBadge score={75} />);
    
    const badge = screen.getByRole("img");
    expect(badge).toHaveClass("bg-green-500");
  });

  it("renders correct color for score 50-69 (yellow)", () => {
    render(<MatchScoreBadge score={55} />);
    
    const badge = screen.getByRole("img");
    expect(badge).toHaveClass("bg-yellow-500");
  });

  it("renders correct color for score < 50 (red)", () => {
    render(<MatchScoreBadge score={35} />);
    
    const badge = screen.getByRole("img");
    expect(badge).toHaveClass("bg-red-500");
  });

  it("has correct aria-label", () => {
    render(<MatchScoreBadge score={92} />);
    
    const badge = screen.getByRole("img");
    expect(badge).toHaveAttribute("aria-label", "Match score: 92%");
  });

  it("applies correct size classes for sm", () => {
    render(<MatchScoreBadge score={50} size="sm" />);
    
    const badge = screen.getByRole("img");
    expect(badge).toHaveClass("h-8", "w-8");
  });

  it("applies correct size classes for lg", () => {
    render(<MatchScoreBadge score={50} size="lg" />);
    
    const badge = screen.getByRole("img");
    expect(badge).toHaveClass("h-14", "w-14");
  });

  it("renders boundary score 70 as green", () => {
    render(<MatchScoreBadge score={70} />);
    
    const badge = screen.getByRole("img");
    expect(badge).toHaveClass("bg-green-500");
  });

  it("renders boundary score 50 as yellow", () => {
    render(<MatchScoreBadge score={50} />);
    
    const badge = screen.getByRole("img");
    expect(badge).toHaveClass("bg-yellow-500");
  });

  it("renders boundary score 49 as red", () => {
    render(<MatchScoreBadge score={49} />);
    
    const badge = screen.getByRole("img");
    expect(badge).toHaveClass("bg-red-500");
  });
});
