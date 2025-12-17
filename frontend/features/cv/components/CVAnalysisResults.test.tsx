import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import { CVAnalysisResults } from "./CVAnalysisResults";
import * as actions from "../actions";
import { CVAnalysis } from "@datn/shared-types";

// Mock the actions
jest.mock("../actions", () => ({
  getCVAnalysis: jest.fn(),
  getCVAnalysisStatus: jest.fn(),
}));

const mockCompletedAnalysis: CVAnalysis = {
  id: "analysis-1",
  cv_id: "cv-1",
  status: "COMPLETED",
  ai_score: 85,
  ai_summary: "Experienced software engineer with strong technical skills.",
  ai_feedback: {
    criteria: { completeness: 80, experience: 90, skills: 85, professionalism: 75 },
    experience_breakdown: { total_years: 5, key_roles: ["Engineer"], industries: ["Tech"] },
    strengths: ["Strong coding skills", "Good communication"],
    improvements: ["Add more projects"],
    formatting_feedback: ["Use bullet points"],
    ats_hints: ["Include relevant keywords"],
  },
  extracted_skills: ["Python", "React", "FastAPI"],
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z",
  experience_breakdown: { total_years: 5, key_roles: ["Engineer"], industries: ["Tech"] },
  formatting_feedback: ["Use bullet points"],
  ats_hints: ["Include relevant keywords"],
  strengths: ["Strong coding skills", "Good communication"],
  improvements: ["Add more projects"],
  criteria_explanation: { completeness: 80, experience: 90, skills: 85, professionalism: 75 },
};

const mockProcessingAnalysis: CVAnalysis = {
  ...mockCompletedAnalysis,
  status: "PROCESSING",
  ai_score: null,
  ai_summary: null,
};

const mockFailedAnalysis: CVAnalysis = {
  ...mockCompletedAnalysis,
  status: "FAILED",
};

