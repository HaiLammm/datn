import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import { SearchResultList } from "./SearchResultList";
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

const mockResults: SearchResultResponse[] = [
  {
    cv_id: "123e4567-e89b-12d3-a456-426614174001",
    user_id: 1,
    relevance_score: 92,
    matched_skills: ["Python", "AWS"],
    cv_summary: "Senior Python developer with cloud experience",
    filename: "john_doe.pdf",
  },
  {
    cv_id: "123e4567-e89b-12d3-a456-426614174002",
    user_id: 2,
    relevance_score: 78,
    matched_skills: ["Python", "Docker"],
    cv_summary: "Full-stack developer with DevOps skills",
    filename: "jane_smith.pdf",
  },
];

const defaultProps = {
  results: mockResults,
  total: 2,
  loading: false,
  error: null,
  limit: 20,
  offset: 0,
  minScore: 0,
  onPageChange: jest.fn(),
  onPageSizeChange: jest.fn(),
  onMinScoreChange: jest.fn(),
  onRetry: jest.fn(),
};

describe("SearchResultList", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders list of results", () => {
    render(<SearchResultList {...defaultProps} />);

    expect(screen.getByText("john_doe.pdf")).toBeInTheDocument();
    expect(screen.getByText("jane_smith.pdf")).toBeInTheDocument();
  });

  it("shows total count of results", () => {
    render(<SearchResultList {...defaultProps} total={23} />);

    expect(screen.getByText("23")).toBeInTheDocument();
    expect(screen.getByText(/ung vien phu hop/i)).toBeInTheDocument();
  });

  it("shows empty state when no results", () => {
    render(
      <SearchResultList {...defaultProps} results={[]} total={0} />
    );

    expect(screen.getByText(/khong tim thay ung vien phu hop/i)).toBeInTheDocument();
    expect(screen.getByText(/su dung cac tu khoa khac/i)).toBeInTheDocument();
    expect(screen.getByText(/giam diem toi thieu/i)).toBeInTheDocument();
    expect(screen.getByText(/mo rong pham vi ky nang/i)).toBeInTheDocument();
  });

  it("shows loading state with skeleton cards", () => {
    render(<SearchResultList {...defaultProps} loading={true} />);

    const skeletonCards = screen.getAllByTestId("skeleton-card");
    expect(skeletonCards.length).toBe(4);
  });

  it("shows error state with message", () => {
    render(
      <SearchResultList {...defaultProps} error="Search failed" results={[]} total={0} />
    );

    expect(screen.getByText(/co loi xay ra/i)).toBeInTheDocument();
    expect(screen.getByText("Search failed")).toBeInTheDocument();
  });

  it("shows retry button in error state", () => {
    const mockOnRetry = jest.fn();
    render(
      <SearchResultList
        {...defaultProps}
        error="Search failed"
        results={[]}
        total={0}
        onRetry={mockOnRetry}
      />
    );

    const retryButton = screen.getByRole("button", { name: /thu lai/i });
    expect(retryButton).toBeInTheDocument();

    fireEvent.click(retryButton);
    expect(mockOnRetry).toHaveBeenCalled();
  });

  it("shows correct rank numbers for each result", () => {
    render(<SearchResultList {...defaultProps} offset={0} />);

    expect(screen.getByText("#1")).toBeInTheDocument();
    expect(screen.getByText("#2")).toBeInTheDocument();
  });

  it("calculates correct rank when offset is applied", () => {
    render(<SearchResultList {...defaultProps} offset={20} />);

    // First result should be #21, second should be #22
    expect(screen.getByText("#21")).toBeInTheDocument();
    expect(screen.getByText("#22")).toBeInTheDocument();
  });

  it("renders min score filter", () => {
    render(<SearchResultList {...defaultProps} />);

    // MinScoreFilter component should be present (Vietnamese with diacritics)
    expect(screen.getByText(/Điểm tối thiểu/i)).toBeInTheDocument();
  });

  it("renders pagination when there are results", () => {
    render(<SearchResultList {...defaultProps} total={50} />);

    // CandidatePagination should show page info
    expect(screen.getByText(/trang/i)).toBeInTheDocument();
  });

  it("does not render pagination when no results", () => {
    render(<SearchResultList {...defaultProps} results={[]} total={0} />);

    // Should show empty state, not pagination
    expect(screen.queryByText(/trang 1/i)).not.toBeInTheDocument();
  });

  it("has correct ARIA labels for result list", () => {
    render(<SearchResultList {...defaultProps} />);

    const list = screen.getByRole("list", { name: /danh sach ket qua tim kiem/i });
    expect(list).toBeInTheDocument();
  });

  it("shows loading ARIA label when loading", () => {
    render(<SearchResultList {...defaultProps} loading={true} />);

    const loadingList = screen.getByRole("list", { name: /dang tai ket qua/i });
    expect(loadingList).toBeInTheDocument();
  });

  it("links each result to correct CV page", () => {
    render(<SearchResultList {...defaultProps} />);

    const viewButtons = screen.getAllByRole("link", { name: /xem cv/i });
    expect(viewButtons[0]).toHaveAttribute(
      "href",
      "/jobs/candidates/123e4567-e89b-12d3-a456-426614174001"
    );
    expect(viewButtons[1]).toHaveAttribute(
      "href",
      "/jobs/candidates/123e4567-e89b-12d3-a456-426614174002"
    );
  });
});
