import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import { JDUploadForm } from "./JDUploadForm";
import * as actions from "../actions";

// Mock next/navigation
jest.mock("next/navigation", () => ({
  useRouter: () => ({
    push: jest.fn(),
    refresh: jest.fn(),
  }),
}));

// Mock next/cache to prevent TextEncoder error
jest.mock("next/cache", () => ({
  revalidatePath: jest.fn(),
  revalidateTag: jest.fn(),
}));

// Mock next/headers
jest.mock("next/headers", () => ({
  headers: jest.fn(() => ({
    get: jest.fn(() => "mock-cookie"),
  })),
  cookies: jest.fn(() => ({
    get: jest.fn(() => ({ value: "mock-token" })),
  })),
}));

// Mock the server action
jest.mock("../actions", () => ({
  createJDAction: jest.fn(),
}));

describe("JDUploadForm", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders all form fields including input mode toggle", () => {
    render(<JDUploadForm />);
    
    expect(screen.getByText(/Tạo Job Description mới/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Tiêu đề/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Paste văn bản/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Tải file lên/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Tạo Job Description/i })).toBeInTheDocument();
  });

  it("switches between text and file upload modes", async () => {
    render(<JDUploadForm />);
    
    // Initially in text mode
    expect(screen.getByLabelText(/Mô tả công việc/i)).toBeInTheDocument();
    
    // Switch to file mode
    const fileRadio = screen.getByLabelText(/Tải file lên/i);
    fireEvent.click(fileRadio);
    
    await waitFor(() => {
      expect(screen.getByText(/Kéo thả file vào đây/i)).toBeInTheDocument();
    });
  });

  it("validates file type (PDF/DOCX only)", async () => {
    render(<JDUploadForm />);
    
    // Switch to file mode
    const fileRadio = screen.getByLabelText(/Tải file lên/i);
    fireEvent.click(fileRadio);
    
    await waitFor(() => {
      expect(screen.getByText(/Kéo thả file vào đây/i)).toBeInTheDocument();
    });
    
    const fileInput = screen.getByLabelText(/Chọn file JD/i) as HTMLInputElement;
    
    // Invalid file
    const invalidFile = new File(["hello"], "hello.txt", { type: "text/plain" });
    fireEvent.change(fileInput, { target: { files: [invalidFile] } });
    
    await waitFor(() => {
      expect(screen.getByText(/Chỉ chấp nhận file PDF hoặc DOCX/i)).toBeInTheDocument();
    });
  });

  it("shows validation errors for empty required fields", async () => {
    (actions.createJDAction as jest.Mock).mockResolvedValueOnce({
      message: "Lỗi validation.",
      errors: {
        title: "Tiêu đề phải có ít nhất 3 ký tự",
        description: "Mô tả phải có ít nhất 10 ký tự",
      },
    });

    render(<JDUploadForm />);
    
    const submitButton = screen.getByRole("button", { name: /Tạo Job Description/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Tiêu đề phải có ít nhất 3 ký tự/i)).toBeInTheDocument();
    });
  });

  it("submits form with valid data", async () => {
    (actions.createJDAction as jest.Mock).mockResolvedValueOnce({
      message: "Job Description đã được tạo thành công!",
      errors: {},
      data: { id: "test-id-123" },
    });

    render(<JDUploadForm />);
    
    // Fill in required fields
    const titleInput = screen.getByLabelText(/Tiêu đề/i);
    fireEvent.change(titleInput, { target: { value: "Senior Python Developer" } });
    
    const descriptionInput = screen.getByLabelText(/Mô tả công việc/i);
    fireEvent.change(descriptionInput, { target: { value: "Looking for a senior developer with Python experience..." } });
    
    const submitButton = screen.getByRole("button", { name: /Tạo Job Description/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(actions.createJDAction).toHaveBeenCalledTimes(1);
    });
  });

  it("shows loading state during submission", async () => {
    (actions.createJDAction as jest.Mock).mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve({ message: "", errors: {} }), 100))
    );

    render(<JDUploadForm />);
    
    const titleInput = screen.getByLabelText(/Tiêu đề/i);
    fireEvent.change(titleInput, { target: { value: "Test Job" } });
    
    const descriptionInput = screen.getByLabelText(/Mô tả công việc/i);
    fireEvent.change(descriptionInput, { target: { value: "Test description for the job..." } });
    
    const submitButton = screen.getByRole("button", { name: /Tạo Job Description/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Đang tạo.../i)).toBeInTheDocument();
    });
  });
});
