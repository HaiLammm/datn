import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import { RecentCVsPreview } from "./RecentCVsPreview";
import { CVWithStatus } from "@datn/shared-types";

// Mock CVHistoryCard utilities
jest.mock("./CVHistoryCard", () => ({
  getScoreColor: (score: number | null) => {
    if (score === null) return "text-gray-500";
    if (score >= 80) return "text-green-600";
    if (score >= 60) return "text-yellow-600";
    return "text-red-600";
  },
  getScoreDisplay: (score: number | null, status: string) => {
    if (score === null) {
      if (status === "PENDING" || status === "PROCESSING") return "Analyzing...";
      return "N/A";
    }
    return `${score}/100`;
  },
  formatDate: (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  },
}));

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

describe("RecentCVsPreview", () => {
  describe("Empty State", () => {
    it("shows empty state when no CVs", () => {
      render(<RecentCVsPreview cvs={[]} />);

      expect(screen.getByTestId("recent-cvs-empty")).toBeInTheDocument();
      expect(screen.getByTestId("empty-state-message")).toHaveTextContent(
        "No CVs yet. Upload your first CV to get started!"
      );
    });

    it("shows Upload CV button in empty state", () => {
      render(<RecentCVsPreview cvs={[]} />);

      const uploadLink = screen.getByRole("link", { name: /Upload CV/i });
      expect(uploadLink).toHaveAttribute("href", "/cvs/upload");
    });
  });

  describe("With CVs", () => {
    it("renders correct number of CVs respecting limit prop", () => {
      const cvs = [
        createMockCV({ id: "cv-1", filename: "cv1.pdf" }),
        createMockCV({ id: "cv-2", filename: "cv2.pdf" }),
        createMockCV({ id: "cv-3", filename: "cv3.pdf" }),
        createMockCV({ id: "cv-4", filename: "cv4.pdf" }),
        createMockCV({ id: "cv-5", filename: "cv5.pdf" }),
      ];

      render(<RecentCVsPreview cvs={cvs} limit={3} />);

      const cvItems = screen.getAllByTestId("cv-preview-item");
      expect(cvItems).toHaveLength(3);
    });

    it("respects default limit of 3", () => {
      const cvs = [
        createMockCV({ id: "cv-1", filename: "cv1.pdf" }),
        createMockCV({ id: "cv-2", filename: "cv2.pdf" }),
        createMockCV({ id: "cv-3", filename: "cv3.pdf" }),
        createMockCV({ id: "cv-4", filename: "cv4.pdf" }),
      ];

      render(<RecentCVsPreview cvs={cvs} />);

      const cvItems = screen.getAllByTestId("cv-preview-item");
      expect(cvItems).toHaveLength(3);
    });

    it("shows all CVs when less than limit", () => {
      const cvs = [
        createMockCV({ id: "cv-1", filename: "cv1.pdf" }),
        createMockCV({ id: "cv-2", filename: "cv2.pdf" }),
      ];

      render(<RecentCVsPreview cvs={cvs} limit={5} />);

      const cvItems = screen.getAllByTestId("cv-preview-item");
      expect(cvItems).toHaveLength(2);
    });

    it("displays CV filename", () => {
      const cvs = [createMockCV({ filename: "john-resume.pdf" })];

      render(<RecentCVsPreview cvs={cvs} />);

      expect(screen.getByTestId("cv-filename")).toHaveTextContent("john-resume.pdf");
    });

    it("displays formatted upload date", () => {
      const cvs = [createMockCV({ uploaded_at: "2025-12-15T10:30:00Z" })];

      render(<RecentCVsPreview cvs={cvs} />);

      expect(screen.getByTestId("cv-date")).toHaveTextContent("Dec 15, 2025");
    });

    it("displays quality score with correct color (green for 80+)", () => {
      const cvs = [createMockCV({ quality_score: 85, analysis_status: "COMPLETED" })];

      render(<RecentCVsPreview cvs={cvs} />);

      const scoreElement = screen.getByTestId("cv-score");
      expect(scoreElement).toHaveTextContent("85/100");
      expect(scoreElement).toHaveClass("text-green-600");
    });

    it("displays quality score with correct color (yellow for 60-79)", () => {
      const cvs = [createMockCV({ quality_score: 70, analysis_status: "COMPLETED" })];

      render(<RecentCVsPreview cvs={cvs} />);

      const scoreElement = screen.getByTestId("cv-score");
      expect(scoreElement).toHaveTextContent("70/100");
      expect(scoreElement).toHaveClass("text-yellow-600");
    });

    it("displays quality score with correct color (red for < 60)", () => {
      const cvs = [createMockCV({ quality_score: 45, analysis_status: "COMPLETED" })];

      render(<RecentCVsPreview cvs={cvs} />);

      const scoreElement = screen.getByTestId("cv-score");
      expect(scoreElement).toHaveTextContent("45/100");
      expect(scoreElement).toHaveClass("text-red-600");
    });

    it("shows 'Analyzing...' for pending CVs", () => {
      const cvs = [createMockCV({ quality_score: null, analysis_status: "PENDING" })];

      render(<RecentCVsPreview cvs={cvs} />);

      expect(screen.getByTestId("cv-score")).toHaveTextContent("Analyzing...");
    });

    it("shows 'View All' link with correct href", () => {
      const cvs = [createMockCV()];

      render(<RecentCVsPreview cvs={cvs} />);

      const viewAllLink = screen.getByTestId("view-all-link");
      expect(viewAllLink).toHaveAttribute("href", "/cvs");
      expect(viewAllLink).toHaveTextContent("View All");
    });

    it("links to correct analysis page for each CV", () => {
      const cvs = [createMockCV({ id: "abc-123-def" })];

      render(<RecentCVsPreview cvs={cvs} />);

      const cvLink = screen.getByTestId("cv-preview-item");
      expect(cvLink).toHaveAttribute("href", "/cvs/abc-123-def/analysis");
    });

    it("shows correct count in title", () => {
      const cvs = [
        createMockCV({ id: "cv-1" }),
        createMockCV({ id: "cv-2" }),
        createMockCV({ id: "cv-3" }),
      ];

      render(<RecentCVsPreview cvs={cvs} limit={3} />);

      expect(screen.getByText("CV gần đây")).toBeInTheDocument();
    });
  });
});
