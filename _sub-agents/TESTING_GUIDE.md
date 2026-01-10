# Testing Guide - AI Sub-Agents Quality Assurance

Hướng dẫn chi tiết về testing và đảm bảo chất lượng cho 3 AI sub-agents.

## 📋 Table of Contents

1. [Testing Strategy](#testing-strategy)
2. [Unit Tests](#unit-tests)
3. [Integration Tests](#integration-tests)
4. [End-to-End Tests](#end-to-end-tests)
5. [Performance Testing](#performance-testing)
6. [Quality Metrics](#quality-metrics)
7. [Test Data](#test-data)

---

## Testing Strategy

### Testing Pyramid

```
                  ┌─────────────────┐
                  │   E2E Tests     │  ← Few, slow, high value
                  │   (5-10 tests)  │
                  └─────────────────┘
                ┌───────────────────────┐
                │  Integration Tests    │  ← Medium coverage
                │  (20-30 tests)        │
                └───────────────────────┘
            ┌───────────────────────────────┐
            │      Unit Tests               │  ← High coverage
            │      (50+ tests)              │
            └───────────────────────────────┘
```

### Test Categories

1. **Unit Tests**: Test individual agent methods in isolation
2. **Integration Tests**: Test agents with real Ollama server
3. **E2E Tests**: Test complete interview flow through API
4. **Performance Tests**: Measure latency and throughput
5. **Quality Tests**: Evaluate output quality and accuracy

---

## Unit Tests

### Setup

```bash
# Install testing dependencies
pip install pytest pytest-asyncio pytest-cov pytest-mock

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=_sub_agents --cov-report=html
```

### Test Structure

```
tests/
├── __init__.py
├── conftest.py                    # Shared fixtures
├── test_base_agent.py             # Base agent tests
├── test_question_generator.py     # QuestionCraft AI tests
├── test_conversation_agent.py     # DialogFlow AI tests
├── test_performance_evaluator.py  # EvalMaster AI tests
└── integration/
    ├── test_full_interview_flow.py
    └── test_agent_performance.py
```

### Example: test_question_generator.py

```python
import pytest
from _sub_agents.agents.question_generator import QuestionGeneratorAgent
from unittest.mock import Mock, patch
import json

@pytest.fixture
def agent():
    """Create QuestionGeneratorAgent instance"""
    return QuestionGeneratorAgent()

@pytest.fixture
def sample_input():
    """Sample input data for testing"""
    return {
        "job_description": "Backend Developer với 2+ năm kinh nghiệm Python...",
        "cv_content": "Nguyễn Văn A, 3 năm kinh nghiệm...",
        "position_level": "middle",
        "num_questions": 5
    }

class TestQuestionGeneratorAgent:
    
    def test_initialization(self, agent):
        """Test agent initializes correctly"""
        assert agent.agent_id == "question-generator"
        assert agent.model == "llama3.2:3b-instruct-fp16"
        assert agent.prompt_template is not None
    
    def test_validate_input_success(self, agent, sample_input):
        """Test input validation with valid data"""
        assert agent._validate_input(sample_input) == True
    
    def test_validate_input_missing_field(self, agent):
        """Test input validation fails with missing field"""
        invalid_input = {
            "job_description": "Test JD"
            # Missing cv_content and position_level
        }
        assert agent._validate_input(invalid_input) == False
    
    def test_build_prompt(self, agent, sample_input):
        """Test prompt building includes all input data"""
        prompt = agent._build_prompt(sample_input)
        
        assert "Backend Developer" in prompt
        assert "Nguyễn Văn A" in prompt
        assert "middle" in prompt
        assert "5" in prompt
    
    @patch('_sub_agents.agents.base_agent.requests.post')
    def test_generate_questions_success(self, mock_post, agent, sample_input):
        """Test successful question generation"""
        # Mock Ollama API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": json.dumps({
                "questions": [
                    {
                        "question_id": "Q1",
                        "category": "technical",
                        "difficulty": "middle",
                        "question_text": "Test question?",
                        "key_points": ["point1", "point2"],
                        "ideal_answer_outline": "Test outline",
                        "evaluation_criteria": ["criteria1"]
                    }
                ]
            })
        }
        mock_post.return_value = mock_response
        
        result = agent.generate_questions(**sample_input)
        
        assert result["status"] == "success"
        assert len(result["questions"]) >= 1
        assert "metadata" in result
    
    @patch('_sub_agents.agents.base_agent.requests.post')
    def test_generate_questions_retry_on_failure(self, mock_post, agent, sample_input):
        """Test retry logic on API failure"""
        # First call fails, second succeeds
        mock_post.side_effect = [
            Exception("Connection error"),
            Mock(
                status_code=200,
                json=lambda: {"response": json.dumps({"questions": []})}
            )
        ]
        
        # Should retry and succeed
        result = agent.generate_questions(**sample_input)
        
        assert mock_post.call_count == 2
    
    def test_calculate_distribution(self, agent):
        """Test category distribution calculation"""
        questions = [
            {"category": "technical"},
            {"category": "technical"},
            {"category": "behavioral"},
            {"category": "situational"}
        ]
        
        distribution = agent._calculate_distribution(questions)
        
        assert distribution["technical"] == 2
        assert distribution["behavioral"] == 1
        assert distribution["situational"] == 1
    
    def test_validate_output_missing_questions(self, agent):
        """Test output validation fails when questions missing"""
        invalid_output = {"status": "success"}
        
        assert agent._validate_output(invalid_output) == False
    
    def test_validate_output_insufficient_questions(self, agent):
        """Test output validation fails with too few questions"""
        invalid_output = {
            "questions": [
                {"question_id": "Q1", "category": "technical"}
            ]
        }
        
        # Assuming min_questions is 3
        assert agent._validate_output(invalid_output) == False

@pytest.mark.integration
class TestQuestionGeneratorIntegration:
    """Integration tests requiring actual Ollama server"""
    
    @pytest.mark.skipif(
        "not config.getoption('--run-integration')",
        reason="Integration tests only run with --run-integration flag"
    )
    def test_real_question_generation(self, agent, sample_input):
        """Test with real Ollama API call"""
        result = agent.generate_questions(**sample_input)
        
        assert result["status"] == "success"
        assert len(result["questions"]) == sample_input["num_questions"]
        
        # Validate first question structure
        first_q = result["questions"][0]
        assert "question_id" in first_q
        assert "category" in first_q
        assert "question_text" in first_q
        assert len(first_q["question_text"]) > 20
```

### Running Tests

```bash
# Run only unit tests (fast)
pytest tests/ -v -m "not integration"

# Run integration tests (requires Ollama)
pytest tests/ -v --run-integration

# Run specific test file
pytest tests/test_question_generator.py -v

# Run with coverage
pytest tests/ --cov=_sub_agents --cov-report=term-missing
```

---

## Integration Tests

### Prerequisites

- Ollama server running on localhost:11434
- Models downloaded: llama3.2:3b-instruct-fp16, qwen2.5:1.5b-instruct-fp16

### Test Full Interview Flow

```python
import pytest
from _sub_agents.agents.question_generator import QuestionGeneratorAgent
from _sub_agents.agents.conversation_agent import ConversationAgent
from _sub_agents.agents.performance_evaluator import PerformanceEvaluatorAgent

@pytest.mark.integration
class TestFullInterviewFlow:
    
    @pytest.fixture
    def agents(self):
        """Initialize all agents"""
        return {
            "question": QuestionGeneratorAgent(),
            "conversation": ConversationAgent(),
            "evaluator": PerformanceEvaluatorAgent()
        }
    
    @pytest.fixture
    def interview_data(self):
        """Sample interview data"""
        with open("_sub-agents/samples/sample_job_descriptions.md") as f:
            jd_content = f.read()
        with open("_sub-agents/samples/sample_cvs.md") as f:
            cv_content = f.read()
        
        return {
            "jd": jd_content.split("## Sample 1")[1].split("---")[0],
            "cv": cv_content.split("## Sample 1")[1].split("---")[0]
        }
    
    async def test_complete_interview_flow(self, agents, interview_data):
        """Test complete flow: generate → converse → evaluate"""
        
        # Step 1: Generate questions
        questions_result = agents["question"].generate_questions(
            job_description=interview_data["jd"],
            cv_content=interview_data["cv"],
            position_level="middle",
            num_questions=3
        )
        
        assert questions_result["status"] == "success"
        questions = questions_result["questions"]
        assert len(questions) == 3
        
        # Step 2: Simulate conversation
        conversation_history = []
        turn_evaluations = []
        
        for question in questions:
            # Mock candidate answer
            candidate_answer = "Tôi có 3 năm kinh nghiệm với Python và FastAPI..."
            
            turn_result = agents["conversation"].process_turn(
                interview_id="test_interview_123",
                current_question=question,
                candidate_answer=candidate_answer,
                conversation_history=conversation_history
            )
            
            assert turn_result["status"] == "success"
            assert "turn_evaluation" in turn_result
            assert "next_action" in turn_result
            
            # Add to history
            conversation_history.append({
                "question": question["question_text"],
                "answer": candidate_answer,
                "score": turn_result["turn_evaluation"]["answer_quality"]["overall_score"]
            })
            turn_evaluations.append(turn_result["turn_evaluation"])
        
        # Step 3: Final evaluation
        eval_result = agents["evaluator"].evaluate_interview(
            interview_id="test_interview_123",
            candidate_info={
                "name": "Nguyễn Văn A",
                "position": "Backend Developer",
                "level": "middle"
            },
            interview_transcript=[
                {
                    "ai_message": q["question_text"],
                    "candidate_message": "Sample answer..."
                }
                for q in questions
            ],
            questions_asked=questions,
            turn_evaluations=turn_evaluations
        )
        
        assert eval_result["status"] == "success"
        assert "overall_evaluation" in eval_result
        assert 0 <= eval_result["overall_evaluation"]["final_score"] <= 10
        assert eval_result["overall_evaluation"]["hiring_recommendation"] in [
            "strong_hire", "hire", "consider", "no_hire"
        ]
```

---

## Performance Testing

### Latency Benchmarks

```python
import pytest
import time
from statistics import mean, stdev

@pytest.mark.performance
class TestAgentPerformance:
    
    def test_question_generator_latency(self, agent, sample_input):
        """Measure question generation latency"""
        latencies = []
        
        for _ in range(10):  # Run 10 times
            start = time.time()
            agent.generate_questions(**sample_input)
            latency = (time.time() - start) * 1000  # ms
            latencies.append(latency)
        
        avg_latency = mean(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
        
        print(f"\nAvg latency: {avg_latency:.0f}ms")
        print(f"P95 latency: {p95_latency:.0f}ms")
        print(f"Std dev: {stdev(latencies):.0f}ms")
        
        # Assert P95 < 5000ms (target)
        assert p95_latency < 5000, f"P95 latency {p95_latency}ms exceeds target"
```

### Load Testing

```python
import asyncio
import aiohttp

async def load_test_agent(num_concurrent=10):
    """Load test with concurrent requests"""
    async def make_request():
        # Simulate API call
        start = time.time()
        result = agent.generate_questions(...)
        return time.time() - start
    
    tasks = [make_request() for _ in range(num_concurrent)]
    latencies = await asyncio.gather(*tasks)
    
    print(f"Concurrent requests: {num_concurrent}")
    print(f"Avg latency: {mean(latencies)*1000:.0f}ms")
    print(f"Max latency: {max(latencies)*1000:.0f}ms")
```

---

## Quality Metrics

### Output Quality Evaluation

```python
def evaluate_question_quality(questions):
    """Manually evaluate question quality"""
    scores = {
        "relevance": 0,     # Are questions relevant to JD/CV?
        "clarity": 0,       # Are questions clear and well-worded?
        "depth": 0,         # Do questions probe deep understanding?
        "diversity": 0      # Good mix of categories?
    }
    
    # Check diversity
    categories = [q["category"] for q in questions]
    unique_categories = len(set(categories))
    scores["diversity"] = unique_categories / 3  # 3 categories total
    
    # Manual review needed for other scores
    # ...
    
    return scores
```

### Acceptance Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Question Relevance | > 80% | Manual review by domain experts |
| Response Time (P95) | < 5s | Automated performance tests |
| Category Distribution | 60-20-20 ± 10% | Automated validation |
| Question Clarity | > 85% | Manual review + readability scores |
| Evaluation Accuracy | > 75% agreement | Compare with human evaluators |

---

## Test Data Management

### Sample Data Structure

```
samples/
├── jd_samples/
│   ├── backend_junior.txt
│   ├── backend_middle.txt
│   └── backend_senior.txt
├── cv_samples/
│   ├── candidate_a.txt
│   ├── candidate_b.txt
│   └── candidate_c.txt
└── expected_outputs/
    ├── questions_middle.json
    └── evaluation_report.json
```

### Golden Test Cases

Maintain golden test cases for regression testing:

```python
GOLDEN_TESTS = [
    {
        "name": "middle_backend_standard",
        "jd": "samples/jd_samples/backend_middle.txt",
        "cv": "samples/cv_samples/candidate_a.txt",
        "expected_min_questions": 10,
        "expected_categories": ["technical", "behavioral", "situational"],
        "expected_difficulty": "middle"
    }
]
```

---

## CI/CD Integration

### GitHub Actions Workflow

```yaml
name: AI Agents Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      ollama:
        image: ollama/ollama:latest
        ports:
          - 11434:11434
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Pull Ollama models
        run: |
          ollama pull llama3.2:3b-instruct-fp16
          ollama pull qwen2.5:1.5b-instruct-fp16
      
      - name: Run unit tests
        run: pytest tests/ -v -m "not integration" --cov
      
      - name: Run integration tests
        run: pytest tests/ -v --run-integration
      
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

---

## Manual Testing Checklist

### Before Release

- [ ] All automated tests passing
- [ ] Manual review of 10 sample question sets
- [ ] Manual review of 5 conversation flows
- [ ] Manual review of 5 evaluation reports
- [ ] Performance benchmarks meet targets
- [ ] No regressions from previous version
- [ ] Documentation updated
- [ ] Integration tests with actual backend API
- [ ] Load testing with expected traffic
- [ ] Edge cases tested (empty inputs, very long inputs, etc.)

---

## Troubleshooting Tests

### Common Issues

**Issue**: Tests fail with "Connection refused"
**Solution**: Ensure Ollama server is running: `ollama serve`

**Issue**: Tests timeout
**Solution**: Increase timeout in config or use smaller test samples

**Issue**: Inconsistent test results
**Solution**: LLM outputs vary - use broader assertions or mock responses

**Issue**: Performance tests fail on CI
**Solution**: CI runners are slower - adjust targets or skip on CI

---

For more information, see:
- [README.md](./README.md) - Project overview
- [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) - Backend integration
- [PROMPT_TUNING.md](./PROMPT_TUNING.md) - Prompt customization
