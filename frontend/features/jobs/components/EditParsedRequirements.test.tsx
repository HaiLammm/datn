import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import { EditParsedRequirements } from "./EditParsedRequirements";
import { ParsedJDRequirements } from "@datn/shared-types";
import * as actions from "../actions";

// Mock the server action
jest.mock("../actions", () => ({
  updateParsedRequirementsAction: jest.fn(),
}));

const mockRequirements: ParsedJDRequirements = {
  required_skills: ["Python", "FastAPI"],
  nice_to_have_skills: ["Docker"],
  min_experience_years: 3,
  job_title_normalized: "Python Developer",
  key_responsibilities: [],
};

describe("EditParsedRequirements", () => {
  const mockOnSave = jest.fn();
  const mockOnCancel = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders editable fields with current values", () => {
    render(
      <EditParsedRequirements
        jdId="test-123"
        currentRequirements={mockRequirements}
        onSave={mockOnSave}
        onCancel={mockOnCancel}
      />
    );
    
    expect(screen.getByText("Python")).toBeInTheDocument();
    expect(screen.getByText("FastAPI")).toBeInTheDocument();
    expect(screen.getByText("Docker")).toBeInTheDocument();
    expect(screen.getByDisplayValue("3")).toBeInTheDocument();
  });

  it("add skills from tag input", async () => {
    render(
      <EditParsedRequirements
        jdId="test-123"
        currentRequirements={mockRequirements}
        onSave={mockOnSave}
        onCancel={mockOnCancel}
      />
    );
    
    const requiredSkillInput = screen.getByLabelText(/Thêm kỹ năng yêu cầu mới/i);
    fireEvent.change(requiredSkillInput, { target: { value: "Django" } });
    
    const addButtons = screen.getAllByRole("button");
    const addButton = addButtons.find(
      (btn) => btn.closest("div")?.contains(requiredSkillInput)
    );
    
    if (addButton) {
      fireEvent.click(addButton);
    }
    
    await waitFor(() => {
      expect(screen.getByText("Django")).toBeInTheDocument();
    });
  });

  it("remove skills from tag input", async () => {
    render(
      <EditParsedRequirements
        jdId="test-123"
        currentRequirements={mockRequirements}
        onSave={mockOnSave}
        onCancel={mockOnCancel}
      />
    );
    
    // Find and click remove button for Python
    const removeButton = screen.getByRole("button", { name: /Xóa Python/i });
    fireEvent.click(removeButton);
    
    await waitFor(() => {
      expect(screen.queryByText("Python")).not.toBeInTheDocument();
    });
  });

  it("save button calls update action", async () => {
    (actions.updateParsedRequirementsAction as jest.Mock).mockResolvedValueOnce({
      success: true,
      message: "Updated successfully",
    });

    render(
      <EditParsedRequirements
        jdId="test-123"
        currentRequirements={mockRequirements}
        onSave={mockOnSave}
        onCancel={mockOnCancel}
      />
    );
    
    const saveButton = screen.getByRole("button", { name: /Lưu thay đổi/i });
    fireEvent.click(saveButton);
    
    await waitFor(() => {
      expect(actions.updateParsedRequirementsAction).toHaveBeenCalledWith(
        "test-123",
        expect.objectContaining({
          required_skills: ["Python", "FastAPI"],
          nice_to_have_skills: ["Docker"],
          min_experience_years: 3,
        })
      );
      expect(mockOnSave).toHaveBeenCalled();
    });
  });

  it("cancel button returns to view mode", () => {
    render(
      <EditParsedRequirements
        jdId="test-123"
        currentRequirements={mockRequirements}
        onSave={mockOnSave}
        onCancel={mockOnCancel}
      />
    );
    
    const cancelButton = screen.getByRole("button", { name: /Hủy/i });
    fireEvent.click(cancelButton);
    
    expect(mockOnCancel).toHaveBeenCalled();
  });

  it("shows error message when save fails", async () => {
    (actions.updateParsedRequirementsAction as jest.Mock).mockResolvedValueOnce({
      success: false,
      message: "Đã xảy ra lỗi khi cập nhật.",
    });

    render(
      <EditParsedRequirements
        jdId="test-123"
        currentRequirements={mockRequirements}
        onSave={mockOnSave}
        onCancel={mockOnCancel}
      />
    );
    
    const saveButton = screen.getByRole("button", { name: /Lưu thay đổi/i });
    fireEvent.click(saveButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Đã xảy ra lỗi khi cập nhật/i)).toBeInTheDocument();
    });
  });
});
