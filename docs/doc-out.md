# Epic: Robust Multilayered CV Processing Pipeline (RAG)

## Epic Summary
*   **Epic Title:** Robust Multilayered CV Processing Pipeline (RAG) - Brownfield Enhancement
*   **Goal:** To establish a robust, multilayered CV processing pipeline using Retrieval-Augmented Generation (RAG) to significantly improve the accuracy of data extraction and the depth of analysis for all submitted CVs. This addresses the current LLM's limitations in handling diverse CV formats and languages.

## Completed User Stories

### 1. Story: Implement Advanced Preprocessing and OCR Layer
*   **As a** System Administrator/Backend Process, **I want** to automatically detect if a CV is text-based or image-based and process it through an appropriate pathway (standard text extraction or a new OCR service), **so that** all uploaded CVs, regardless of format, can be accurately converted into raw text for the next stage of the AI analysis pipeline.

### 2. Story: Integrate RAG with Vector Database
*   **As an** AI analysis service, **I want** to augment the LLM's understanding by retrieving relevant context (e.g., job descriptions, scoring criteria) from a vector database (ChromaDB), **so that** the LLM can perform a more informed, accurate, and context-aware CV analysis, especially when determining qualification status and suggesting relevant roles.

### 3. Story: Develop Final Analysis and Structured JSON Output
*   **As an** AI analysis service, **I want to** leverage the RAG-augmented context to guide the LLM in generating a structured JSON output that includes a qualification status, a detailed score, comprehensive reasoning, and suggested roles, **so that** this rich, predictable data can be reliably stored in the database and consumed by the frontend to provide a more detailed and valuable user experience.
