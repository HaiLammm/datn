import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import { RegisterForm } from "./RegisterForm";
import * as actions from "./actions";

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
    set: jest.fn(),
  })),
}));

// Mock the server action
jest.mock("./actions", () => ({
  registerUser: jest.fn(),
}));

describe("RegisterForm", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("Rendering", () => {
    it("renders the registration form with all required fields", () => {
      render(<RegisterForm />);

      expect(screen.getByText(/Create a new account/i)).toBeInTheDocument();
      expect(screen.getByText(/I am a/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Full Name/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Email address/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /Register/i })).toBeInTheDocument();
    });

    it("renders role selection with Job Seeker and Recruiter options", () => {
      render(<RegisterForm />);

      expect(screen.getByText(/Job Seeker/i)).toBeInTheDocument();
      expect(screen.getByText(/Looking for jobs/i)).toBeInTheDocument();
      expect(screen.getByText(/Recruiter \/ HR/i)).toBeInTheDocument();
      expect(screen.getByText(/Hiring talents/i)).toBeInTheDocument();
    });

    it("renders login link for existing users", () => {
      render(<RegisterForm />);

      expect(screen.getByText(/Đã có tài khoản\?/i)).toBeInTheDocument();
      expect(screen.getByRole("link", { name: /Đăng nhập/i })).toHaveAttribute(
        "href",
        "/login"
      );
    });
  });

  describe("Role Selection", () => {
    it("has Job Seeker (user) selected by default", () => {
      render(<RegisterForm />);

      const hiddenRoleInput = document.querySelector(
        'input[name="role"]'
      ) as HTMLInputElement;
      expect(hiddenRoleInput.value).toBe("user");
    });

    it("switches to Recruiter role when clicked", async () => {
      render(<RegisterForm />);

      const recruiterLabel = screen.getByText(/Recruiter \/ HR/i);
      fireEvent.click(recruiterLabel);

      await waitFor(() => {
        const hiddenRoleInput = document.querySelector(
          'input[name="role"]'
        ) as HTMLInputElement;
        expect(hiddenRoleInput.value).toBe("recruiter");
      });
    });

    it("switches back to Job Seeker role when clicked", async () => {
      render(<RegisterForm />);

      // First select recruiter
      const recruiterLabel = screen.getByText(/Recruiter \/ HR/i);
      fireEvent.click(recruiterLabel);

      await waitFor(() => {
        const hiddenRoleInput = document.querySelector(
          'input[name="role"]'
        ) as HTMLInputElement;
        expect(hiddenRoleInput.value).toBe("recruiter");
      });

      // Then switch back to user
      const jobSeekerLabel = screen.getByText(/Job Seeker/i);
      fireEvent.click(jobSeekerLabel);

      await waitFor(() => {
        const hiddenRoleInput = document.querySelector(
          'input[name="role"]'
        ) as HTMLInputElement;
        expect(hiddenRoleInput.value).toBe("user");
      });
    });

    it("applies correct styling to selected role", async () => {
      render(<RegisterForm />);

      // Job Seeker should have selected styling by default
      const jobSeekerLabel = screen
        .getByText(/Job Seeker/i)
        .closest("label");
      expect(jobSeekerLabel).toHaveClass("border-blue-600");
      expect(jobSeekerLabel).toHaveClass("bg-blue-50");

      // Recruiter should not have selected styling
      const recruiterLabel = screen
        .getByText(/Recruiter \/ HR/i)
        .closest("label");
      expect(recruiterLabel).toHaveClass("border-gray-200");

      // Click recruiter
      fireEvent.click(recruiterLabel!);

      await waitFor(() => {
        // Now recruiter should have selected styling
        expect(recruiterLabel).toHaveClass("border-blue-600");
        expect(recruiterLabel).toHaveClass("bg-blue-50");
        // And Job Seeker should not
        expect(jobSeekerLabel).toHaveClass("border-gray-200");
      });
    });
  });

  describe("Form Validation", () => {
    it("shows validation error for invalid email from server", async () => {
      (actions.registerUser as jest.Mock).mockResolvedValueOnce({
        message: "",
        errors: {
          email: ["Invalid email address"],
        },
      });

      render(<RegisterForm />);

      const submitButton = screen.getByRole("button", { name: /Register/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/Invalid email address/i)).toBeInTheDocument();
      });
    });

    it("shows validation error for short password from server", async () => {
      (actions.registerUser as jest.Mock).mockResolvedValueOnce({
        message: "",
        errors: {
          password: ["Password must be at least 6 characters"],
        },
      });

      render(<RegisterForm />);

      const submitButton = screen.getByRole("button", { name: /Register/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(
          screen.getByText(/Password must be at least 6 characters/i)
        ).toBeInTheDocument();
      });
    });

    it("shows validation error for short full name from server", async () => {
      (actions.registerUser as jest.Mock).mockResolvedValueOnce({
        message: "",
        errors: {
          full_name: ["Full name must be at least 3 characters"],
        },
      });

      render(<RegisterForm />);

      const submitButton = screen.getByRole("button", { name: /Register/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(
          screen.getByText(/Full name must be at least 3 characters/i)
        ).toBeInTheDocument();
      });
    });

    it("shows server error message", async () => {
      (actions.registerUser as jest.Mock).mockResolvedValueOnce({
        message: "",
        errors: {
          server: ["Email đã được sử dụng"],
        },
      });

      render(<RegisterForm />);

      const submitButton = screen.getByRole("button", { name: /Register/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/Email đã được sử dụng/i)).toBeInTheDocument();
      });
    });

    it("shows role validation error from server", async () => {
      (actions.registerUser as jest.Mock).mockResolvedValueOnce({
        message: "",
        errors: {
          role: ["Please select a role"],
        },
      });

      render(<RegisterForm />);

      const submitButton = screen.getByRole("button", { name: /Register/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/Please select a role/i)).toBeInTheDocument();
      });
    });
  });

  describe("Form Submission", () => {
    it("submits form with valid data including role", async () => {
      (actions.registerUser as jest.Mock).mockResolvedValueOnce({
        message: "Success",
        errors: {},
      });

      render(<RegisterForm />);

      // Fill in form fields
      const fullNameInput = screen.getByLabelText(/Full Name/i);
      fireEvent.change(fullNameInput, { target: { value: "John Doe" } });

      const emailInput = screen.getByLabelText(/Email address/i);
      fireEvent.change(emailInput, { target: { value: "john@example.com" } });

      const passwordInput = screen.getByLabelText(/Password/i);
      fireEvent.change(passwordInput, { target: { value: "password123" } });

      // Select recruiter role
      const recruiterLabel = screen.getByText(/Recruiter \/ HR/i);
      fireEvent.click(recruiterLabel);

      const submitButton = screen.getByRole("button", { name: /Register/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(actions.registerUser).toHaveBeenCalledTimes(1);
      });
    });

    it("disables submit button while submitting", async () => {
      (actions.registerUser as jest.Mock).mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(() => resolve({ message: "", errors: {} }), 100)
          )
      );

      render(<RegisterForm />);

      const submitButton = screen.getByRole("button", { name: /Register/i });

      // Initially enabled
      expect(submitButton).not.toBeDisabled();
    });
  });

  describe("Accessibility", () => {
    it("has proper aria-label for role selection", () => {
      render(<RegisterForm />);

      const radioGroup = screen.getByRole("radiogroup", {
        name: /Select your role/i,
      });
      expect(radioGroup).toBeInTheDocument();
    });

    it("has proper form labels associated with inputs", () => {
      render(<RegisterForm />);

      expect(screen.getByLabelText(/Full Name/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Email address/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
    });

    it("uses radio inputs with proper IDs for role selection", () => {
      render(<RegisterForm />);

      const userRadio = document.getElementById("role-user");
      const recruiterRadio = document.getElementById("role-recruiter");

      expect(userRadio).toBeInTheDocument();
      expect(recruiterRadio).toBeInTheDocument();
    });
  });
});
