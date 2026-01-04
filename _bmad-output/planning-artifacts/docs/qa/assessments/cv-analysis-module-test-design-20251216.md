# Test Design: CV Analysis Module

**Date:** 2025-12-16
**Designer:** Quinn (Test Architect)
**Scope:** End-to-end CV Analysis Pipeline
**Trigger:** Quality issue detected - incorrect career field classification during CV upload

---

## Executive Summary

This test design addresses a **critical accuracy issue** discovered during CV upload testing where the system incorrectly classified an IT professional's CV as a "Trade Marketing Executive" profile. The root cause analysis suggests issues in:

1. PDF text extraction quality
2. RAG context retrieval accuracy
3. LLM response validation
4. Skill extraction logic

---

## Test Strategy Overview

| Metric | Value |
|--------|-------|
| **Total test scenarios** | 47 |
| **Unit tests** | 18 (38%) |
| **Integration tests** | 19 (40%) |
| **E2E tests** | 10 (22%) |
| **Priority distribution** | P0: 15, P1: 18, P2: 10, P3: 4 |

---

## Component Architecture Under Test

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CV ANALYSIS PIPELINE                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌──────────┐│
│  │ PDF/DOCX    │──▶│ Text        │──▶│ RAG Context │──▶│ LLM      ││
│  │ Upload      │   │ Extraction  │   │ Retrieval   │   │ Analysis ││
│  └─────────────┘   └─────────────┘   └─────────────┘   └──────────┘│
│         │                │                 │                │       │
│         ▼                ▼                 ▼                ▼       │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌──────────┐│
│  │ File        │   │ OCR         │   │ Embedding   │   │ Response ││
│  │ Validation  │   │ Detection   │   │ Generation  │   │ Parsing  ││
│  └─────────────┘   └─────────────┘   └─────────────┘   └──────────┘│
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Test Scenarios by Component

### Component 1: File Upload & Validation

#### AC1.1: File type validation

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| CV-UNIT-001 | Unit | P0 | Validate PDF file extension accepted | Pure validation logic |
| CV-UNIT-002 | Unit | P0 | Validate DOCX file extension accepted | Pure validation logic |
| CV-UNIT-003 | Unit | P1 | Reject invalid file types (txt, jpg, exe) | Security boundary |
| CV-UNIT-004 | Unit | P1 | Validate file size limits (max 10MB) | Resource protection |
| CV-INT-001 | Integration | P0 | Upload valid PDF creates CV record in DB | Data persistence flow |
| CV-INT-002 | Integration | P1 | Upload triggers async analysis task | Background job integration |

#### AC1.2: File storage

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| CV-INT-003 | Integration | P1 | File saved with UUID naming convention | File system interaction |
| CV-INT-004 | Integration | P2 | File permissions set correctly | Security requirement |
| CV-UNIT-005 | Unit | P2 | UUID generation is unique | Algorithm correctness |

---

### Component 2: Text Extraction (CRITICAL - Root Cause Area)

#### AC2.1: PDF text extraction

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| CV-UNIT-006 | Unit | P0 | **Extract text from standard PDF** | Core functionality |
| CV-UNIT-007 | Unit | P0 | **Extract text from multi-page PDF** | Common use case |
| CV-UNIT-008 | Unit | P0 | **Extract text preserves Vietnamese characters** | Locale support |
| CV-UNIT-009 | Unit | P1 | Handle PDF with embedded images | Edge case |
| CV-UNIT-010 | Unit | P1 | Handle password-protected PDF gracefully | Error handling |
| CV-INT-005 | Integration | P0 | **Extracted text matches original CV content** | Data integrity |
| CV-INT-006 | Integration | P0 | **Log extracted text for debugging** | Observability |

#### AC2.2: DOCX text extraction

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| CV-UNIT-011 | Unit | P1 | Extract text from DOCX paragraphs | Core functionality |
| CV-UNIT-012 | Unit | P1 | Extract text from DOCX tables | Table data capture |
| CV-INT-007 | Integration | P1 | DOCX with complex formatting extracts correctly | Real-world documents |

#### AC2.3: OCR detection and fallback

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| CV-UNIT-013 | Unit | P1 | Detect when OCR is needed (< 100 chars) | Heuristic accuracy |
| CV-UNIT-014 | Unit | P1 | Detect when OCR is needed (low printable ratio) | Heuristic accuracy |
| CV-UNIT-015 | Unit | P2 | Detect section headers presence | Heuristic accuracy |
| CV-INT-008 | Integration | P1 | OCR extraction produces readable text | OCR quality |
| CV-INT-009 | Integration | P2 | OCR handles Vietnamese text correctly | Locale support |

---

### Component 3: RAG Context Retrieval (CRITICAL - Root Cause Area)

#### AC3.1: Embedding generation

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| CV-UNIT-016 | Unit | P1 | Generate embedding from CV text | Core RAG functionality |
| CV-INT-010 | Integration | P1 | Embedding dimension matches model spec (384) | Model compatibility |

