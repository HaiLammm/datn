import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import { ProfileCard } from "./ProfileCard";
import type { User } from "@datn/shared-types";

function createMockUser(overrides: Partial<User> = {}): User {
  return {
    id: "1",
    email: "test@example.com",
    role: "job_seeker",
    is_active: true,
    created_at: "2025-01-15T10:30:00Z",
    updated_at: "2025-01-15T10:30:00Z",
    ...overrides,
  };
}

describe("ProfileCard", () => {
  describe("User Email Display", () => {
    it("renders user email correctly", () => {
      const user = createMockUser({ email: "johndoe@example.com" });
      render(<ProfileCard user={user} />);

      expect(screen.getByTestId("profile-email")).toHaveTextContent(
        "johndoe@example.com"
      );
    });
  });

  describe("Member Since Date", () => {
    it("renders member since date correctly formatted", () => {
      const user = createMockUser({ created_at: "2025-01-15T10:30:00Z" });
      render(<ProfileCard user={user} />);

      expect(screen.getByTestId("profile-member-since")).toHaveTextContent(
        "January 15, 2025"
      );
    });

    it("shows N/A when created_at is undefined", () => {
      const user = createMockUser({ created_at: undefined });
      render(<ProfileCard user={user} />);

      expect(screen.getByTestId("profile-member-since")).toHaveTextContent(
        "N/A"
      );
    });
  });

  describe("Avatar Placeholder", () => {
    it("displays first letter of email as fallback when no full name", () => {
      const user = createMockUser({
        email: "test@example.com",
        full_name: undefined,
      });
      render(<ProfileCard user={user} />);

      expect(screen.getByTestId("avatar-fallback")).toHaveTextContent("T");
    });

    it("displays initials from full name when available", () => {
      const user = createMockUser({ full_name: "John Doe" });
      render(<ProfileCard user={user} />);

      expect(screen.getByTestId("avatar-fallback")).toHaveTextContent("JD");
    });

    it("displays single initial for single-word name", () => {
      const user = createMockUser({ full_name: "John" });
      render(<ProfileCard user={user} />);

      expect(screen.getByTestId("avatar-fallback")).toHaveTextContent("J");
    });

    it("handles multi-word names correctly", () => {
      const user = createMockUser({ full_name: "John Michael Doe" });
      render(<ProfileCard user={user} />);

      // Should take first and last name initials
      expect(screen.getByTestId("avatar-fallback")).toHaveTextContent("JD");
    });
  });

  describe("Full Name Display", () => {
    it("displays full name when provided", () => {
      const user = createMockUser({ full_name: "John Doe" });
      render(<ProfileCard user={user} />);

      expect(screen.getByTestId("profile-full-name")).toHaveTextContent(
        "John Doe"
      );
    });

    it("does not display full name element when not provided", () => {
      const user = createMockUser({ full_name: undefined });
      render(<ProfileCard user={user} />);

      expect(screen.queryByTestId("profile-full-name")).not.toBeInTheDocument();
    });
  });

  describe("Card Structure", () => {
    it("renders the profile card container", () => {
      const user = createMockUser();
      render(<ProfileCard user={user} />);

      expect(screen.getByTestId("profile-card")).toBeInTheDocument();
    });

    it("renders the avatar element", () => {
      const user = createMockUser();
      render(<ProfileCard user={user} />);

      expect(screen.getByTestId("profile-avatar")).toBeInTheDocument();
    });
  });
});
