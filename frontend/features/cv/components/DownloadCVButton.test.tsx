/**
 * @jest-environment jsdom
 */
import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import { DownloadCVButton } from "./DownloadCVButton";

// Mock sonner toast
jest.mock("sonner", () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

// Mock fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

// Mock URL.createObjectURL and URL.revokeObjectURL
const mockCreateObjectURL = jest.fn(() => "blob:mock-url");
const mockRevokeObjectURL = jest.fn();
global.URL.createObjectURL = mockCreateObjectURL;
global.URL.revokeObjectURL = mockRevokeObjectURL;

describe("DownloadCVButton", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockFetch.mockResolvedValue({
      ok: true,
      headers: new Headers(),
      blob: () => Promise.resolve(new Blob(["test content"], { type: "application/pdf" })),
    });
  });

  describe("Rendering - Icon Variant", () => {
    it("renders download icon button for icon variant", () => {
      render(
        <DownloadCVButton cvId="test-cv-id" filename="my-resume.pdf" variant="icon" />
      );

      const button = screen.getByTestId("download-cv-button");
      expect(button).toBeInTheDocument();
    });

    it("has title attribute for icon variant", () => {
      render(
        <DownloadCVButton cvId="test-cv-id" filename="my-resume.pdf" variant="icon" />
      );

      const button = screen.getByTestId("download-cv-button");
      expect(button).toHaveAttribute("title", "Download");
    });
  });

  describe("Rendering - Button Variant", () => {
    it("renders download button with text for button variant", () => {
      render(
        <DownloadCVButton cvId="test-cv-id" filename="my-resume.pdf" variant="button" />
      );

      const button = screen.getByTestId("download-cv-button");
      expect(button).toBeInTheDocument();
      expect(screen.getByText("Download")).toBeInTheDocument();
    });

    it("defaults to button variant when not specified", () => {
      render(
        <DownloadCVButton cvId="test-cv-id" filename="my-resume.pdf" />
      );

      expect(screen.getByText("Download")).toBeInTheDocument();
    });
  });

  describe("Loading State", () => {
    it("shows loading spinner during download for button variant", async () => {
      // Make fetch return a promise that we control
      let resolveFetch: (value: unknown) => void;
      mockFetch.mockReturnValue(
        new Promise((resolve) => {
          resolveFetch = resolve;
        })
      );

      render(
        <DownloadCVButton cvId="test-cv-id" filename="my-resume.pdf" variant="button" />
      );

      const button = screen.getByTestId("download-cv-button");
      fireEvent.click(button);

      // Should show loading state
      await waitFor(() => {
        expect(screen.getByTestId("download-cv-button-loading")).toBeInTheDocument();
      });

      // Resolve the fetch
      resolveFetch!({
        ok: true,
        headers: new Headers(),
        blob: () => Promise.resolve(new Blob(["test"])),
      });
    });

    it("disables button while downloading", async () => {
      let resolveFetch: (value: unknown) => void;
      mockFetch.mockReturnValue(
        new Promise((resolve) => {
          resolveFetch = resolve;
        })
      );

      render(
        <DownloadCVButton cvId="test-cv-id" filename="my-resume.pdf" />
      );

      const button = screen.getByTestId("download-cv-button");
      fireEvent.click(button);

      await waitFor(() => {
        expect(button).toBeDisabled();
      });

      resolveFetch!({
        ok: true,
        headers: new Headers(),
        blob: () => Promise.resolve(new Blob(["test"])),
      });
    });
  });

  describe("Download Action", () => {
    it("triggers download action on click", async () => {
      render(
        <DownloadCVButton cvId="test-cv-id" filename="my-resume.pdf" />
      );

      const button = screen.getByTestId("download-cv-button");
      fireEvent.click(button);

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          "/api/cvs/test-cv-id/download",
          expect.objectContaining({
            method: "GET",
            credentials: "include",
          })
        );
      });
    });

    it("creates blob URL and triggers download", async () => {
      render(
        <DownloadCVButton cvId="test-cv-id" filename="my-resume.pdf" />
      );

      const button = screen.getByTestId("download-cv-button");
      fireEvent.click(button);

      await waitFor(() => {
        expect(mockCreateObjectURL).toHaveBeenCalled();
        expect(mockRevokeObjectURL).toHaveBeenCalledWith("blob:mock-url");
      });
    });

    it("shows success toast after download", async () => {
      const { toast } = await import("sonner");
      
      render(
        <DownloadCVButton cvId="test-cv-id" filename="my-resume.pdf" />
      );

      const button = screen.getByTestId("download-cv-button");
      fireEvent.click(button);

      await waitFor(() => {
        expect(toast.success).toHaveBeenCalledWith('Downloaded "my-resume.pdf"');
      });
    });
  });

  describe("Error Handling", () => {
    it("shows error toast when download fails with 404", async () => {
      const { toast } = await import("sonner");
      mockFetch.mockResolvedValue({
        ok: false,
        status: 404,
        headers: new Headers(),
      });

      render(
        <DownloadCVButton cvId="test-cv-id" filename="my-resume.pdf" />
      );

      const button = screen.getByTestId("download-cv-button");
      fireEvent.click(button);

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith("CV file not found");
      });
    });

    it("shows error toast when download fails with 403", async () => {
      const { toast } = await import("sonner");
      mockFetch.mockResolvedValue({
        ok: false,
        status: 403,
        headers: new Headers(),
      });

      render(
        <DownloadCVButton cvId="test-cv-id" filename="my-resume.pdf" />
      );

      const button = screen.getByTestId("download-cv-button");
      fireEvent.click(button);

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith("You do not have permission to download this CV");
      });
    });

    it("shows error toast when download fails with 401", async () => {
      const { toast } = await import("sonner");
      mockFetch.mockResolvedValue({
        ok: false,
        status: 401,
        headers: new Headers(),
      });

      render(
        <DownloadCVButton cvId="test-cv-id" filename="my-resume.pdf" />
      );

      const button = screen.getByTestId("download-cv-button");
      fireEvent.click(button);

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith("Please log in to download");
      });
    });

    it("shows generic error when fetch throws", async () => {
      const { toast } = await import("sonner");
      mockFetch.mockRejectedValue(new Error("Network error"));

      render(
        <DownloadCVButton cvId="test-cv-id" filename="my-resume.pdf" />
      );

      const button = screen.getByTestId("download-cv-button");
      fireEvent.click(button);

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith("Network error");
      });
    });
  });
});
