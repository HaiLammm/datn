import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import { AccountActions } from "./AccountActions";

describe("AccountActions", () => {
  describe("Change Password Button", () => {
    it("renders the change password button", () => {
      render(<AccountActions />);

      expect(screen.getByTestId("change-password-button")).toBeInTheDocument();
    });

    it("change password button contains correct link", () => {
      render(<AccountActions />);

      const button = screen.getByTestId("change-password-button");
      expect(button).toHaveAttribute("href", "/forgot-password");
    });

    it("change password button displays correct text", () => {
      render(<AccountActions />);

      expect(screen.getByTestId("change-password-button")).toHaveTextContent(
        "Change Password"
      );
    });
  });

  describe("Delete Account Button", () => {
    it("renders the delete account button", () => {
      render(<AccountActions />);

      expect(screen.getByTestId("delete-account-button")).toBeInTheDocument();
    });

    it("delete account button is disabled", () => {
      render(<AccountActions />);

      expect(screen.getByTestId("delete-account-button")).toBeDisabled();
    });

    it("delete account button displays correct text", () => {
      render(<AccountActions />);

      expect(screen.getByTestId("delete-account-button")).toHaveTextContent(
        "Delete Account"
      );
    });
  });

  describe("Card Structure", () => {
    it("renders the account actions container", () => {
      render(<AccountActions />);

      expect(screen.getByTestId("account-actions")).toBeInTheDocument();
    });
  });
});
