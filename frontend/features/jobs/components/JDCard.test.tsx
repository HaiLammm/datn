import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import { JDCard } from "./JDCard";
import { JobDescriptionResponse } from "@datn/shared-types";

// Mock next/link
jest.mock("next/link", () => {
  const MockLink = ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  );
  MockLink.displayName = "MockLink";
  return MockLink;
});

// Mock the server action
jest.mock("../actions", () => ({
  deleteJDAction: jest.fn(),
}));

const mockJD: JobDescriptionResponse = {
  id: "test-jd-123",
  title: "Senior Python Developer",
  description: "Looking for a Python developer...",
  location_type: "remote",
  user_id: 1,
  uploaded_at: "2024-01-15T10:00:00Z",
  is_active: true,
  parse_status: "completed",
  parsed_requirements: {
    required_skills: ["Python", "FastAPI"],
    nice_to_have_skills: ["Docker"],
    min_experience_years: 3,
    job_title_normalized: "Python Developer",
    key_responsibilities: [],
  },
};

describe("JDCard", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders JD info correctly", () => {
    render(<JDCard jd={mockJD} />);
    
    expect(screen.getByText("Senior Python Developer")).toBeInTheDocument();
    expect(screen.getByText("Remote")).toBeInTheDocument();
    expect(screen.getByText("2 kỹ năng")).toBeInTheDocument();
  });

  it("shows correct status badge color for completed", () => {
    render(<JDCard jd={mockJD} />);
    
    const badge = screen.getByText("Hoàn thành");
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass("bg-green-100");
    expect(badge).toHaveClass("text-green-700");
  });

  it("shows correct status badge color for pending", () => {
    const pendingJD = { ...mockJD, parse_status: "pending" as const };
    render(<JDCard jd={pendingJD} />);
    
    const badge = screen.getByText("Chờ xử lý");
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass("bg-yellow-100");
  });

  it("shows correct status badge color for processing", () => {
    const processingJD = { ...mockJD, parse_status: "processing" as const };
    render(<JDCard jd={processingJD} />);
    
    const badge = screen.getByText("Đang phân tích");
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass("bg-blue-100");
  });

  it("shows correct status badge color for failed", () => {
    const failedJD = { ...mockJD, parse_status: "failed" as const };
    render(<JDCard jd={failedJD} />);
    
    const badge = screen.getByText("Thất bại");
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass("bg-red-100");
  });

  it("links to detail page", () => {
    render(<JDCard jd={mockJD} />);
    
    const detailLink = screen.getByText("Xem chi tiết");
    expect(detailLink.closest("a")).toHaveAttribute("href", "/jobs/jd/test-jd-123");
  });

  it("shows delete confirmation dialog when delete button clicked", async () => {
    render(<JDCard jd={mockJD} />);
    
    const deleteButton = screen.getByRole("button", { name: /Xóa JD/i });
    fireEvent.click(deleteButton);
    
    await waitFor(() => {
      expect(screen.getByText("Xác nhận xóa")).toBeInTheDocument();
      expect(screen.getByText(/Bạn có chắc chắn muốn xóa JD/i)).toBeInTheDocument();
    });
  });
});
