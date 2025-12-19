import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import { DeleteCVButton } from "./DeleteCVButton";

// Mock next/navigation
const mockPush = jest.fn();
jest.mock("next/navigation", () => ({
  useRouter: () => ({
    push: mockPush,
    refresh: jest.fn(),
  }),
}));

// Mock the deleteCVAction
const mockDeleteCVAction = jest.fn();
jest.mock("@/features/cv/actions", () => ({
  deleteCVAction: (...args: unknown[]) => mockDeleteCVAction(...args),
}));

// Mock sonner toast
jest.mock("sonner", () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

describe("DeleteCVButton", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockDeleteCVAction.mockResolvedValue({ success: true });
  });

  describe("Rendering", () => {
    it("renders delete button with correct text", () => {
      render(
        <DeleteCVButton cvId="test-cv-id" filename="my-resume.pdf" />
      );

      expect(screen.getByRole("button", { name: /delete/i })).toBeInTheDocument();
    });

    it("passes cvId and filename to DeleteCVDialog", () => {
      render(
        <DeleteCVButton
          cvId="test-cv-123"
          filename="test-resume.pdf"
          redirectTo="/cvs"
        />
      );

      // Button should be rendered (from DeleteCVDialog)
      const deleteButton = screen.getByRole("button", { name: /delete/i });
      expect(deleteButton).toBeInTheDocument();
    });
  });

  describe("Delete confirmation dialog", () => {
    it("opens confirmation dialog when clicked", async () => {
      render(
        <DeleteCVButton cvId="test-cv-id" filename="my-resume.pdf" />
      );

      const deleteButton = screen.getByRole("button", { name: /delete/i });
      fireEvent.click(deleteButton);

      await waitFor(() => {
        expect(screen.getByRole("alertdialog")).toBeInTheDocument();
      });

      expect(screen.getByText(/Are you sure you want to delete/)).toBeInTheDocument();
      expect(screen.getByText(/"my-resume.pdf"/)).toBeInTheDocument();
    });

    it("shows cancel button in dialog", async () => {
      render(
        <DeleteCVButton cvId="test-cv-id" filename="my-resume.pdf" />
      );

      fireEvent.click(screen.getByRole("button", { name: /delete/i }));

      await waitFor(() => {
        expect(screen.getByRole("button", { name: /cancel/i })).toBeInTheDocument();
      });
    });
  });

  describe("Redirect after successful deletion", () => {
    it("calls router.push with redirectTo after successful deletion", async () => {
      mockDeleteCVAction.mockResolvedValue({ success: true });

      render(
        <DeleteCVButton
          cvId="test-cv-id"
          filename="my-resume.pdf"
          redirectTo="/cvs"
        />
      );

      // Open dialog
      fireEvent.click(screen.getByRole("button", { name: /delete/i }));

      await waitFor(() => {
        expect(screen.getByRole("alertdialog")).toBeInTheDocument();
      });

      // Confirm deletion
      const confirmButtons = screen.getAllByRole("button", { name: /delete/i });
      const confirmButton = confirmButtons[confirmButtons.length - 1];
      fireEvent.click(confirmButton);

      await waitFor(() => {
        expect(mockDeleteCVAction).toHaveBeenCalledWith("test-cv-id");
      });

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith("/cvs");
      });
    });

    it("uses default redirectTo /cvs when not specified", async () => {
      mockDeleteCVAction.mockResolvedValue({ success: true });

      render(
        <DeleteCVButton cvId="test-cv-id" filename="my-resume.pdf" />
      );

      fireEvent.click(screen.getByRole("button", { name: /delete/i }));

      await waitFor(() => {
        expect(screen.getByRole("alertdialog")).toBeInTheDocument();
      });

      const confirmButtons = screen.getAllByRole("button", { name: /delete/i });
      fireEvent.click(confirmButtons[confirmButtons.length - 1]);

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith("/cvs");
      });
    });
  });

  describe("Error handling", () => {
    it("does not redirect on deletion failure", async () => {
      mockDeleteCVAction.mockResolvedValue({
        success: false,
        message: "Failed to delete CV",
      });

      render(
        <DeleteCVButton cvId="test-cv-id" filename="my-resume.pdf" />
      );

      fireEvent.click(screen.getByRole("button", { name: /delete/i }));

      await waitFor(() => {
        expect(screen.getByRole("alertdialog")).toBeInTheDocument();
      });

      const confirmButtons = screen.getAllByRole("button", { name: /delete/i });
      fireEvent.click(confirmButtons[confirmButtons.length - 1]);

      await waitFor(() => {
        expect(mockDeleteCVAction).toHaveBeenCalledWith("test-cv-id");
      });

      // Wait a bit to ensure redirect would have happened if it was going to
      await new Promise((resolve) => setTimeout(resolve, 100));
      expect(mockPush).not.toHaveBeenCalled();
    });

    it("shows error toast on deletion failure", async () => {
      const { toast } = await import("sonner");
      mockDeleteCVAction.mockResolvedValue({
        success: false,
        message: "Server error occurred",
      });

      render(
        <DeleteCVButton cvId="test-cv-id" filename="my-resume.pdf" />
      );

      fireEvent.click(screen.getByRole("button", { name: /delete/i }));

      await waitFor(() => {
        expect(screen.getByRole("alertdialog")).toBeInTheDocument();
      });

      const confirmButtons = screen.getAllByRole("button", { name: /delete/i });
      fireEvent.click(confirmButtons[confirmButtons.length - 1]);

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith("Server error occurred");
      });
    });
  });
});