describe("CVAnalysisResults", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders loading state for PROCESSING status", () => {
    render(<CVAnalysisResults cvId="cv-1" initialAnalysis={mockProcessingAnalysis} />);

    expect(screen.getByText(/Analyzing your CV/i)).toBeInTheDocument();
  });

  it("renders loading state for PENDING status", () => {
    const pendingAnalysis = { ...mockProcessingAnalysis, status: "PENDING" as const };
    render(<CVAnalysisResults cvId="cv-1" initialAnalysis={pendingAnalysis} />);

    expect(screen.getByText(/Analyzing your CV/i)).toBeInTheDocument();
  });

  it("renders failed state correctly", () => {
    render(<CVAnalysisResults cvId="cv-1" initialAnalysis={mockFailedAnalysis} />);

    expect(screen.getByText(/Analysis Failed/i)).toBeInTheDocument();
    expect(screen.getByText(/error while analyzing your CV/i)).toBeInTheDocument();
  });

  it("renders completed analysis with score", () => {
    render(<CVAnalysisResults cvId="cv-1" initialAnalysis={mockCompletedAnalysis} />);

    expect(screen.getByText(/CV Quality Score/i)).toBeInTheDocument();
    // Score 85 appears in both gauge and criteria - use getAllByText
    expect(screen.getAllByText("85").length).toBeGreaterThanOrEqual(1);
  });

  it("renders professional summary", () => {
    render(<CVAnalysisResults cvId="cv-1" initialAnalysis={mockCompletedAnalysis} />);

    expect(screen.getByText(/Professional Summary/i)).toBeInTheDocument();
    expect(screen.getByText(/Experienced software engineer/i)).toBeInTheDocument();
  });

  it("renders extracted skills", () => {
    render(<CVAnalysisResults cvId="cv-1" initialAnalysis={mockCompletedAnalysis} />);

    expect(screen.getByText(/Extracted Skills/i)).toBeInTheDocument();
    expect(screen.getByText("Python")).toBeInTheDocument();
    expect(screen.getByText("React")).toBeInTheDocument();
    expect(screen.getByText("FastAPI")).toBeInTheDocument();
  });

  it("renders criteria breakdown", () => {
    render(<CVAnalysisResults cvId="cv-1" initialAnalysis={mockCompletedAnalysis} />);

    expect(screen.getByText("Completeness")).toBeInTheDocument();
    expect(screen.getByText("Experience")).toBeInTheDocument();
    expect(screen.getByText("Skills")).toBeInTheDocument();
    expect(screen.getByText("Professionalism")).toBeInTheDocument();
  });

  it("renders experience overview section", () => {
    render(<CVAnalysisResults cvId="cv-1" initialAnalysis={mockCompletedAnalysis} />);

    expect(screen.getByText(/Experience Overview/i)).toBeInTheDocument();
    expect(screen.getByText(/Years of Experience/i)).toBeInTheDocument();
  });

  it("renders feedback section with strengths and improvements", () => {
    render(<CVAnalysisResults cvId="cv-1" initialAnalysis={mockCompletedAnalysis} />);

    expect(screen.getByText(/Detailed Feedback/i)).toBeInTheDocument();
    expect(screen.getByText(/Key Strengths/i)).toBeInTheDocument();
    expect(screen.getByText(/Areas for Improvement/i)).toBeInTheDocument();
  });

  it("polls for status when analysis is processing", async () => {
    (actions.getCVAnalysisStatus as jest.Mock).mockResolvedValue({ status: "COMPLETED" });
    (actions.getCVAnalysis as jest.Mock).mockResolvedValue(mockCompletedAnalysis);

    jest.useFakeTimers();

    render(<CVAnalysisResults cvId="cv-1" initialAnalysis={mockProcessingAnalysis} />);

    // Fast-forward timers
    jest.advanceTimersByTime(3000);

    await waitFor(() => {
      expect(actions.getCVAnalysisStatus).toHaveBeenCalledWith("cv-1");
    });

    jest.useRealTimers();
  });

  it("stops polling when status changes to COMPLETED", async () => {
    (actions.getCVAnalysisStatus as jest.Mock).mockResolvedValue({ status: "COMPLETED" });
    (actions.getCVAnalysis as jest.Mock).mockResolvedValue(mockCompletedAnalysis);

    jest.useFakeTimers();

    render(<CVAnalysisResults cvId="cv-1" initialAnalysis={mockProcessingAnalysis} />);

    // Fast-forward to trigger polling
    jest.advanceTimersByTime(3000);

    await waitFor(() => {
      expect(actions.getCVAnalysis).toHaveBeenCalledWith("cv-1");
    });

    // After getting COMPLETED status, polling should stop
    jest.advanceTimersByTime(6000);

    // Should not have made additional calls
    expect(actions.getCVAnalysisStatus).toHaveBeenCalledTimes(1);

    jest.useRealTimers();
  });

  it("handles failed status during polling", async () => {
    (actions.getCVAnalysisStatus as jest.Mock).mockResolvedValue({ status: "FAILED" });

    jest.useFakeTimers();

    render(
      <CVAnalysisResults cvId="cv-1" initialAnalysis={mockProcessingAnalysis} />
    );

    // Fast-forward timers
    jest.advanceTimersByTime(3000);

    await waitFor(() => {
      expect(actions.getCVAnalysisStatus).toHaveBeenCalledWith("cv-1");
    });

    jest.useRealTimers();
  });

  // Story 5.6: Skill Breakdown UI Integration Tests
  describe("Skill Analysis Integration (Story 5.6)", () => {
    const mockAnalysisWithSkillBreakdown: CVAnalysis = {
      ...mockCompletedAnalysis,
      skill_breakdown: {
        completeness_score: 5,
        categorization_score: 4,
        evidence_score: 4,
        market_relevance_score: 4,
        total_score: 17
      },
      skill_categories: {
        programming_languages: ["Python", "JavaScript"],
        frameworks: ["React", "FastAPI"],
        databases: ["PostgreSQL"],
        devops: ["Docker"],
        soft_skills: ["Teamwork"],
        other: []
      },
      skill_recommendations: [
        "Consider learning Kubernetes for container orchestration",
        "Add more cloud skills like AWS or GCP"
      ]
    };

    it("renders Skill Analysis section when skill_breakdown is present", () => {
      render(<CVAnalysisResults cvId="cv-1" initialAnalysis={mockAnalysisWithSkillBreakdown} />);

      expect(screen.getByText(/Skill Analysis/i)).toBeInTheDocument();
      expect(screen.getByText(/Skill Score/i)).toBeInTheDocument();
      expect(screen.getByText("17")).toBeInTheDocument(); // total score
    });

    it("renders SkillCategoriesDisplay when skill_categories is present", () => {
      render(<CVAnalysisResults cvId="cv-1" initialAnalysis={mockAnalysisWithSkillBreakdown} />);

      expect(screen.getByText(/Skills Breakdown/i)).toBeInTheDocument();
      expect(screen.getByText(/Programming Languages/)).toBeInTheDocument();
      expect(screen.getByText("Python")).toBeInTheDocument();
      expect(screen.getByText("React")).toBeInTheDocument();
    });

    it("falls back to SkillCloud when skill_categories is absent", () => {
      render(<CVAnalysisResults cvId="cv-1" initialAnalysis={mockCompletedAnalysis} />);

      expect(screen.getByText(/Extracted Skills/i)).toBeInTheDocument();
      expect(screen.getByText("Python")).toBeInTheDocument();
      expect(screen.queryByText(/Skills Breakdown/i)).not.toBeInTheDocument();
    });

    it("renders Skill Recommendations section when recommendations exist", () => {
      render(<CVAnalysisResults cvId="cv-1" initialAnalysis={mockAnalysisWithSkillBreakdown} />);

      expect(screen.getByText(/Skill Development Recommendations/i)).toBeInTheDocument();
      expect(screen.getByText(/Consider learning Kubernetes/)).toBeInTheDocument();
      expect(screen.getByText(/Add more cloud skills/)).toBeInTheDocument();
    });

    it("does not render Recommendations section when array is empty", () => {
      const analysisWithEmptyRecommendations: CVAnalysis = {
        ...mockAnalysisWithSkillBreakdown,
        skill_recommendations: []
      };

      render(<CVAnalysisResults cvId="cv-1" initialAnalysis={analysisWithEmptyRecommendations} />);

      expect(screen.queryByText(/Skill Development Recommendations/i)).not.toBeInTheDocument();
    });

    it("does not render Recommendations section when null", () => {
      const analysisWithNullRecommendations: CVAnalysis = {
        ...mockAnalysisWithSkillBreakdown,
        skill_recommendations: null
      };

      render(<CVAnalysisResults cvId="cv-1" initialAnalysis={analysisWithNullRecommendations} />);

      expect(screen.queryByText(/Skill Development Recommendations/i)).not.toBeInTheDocument();
    });

    it("does not render Skill Analysis section when skill_breakdown is null", () => {
      const analysisWithoutSkillBreakdown: CVAnalysis = {
        ...mockCompletedAnalysis,
        skill_breakdown: null
      };

      render(<CVAnalysisResults cvId="cv-1" initialAnalysis={analysisWithoutSkillBreakdown} />);

      expect(screen.queryByText(/Skill Analysis/i)).not.toBeInTheDocument();
    });

    it("maintains existing UI sections when new skill fields are present", () => {
      render(<CVAnalysisResults cvId="cv-1" initialAnalysis={mockAnalysisWithSkillBreakdown} />);

      // Existing sections should still be present
      expect(screen.getByText(/CV Quality Score/i)).toBeInTheDocument();
      expect(screen.getByText(/Professional Summary/i)).toBeInTheDocument();
      expect(screen.getByText(/Experience Overview/i)).toBeInTheDocument();
      expect(screen.getByText(/Detailed Feedback/i)).toBeInTheDocument();
    });
  });
});
