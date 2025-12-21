import { render, screen } from "@testing-library/react";
import { LoadingSpinner } from "./loading-spinner";

describe("LoadingSpinner", () => {
  it("renders spinner element", () => {
    render(<LoadingSpinner />);
    expect(screen.getByTestId("loading-spinner")).toBeInTheDocument();
  });

  it("renders with message", () => {
    render(<LoadingSpinner message="Loading..." />);
    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("applies size classes correctly", () => {
    const { rerender } = render(<LoadingSpinner size="sm" />);
    expect(screen.getByTestId("loading-spinner")).toHaveClass("h-4", "w-4");

    rerender(<LoadingSpinner size="lg" />);
    expect(screen.getByTestId("loading-spinner")).toHaveClass("h-8", "w-8");
  });

  it("applies custom className", () => {
    render(<LoadingSpinner className="custom-class" />);
    expect(
      screen.getByTestId("loading-spinner").parentElement
    ).toHaveClass("custom-class");
  });

  it("renders centered version with relative container", () => {
    const { container } = render(<LoadingSpinner centered />);
    expect(container.querySelector(".relative")).toBeInTheDocument();
    expect(container.querySelector(".absolute")).toBeInTheDocument();
  });
});
