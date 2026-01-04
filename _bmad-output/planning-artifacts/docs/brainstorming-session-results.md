# Brainstorming Session Results

**Session Date:** 2025-12-12
**Facilitator:** Business Analyst Mary
**Participant:** User

## Executive Summary

**Topic:** Robust Multilayered CV Processing Pipeline (RAG)

**Session Goals:** Focused Ideation on Solving Specific Known Problems related to the RAG pipeline, specifically: Extraction Accuracy, Analysis Quality, and Structured Output.

**Techniques Used:** Morphological Analysis, Question Storming, First Principles Thinking

**Total Ideas Generated:** 15+ (across all components)

### Key Themes Identified:
- **Tiered/Hybrid Strategies:** A recurring theme was the use of multi-step, hybrid approaches to balance speed with accuracy (e.g., tiered routing heuristic, hybrid query formulation).
- **Explicit Prompt Engineering:** A strong emphasis on creating highly detailed and structured prompts to guide the LLM's behavior and ensure reliable, structured output.
- **Robustness and Fallbacks:** Designing for failure by implementing clear fallback strategies for JSON parsing and other potential points of failure.
- **Data-Driven Decisions:** Relying on Proof-of-Concept (PoC) testing to determine optimal parameters (e.g., OCR library choice, `top-k` value).

---

## Technique Sessions

### Morphological Analysis - Breaking down the pipeline

**Description:** The session involved breaking down the "Robust Multilayered CV Processing Pipeline (RAG)" into its core components and sub-components to create a clear map for focused ideation.

**Ideas Generated:**
1.  **Component 1: Input Preprocessing** (File Routing & Text Extraction)
    - 1.A: Heuristic/Routing Logic
    - 1.B: OCR Library Selection
    - 1.C: Text Splitting/Enhancement
2.  **Component 2: RAG Setup** (Knowledge Base & Indexing)
    - 2.A: Indexing Content
    - 2.B: Indexing Chunking
    - 2.C: Embedding Model
3.  **Component 3: Context Augmentation** (RAG Retrieval Strategy)
    - 3.A: Query Formulation
    - 3.B: Retrieval Parameter (top-k)
    - 3.C: Retrieval Type
4.  **Component 4: LLM Core Analysis** (Prompt Strategy & Engineering)
    - 4.A: Prompt Augmentation
    - 4.B: LLM Role/Instruction
    - 4.C: Scoring Logic Integration
5.  **Component 5: Structured Data Output** (Output Parsing & Validation)
    - 5.A: JSON Enforcing Method
    - 5.B: Output Schema Fields
    - 5.C: Parsing Fallback

**Insights Discovered:**
- By breaking the pipeline into distinct components, it became clear that each stage requires its own tailored strategy rather than a one-size-fits-all solution.

---

## Idea Categorization

### Immediate Opportunities
*Ideas ready to implement now as part of the 3-story plan.*

1.  **Tiered "Fail-Fast" Routing Heuristic**
    - Description: Use a sequence of checks (Character Count -> Text Object Ratio -> Garbled Text Check) to efficiently route CVs for OCR.
    - Why immediate: It's a core requirement for Story 1 and directly addresses performance and accuracy constraints.
    - Resources needed: Python libraries for PDF parsing (existing), possibly a lightweight NLP library.
2.  **Hybrid RAG Query Formulation**
    - Description: Combine a precise query from structured JSON data with a contextual query from the CV's experience section.
    - Why immediate: This is a core part of Story 2 and is critical for retrieving relevant context for the LLM.
    - Resources needed: Vector DB client, embedding model client.
3.  **Layered JSON Enforcement and Validation**
    - Description: Use Pydantic schema injection in the prompt, followed by strict validation and a lightweight `json_repair` fallback.
    - Why immediate: This is a core requirement for Story 3 to ensure data integrity and system stability.
    - Resources needed: `json_repair` library (or similar).

### Future Innovations
*Ideas requiring further development/research post-MVP.*

1.  **Automated Knowledge Base Updates**
    - Description: A system to automatically ingest new Job Descriptions or updated scoring rubrics into the Vector DB.
    - Development needed: A separate service or scheduled task to monitor for new documents, process, chunk, and embed them.
    - Timeline estimate: Post-MVP, 1-2 sprints.
2.  **Dynamic `top-k` Adjustment**
    - Description: Instead of a fixed `top-k`, dynamically adjust the number of retrieved documents based on the complexity of the CV or the ambiguity of the query.
    - Development needed: Research and PoC into query analysis techniques.
    - Timeline estimate: Post-MVP.

---

## Action Planning

### Top 3 Priority Ideas

1.  **Priority #1: Implement Tiered Routing Heuristic & EasyOCR PoC**
    - Rationale: This is the foundational first step (Story 1) for the entire pipeline. The choice of OCR library and the routing logic's performance are critical dependencies.
    - Next steps: Implement the tiered logic in `cv.service.py`. Conduct a PoC comparing `EasyOCR` against alternatives on a sample set of Vietnamese and English CVs.
    - Resources needed: `EasyOCR` library, sample CV documents.
    - Timeline: Within the first story's development cycle.
2.  **Priority #2: Implement Hybrid Query & Advanced RAG Retrieval**
    - Rationale: This forms the core of the "intelligence" of the system (Story 2). The quality of retrieved context directly impacts the final analysis. The decision to use Parent Document Retrieval is key.
    - Next steps: Implement the `VectorDBService` in `ai.service.py`. Develop the hybrid query logic and the three-tiered retrieval strategy (Hybrid Search -> RRF -> Parent Document Retrieval).
    - Resources needed: ChromaDB client, `nomic-embed-text` model access.
    - Timeline: Within the second story's development cycle.
3.  **Priority #3: Implement Structured Prompting & Fallback Parsing**
    - Rationale: This ensures the output is reliable, structured, and resilient (Story 3), making the data usable for the frontend and preventing system failures.
    - Next steps: Refine the LLM prompt to include the detailed structure, role, and rules. Implement the Pydantic validation and `json_repair` fallback logic in `ai.service.py`.
    - Resources needed: `json_repair` library.
    - Timeline: Within the third story's development cycle.

---

## Reflection & Follow-up

### What Worked Well
- The Morphological Analysis technique was highly effective at breaking down a complex system into manageable components.
- The focused ideation approach led to concrete, actionable strategies for each component rather than vague ideas.

### Areas for Further Exploration
- **Chunking Strategy PoC:** While we have a good strategy on paper, a small PoC to test different chunk sizes and their impact on retrieval relevance would be beneficial.
- **Reranking Algorithms:** We've chosen RRF, but exploring other reranking methods in the future could provide incremental improvements.

### Questions That Emerged
- What is the most effective way to create and manage the "Scoring Criteria" documents for the Knowledge Base?
- How will the system be stress-tested to ensure it adheres to the 300s NFR under concurrent loads?

---
*Session facilitated using the BMAD-METHOD™ brainstorming framework*