#### AC3.2: Context retrieval accuracy

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| CV-INT-011 | Integration | P0 | **IT CV retrieves IT-related job descriptions** | Relevance accuracy |
| CV-INT-012 | Integration | P0 | **Marketing CV retrieves marketing job descriptions** | Relevance accuracy |
| CV-INT-013 | Integration | P0 | **Retrieved context does NOT include unrelated fields** | Negative test |
| CV-INT-014 | Integration | P1 | Top-K results are sorted by relevance score | Ranking correctness |
| CV-INT-015 | Integration | P1 | Empty/invalid CV text returns empty context | Error handling |
| CV-INT-016 | Integration | P2 | RAG fallback when ChromaDB unavailable | Resilience |

#### AC3.3: Context formatting

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| CV-UNIT-017 | Unit | P2 | Format context for LLM prompt correctly | Prompt engineering |
| CV-UNIT-018 | Unit | P2 | Handle empty context gracefully | Edge case |

---

### Component 4: LLM Analysis (CRITICAL - Root Cause Area)

#### AC4.1: Prompt construction

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| CV-INT-017 | Integration | P0 | **Prompt includes actual CV content** | Prompt accuracy |
| CV-INT-018 | Integration | P0 | **Prompt includes relevant RAG context only** | Context pollution prevention |
| CV-INT-019 | Integration | P1 | CV content truncated to 3000 chars max | Token limit |

#### AC4.2: Response parsing and validation

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| CV-UNIT-019 | Unit | P0 | **Parse valid JSON response** | Core parsing |
| CV-UNIT-020 | Unit | P0 | **Validate score range (0-100)** | Data integrity |
| CV-UNIT-021 | Unit | P0 | **Validate criteria sub-scores (0-100)** | Data integrity |
| CV-UNIT-022 | Unit | P1 | Handle malformed JSON gracefully | Error handling |
| CV-UNIT-023 | Unit | P1 | Validate skills is array of strings | Type validation |
| CV-INT-020 | Integration | P1 | Retry on Ollama API timeout | Resilience |

#### AC4.3: Analysis accuracy validation (NEW - CRITICAL)

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| CV-E2E-001 | E2E | P0 | **IT Developer CV produces IT-related summary** | Accuracy validation |
| CV-E2E-002 | E2E | P0 | **Marketing CV produces marketing-related summary** | Accuracy validation |
| CV-E2E-003 | E2E | P0 | **Extracted skills match actual CV skills** | Skill extraction accuracy |
| CV-E2E-004 | E2E | P0 | **Experience years extracted correctly** | Data accuracy |
| CV-E2E-005 | E2E | P1 | Summary language matches CV language | Locale handling |

---

### Component 5: Data Persistence

#### AC5.1: Analysis result storage

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| CV-INT-021 | Integration | P1 | Analysis results saved to CVAnalysis table | Data persistence |
| CV-INT-022 | Integration | P1 | Status transitions: PENDING → PROCESSING → COMPLETED | State machine |
| CV-INT-023 | Integration | P1 | Status transitions: PENDING → PROCESSING → FAILED | Error state |
| CV-INT-024 | Integration | P2 | Analysis timestamp recorded correctly | Audit trail |

---

### Component 6: End-to-End User Journeys

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| CV-E2E-006 | E2E | P0 | **Upload IT CV → Get accurate IT analysis** | Critical path |
| CV-E2E-007 | E2E | P1 | Upload Marketing CV → Get accurate marketing analysis | Critical path |
| CV-E2E-008 | E2E | P1 | Upload bilingual CV → Analysis handles both languages | Locale support |
| CV-E2E-009 | E2E | P2 | Poll status until COMPLETED | Async flow |
| CV-E2E-010 | E2E | P2 | Delete CV removes analysis records | Cascade delete |

---

## Specific Test Cases for Discovered Issue

Based on the bug where an IT CV was classified as "Trade Marketing Executive", these tests are **MANDATORY**:

### Golden Test Cases (P0)

