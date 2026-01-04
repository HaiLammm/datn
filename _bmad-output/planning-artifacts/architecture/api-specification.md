# API Specification

## REST API Specification

```yaml
openapi: 3.0.0
info:
  title: AI Recruitment Platform API
  version: 1.0.0
  description: API for AI-powered CV analysis, job matching, and user management.
servers:
  - url: http://localhost:8000/api/v1
    description: Development server
  - url: https://api.ai-recruitment.com/api/v1 # Placeholder for production
    description: Production server
security:
  - CookieAuth: []
components:
  securitySchemes:
    CookieAuth:
      type: apiKey
      in: cookie
      name: access_token # The name of the cookie FastAPI sets
  schemas:
    ErrorResponse:
      type: object
      properties:
        detail:
          type: string
          description: Detailed error message
      example:
        detail: "Tài khoản không tồn tại hoặc mật khẩu không đúng."

    # Existing Auth Schemas
    UserLoginInput:
      type: object
      required:
        - email
        - password
      properties:
        email:
          type: string
          format: email
        password:
          type: string
          format: password
    UserRegisterInput:
      type: object
      required:
        - email
        - password
      properties:
        email:
          type: string
          format: email
        password:
          type: string
          format: password
    VerifyEmailInput:
      type: object
      required:
        - email
        - activation_code
      properties:
        email:
          type: string
          format: email
        activation_code:
          type: string
    User: # Placeholder for User profile schema
      type: object
      properties:
        id:
          type: string
          format: uuid
        email:
          type: string
          format: email
        is_active:
          type: boolean
        # ... other user fields

    # New CV Schemas
    CVUploadInput:
      type: object
      required:
        - file
      properties:
        file:
          type: string
          format: binary # For file upload
    CV: # Schema for CV response
      type: object
      properties:
        id:
          type: string
          format: uuid
        user_id:
          type: string
          format: uuid
        filename:
          type: string
        uploaded_at:
          type: string
          format: date-time
        parsed_content:
          type: object
        summary:
          type: string
        quality_score:
          type: integer
        ats_compatibility_feedback:
          type: string
        is_active:
          type: boolean
        extracted_skills:
          type: array
          items:
            type: string
        total_experience_years:
          type: integer
    CVList:
      type: array
      items:
        $ref: '#/components/schemas/CV'

    # New JobDescription Schemas
    JDUploadInput:
      type: object
      required:
        - title
        - description
        - file # Optional: for uploading JD document
      properties:
        file:
          type: string
          format: binary # For file upload
        title:
          type: string
        description:
          type: string
        required_skills:
          type: array
          items:
            type: string
        min_experience_years:
          type: integer
        location_type:
          type: string
          enum: [ "remote", "hybrid", "on-site" ]
        salary_min:
          type: integer
        salary_max:
          type: integer
    JobDescription:
      type: object
      properties:
        id:
          type: string
          format: uuid
        user_id:
          type: string
          format: uuid
        title:
          type: string
        description:
          type: string
        uploaded_at:
          type: string
          format: date-time
        is_active:
          type: boolean
        required_skills:
          type: array
          items:
            type: string
        min_experience_years:
          type: integer
        location_type:
          type: string
          enum: [ "remote", "hybrid", "on-site" ]
        salary_min:
          type: integer
        salary_max:
          type: integer

    CandidateMatchResult: # Placeholder for candidate matching results
      type: object
      properties:
        candidate_id:
          type: string
          format: uuid
        cv_id:
          type: string
          format: uuid
        match_score:
          type: number
          format: float
        reasons:
          type: array
          items:
            type: string

paths:
  /auth/register:
    post:
      summary: Register a new user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserRegisterInput'
      responses:
        '200':
          description: User successfully registered, activation email sent
        '400':
          description: Invalid input or user already exists
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
  /auth/verify-email:
    post:
      summary: Verify user email with activation code
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/VerifyEmailInput'
      responses:
        '200':
          description: Email successfully verified
        '400':
          description: Invalid email or activation code
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
  /auth/login:
    post:
      summary: Authenticate user and receive access tokens
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserLoginInput'
      responses:
        '200':
          description: User logged in, HttpOnly cookies set for access_token and refresh_token
          headers:
            Set-Cookie:
              schema:
                type: string
                example: "access_token=your-token; HttpOnly; Path=/; SameSite=Lax; refresh_token=your-refresh-token; HttpOnly; Path=/; SameSite=Lax;"
        '400':
          description: Invalid credentials
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
  /auth/request-password-change:
    post:
      summary: Request a password change (sends OTP) - Authenticated
      # ... other request/response schemas
      responses:
        '200':
          description: OTP sent to user email
        '401':
          description: Unauthorized
        '400':
          description: Invalid input
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
  /auth/change-password:
    post:
      summary: Change password using OTP - Authenticated
      # ... other request/response schemas
      responses:
        '200':
          description: Password successfully changed
        '401':
          description: Unauthorized
        '400':
          description: Invalid OTP or password
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
  /auth/forgot-password:
    post:
      summary: Request password reset (sends OTP) - Unauthenticated
      # ... other request/response schemas
      responses:
        '200':
          description: OTP sent to user email
        '400':
          description: Invalid email
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
  /auth/reset-password:
    post:
      summary: Reset password using OTP - Unauthenticated
      # ... other request/response schemas
      responses:
        '200':
          description: Password successfully reset
        '400':
          description: Invalid OTP or password
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

  /users/me:
    get:
      summary: Get current authenticated user's profile
      security:
        - CookieAuth: []
      responses:
        '200':
          description: Current user's profile
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '401':
          description: Unauthorized
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

  /cvs:
    post:
      summary: Upload a new CV for analysis
      security:
        - CookieAuth: []
      requestBody:
        required: true
        content:
          multipart/form-data: # For file upload
            schema:
              $ref: '#/components/schemas/CVUploadInput'
      responses:
        '201':
          description: CV uploaded and analysis initiated
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CV'
        '400':
          description: Invalid file format or request
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '401':
          description: Unauthorized
    get:
      summary: Get all CVs uploaded by the current user
      security:
        - CookieAuth: []
      responses:
        '200':
          description: List of user's CVs
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CVList'
        '401':
          description: Unauthorized

  /cvs/{cv_id}:
    get:
      summary: Get details of a specific CV by ID
      security:
        - CookieAuth: []
      parameters:
        - name: cv_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: CV details and analysis
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CV'
        '401':
          description: Unauthorized
        '404':
          description: CV not found or not owned by user
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
    delete:
      summary: Delete a specific CV by ID
      security:
        - CookieAuth: []
      parameters:
        - name: cv_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '204':
          description: CV successfully deleted
        '401':
          description: Unauthorized
        '404':
          description: CV not found or not owned by user
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

  /jobs/jd:
    post:
      summary: Upload a new Job Description
      security:
        - CookieAuth: []
      requestBody:
        required: true
        content:
          multipart/form-data: # For file upload or structured data
            schema:
              $ref: '#/components/schemas/JDUploadInput'
      responses:
        '201':
          description: Job Description uploaded and processed
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/JobDescription'
        '400':
          description: Invalid input or request
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '401':
          description: Unauthorized

  /jobs/jd/{jd_id}/candidates:
    get:
      summary: Get ranked candidates for a specific Job Description
      security:
        - CookieAuth: []
      parameters:
        - name: jd_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: List of ranked candidates
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/CandidateMatchResult'
        '401':
          description: Unauthorized
        '404':
          description: Job Description not found or not owned by user
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

  /jobs/search:
    post:
      summary: Semantic search for candidates based on query
      security:
        - CookieAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - query
              properties:
                query:
                  type: string
                  description: Natural language search query for candidates
      responses:
        '200':
          description: List of candidates matching the query
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/CandidateMatchResult'
        '401':
          description: Unauthorized
        '400':
          description: Invalid search query
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
```

---