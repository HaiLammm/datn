import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import { CVHistoryCard, getScoreColor, getScoreDisplay, formatDate } from "./CVHistoryCard";
import { CVWithStatus } from "@datn/shared-types";

// Mock the child components
jest.mock("./DeleteCVDialog", () => ({
  DeleteCVDialog: ({ filename }: { cvId: string; filename: string }) => (
    <button data-testid="delete-dialog">Delete {filename}</button>
  ),
}));

jest.mock("./CVVisibilityToggle", () => ({
  CVVisibilityToggle: ({ isPublic }: { cvId: string; isPublic: boolean }) => (
    <div data-testid="visibility-toggle">Visibility: {isPublic ? "Public" : "Private"}</div>
  ),
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

describe("CVHistoryCard", () => {
  describe("Rendering", () => {
    it("renders CV filename correctly", () => {
      const cv = createMockCV({ filename: "john-doe-cv.pdf" });
      render(<CVHistoryCard cv={cv} />);
      
      expect(screen.getByText("john-doe-cv.pdf")).toBeInTheDocument();
    });

    it("formats upload date correctly (e.g., 'Dec 15, 2025')", () => {
      const cv = createMockCV({ uploaded_at: "2025-12-15T10:30:00Z" });
      render(<CVHistoryCard cv={cv} />);
      
      expect(screen.getByText(/Uploaded Dec 15, 2025/)).toBeInTheDocument();
    });

    it("renders View Analysis link with correct href", () => {
      const cv = createMockCV({ id: "abc-123-def" });
      render(<CVHistoryCard cv={cv} />);
      
      const link = screen.getByTestId("view-analysis-link");
      expect(link).toHaveAttribute("href", "/cvs/abc-123-def/analysis");
    });

    it("renders visibility toggle", () => {
      const cv = createMockCV({ is_public: true });
      render(<CVHistoryCard cv={cv} />);
      
      expect(screen.getByTestId("visibility-toggle")).toBeInTheDocument();
      expect(screen.getByText("Visibility: Public")).toBeInTheDocument();
    });

    it("renders delete dialog", () => {
      const cv = createMockCV({ filename: "test-cv.pdf" });
      render(<CVHistoryCard cv={cv} />);
      
      expect(screen.getByTestId("delete-dialog")).toBeInTheDocument();
    });
  });

  describe("Quality Score Display", () => {
    it("displays green score text for 80+", () => {
      const cv = createMockCV({ quality_score: 85, analysis_status: "COMPLETED" });
      render(<CVHistoryCard cv={cv} />);
      
      const scoreElement = screen.getByTestId("quality-score");
      expect(scoreElement).toHaveTextContent("85/100");
      expect(scoreElement).toHaveClass("text-green-600");
    });

    it("displays green score text for exactly 80", () => {
      const cv = createMockCV({ quality_score: 80, analysis_status: "COMPLETED" });
      render(<CVHistoryCard cv={cv} />);
      
      const scoreElement = screen.getByTestId("quality-score");
      expect(scoreElement).toHaveTextContent("80/100");
      expect(scoreElement).toHaveClass("text-green-600");
    });

    it("displays yellow score text for 60-79", () => {
      const cv = createMockCV({ quality_score: 70, analysis_status: "COMPLETED" });
      render(<CVHistoryCard cv={cv} />);
      
      const scoreElement = screen.getByTestId("quality-score");
      expect(scoreElement).toHaveTextContent("70/100");
      expect(scoreElement).toHaveClass("text-yellow-600");
    });

    it("displays yellow score text for exactly 60", () => {
      const cv = createMockCV({ quality_score: 60, analysis_status: "COMPLETED" });
      render(<CVHistoryCard cv={cv} />);
      
      const scoreElement = screen.getByTestId("quality-score");
      expect(scoreElement).toHaveTextContent("60/100");
      expect(scoreElement).toHaveClass("text-yellow-600");
    });

    it("displays red score text for < 60", () => {
      const cv = createMockCV({ quality_score: 45, analysis_status: "COMPLETED" });
      render(<CVHistoryCard cv={cv} />);
      
      const scoreElement = screen.getByTestId("quality-score");
      expect(scoreElement).toHaveTextContent("45/100");
      expect(scoreElement).toHaveClass("text-red-600");
    });

    it("displays red score text for 0", () => {
      const cv = createMockCV({ quality_score: 0, analysis_status: "COMPLETED" });
      render(<CVHistoryCard cv={cv} />);
      
      const scoreElement = screen.getByTestId("quality-score");
      expect(scoreElement).toHaveTextContent("0/100");
      expect(scoreElement).toHaveClass("text-red-600");
    });

    it("shows 'Analyzing...' for null score with PENDING status", () => {
      const cv = createMockCV({ quality_score: null, analysis_status: "PENDING" });
      render(<CVHistoryCard cv={cv} />);
      
      const scoreElement = screen.getByTestId("quality-score");
      expect(scoreElement).toHaveTextContent("Analyzing...");
      expect(scoreElement).toHaveClass("text-gray-500");
    });

    it("shows 'Analyzing...' for null score with PROCESSING status", () => {
      const cv = createMockCV({ quality_score: null, analysis_status: "PROCESSING" });
      render(<CVHistoryCard cv={cv} />);
      
      const scoreElement = screen.getByTestId("quality-score");
      expect(scoreElement).toHaveTextContent("Analyzing...");
      expect(scoreElement).toHaveClass("text-gray-500");
    });

    it("shows 'N/A' for null score with FAILED status", () => {
      const cv = createMockCV({ quality_score: null, analysis_status: "FAILED" });
      render(<CVHistoryCard cv={cv} />);
      
      const scoreElement = screen.getByTestId("quality-score");
      expect(scoreElement).toHaveTextContent("N/A");
      expect(scoreElement).toHaveClass("text-gray-500");
    });

    it("handles null score gracefully with COMPLETED status", () => {
      const cv = createMockCV({ quality_score: null, analysis_status: "COMPLETED" });
      render(<CVHistoryCard cv={cv} />);
      
      const scoreElement = screen.getByTestId("quality-score");
      expect(scoreElement).toHaveTextContent("N/A");
      expect(scoreElement).toHaveClass("text-gray-500");
    });
  });

  describe("Status Badge", () => {
    it("shows Completed badge for COMPLETED status", () => {
      const cv = createMockCV({ analysis_status: "COMPLETED" });
      render(<CVHistoryCard cv={cv} />);
      
      expect(screen.getByText("Completed")).toBeInTheDocument();
    });

    it("shows Processing badge for PROCESSING status", () => {
      const cv = createMockCV({ analysis_status: "PROCESSING" });
      render(<CVHistoryCard cv={cv} />);
      
      expect(screen.getByText("Processing")).toBeInTheDocument();
    });

    it("shows Failed badge for FAILED status", () => {
      const cv = createMockCV({ analysis_status: "FAILED" });
      render(<CVHistoryCard cv={cv} />);
      
      expect(screen.getByText("Failed")).toBeInTheDocument();
    });

    it("shows Pending badge for PENDING status", () => {
      const cv = createMockCV({ analysis_status: "PENDING" });
      render(<CVHistoryCard cv={cv} />);
      
      expect(screen.getByText("Pending")).toBeInTheDocument();
    });
  });
});

describe("Utility Functions", () => {
  describe("getScoreColor", () => {
    it("returns gray for null score", () => {
      expect(getScoreColor(null)).toBe("text-gray-500");
    });

    it("returns green for score >= 80", () => {
      expect(getScoreColor(80)).toBe("text-green-600");
      expect(getScoreColor(100)).toBe("text-green-600");
    });

    it("returns yellow for score 60-79", () => {
      expect(getScoreColor(60)).toBe("text-yellow-600");
      expect(getScoreColor(79)).toBe("text-yellow-600");
    });

    it("returns red for score < 60", () => {
      expect(getScoreColor(59)).toBe("text-red-600");
      expect(getScoreColor(0)).toBe("text-red-600");
    });
  });

  describe("getScoreDisplay", () => {
    it("returns 'Analyzing...' for null score with PENDING status", () => {
      expect(getScoreDisplay(null, "PENDING")).toBe("Analyzing...");
    });

    it("returns 'Analyzing...' for null score with PROCESSING status", () => {
      expect(getScoreDisplay(null, "PROCESSING")).toBe("Analyzing...");
    });

    it("returns 'N/A' for null score with FAILED status", () => {
      expect(getScoreDisplay(null, "FAILED")).toBe("N/A");
    });

    it("returns 'N/A' for null score with COMPLETED status", () => {
      expect(getScoreDisplay(null, "COMPLETED")).toBe("N/A");
    });

    it("returns formatted score for valid score", () => {
      expect(getScoreDisplay(85, "COMPLETED")).toBe("85/100");
      expect(getScoreDisplay(0, "COMPLETED")).toBe("0/100");
    });
  });

  describe("formatDate", () => {
    it("formats date correctly to 'Dec 15, 2025' format", () => {
      expect(formatDate("2025-12-15T10:30:00Z")).toBe("Dec 15, 2025");
    });

    it("handles different date formats", () => {
      expect(formatDate("2025-01-01T00:00:00Z")).toBe("Jan 1, 2025");
      expect(formatDate("2024-06-20T15:45:30Z")).toBe("Jun 20, 2024");
    });
  });
});
