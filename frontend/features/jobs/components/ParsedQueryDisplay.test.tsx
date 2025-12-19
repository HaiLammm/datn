import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import { ParsedQueryDisplay } from "./ParsedQueryDisplay";
import { ParsedQueryResponse } from "@datn/shared-types";

describe("ParsedQueryDisplay", () => {
  it("renders extracted skills as badges", () => {
    const parsedQuery: ParsedQueryResponse = {
      extracted_skills: ["Python", "AWS", "Docker"],
      experience_keywords: [],
      raw_query: "Python developer with AWS experience",
    };

    render(<ParsedQueryDisplay parsedQuery={parsedQuery} />);

    expect(screen.getByText("Python")).toBeInTheDocument();
    expect(screen.getByText("AWS")).toBeInTheDocument();
    expect(screen.getByText("Docker")).toBeInTheDocument();
    expect(screen.getByText(/ky nang tim kiem/i)).toBeInTheDocument();
  });

  it("renders experience keywords as badges", () => {
    const parsedQuery: ParsedQueryResponse = {
      extracted_skills: [],
      experience_keywords: ["3+ years", "Senior"],
      raw_query: "Senior developer with 3+ years experience",
    };

    render(<ParsedQueryDisplay parsedQuery={parsedQuery} />);

    expect(screen.getByText("3+ years")).toBeInTheDocument();
    expect(screen.getByText("Senior")).toBeInTheDocument();
    expect(screen.getByText(/kinh nghiem/i)).toBeInTheDocument();
  });

  it("renders both skills and experience keywords", () => {
    const parsedQuery: ParsedQueryResponse = {
      extracted_skills: ["Python", "React"],
      experience_keywords: ["5 years"],
      raw_query: "Python React developer 5 years",
    };

    render(<ParsedQueryDisplay parsedQuery={parsedQuery} />);

    expect(screen.getByText("Python")).toBeInTheDocument();
    expect(screen.getByText("React")).toBeInTheDocument();
    expect(screen.getByText("5 years")).toBeInTheDocument();
  });

  it("returns null when both skills and experience are empty", () => {
    const parsedQuery: ParsedQueryResponse = {
      extracted_skills: [],
      experience_keywords: [],
      raw_query: "some query",
    };

    const { container } = render(<ParsedQueryDisplay parsedQuery={parsedQuery} />);

    expect(container.firstChild).toBeNull();
  });

  it("shows raw query when expanded", () => {
    const parsedQuery: ParsedQueryResponse = {
      extracted_skills: ["Python"],
      experience_keywords: [],
      raw_query: "Python developer with AWS experience",
    };

    render(<ParsedQueryDisplay parsedQuery={parsedQuery} />);

    // Raw query should be hidden by default
    expect(screen.queryByText(/"Python developer with AWS experience"/)).not.toBeInTheDocument();

    // Click to expand
    const expandButton = screen.getByRole("button", { name: /xem query goc/i });
    fireEvent.click(expandButton);

    // Raw query should now be visible
    expect(screen.getByText(/"Python developer with AWS experience"/)).toBeInTheDocument();
  });

  it("hides raw query when collapsed", () => {
    const parsedQuery: ParsedQueryResponse = {
      extracted_skills: ["Python"],
      experience_keywords: [],
      raw_query: "Python developer",
    };

    render(<ParsedQueryDisplay parsedQuery={parsedQuery} />);

    // Expand
    const expandButton = screen.getByRole("button", { name: /xem query goc/i });
    fireEvent.click(expandButton);
    expect(screen.getByText(/"Python developer"/)).toBeInTheDocument();

    // Collapse
    const collapseButton = screen.getByRole("button", { name: /an query goc/i });
    fireEvent.click(collapseButton);

    // Raw query should be hidden again
    expect(screen.queryByText(/"Python developer"/)).not.toBeInTheDocument();
  });

  it("shows header text about query analysis", () => {
    const parsedQuery: ParsedQueryResponse = {
      extracted_skills: ["Python"],
      experience_keywords: [],
      raw_query: "Python developer",
    };

    render(<ParsedQueryDisplay parsedQuery={parsedQuery} />);

    expect(screen.getByText(/he thong da phan tich query cua ban/i)).toBeInTheDocument();
  });
});
