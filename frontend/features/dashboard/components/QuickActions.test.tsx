import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import { QuickActions } from "./QuickActions";

describe("QuickActions", () => {
  describe("Rendering", () => {
    it("renders upload CV button with correct link", () => {
      render(<QuickActions />);

      const uploadButton = screen.getByTestId("upload-cv-button");
      expect(uploadButton).toBeInTheDocument();
      expect(uploadButton).toHaveAttribute("href", "/cvs/upload");
    });

    it("renders view history button with correct link", () => {
      render(<QuickActions />);

      const historyButton = screen.getByTestId("view-history-button");
      expect(historyButton).toBeInTheDocument();
      expect(historyButton).toHaveAttribute("href", "/cvs");
    });

    it("displays correct text on upload button", () => {
      render(<QuickActions />);

      expect(screen.getByText("Upload New CV")).toBeInTheDocument();
    });

    it("displays correct text on history button", () => {
      render(<QuickActions />);

      expect(screen.getByText("View CV History")).toBeInTheDocument();
    });

    it("renders Quick Actions title", () => {
      render(<QuickActions />);

      expect(screen.getByText("Quick Actions")).toBeInTheDocument();
    });
  });

  describe("Accessibility", () => {
    it("upload button is focusable (accessible via keyboard)", () => {
      render(<QuickActions />);

      const uploadButton = screen.getByTestId("upload-cv-button");
      uploadButton.focus();
      expect(uploadButton).toHaveFocus();
    });

    it("view history button is focusable (accessible via keyboard)", () => {
      render(<QuickActions />);

      const historyButton = screen.getByTestId("view-history-button");
      historyButton.focus();
      expect(historyButton).toHaveFocus();
    });

    it("buttons are links and accessible", () => {
      render(<QuickActions />);

      const uploadLink = screen.getByRole("link", { name: /Upload New CV/i });
      const historyLink = screen.getByRole("link", { name: /View CV History/i });

      expect(uploadLink).toBeInTheDocument();
      expect(historyLink).toBeInTheDocument();
    });
  });

  describe("Icons", () => {
    it("buttons contain SVG icons", () => {
      render(<QuickActions />);

      const uploadButton = screen.getByTestId("upload-cv-button");
      const historyButton = screen.getByTestId("view-history-button");

      // Check that SVG icons are present (lucide-react icons render as SVG)
      expect(uploadButton.querySelector("svg")).toBeInTheDocument();
      expect(historyButton.querySelector("svg")).toBeInTheDocument();
    });
  });
});
