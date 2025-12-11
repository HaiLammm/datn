# External APIs

## Email Sending Service (SMTP Provider)

-   **Purpose:** To reliably send transactional emails to users for account activation, password reset requests, and other system notifications.
-   **Documentation:** Varies by provider (e.g., SendGrid, Mailgun, AWS SES, Gmail SMTP). Typically involves standard SMTP protocol documentation.
-   **Base URL(s):** Provider-specific SMTP server address (e.g., `smtp.sendgrid.net`, `smtp.mailgun.org`, `email-smtp.us-east-1.amazonaws.com`).
-   **Authentication:** Typically requires a username (often an API key or dedicated SMTP username) and a password (or API key). Authentication is performed over TLS.
-   **Rate Limits:** Provider-specific. Free tiers usually have daily sending limits (e.g., 100-10,000 emails/day), which scale with paid plans.
-   **Key Endpoints Used:** Standard SMTP commands (`HELO`, `AUTH`, `MAIL FROM`, `RCPT TO`, `DATA`, `QUIT`).
-   **Integration Notes:**
    *   The `fastapi-mail` library handles the SMTP communication.
    *   Credentials will be stored securely as environment variables.

---