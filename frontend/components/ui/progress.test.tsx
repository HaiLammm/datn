import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import { Progress } from "./progress";

describe("Progress", () => {
  it("renders with default props", () => {
    render(<Progress />);
    const progressBar = screen.getByRole("progressbar");
    expect(progressBar).toBeInTheDocument();
    expect(progressBar).toHaveClass("h-2"); // default size 'md'
  });

  it("sets the correct value for the progress indicator", () => {
    render(<Progress value={65} />);
    const indicator = screen.getByTestId("progress-indicator");
    expect(indicator).toHaveStyle("transform: translateX(-35%)");
  });

  it("handles a value of 0", () => {
    render(<Progress value={0} />);
    const indicator = screen.getByTestId("progress-indicator");
    expect(indicator).toHaveStyle("transform: translateX(-100%)");
  });

  it("handles a value of 100", () => {
    render(<Progress value={100} />);
    const indicator = screen.getByTestId("progress-indicator");
    expect(indicator).toHaveStyle("transform: translateX(-0%)");
  });

  it("displays the percentage label when showLabel is true", () => {
    render(<Progress value={75} showLabel />);
    expect(screen.getByText("75%")).toBeInTheDocument();
  });

  it("does not display the percentage label by default", () => {
    render(<Progress value={75} />);
    expect(screen.queryByText("75%")).not.toBeInTheDocument();
  });

  it("applies the correct size class for 'sm'", () => {
    render(<Progress value={50} size="sm" />);
    const progressBar = screen.getByRole("progressbar");
    expect(progressBar).toHaveClass("h-1");
  });

  it("applies the correct size class for 'lg'", () => {
    render(<Progress value={50} size="lg" />);
    const progressBar = screen.getByRole("progressbar");
    expect(progressBar).toHaveClass("h-3");
  });

  it("passes through additional classNames", () => {
    render(<Progress value={50} className="my-custom-class" />);
    const progressBar = screen.getByRole("progressbar");
    expect(progressBar).toHaveClass("my-custom-class");
  });
});
