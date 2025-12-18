import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import { JDList } from "./JDList";
import { JobDescriptionResponse } from "@datn/shared-types";

// Mock next/link
jest.mock("next/link", () => {
  const MockLink = ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  );
  MockLink.displayName = "MockLink";
  return MockLink;
});

// Mock next/cache to prevent TextEncoder error
jest.mock("next/cache", () => ({
  revalidatePath: jest.fn(),
  revalidateTag: jest.fn(),
}));

// Mock the actions module to prevent importing next/cache transitively
jest.mock("../actions", () => ({
  deleteJDAction: jest.fn().mockResolvedValue({ success: true, message: "Deleted" }),
}));

const mockJDs: JobDescriptionResponse[] = [
  {
    id: "jd-1",
    title: "Python Developer",
    description: "Looking for Python dev...",
    location_type: "remote",
    user_id: 1,
    uploaded_at: "2024-01-15T10:00:00Z",
    is_active: true,
    parse_status: "completed",
  },
  {
    id: "jd-2",
    title: "React Developer",
    description: "Looking for React dev...",
    location_type: "hybrid",
    user_id: 1,
    uploaded_at: "2024-01-16T10:00:00Z",
    is_active: true,
    parse_status: "pending",
  },
];

describe("JDList", () => {
  it("renders list of JD cards", () => {
    render(<JDList initialJDs={mockJDs} />);
    
    expect(screen.getByText("Python Developer")).toBeInTheDocument();
    expect(screen.getByText("React Developer")).toBeInTheDocument();
  });

  it("shows empty state message when no JDs", () => {
    render(<JDList initialJDs={[]} />);
    
    expect(screen.getByText("Chưa có Job Description nào")).toBeInTheDocument();
    expect(screen.getByText(/Hãy tạo JD đầu tiên/i)).toBeInTheDocument();
    expect(screen.getByText("Tạo JD đầu tiên")).toBeInTheDocument();
  });

  it("links to upload page in empty state", () => {
    render(<JDList initialJDs={[]} />);
    
    const createLink = screen.getByText("Tạo JD đầu tiên");
    expect(createLink.closest("a")).toHaveAttribute("href", "/jobs/jd/upload");
  });
});
