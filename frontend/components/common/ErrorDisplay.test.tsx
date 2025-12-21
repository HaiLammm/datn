import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import { ErrorDisplay } from "./ErrorDisplay";

describe("ErrorDisplay", () => {
  describe("Inline variant (default)", () => {
    it("renders error message", () => {
      render(<ErrorDisplay message="Something went wrong" />);

      expect(screen.getByTestId("error-display")).toBeInTheDocument();
      expect(screen.getByText("Something went wrong")).toBeInTheDocument();
    });

    it("renders retry button when onRetry is provided", () => {
      const onRetry = jest.fn();
      render(<ErrorDisplay message="Error" onRetry={onRetry} />);

      expect(screen.getByTestId("error-retry-button")).toBeInTheDocument();
    });

    it("does not render retry button when onRetry is not provided", () => {
      render(<ErrorDisplay message="Error" />);

      expect(screen.queryByTestId("error-retry-button")).not.toBeInTheDocument();
    });

    it("calls onRetry when retry button is clicked", () => {
      const onRetry = jest.fn();
      render(<ErrorDisplay message="Error" onRetry={onRetry} />);

      fireEvent.click(screen.getByTestId("error-retry-button"));
      expect(onRetry).toHaveBeenCalledTimes(1);
    });

    it("disables retry button when isRetrying is true", () => {
      const onRetry = jest.fn();
      render(<ErrorDisplay message="Error" onRetry={onRetry} isRetrying />);

      expect(screen.getByTestId("error-retry-button")).toBeDisabled();
    });

    it("shows custom retry text", () => {
      render(
        <ErrorDisplay message="Error" onRetry={() => {}} retryText="Try Again" />
      );

      expect(screen.getByText("Try Again")).toBeInTheDocument();
    });
  });

  describe("Card variant", () => {
    it("renders with card styling", () => {
      render(<ErrorDisplay message="Error" variant="card" />);

      const display = screen.getByTestId("error-display");
      expect(display).toHaveClass("p-6");
      expect(display).toHaveClass("rounded-lg");
    });

    it("renders title when provided", () => {
      render(
        <ErrorDisplay
          message="Details about the error"
          title="Error Title"
          variant="card"
        />
      );

      expect(screen.getByText("Error Title")).toBeInTheDocument();
      expect(screen.getByText("Details about the error")).toBeInTheDocument();
    });

    it("renders retry button in card variant", () => {
      const onRetry = jest.fn();
      render(
        <ErrorDisplay
          message="Error"
          variant="card"
          onRetry={onRetry}
        />
      );

      expect(screen.getByTestId("error-retry-button")).toBeInTheDocument();
    });
  });

  describe("Custom className", () => {
    it("applies custom className", () => {
      render(<ErrorDisplay message="Error" className="custom-class" />);

      expect(screen.getByTestId("error-display")).toHaveClass("custom-class");
    });
  });
});
