# AI Sub-Agents Tests

This directory contains comprehensive tests for the 3 AI sub-agents.

## Test Structure

```
tests/
├── conftest.py                    # Shared fixtures and configuration
├── test_base_agent.py             # Base agent tests
├── test_question_generator.py     # QuestionCraft AI tests
├── test_conversation_agent.py     # DialogFlow AI tests (to be expanded)
├── test_performance_evaluator.py  # EvalMaster AI tests (to be expanded)
└── integration/
    ├── test_full_interview_flow.py   # End-to-end tests
    └── test_agent_performance.py     # Performance benchmarks
```

## Running Tests

### Quick Start

```bash
# Run all unit tests (fast, no Ollama required)
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=_sub_agents --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Integration Tests

Integration tests require a running Ollama server with models loaded.

```bash
# Prerequisites
ollama serve  # In separate terminal
ollama pull llama3.2:3b-instruct-fp16
ollama pull qwen2.5:1.5b-instruct-fp16

# Run integration tests
pytest tests/ -v --run-integration
```

### Specific Test Categories

```bash
# Run only unit tests
pytest tests/ -v -m "not integration"

# Run only integration tests
pytest tests/ -v -m "integration" --run-integration

# Run only performance tests
pytest tests/ -v -m "performance"

# Run specific test file
pytest tests/test_question_generator.py -v

# Run specific test class
pytest tests/test_base_agent.py::TestOllamaAPICall -v

# Run specific test function
pytest tests/test_base_agent.py::TestOllamaAPICall::test_successful_api_call -v
```

## Test Coverage Goals

| Component | Target Coverage | Current Status |
|-----------|----------------|----------------|
| base_agent.py | 90%+ | ✅ Implemented |
| question_generator.py | 85%+ | ✅ Implemented |
| conversation_agent.py | 85%+ | 🚧 To expand |
| performance_evaluator.py | 85%+ | 🚧 To expand |

## Writing New Tests

### Test Naming Convention

```python
# Class names: Test<FeatureName>
class TestInputValidation:
    pass

# Method names: test_<what>_<condition>_<expected>
def test_validate_input_missing_field_returns_false():
    pass
```

### Using Fixtures

```python
@pytest.fixture
def sample_data():
    """Fixture docstring describing the data"""
    return {"key": "value"}

def test_something(sample_data):
    """Use fixture as function parameter"""
    assert sample_data["key"] == "value"
```

### Mocking External Dependencies

```python
from unittest.mock import Mock, patch

@patch('_sub_agents.agents.base_agent.requests.post')
def test_with_mock(mock_post):
    """Mock external HTTP calls"""
    mock_post.return_value = Mock(status_code=200)
    # ... test code
```

### Marking Tests

```python
# Mark as integration test
@pytest.mark.integration
def test_real_ollama_call():
    pass

# Mark as slow test
@pytest.mark.slow
def test_long_running():
    pass

# Mark as performance test
@pytest.mark.performance
def test_latency_benchmark():
    pass
```

## Test Data

Sample test data is available in `_sub-agents/samples/`:
- `sample_job_descriptions.md` - JD samples for different levels
- `sample_cvs.md` - CV samples for different candidates
- `sample_interview_transcripts.md` - Complete interview examples

## Debugging Tests

```bash
# Run with verbose output
pytest tests/ -vv

# Stop at first failure
pytest tests/ -x

# Drop into debugger on failure
pytest tests/ --pdb

# Show print statements
pytest tests/ -s

# Run only failed tests from last run
pytest tests/ --lf
```

## CI/CD Integration

Tests are automatically run in CI/CD pipeline:
- On every push to main branch
- On every pull request
- Nightly integration test suite

See `.github/workflows/tests.yml` for configuration.

## Performance Benchmarks

Performance tests measure:
- Latency (P50, P95, P99)
- Throughput (requests/second)
- Resource usage (CPU, memory)
- Consistency (variance across runs)

Run benchmarks:
```bash
pytest tests/integration/test_agent_performance.py -v
```

## Known Issues

1. **Ollama Connection**: Integration tests require Ollama running on localhost:11434
2. **Model Availability**: Ensure models are pulled before running integration tests
3. **Test Data**: Some tests use hardcoded Vietnamese text - may need i18n
4. **LLM Variance**: LLM outputs vary, so some assertions use ranges instead of exact matches

## Contributing

When adding new features:
1. Write tests first (TDD)
2. Ensure tests pass locally
3. Check coverage doesn't decrease
4. Update this README if adding new test categories

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Testing Guide](../TESTING_GUIDE.md) - Comprehensive testing guide
- [Integration Guide](../INTEGRATION_GUIDE.md) - Backend integration