```python
# Test Case: CV-E2E-001 - IT Developer CV Classification
def test_it_developer_cv_produces_it_summary():
    """
    Given: A CV containing IT skills (Python, JavaScript, React)
    When: The CV is analyzed
    Then: 
        - ai_summary mentions IT/Software/Developer (NOT marketing)
        - extracted_skills contains programming languages
        - experience_breakdown.industries includes "IT" or "Software"
    """
    cv_content = "Luong Hai Lam - Full Stack Developer..."
    result = analyze_cv(cv_content)
    
    assert "marketing" not in result.ai_summary.lower()
    assert "trade" not in result.ai_summary.lower()
    assert "hygiene" not in result.ai_summary.lower()
    assert any(skill in result.extracted_skills for skill in ["Python", "JavaScript", "React"])

# Test Case: CV-INT-013 - RAG Context Relevance
def test_rag_does_not_return_unrelated_jobs():
    """
    Given: CV text about IT/Software development
    When: RAG retrieves context
    Then: Retrieved job descriptions are IT-related, NOT marketing/hygiene
    """
    cv_text = "Experience with Python, Django, React, PostgreSQL..."
    context = rag_service.retrieve_context(cv_text)
    
    for doc in context:
        assert "trade marketing" not in doc.content.lower()
        assert "hygiene products" not in doc.content.lower()

# Test Case: CV-INT-017 - Prompt Includes Actual CV
def test_prompt_contains_actual_cv_content():
    """
    Given: A CV with specific identifiable content
    When: LLM prompt is constructed
    Then: Prompt contains the actual CV content, not training data
    """
    unique_marker = "UNIQUE_TEST_MARKER_12345"
    cv_text = f"Name: Test User. Skills: {unique_marker}"
    
    prompt = build_analysis_prompt(cv_text, rag_context)
    
    assert unique_marker in prompt
```

---

## Risk Coverage

| Risk ID | Risk Description | Test Coverage |
|---------|------------------|---------------|
| RISK-001 | Wrong career field classification | CV-E2E-001, CV-E2E-002, CV-INT-011, CV-INT-012 |
| RISK-002 | RAG retrieves unrelated context | CV-INT-013, CV-INT-014 |
| RISK-003 | LLM hallucinates from training data | CV-INT-017, CV-INT-018, CV-E2E-003 |
| RISK-004 | PDF text extraction failure | CV-UNIT-006, CV-UNIT-007, CV-INT-005 |
| RISK-005 | Vietnamese text corruption | CV-UNIT-008, CV-INT-009 |
| RISK-006 | Skills mismatch | CV-E2E-003, CV-UNIT-023 |

---

## Recommended Execution Order

### Phase 1: Fail Fast (P0 Critical)
1. CV-UNIT-006, CV-UNIT-007, CV-UNIT-008 (Text extraction)
2. CV-INT-005, CV-INT-006 (Extraction verification)
3. CV-INT-011, CV-INT-012, CV-INT-013 (RAG accuracy)
4. CV-INT-017, CV-INT-018 (Prompt construction)
5. CV-E2E-001, CV-E2E-002 (End-to-end accuracy)

### Phase 2: Core Functionality (P1)
1. All remaining INT tests
2. E2E-005 through E2E-008

### Phase 3: Edge Cases (P2+)
1. P2 unit tests
2. P2 integration tests
3. P3 if time permits

---

## Test Data Requirements

### Sample CVs Needed

| CV Type | Language | Purpose |
|---------|----------|---------|
| IT Developer | English | Baseline IT classification |
| IT Developer | Vietnamese | Vietnamese locale testing |
| Marketing Manager | English | Marketing classification |
| Mixed/Bilingual | EN/VI | Bilingual handling |
| Scanned PDF | Vietnamese | OCR testing |
| Complex formatting | English | Extraction robustness |

### ChromaDB Test Data

- Create isolated test collection
- Seed with controlled job descriptions
- Ensure clear separation between IT and Marketing domains

---

## Observability Recommendations

To debug future classification issues:

1. **Log extracted CV text** before RAG query
2. **Log RAG retrieved documents** with scores
3. **Log full LLM prompt** sent to Ollama
4. **Log raw LLM response** before parsing
5. **Add trace IDs** for end-to-end request tracking

---

## Quality Gate YAML Block

```yaml
test_design:
  module: cv-analysis
  date: 2025-12-16
  scenarios_total: 47
  by_level:
    unit: 18
    integration: 19
    e2e: 10
  by_priority:
    p0: 15
    p1: 18
    p2: 10
    p3: 4
  coverage_gaps: []
  critical_tests:
    - CV-E2E-001: IT CV accuracy validation
    - CV-E2E-002: Marketing CV accuracy validation
    - CV-INT-013: RAG relevance validation
    - CV-INT-017: Prompt content validation
  risk_mitigations:
    RISK-001: [CV-E2E-001, CV-E2E-002, CV-INT-011, CV-INT-012]
    RISK-002: [CV-INT-013, CV-INT-014]
    RISK-003: [CV-INT-017, CV-INT-018, CV-E2E-003]
```

---

## Trace References

```
Test design matrix: docs/qa/assessments/cv-analysis-module-test-design-20251216.md
P0 tests identified: 15
Critical accuracy tests: 5 (CV-E2E-001 through CV-E2E-005)
Recommended immediate action: Implement CV-INT-006 (log extracted text) for debugging
```

---

## Appendix: Test Implementation Priority

### Immediate (This Sprint)
1. **CV-INT-006**: Add logging for extracted text
2. **CV-INT-013**: RAG relevance validation test
3. **CV-E2E-001**: IT CV golden test

### Short Term (Next Sprint)
1. All P0 tests
2. P1 integration tests

### Medium Term
1. Full test suite implementation
2. CI/CD integration
