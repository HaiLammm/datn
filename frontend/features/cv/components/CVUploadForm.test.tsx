import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import { CVUploadForm } from "./CVUploadForm";

// Mock next/navigation
const mockPush = jest.fn();
const mockRefresh = jest.fn();
jest.mock("next/navigation", () => ({
  useRouter: () => ({
    push: mockPush,
    refresh: mockRefresh,
  }),
}));

// Mock sonner toast
jest.mock("sonner", () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

// Mock useFileUpload hook
const mockUpload = jest.fn();
const mockReset = jest.fn();

jest.mock("@/lib/hooks/useFileUpload", () => ({
  useFileUpload: () => ({
    isUploading: false,
    progress: 0,
    error: null,
    isSuccess: false,
    upload: mockUpload,
    reset: mockReset,
  }),
}));

describe("CVUploadForm", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders the upload form correctly", () => {
    render(<CVUploadForm />);
    expect(screen.getByText(/Tải lên CV của bạn/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Chọn file CV \(PDF hoặc DOCX\)/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Tải lên CV/i })).toBeInTheDocument();
  });

  it("displays an error for invalid file type on client-side validation", async () => {
    render(<CVUploadForm />);
    const fileInput = screen.getByLabelText(/Chọn file CV \(PDF hoặc DOCX\)/i) as HTMLInputElement;

    const invalidFile = new File(["hello"], "hello.txt", { type: "text/plain" });
    fireEvent.change(fileInput, { target: { files: [invalidFile] } });

    await waitFor(() => {
      expect(screen.getByText(/Chỉ chấp nhận file PDF hoặc DOCX\./i)).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /Tải lên CV/i })).toBeDisabled();
    });
  });

  it("displays an error for file exceeding size limit", async () => {
    render(<CVUploadForm />);
    const fileInput = screen.getByLabelText(/Chọn file CV \(PDF hoặc DOCX\)/i) as HTMLInputElement;

    // Create a file larger than 5MB
    const largeContent = new Array(6 * 1024 * 1024).fill("a").join("");
    const largeFile = new File([largeContent], "large.pdf", { type: "application/pdf" });
    fireEvent.change(fileInput, { target: { files: [largeFile] } });

    await waitFor(() => {
      expect(screen.getByText(/Kích thước file tối đa là 5MB\./i)).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /Tải lên CV/i })).toBeDisabled();
    });
  });

  it("allows selecting a valid PDF file", async () => {
    render(<CVUploadForm />);
    const fileInput = screen.getByLabelText(/Chọn file CV \(PDF hoặc DOCX\)/i) as HTMLInputElement;

    const validPdf = new File(["pdf content"], "resume.pdf", { type: "application/pdf" });
    fireEvent.change(fileInput, { target: { files: [validPdf] } });

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /Tải lên CV/i })).toBeEnabled();
      expect(screen.getByText(/Đã chọn: resume.pdf/i)).toBeInTheDocument();
    });
  });

  it("allows selecting a valid DOCX file", async () => {
    render(<CVUploadForm />);
    const fileInput = screen.getByLabelText(/Chọn file CV \(PDF hoặc DOCX\)/i) as HTMLInputElement;

    const validDocx = new File(["docx content"], "resume.docx", {
      type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    });
    fireEvent.change(fileInput, { target: { files: [validDocx] } });

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /Tải lên CV/i })).toBeEnabled();
      expect(screen.getByText(/Đã chọn: resume.docx/i)).toBeInTheDocument();
    });
  });

  it("calls upload when form is submitted with valid file", async () => {
    render(<CVUploadForm />);
    const fileInput = screen.getByLabelText(/Chọn file CV \(PDF hoặc DOCX\)/i) as HTMLInputElement;
    const submitButton = screen.getByRole("button", { name: /Tải lên CV/i });

    const validPdf = new File(["pdf content"], "resume.pdf", { type: "application/pdf" });
    fireEvent.change(fileInput, { target: { files: [validPdf] } });

    await waitFor(() => {
      expect(submitButton).toBeEnabled();
    });

    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockUpload).toHaveBeenCalledWith(
        expect.objectContaining({
          file: validPdf,
          url: "/api/cvs/upload",
          fieldName: "file",
        })
      );
    });
  });

  it("resets upload state when file changes", async () => {
    render(<CVUploadForm />);
    const fileInput = screen.getByLabelText(/Chọn file CV \(PDF hoặc DOCX\)/i) as HTMLInputElement;

    const validPdf = new File(["pdf content"], "resume.pdf", { type: "application/pdf" });
    fireEvent.change(fileInput, { target: { files: [validPdf] } });

    await waitFor(() => {
      expect(mockReset).toHaveBeenCalled();
    });
  });
});

describe("CVUploadForm - Upload States", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("shows progress indicator during upload", () => {
    // Mock uploading state
    const useFileUploadModule = jest.requireMock("@/lib/hooks/useFileUpload");
    jest.spyOn(useFileUploadModule, "useFileUpload").mockReturnValue({
      isUploading: true,
      progress: 45,
      error: null,
      isSuccess: false,
      upload: mockUpload,
      reset: mockReset,
    });

    render(<CVUploadForm />);

    expect(screen.getByTestId("upload-progress")).toBeInTheDocument();
    expect(screen.getByText("45%")).toBeInTheDocument();
    // Check upload progress area specifically
    const progressArea = screen.getByTestId("upload-progress");
    expect(progressArea).toHaveTextContent(/Đang tải lên/i);
  });

  it("shows success state after upload", () => {
    const useFileUploadModule = jest.requireMock("@/lib/hooks/useFileUpload");
    jest.spyOn(useFileUploadModule, "useFileUpload").mockReturnValue({
      isUploading: false,
      progress: 100,
      error: null,
      isSuccess: true,
      upload: mockUpload,
      reset: mockReset,
    });

    render(<CVUploadForm />);

    expect(screen.getByTestId("upload-success")).toBeInTheDocument();
    expect(screen.getByText(/CV đã được tải lên thành công/i)).toBeInTheDocument();
  });

  it("shows error state with retry button", () => {
    const useFileUploadModule = jest.requireMock("@/lib/hooks/useFileUpload");
    jest.spyOn(useFileUploadModule, "useFileUpload").mockReturnValue({
      isUploading: false,
      progress: 0,
      error: "Upload failed",
      isSuccess: false,
      upload: mockUpload,
      reset: mockReset,
    });

    render(<CVUploadForm />);

    expect(screen.getByTestId("error-display")).toBeInTheDocument();
    expect(screen.getByText("Upload failed")).toBeInTheDocument();
    expect(screen.getByTestId("error-retry-button")).toBeInTheDocument();
  });
});
