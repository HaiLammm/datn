import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import { UserStats } from "./UserStats";
import type { UserStats as UserStatsType } from "@datn/shared-types";

function createMockStats(overrides: Partial<UserStatsType> = {}): UserStatsType {
  return {
    total_cvs: 5,
    average_score: 75,
    best_score: 92,
    total_unique_skills: 15,
    top_skills: ["Python", "JavaScript", "React"],
    ...overrides,
  };
}

describe("UserStats", () => {
  describe("Statistics Display", () => {
    it("renders all statistics when data is provided", () => {
      const stats = createMockStats();
      render(<UserStats stats={stats} />);

      expect(screen.getByTestId("stat-total-cvs")).toBeInTheDocument();
      expect(screen.getByTestId("stat-average-score")).toBeInTheDocument();
      expect(screen.getByTestId("stat-best-score")).toBeInTheDocument();
      expect(screen.getByTestId("stat-total-skills")).toBeInTheDocument();
    });

    it("displays correct total CVs value", () => {
      const stats = createMockStats({ total_cvs: 10 });
      render(<UserStats stats={stats} />);

      expect(screen.getByTestId("total-cvs-value")).toHaveTextContent("10");
    });

    it("displays correct average score value", () => {
      const stats = createMockStats({ average_score: 82 });
      render(<UserStats stats={stats} />);

      expect(screen.getByTestId("average-score-value")).toHaveTextContent("82");
    });

    it("displays correct best score value", () => {
      const stats = createMockStats({ best_score: 95 });
      render(<UserStats stats={stats} />);

      expect(screen.getByTestId("best-score-value")).toHaveTextContent("95");
    });

    it("displays correct total unique skills value", () => {
      const stats = createMockStats({ total_unique_skills: 20 });
      render(<UserStats stats={stats} />);

      expect(screen.getByTestId("total-skills-value")).toHaveTextContent("20");
    });

    it("rounds average score to nearest integer", () => {
      const stats = createMockStats({ average_score: 76.7 });
      render(<UserStats stats={stats} />);

      expect(screen.getByTestId("average-score-value")).toHaveTextContent("77");
    });
  });

  describe("Top Skills Display", () => {
    it("renders top skills when available", () => {
      const stats = createMockStats({
        top_skills: ["Python", "JavaScript", "React"],
      });
      render(<UserStats stats={stats} />);

      expect(screen.getByTestId("top-skills-section")).toBeInTheDocument();
      expect(screen.getByTestId("top-skill-0")).toHaveTextContent("Python");
      expect(screen.getByTestId("top-skill-1")).toHaveTextContent("JavaScript");
      expect(screen.getByTestId("top-skill-2")).toHaveTextContent("React");
    });

    it("does not render top skills section when empty", () => {
      const stats = createMockStats({ top_skills: [] });
      render(<UserStats stats={stats} />);

      expect(screen.queryByTestId("top-skills-section")).not.toBeInTheDocument();
    });
  });

  describe("Null/Empty States", () => {
    it("shows N/A when average score is null", () => {
      const stats = createMockStats({ average_score: null });
      render(<UserStats stats={stats} />);

      expect(screen.getByTestId("average-score-value")).toHaveTextContent("N/A");
    });

    it("shows N/A when best score is null", () => {
      const stats = createMockStats({ best_score: null });
      render(<UserStats stats={stats} />);

      expect(screen.getByTestId("best-score-value")).toHaveTextContent("N/A");
    });

    it("shows 0 for total CVs when stats is null", () => {
      render(<UserStats stats={null} />);

      expect(screen.getByTestId("total-cvs-value")).toHaveTextContent("0");
    });

    it("shows N/A for scores when stats is null", () => {
      render(<UserStats stats={null} />);

      expect(screen.getByTestId("average-score-value")).toHaveTextContent("N/A");
      expect(screen.getByTestId("best-score-value")).toHaveTextContent("N/A");
    });

    it("shows empty message when stats is null", () => {
      render(<UserStats stats={null} />);

      expect(screen.getByTestId("stats-empty-message")).toHaveTextContent(
        "Upload your first CV to start tracking your progress!"
      );
    });

    it("shows empty message when total CVs is 0", () => {
      const stats = createMockStats({ total_cvs: 0 });
      render(<UserStats stats={stats} />);

      expect(screen.getByTestId("stats-empty-message")).toBeInTheDocument();
    });

    it("does not show empty message when has CVs", () => {
      const stats = createMockStats({ total_cvs: 3 });
      render(<UserStats stats={stats} />);

      expect(screen.queryByTestId("stats-empty-message")).not.toBeInTheDocument();
    });
  });

  describe("Score Colors", () => {
    it("applies green color for high average score (80+)", () => {
      const stats = createMockStats({ average_score: 85 });
      render(<UserStats stats={stats} />);

      const averageCard = screen.getByTestId("stat-average-score");
      const icon = averageCard.querySelector(".rounded-full");
      expect(icon).toHaveClass("bg-green-100");
    });

    it("applies yellow color for medium average score (60-79)", () => {
      const stats = createMockStats({ average_score: 70 });
      render(<UserStats stats={stats} />);

      const averageCard = screen.getByTestId("stat-average-score");
      const icon = averageCard.querySelector(".rounded-full");
      expect(icon).toHaveClass("bg-yellow-100");
    });

    it("applies red color for low average score (<60)", () => {
      const stats = createMockStats({ average_score: 45 });
      render(<UserStats stats={stats} />);

      const averageCard = screen.getByTestId("stat-average-score");
      const icon = averageCard.querySelector(".rounded-full");
      expect(icon).toHaveClass("bg-red-100");
    });

    it("applies gray color when score is null", () => {
      const stats = createMockStats({ average_score: null });
      render(<UserStats stats={stats} />);

      const averageCard = screen.getByTestId("stat-average-score");
      const icon = averageCard.querySelector(".rounded-full");
      expect(icon).toHaveClass("bg-gray-100");
    });
  });

  describe("Card Structure", () => {
    it("renders the user stats container", () => {
      const stats = createMockStats();
      render(<UserStats stats={stats} />);

      expect(screen.getByTestId("user-stats")).toBeInTheDocument();
    });
  });
});
