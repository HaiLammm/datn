import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import { CVUploadForm } from "./CVUploadForm";
import * as actions from "../actions";

// Mock the server action
jest.mock("../actions", () => ({
  createCVAction: jest.fn(),
}));

describe("CVUploadForm", () => {
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
      expect(fileInput.files?.[0]).toBe(invalidFile);
      expect(screen.getByText(/Chỉ chấp nhận file PDF hoặc DOCX\./i)).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /Tải lên CV/i })).toBeDisabled();
    });
  });

  it("allows selecting a valid PDF file", async () => {
    render(<CVUploadForm />);
    const fileInput = screen.getByLabelText(/Chọn file CV \(PDF hoặc DOCX\)/i) as HTMLInputElement;

    const validPdf = new File(["pdf content"], "resume.pdf", { type: "application/pdf" });
    fireEvent.change(fileInput, { target: { files: [validPdf] } });

    await waitFor(() => {
      expect(fileInput.files?.[0]).toBe(validPdf);
      expect(screen.getByRole("button", { name: /Tải lên CV/i })).toBeEnabled();
    });
  });

  it("submits the form with a valid file and displays success message", async () => {
    jest.clearAllMocks(); // Clear mocks before this test
    (actions.createCVAction as jest.Mock).mockResolvedValueOnce({
      message: "CV đã được tải lên thành công!",
      errors: {},
    });
    render(<CVUploadForm />);
    const fileInput = screen.getByLabelText(/Chọn file CV \(PDF hoặc DOCX\)/i) as HTMLInputElement;
    const submitButton = screen.getByRole("button", { name: /Tải lên CV/i });

    const validPdf = new File(["pdf content"], "resume.pdf", { type: "application/pdf" });
    Object.defineProperty(fileInput, "files", {
      value: [validPdf],
    });
    fireEvent.change(fileInput); // Trigger change event after setting files

    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(actions.createCVAction).toHaveBeenCalledTimes(1);
      expect(screen.getByText(/CV đã được tải lên thành công!/i)).toBeInTheDocument();
    });
  });

  it("displays error message from server action", async () => {
    jest.clearAllMocks(); // Clear mocks before this test
    (actions.createCVAction as jest.Mock).mockResolvedValueOnce({
      message: "Đã xảy ra lỗi khi tải lên CV.",
      errors: {},
    });

    render(<CVUploadForm />);
    const fileInput = screen.getByLabelText(/Chọn file CV \(PDF hoặc DOCX\)/i) as HTMLInputElement;
    const submitButton = screen.getByRole("button", { name: /Tải lên CV/i });

    const validPdf = new File(["pdf content"], "error_cv.pdf", { type: "application/pdf" });
    Object.defineProperty(fileInput, "files", {
      value: [validPdf],
    });
    fireEvent.change(fileInput); // Trigger change event after setting files

    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(actions.createCVAction).toHaveBeenCalledTimes(1);
      expect(screen.getByText(/Đã xảy ra lỗi khi tải lên CV./i)).toBeInTheDocument();
    });
  });
});
