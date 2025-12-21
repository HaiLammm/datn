import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import { CVHistoryList } from "./CVHistoryList";
import { CVWithStatus } from "@datn/shared-types";

// Mock the CVHistoryCard component
jest.mock("./CVHistoryCard", () => ({
  CVHistoryCard: ({ cv }: { cv: CVWithStatus }) => (
    <div data-testid="cv-history-card">{cv.filename}</div>
  ),
}));

// Mock the DeleteModeContext
const mockResetConfirmation = jest.fn();
jest.mock("@/features/cv/context/DeleteModeContext", () => ({
  useDeleteMode: () => ({
    skipConfirmation: false,
    resetConfirmation: mockResetConfirmation,
  }),
}));

// Helper to create mock CV data
function createMockCV(overrides: Partial<CVWithStatus> = {}): CVWithStatus {
  return {
    id: `cv-${Math.random().toString(36).substr(2, 9)}`,
    user_id: 1,
    filename: "resume.pdf",
    file_path: "/uploads/resume.pdf",
    uploaded_at: "2025-12-15T10:30:00Z",
    is_active: true,
    is_public: false,
    analysis_status: "COMPLETED",
    quality_score: 85,
    ...overrides,
  };
}

describe("CVHistoryList", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("CV Count Header", () => {
    it("shows correct CV count in header for single CV", () => {
      const cvs = [createMockCV()];
      render(<CVHistoryList cvs={cvs} />);

      expect(screen.getByTestId("cv-count")).toHaveTextContent("Your CVs (1 total)");
    });

    it("shows correct CV count in header for multiple CVs", () => {
      const cvs = [
        createMockCV({ filename: "cv1.pdf" }),
        createMockCV({ filename: "cv2.pdf" }),
        createMockCV({ filename: "cv3.pdf" }),
      ];
      render(<CVHistoryList cvs={cvs} />);

      expect(screen.getByTestId("cv-count")).toHaveTextContent("Your CVs (3 total)");
    });
  });

  describe("Rendering CV Cards", () => {
    it("renders all CV cards", () => {
      const cvs = [
        createMockCV({ filename: "resume-v1.pdf" }),
        createMockCV({ filename: "resume-v2.pdf" }),
        createMockCV({ filename: "resume-v3.pdf" }),
      ];
      render(<CVHistoryList cvs={cvs} />);

      const cards = screen.getAllByTestId("cv-history-card");
      expect(cards).toHaveLength(3);
    });

    it("renders CV cards with correct filenames", () => {
      const cvs = [
        createMockCV({ filename: "first-cv.pdf" }),
        createMockCV({ filename: "second-cv.pdf" }),
      ];
      render(<CVHistoryList cvs={cvs} />);

      expect(screen.getByText("first-cv.pdf")).toBeInTheDocument();
      expect(screen.getByText("second-cv.pdf")).toBeInTheDocument();
    });
  });

  describe("Empty State", () => {
    it("shows empty state when cvs.length === 0", () => {
      render(<CVHistoryList cvs={[]} />);

      expect(screen.getByTestId("no-cvs-empty-state")).toBeInTheDocument();
      expect(screen.getByText("No CVs uploaded yet")).toBeInTheDocument();
    });

    it("empty state has upload button with correct link /cvs/upload", () => {
      render(<CVHistoryList cvs={[]} />);

      const uploadLink = screen.getByTestId("upload-first-cv-link");
      expect(uploadLink).toHaveAttribute("href", "/cvs/upload");
      expect(uploadLink).toHaveTextContent("Upload Your First CV");
    });

    it("empty state shows helpful message", () => {
      render(<CVHistoryList cvs={[]} />);

      expect(
        screen.getByText("Get started by uploading your first CV for analysis.")
      ).toBeInTheDocument();
    });
  });

  describe("Grid Layout", () => {
    it("grid layout classes applied correctly", () => {
      const cvs = [createMockCV()];
      render(<CVHistoryList cvs={cvs} />);

      const grid = screen.getByTestId("cv-grid");
      expect(grid).toHaveClass("grid");
      expect(grid).toHaveClass("grid-cols-1");
      expect(grid).toHaveClass("md:grid-cols-2");
      expect(grid).toHaveClass("lg:grid-cols-3");
      expect(grid).toHaveClass("gap-6");
    });
  });

  describe("Delete Mode Banner", () => {
    it("does not show delete mode banner when skipConfirmation is false", () => {
      const cvs = [createMockCV()];
      render(<CVHistoryList cvs={cvs} />);

      expect(
        screen.queryByText(/Quick delete mode is enabled/i)
      ).not.toBeInTheDocument();
    });
  });
});

// Note: Testing skipConfirmation=true requires a different approach
// using a test wrapper that provides the context value directly.
// The current mock pattern doesn't support dynamic mock values.
