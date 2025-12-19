import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import { SearchBar } from "./SearchBar";

describe("SearchBar", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders search input and button", () => {
    render(<SearchBar onSearch={jest.fn()} />);

    expect(screen.getByRole("searchbox")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /tim kiem/i })).toBeInTheDocument();
  });

  it("renders with custom placeholder", () => {
    render(<SearchBar onSearch={jest.fn()} placeholder="Custom placeholder..." />);

    expect(screen.getByPlaceholderText("Custom placeholder...")).toBeInTheDocument();
  });

  it("renders with initial value", () => {
    render(<SearchBar onSearch={jest.fn()} initialValue="Python developer" />);

    expect(screen.getByRole("searchbox")).toHaveValue("Python developer");
  });

  it("calls onSearch when form is submitted with valid query", () => {
    const mockOnSearch = jest.fn();
    render(<SearchBar onSearch={mockOnSearch} />);

    const input = screen.getByRole("searchbox");
    fireEvent.change(input, { target: { value: "Python developer" } });
    fireEvent.submit(screen.getByRole("search"));

    expect(mockOnSearch).toHaveBeenCalledWith("Python developer");
  });

  it("trims whitespace from query before calling onSearch", () => {
    const mockOnSearch = jest.fn();
    render(<SearchBar onSearch={mockOnSearch} />);

    const input = screen.getByRole("searchbox");
    fireEvent.change(input, { target: { value: "  Python developer  " } });
    fireEvent.submit(screen.getByRole("search"));

    expect(mockOnSearch).toHaveBeenCalledWith("Python developer");
  });

  it("does not call onSearch when query is too short", () => {
    const mockOnSearch = jest.fn();
    render(<SearchBar onSearch={mockOnSearch} />);

    const input = screen.getByRole("searchbox");
    fireEvent.change(input, { target: { value: "a" } });
    fireEvent.submit(screen.getByRole("search"));

    expect(mockOnSearch).not.toHaveBeenCalled();
  });

  it("shows clear button when query is not empty", () => {
    render(<SearchBar onSearch={jest.fn()} />);

    const input = screen.getByRole("searchbox");
    fireEvent.change(input, { target: { value: "test" } });

    expect(screen.getByRole("button", { name: /xoa query/i })).toBeInTheDocument();
  });

  it("hides clear button when query is empty", () => {
    render(<SearchBar onSearch={jest.fn()} />);

    expect(screen.queryByRole("button", { name: /xoa query/i })).not.toBeInTheDocument();
  });

  it("clears input when clear button is clicked", () => {
    render(<SearchBar onSearch={jest.fn()} />);

    const input = screen.getByRole("searchbox");
    fireEvent.change(input, { target: { value: "test query" } });

    const clearButton = screen.getByRole("button", { name: /xoa query/i });
    fireEvent.click(clearButton);

    expect(input).toHaveValue("");
  });

  it("disables submit button when query is too short", () => {
    render(<SearchBar onSearch={jest.fn()} />);

    const input = screen.getByRole("searchbox");
    const submitButton = screen.getByRole("button", { name: /tim kiem/i });

    expect(submitButton).toBeDisabled();

    fireEvent.change(input, { target: { value: "a" } });
    expect(submitButton).toBeDisabled();

    fireEvent.change(input, { target: { value: "ab" } });
    expect(submitButton).not.toBeDisabled();
  });

  it("disables input and submit button when loading", () => {
    render(<SearchBar onSearch={jest.fn()} loading={true} />);

    expect(screen.getByRole("searchbox")).toBeDisabled();
    // Button still has aria-label "Tim kiem" but shows "Dang tim..." text
    expect(screen.getByRole("button", { name: /tim kiem/i })).toBeDisabled();
  });

  it("shows loading state in button", () => {
    render(<SearchBar onSearch={jest.fn()} loading={true} />);

    expect(screen.getByText(/dang tim/i)).toBeInTheDocument();
  });

  it("has correct ARIA attributes", () => {
    render(<SearchBar onSearch={jest.fn()} />);

    expect(screen.getByRole("search")).toBeInTheDocument();
    expect(screen.getByRole("searchbox")).toHaveAttribute("aria-label");
    expect(screen.getByRole("button", { name: /tim kiem/i })).toHaveAttribute("aria-label");
  });

  it("clears input on Escape key", () => {
    render(<SearchBar onSearch={jest.fn()} />);

    const input = screen.getByRole("searchbox");
    fireEvent.change(input, { target: { value: "test query" } });
    fireEvent.keyDown(input, { key: "Escape" });

    expect(input).toHaveValue("");
  });
});
