import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import { NoCVsYet } from "./NoCVsYet";

describe("NoCVsYet", () => {
  it("renders with default props", () => {
    render(<NoCVsYet />);

    expect(screen.getByTestId("no-cvs-empty-state")).toBeInTheDocument();
    expect(screen.getByText("No CVs uploaded yet")).toBeInTheDocument();
    expect(
      screen.getByText("Get started by uploading your first CV for analysis.")
    ).toBeInTheDocument();
    expect(screen.getByTestId("upload-first-cv-link")).toBeInTheDocument();
  });

  it("renders with custom title and description", () => {
    render(
      <NoCVsYet
        title="Custom Title"
        description="Custom description text."
      />
    );

    expect(screen.getByText("Custom Title")).toBeInTheDocument();
    expect(screen.getByText("Custom description text.")).toBeInTheDocument();
  });

  it("renders upload link with correct href", () => {
    render(<NoCVsYet />);

    const link = screen.getByTestId("upload-first-cv-link");
    expect(link).toHaveAttribute("href", "/cvs/upload");
    expect(link).toHaveTextContent("Upload Your First CV");
  });

  it("hides upload link when showUploadLink is false", () => {
    render(<NoCVsYet showUploadLink={false} />);

    expect(screen.queryByTestId("upload-first-cv-link")).not.toBeInTheDocument();
  });

  it("renders custom action instead of upload link", () => {
    render(
      <NoCVsYet
        customAction={<button data-testid="custom-action">Custom Action</button>}
      />
    );

    expect(screen.queryByTestId("upload-first-cv-link")).not.toBeInTheDocument();
    expect(screen.getByTestId("custom-action")).toBeInTheDocument();
  });

  it("renders document icon", () => {
    render(<NoCVsYet />);

    const container = screen.getByTestId("no-cvs-empty-state");
    expect(container.querySelector("svg")).toBeInTheDocument();
  });
});
