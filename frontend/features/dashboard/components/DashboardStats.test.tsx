import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import { DashboardStats, calculateStats } from "./DashboardStats";
import { CVWithStatus } from "@datn/shared-types";

// Helper to create mock CV data
function createMockCV(overrides: Partial<CVWithStatus> = {}): CVWithStatus {
  return {
    id: "test-cv-id-123",
    user_id: 1,
    filename: "my-resume.pdf",
    file_path: "/uploads/my-resume.pdf",
    uploaded_at: "2025-12-15T10:30:00Z",
    is_active: true,
    is_public: false,
    analysis_status: "COMPLETED",
    quality_score: 85,
    ...overrides,
  };
}

describe("DashboardStats", () => {
  describe("Total CVs", () => {
    it("displays correct total CV count", () => {
      const cvs = [
        createMockCV({ id: "cv-1" }),
        createMockCV({ id: "cv-2" }),
        createMockCV({ id: "cv-3" }),
      ];

      render(<DashboardStats cvs={cvs} />);

      expect(screen.getByTestId("total-cvs-value")).toHaveTextContent("3");
    });

    it("displays 0 for empty CV list", () => {
      render(<DashboardStats cvs={[]} />);

      expect(screen.getByTestId("total-cvs-value")).toHaveTextContent("0");
    });
  });

  describe("Average Score", () => {
    it("calculates and displays average score correctly", () => {
      const cvs = [
        createMockCV({ id: "cv-1", quality_score: 80 }),
        createMockCV({ id: "cv-2", quality_score: 70 }),
        createMockCV({ id: "cv-3", quality_score: 90 }),
      ];

      render(<DashboardStats cvs={cvs} />);

      // Average: (80 + 70 + 90) / 3 = 80
      expect(screen.getByTestId("average-score-value")).toHaveTextContent("80");
    });

    it("rounds average score to nearest integer", () => {
      const cvs = [
        createMockCV({ id: "cv-1", quality_score: 81 }),
        createMockCV({ id: "cv-2", quality_score: 72 }),
      ];

      render(<DashboardStats cvs={cvs} />);

      // Average: (81 + 72) / 2 = 76.5 -> rounded to 77
      expect(screen.getByTestId("average-score-value")).toHaveTextContent("77");
    });

    it("shows N/A when no completed CVs", () => {
      render(<DashboardStats cvs={[]} />);

      expect(screen.getByTestId("average-score-value")).toHaveTextContent("N/A");
    });

    it("excludes CVs with null scores from average calculation", () => {
      const cvs = [
        createMockCV({ id: "cv-1", quality_score: 80 }),
        createMockCV({ id: "cv-2", quality_score: null, analysis_status: "PENDING" }),
        createMockCV({ id: "cv-3", quality_score: 60 }),
      ];

      render(<DashboardStats cvs={cvs} />);

      // Only cv-1 (80) and cv-3 (60) counted, average = 70
      expect(screen.getByTestId("average-score-value")).toHaveTextContent("70");
    });

    it("shows N/A when all CVs have null scores", () => {
      const cvs = [
        createMockCV({ id: "cv-1", quality_score: null, analysis_status: "PENDING" }),
        createMockCV({ id: "cv-2", quality_score: null, analysis_status: "PROCESSING" }),
      ];

      render(<DashboardStats cvs={cvs} />);

      expect(screen.getByTestId("average-score-value")).toHaveTextContent("N/A");
    });
  });

  describe("Best Score", () => {
    it("displays best (highest) score correctly", () => {
      const cvs = [
        createMockCV({ id: "cv-1", quality_score: 65 }),
        createMockCV({ id: "cv-2", quality_score: 92 }),
        createMockCV({ id: "cv-3", quality_score: 78 }),
      ];

      render(<DashboardStats cvs={cvs} />);

      expect(screen.getByTestId("best-score-value")).toHaveTextContent("92");
    });

    it("shows N/A when no CVs have scores", () => {
      render(<DashboardStats cvs={[]} />);

      expect(screen.getByTestId("best-score-value")).toHaveTextContent("N/A");
    });

    it("handles single CV correctly", () => {
      const cvs = [createMockCV({ quality_score: 85 })];

      render(<DashboardStats cvs={cvs} />);

      expect(screen.getByTestId("best-score-value")).toHaveTextContent("85");
    });
  });

  describe("Empty State", () => {
    it("shows encouraging message when no CVs", () => {
      render(<DashboardStats cvs={[]} />);

      expect(screen.getByTestId("stats-empty-message")).toHaveTextContent(
        "Upload your first CV to start tracking your progress!"
      );
    });

    it("does not show empty message when CVs exist", () => {
      const cvs = [createMockCV()];

      render(<DashboardStats cvs={cvs} />);

      expect(screen.queryByTestId("stats-empty-message")).not.toBeInTheDocument();
    });
  });

  describe("Score Colors", () => {
    it("applies green color for high average score (80+)", () => {
      const cvs = [
        createMockCV({ id: "cv-1", quality_score: 90 }),
        createMockCV({ id: "cv-2", quality_score: 85 }),
      ];

      render(<DashboardStats cvs={cvs} />);

      const averageCard = screen.getByTestId("stat-average-score");
      const icon = averageCard.querySelector(".rounded-full");
      expect(icon).toHaveClass("bg-green-100");
    });

    it("applies yellow color for medium average score (60-79)", () => {
      const cvs = [
        createMockCV({ id: "cv-1", quality_score: 70 }),
        createMockCV({ id: "cv-2", quality_score: 65 }),
      ];

      render(<DashboardStats cvs={cvs} />);

      const averageCard = screen.getByTestId("stat-average-score");
      const icon = averageCard.querySelector(".rounded-full");
      expect(icon).toHaveClass("bg-yellow-100");
    });

    it("applies red color for low average score (<60)", () => {
      const cvs = [
        createMockCV({ id: "cv-1", quality_score: 45 }),
        createMockCV({ id: "cv-2", quality_score: 50 }),
      ];

      render(<DashboardStats cvs={cvs} />);

      const averageCard = screen.getByTestId("stat-average-score");
      const icon = averageCard.querySelector(".rounded-full");
      expect(icon).toHaveClass("bg-red-100");
    });

    it("applies gray color when no scores available", () => {
      render(<DashboardStats cvs={[]} />);

      const averageCard = screen.getByTestId("stat-average-score");
      const icon = averageCard.querySelector(".rounded-full");
      expect(icon).toHaveClass("bg-gray-100");
    });
  });
});

describe("calculateStats", () => {
  it("returns correct stats for CVs with scores", () => {
    const cvs = [
      createMockCV({ id: "cv-1", quality_score: 80 }),
      createMockCV({ id: "cv-2", quality_score: 70 }),
      createMockCV({ id: "cv-3", quality_score: 90 }),
    ];

    const stats = calculateStats(cvs);

    expect(stats.totalCvs).toBe(3);
    expect(stats.averageScore).toBe(80);
    expect(stats.bestScore).toBe(90);
  });

  it("returns null scores for empty CV list", () => {
    const stats = calculateStats([]);

    expect(stats.totalCvs).toBe(0);
    expect(stats.averageScore).toBeNull();
    expect(stats.bestScore).toBeNull();
  });

  it("excludes null scores from calculations", () => {
    const cvs = [
      createMockCV({ id: "cv-1", quality_score: 80 }),
      createMockCV({ id: "cv-2", quality_score: null }),
      createMockCV({ id: "cv-3", quality_score: 60 }),
    ];

    const stats = calculateStats(cvs);

    expect(stats.totalCvs).toBe(3);
    expect(stats.averageScore).toBe(70);
    expect(stats.bestScore).toBe(80);
  });
});
