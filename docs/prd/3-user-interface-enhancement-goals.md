# 3. User Interface Enhancement Goals

### 3.1. Integration with Existing UI
New UI elements and components will strictly adhere to the project's established design system, utilizing Shadcn/ui and Tailwind CSS. Integration will prioritize reusability of existing UI components and maintain visual consistency with the defined color palette, typography ('Be Vietnam Pro'), and global styling patterns. The focus will be on extending existing patterns to accommodate new features, rather than introducing new, disparate design languages.

### 3.2. Modified/New Screens and Views
*   **For Job Seekers:**
    *   **CV Upload and Analysis Page:** A dedicated interface for uploading CVs, triggering analysis, and viewing results (summary, score, feedback).
    *   **CV History Page:** A screen to display a list of previously uploaded CVs and their respective analysis outputs.
*   **For Talent Seekers:**
    *   **JD Upload and Candidate Search Page:** An interface for uploading Job Descriptions, performing semantic candidate searches, and reviewing matched profiles.
*   **For Administrators:**
    *   **Admin Monitoring Dashboard:** A dashboard to display real-time AI resource utilization (GPU/RAM), inference latency, and system logs access.
    *   **User Management Console:** An interface to view a list of users and perform basic actions like banning or suspending accounts.

### 3.3. UI Consistency Requirements
To maintain UI consistency, all new and modified components shall:
*   Utilize `cn()` for merging Tailwind CSS classes.
*   Avoid inline `style={{}}` attributes and separate CSS files.
*   Strictly adhere to the defined color palette and 'Be Vietnam Pro' typography.
*   Follow established interaction patterns and component usages (e.g., Shadcn/ui button variants, input styles).
