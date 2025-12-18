import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import { SkillBadges } from "./SkillBadges";

describe("SkillBadges", () => {
  it("renders skills correctly", () => {
    render(<SkillBadges skills={["Python", "FastAPI"]} type="matched" />);
    
    expect(screen.getByText("Python")).toBeInTheDocument();
    expect(screen.getByText("FastAPI")).toBeInTheDocument();
  });

  it("renders correct color for matched type (green)", () => {
    render(<SkillBadges skills={["Python"]} type="matched" />);
    
    const badge = screen.getByText("Python");
    expect(badge).toHaveClass("bg-green-100");
    expect(badge).toHaveClass("text-green-800");
  });

  it("renders correct color for missing type (red)", () => {
    render(<SkillBadges skills={["Kubernetes"]} type="missing" />);
    
    const badge = screen.getByText("Kubernetes");
    expect(badge).toHaveClass("bg-red-100");
    expect(badge).toHaveClass("text-red-800");
  });

  it("renders correct color for extra type (gray)", () => {
    render(<SkillBadges skills={["Docker"]} type="extra" />);
    
    const badge = screen.getByText("Docker");
    expect(badge).toHaveClass("bg-gray-100");
    expect(badge).toHaveClass("text-gray-800");
  });

  it('shows "+N more" when skills exceed maxDisplay', () => {
    const skills = ["Python", "FastAPI", "Docker", "PostgreSQL", "Redis", "Kubernetes"];
    render(<SkillBadges skills={skills} type="matched" maxDisplay={3} />);
    
    expect(screen.getByText("Python")).toBeInTheDocument();
    expect(screen.getByText("FastAPI")).toBeInTheDocument();
    expect(screen.getByText("Docker")).toBeInTheDocument();
    expect(screen.getByText("+3 more")).toBeInTheDocument();
    expect(screen.queryByText("PostgreSQL")).not.toBeInTheDocument();
  });

  it("shows all skills when clicking +N more", () => {
    const skills = ["Python", "FastAPI", "Docker", "PostgreSQL", "Redis"];
    render(<SkillBadges skills={skills} type="matched" maxDisplay={2} />);
    
    fireEvent.click(screen.getByText("+3 more"));
    
    expect(screen.getByText("PostgreSQL")).toBeInTheDocument();
    expect(screen.getByText("Redis")).toBeInTheDocument();
    expect(screen.getByText("Show less")).toBeInTheDocument();
  });

  it("returns null for empty skills array", () => {
    const { container } = render(<SkillBadges skills={[]} type="matched" />);
    
    expect(container.firstChild).toBeNull();
  });

  it("has correct aria-label", () => {
    render(<SkillBadges skills={["Python"]} type="matched" />);
    
    const list = screen.getByRole("list");
    expect(list).toHaveAttribute("aria-label", "Matched skills");
  });

  it("renders items with listitem role", () => {
    render(<SkillBadges skills={["Python", "FastAPI"]} type="missing" />);
    
    const listItems = screen.getAllByRole("listitem");
    expect(listItems).toHaveLength(2);
  });
});
