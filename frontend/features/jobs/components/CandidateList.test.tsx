import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import { CandidateList } from "./CandidateList";
import { RankedCandidateListResponse } from "@datn/shared-types";

// Mock next/link
jest.mock("next/link", () => {
  const MockLink = ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  );
  MockLink.displayName = "MockLink";
  return MockLink;
});

// Mock server actions
jest.mock("../actions", () => ({
  getCandidatesAction: jest.fn(),
}));

const mockInitialData: RankedCandidateListResponse = {
  items: [
    {
      cv_id: "cv-1",
      user_id: 1,
      match_score: 85,
      breakdown: {
        matched_skills: ["Python", "FastAPI"],
        missing_skills: ["Kubernetes"],
        extra_skills: ["Docker"],
        skill_score: 55,
        experience_score: 30,
        experience_years: 4,
      },
      cv_summary: "Senior Python developer",
      filename: "john_doe.pdf",
    },
    {
      cv_id: "cv-2",
      user_id: 2,
      match_score: 70,
      breakdown: {
        matched_skills: ["Python"],
        missing_skills: ["FastAPI", "Kubernetes"],
        extra_skills: [],
        skill_score: 40,
        experience_score: 30,
        experience_years: 5,
      },
      cv_summary: "Mid-level developer",
      filename: "jane_smith.pdf",
    },
  ],
  total: 2,
  limit: 20,
  offset: 0,
};

describe("CandidateList", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders list of candidates from initial data", () => {
    render(<CandidateList jdId="jd-123" initialData={mockInitialData} />);
    
    expect(screen.getByText("john_doe.pdf")).toBeInTheDocument();
    expect(screen.getByText("jane_smith.pdf")).toBeInTheDocument();
  });

  it("shows correct rank numbers", () => {
    render(<CandidateList jdId="jd-123" initialData={mockInitialData} />);
    
    expect(screen.getByText("#1")).toBeInTheDocument();
    expect(screen.getByText("#2")).toBeInTheDocument();
  });

  it("shows empty state when no candidates", () => {
    const emptyData: RankedCandidateListResponse = {
      items: [],
      total: 0,
      limit: 20,
      offset: 0,
    };
    render(<CandidateList jdId="jd-123" initialData={emptyData} />);
    
    expect(screen.getByText("Không tìm thấy ứng viên phù hợp")).toBeInTheDocument();
  });

  it("shows pagination info", () => {
    render(<CandidateList jdId="jd-123" initialData={mockInitialData} />);
    
    expect(screen.getByText(/Hiển thị 1-2 của 2 ứng viên/)).toBeInTheDocument();
  });

  it("displays min score filter", () => {
    render(<CandidateList jdId="jd-123" initialData={mockInitialData} />);
    
    expect(screen.getByText(/Điểm tối thiểu:/)).toBeInTheDocument();
  });

  it("shows loading state when no initial data", async () => {
    const { getCandidatesAction } = require("../actions");
    getCandidatesAction.mockImplementation(() => new Promise(() => {})); // Never resolves
    
    render(<CandidateList jdId="jd-123" />);
    
    expect(screen.getByText("Đang tải danh sách ứng viên...")).toBeInTheDocument();
  });

  it("shows error state with retry button", async () => {
    const { getCandidatesAction } = require("../actions");
    getCandidatesAction.mockResolvedValueOnce(null);
    
    render(<CandidateList jdId="jd-123" />);
    
    await waitFor(() => {
      expect(screen.getByText("Đã xảy ra lỗi")).toBeInTheDocument();
      expect(screen.getByText("Thử lại")).toBeInTheDocument();
    });
  });
});
