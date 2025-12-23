import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import { MatchBreakdown } from "./MatchBreakdown";
import { MatchBreakdownResponse } from "@datn/shared-types";

const createMockBreakdown = (
  overrides: Partial<MatchBreakdownResponse> = {}
): MatchBreakdownResponse => ({
  matched_skills: ["Python", "FastAPI"],
  missing_skills: ["Kubernetes"],
  extra_skills: ["Docker"],
  skill_score: 55,
  experience_score: 25,
  experience_years: 4,
  required_experience_years: 5,
  ...overrides,
});

describe("MatchBreakdown", () => {
  describe("Expand/Collapse behavior", () => {
    it("renders collapsed by default", () => {
      render(<MatchBreakdown breakdown={createMockBreakdown()} />);

      expect(screen.getByText("Chi tiết đánh giá")).toBeInTheDocument();
      expect(screen.queryByText("Kỹ năng phù hợp:")).not.toBeInTheDocument();
    });

    it("expands when clicked", () => {
      render(<MatchBreakdown breakdown={createMockBreakdown()} />);

      fireEvent.click(screen.getByText("Chi tiết đánh giá"));

      expect(screen.getByText("Kỹ năng phù hợp:")).toBeInTheDocument();
      expect(screen.getByText("Kỹ năng còn thiếu:")).toBeInTheDocument();
    });

    it("collapses when clicked again", () => {
      render(<MatchBreakdown breakdown={createMockBreakdown()} />);

      fireEvent.click(screen.getByText("Chi tiết đánh giá"));
      expect(screen.getByText("Kỹ năng phù hợp:")).toBeInTheDocument();

      fireEvent.click(screen.getByText("Chi tiết đánh giá"));
      expect(screen.queryByText("Kỹ năng phù hợp:")).not.toBeInTheDocument();
    });
  });

  describe("Experience display with comparison", () => {
    it("shows comparison format when JD has requirement", () => {
      render(
        <MatchBreakdown
          breakdown={createMockBreakdown({
            experience_years: 3,
            required_experience_years: 5,
          })}
        />
      );

      fireEvent.click(screen.getByText("Chi tiết đánh giá"));

      expect(screen.getByText(/3\/5 năm \(yêu cầu 5 năm\)/)).toBeInTheDocument();
    });

    it("shows only years when no JD requirement", () => {
      render(
        <MatchBreakdown
          breakdown={createMockBreakdown({
            experience_years: 4,
            required_experience_years: null,
          })}
        />
      );

      fireEvent.click(screen.getByText("Chi tiết đánh giá"));

      expect(screen.getByText(/4 năm/)).toBeInTheDocument();
      expect(screen.queryByText(/yêu cầu/)).not.toBeInTheDocument();
    });

    it("shows only years when JD requirement is 0", () => {
      render(
        <MatchBreakdown
          breakdown={createMockBreakdown({
            experience_years: 4,
            required_experience_years: 0,
          })}
        />
      );

      fireEvent.click(screen.getByText("Chi tiết đánh giá"));

      expect(screen.getByText(/4 năm/)).toBeInTheDocument();
      expect(screen.queryByText(/yêu cầu/)).not.toBeInTheDocument();
    });

    it("shows 'Không xác định' when experience_years is null", () => {
      render(
        <MatchBreakdown
          breakdown={createMockBreakdown({
            experience_years: null,
            required_experience_years: 5,
          })}
        />
      );

      fireEvent.click(screen.getByText("Chi tiết đánh giá"));

      expect(screen.getByText(/Không xác định/)).toBeInTheDocument();
    });
  });

  describe("Experience color coding", () => {
    it("shows green when experience meets requirement", () => {
      render(
        <MatchBreakdown
          breakdown={createMockBreakdown({
            experience_years: 5,
            required_experience_years: 5,
          })}
        />
      );

      fireEvent.click(screen.getByText("Chi tiết đánh giá"));

      const experienceSpan = screen.getByText(/5\/5 năm/).closest("span");
      expect(experienceSpan).toHaveClass("text-green-600");
    });

    it("shows green when experience exceeds requirement", () => {
      render(
        <MatchBreakdown
          breakdown={createMockBreakdown({
            experience_years: 10,
            required_experience_years: 5,
          })}
        />
      );

      fireEvent.click(screen.getByText("Chi tiết đánh giá"));

      const experienceSpan = screen.getByText(/10\/5 năm/).closest("span");
      expect(experienceSpan).toHaveClass("text-green-600");
    });

    it("shows yellow when experience is close to requirement (70-99%)", () => {
      render(
        <MatchBreakdown
          breakdown={createMockBreakdown({
            experience_years: 4,
            required_experience_years: 5,
          })}
        />
      );

      fireEvent.click(screen.getByText("Chi tiết đánh giá"));

      const experienceSpan = screen.getByText(/4\/5 năm/).closest("span");
      expect(experienceSpan).toHaveClass("text-yellow-600");
    });

    it("shows red when experience is significantly below requirement (<70%)", () => {
      render(
        <MatchBreakdown
          breakdown={createMockBreakdown({
            experience_years: 2,
            required_experience_years: 5,
          })}
        />
      );

      fireEvent.click(screen.getByText("Chi tiết đánh giá"));

      const experienceSpan = screen.getByText(/2\/5 năm/).closest("span");
      expect(experienceSpan).toHaveClass("text-red-600");
    });

    it("shows gray when no requirement (no color coding needed)", () => {
      render(
        <MatchBreakdown
          breakdown={createMockBreakdown({
            experience_years: 4,
            required_experience_years: null,
          })}
        />
      );

      fireEvent.click(screen.getByText("Chi tiết đánh giá"));

      const experienceSpan = screen.getByText(/4 năm/).closest("span");
      expect(experienceSpan).toHaveClass("text-gray-600");
    });

    it("shows gray when experience_years is null", () => {
      render(
        <MatchBreakdown
          breakdown={createMockBreakdown({
            experience_years: null,
            required_experience_years: 5,
          })}
        />
      );

      fireEvent.click(screen.getByText("Chi tiết đánh giá"));

      const experienceSpan = screen.getByText(/Không xác định/).closest("span");
      expect(experienceSpan).toHaveClass("text-gray-600");
    });
  });

  describe("Score display", () => {
    it("displays skill score correctly", () => {
      render(
        <MatchBreakdown
          breakdown={createMockBreakdown({ skill_score: 55.5 })}
        />
      );

      fireEvent.click(screen.getByText("Chi tiết đánh giá"));

      expect(screen.getByText(/55\.5%/)).toBeInTheDocument();
    });

    it("displays experience score correctly", () => {
      render(
        <MatchBreakdown
          breakdown={createMockBreakdown({ experience_score: 25.0 })}
        />
      );

      fireEvent.click(screen.getByText("Chi tiết đánh giá"));

      expect(screen.getByText(/Điểm kinh nghiệm:/)).toBeInTheDocument();
      expect(screen.getByText(/25\.0%/)).toBeInTheDocument();
    });
  });

  describe("Skills display", () => {
    it("shows matched skills section when present", () => {
      render(
        <MatchBreakdown
          breakdown={createMockBreakdown({
            matched_skills: ["Python", "FastAPI"],
          })}
        />
      );

      fireEvent.click(screen.getByText("Chi tiết đánh giá"));

      expect(screen.getByText("Kỹ năng phù hợp:")).toBeInTheDocument();
    });

    it("hides matched skills section when empty", () => {
      render(
        <MatchBreakdown
          breakdown={createMockBreakdown({
            matched_skills: [],
          })}
        />
      );

      fireEvent.click(screen.getByText("Chi tiết đánh giá"));

      expect(screen.queryByText("Kỹ năng phù hợp:")).not.toBeInTheDocument();
    });

    it("shows missing skills section when present", () => {
      render(
        <MatchBreakdown
          breakdown={createMockBreakdown({
            missing_skills: ["Kubernetes"],
          })}
        />
      );

      fireEvent.click(screen.getByText("Chi tiết đánh giá"));

      expect(screen.getByText("Kỹ năng còn thiếu:")).toBeInTheDocument();
    });

    it("hides missing skills section when empty", () => {
      render(
        <MatchBreakdown
          breakdown={createMockBreakdown({
            missing_skills: [],
          })}
        />
      );

      fireEvent.click(screen.getByText("Chi tiết đánh giá"));

      expect(screen.queryByText("Kỹ năng còn thiếu:")).not.toBeInTheDocument();
    });

    it("shows extra skills section when present", () => {
      render(
        <MatchBreakdown
          breakdown={createMockBreakdown({
            extra_skills: ["Docker", "AWS"],
          })}
        />
      );

      fireEvent.click(screen.getByText("Chi tiết đánh giá"));

      expect(screen.getByText("Kỹ năng bổ sung:")).toBeInTheDocument();
    });

    it("hides extra skills section when empty", () => {
      render(
        <MatchBreakdown
          breakdown={createMockBreakdown({
            extra_skills: [],
          })}
        />
      );

      fireEvent.click(screen.getByText("Chi tiết đánh giá"));

      expect(screen.queryByText("Kỹ năng bổ sung:")).not.toBeInTheDocument();
    });
  });

  describe("Accessibility", () => {
    it("has correct aria-expanded attribute", () => {
      render(<MatchBreakdown breakdown={createMockBreakdown()} />);

      const button = screen.getByRole("button");
      expect(button).toHaveAttribute("aria-expanded", "false");

      fireEvent.click(button);
      expect(button).toHaveAttribute("aria-expanded", "true");
    });

    it("has correct aria-controls attribute", () => {
      render(<MatchBreakdown breakdown={createMockBreakdown()} />);

      const button = screen.getByRole("button");
      expect(button).toHaveAttribute("aria-controls", "breakdown-content");
    });
  });
});
