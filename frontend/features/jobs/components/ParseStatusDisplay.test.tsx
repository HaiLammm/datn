import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import { ParseStatusDisplay } from "./ParseStatusDisplay";
import * as actions from "../actions";

// Mock the server action
jest.mock("../actions", () => ({
  getJDParseStatusAction: jest.fn(),
}));

describe("ParseStatusDisplay", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it("shows pending/processing status with loading state", () => {
    render(
      <ParseStatusDisplay
        jdId="test-123"
        initialStatus="pending"
      />
    );
    
    expect(screen.getByText("Chờ xử lý...")).toBeInTheDocument();
  });

  it("shows processing status", () => {
    render(
      <ParseStatusDisplay
        jdId="test-123"
        initialStatus="processing"
      />
    );
    
    expect(screen.getByText("Đang phân tích JD...")).toBeInTheDocument();
  });

  it("shows parsed requirements when completed", () => {
    const parsedRequirements = {
      required_skills: ["Python", "FastAPI"],
      nice_to_have_skills: ["Docker"],
      min_experience_years: 3,
      job_title_normalized: "Python Developer",
      key_responsibilities: ["Build APIs", "Write tests"],
    };

    render(
      <ParseStatusDisplay
        jdId="test-123"
        initialStatus="completed"
        initialParsedRequirements={parsedRequirements}
      />
    );
    
    expect(screen.getByText("Phân tích hoàn tất")).toBeInTheDocument();
    expect(screen.getByText("Python")).toBeInTheDocument();
    expect(screen.getByText("FastAPI")).toBeInTheDocument();
    expect(screen.getByText("Docker")).toBeInTheDocument();
    expect(screen.getByText(/3 năm/i)).toBeInTheDocument();
  });

  it("shows error message when failed", () => {
    render(
      <ParseStatusDisplay
        jdId="test-123"
        initialStatus="failed"
      />
    );
    
    expect(screen.getByText("Phân tích thất bại")).toBeInTheDocument();
  });

  it("renders edit button when status is completed and onEditClick provided", () => {
    const mockOnEdit = jest.fn();
    const parsedRequirements = {
      required_skills: ["Python"],
      nice_to_have_skills: [],
      min_experience_years: null,
      job_title_normalized: null,
      key_responsibilities: [],
    };

    render(
      <ParseStatusDisplay
        jdId="test-123"
        initialStatus="completed"
        initialParsedRequirements={parsedRequirements}
        onEditClick={mockOnEdit}
      />
    );
    
    expect(screen.getByRole("button", { name: /Chỉnh sửa/i })).toBeInTheDocument();
  });

  it("polls for status updates when pending", async () => {
    (actions.getJDParseStatusAction as jest.Mock).mockResolvedValue({
      parse_status: "completed",
      parsed_requirements: {
        required_skills: ["Python"],
        nice_to_have_skills: [],
        min_experience_years: 2,
        job_title_normalized: "Developer",
        key_responsibilities: [],
      },
      parse_error: null,
    });

    render(
      <ParseStatusDisplay
        jdId="test-123"
        initialStatus="pending"
      />
    );

    // Advance timers to trigger polling
    jest.advanceTimersByTime(3000);

    await waitFor(() => {
      expect(actions.getJDParseStatusAction).toHaveBeenCalledWith("test-123");
    });
  });
});
