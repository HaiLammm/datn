"""
Unit tests for BaseAgent class
Tests common functionality shared by all agents
"""

import pytest
import json
from unittest.mock import Mock, patch, mock_open
from _sub_agents.agents.base_agent import BaseAgent


# Concrete implementation for testing abstract BaseAgent
class TestAgent(BaseAgent):
    """Concrete agent for testing base functionality"""
    
    def process(self, input_data):
        """Simple implementation for testing"""
        return {"status": "success", "data": input_data}


@pytest.fixture
def mock_config():
    """Mock configuration data"""
    return {
        "agent_id": "test-agent",
        "agent_name": "Test Agent",
        "model": "test-model:1b",
        "model_parameters": {
            "temperature": 0.7,
            "top_p": 0.9,
            "num_predict": 1024
        },
        "ollama_settings": {
            "host": "http://localhost:11434",
            "timeout": 30,
            "keep_alive": "5m"
        },
        "prompt_settings": {
            "prompt_file": "../prompts/test_prompt.txt",
            "output_format": "json"
        },
        "performance_settings": {
            "max_retries": 2,
            "target_latency_ms": 3000
        },
        "logging": {
            "log_level": "INFO",
            "log_requests": True
        }
    }


@pytest.fixture
def mock_prompt():
    """Mock prompt content"""
    return "You are a test agent. Process the input and return JSON."


@pytest.fixture
def agent(mock_config, mock_prompt):
    """Create TestAgent instance with mocked config and prompt"""
    with patch('builtins.open', mock_open(read_data=json.dumps(mock_config))):
        with patch.object(TestAgent, '_load_prompt', return_value=mock_prompt):
            return TestAgent("mock_config.json")


class TestBaseAgentInitialization:
    """Test agent initialization"""
    
    def test_initialization_success(self, agent):
        """Test agent initializes with correct values"""
        assert agent.agent_id == "test-agent"
        assert agent.agent_name == "Test Agent"
        assert agent.model == "test-model:1b"
        assert agent.ollama_host == "http://localhost:11434"
        assert agent.timeout == 30
        assert agent.max_retries == 2
    
    def test_load_invalid_config(self):
        """Test initialization fails with invalid config"""
        with patch('builtins.open', mock_open(read_data="invalid json")):
            with pytest.raises(ValueError):
                TestAgent("invalid_config.json")
    
    def test_config_file_not_found(self):
        """Test initialization fails when config file missing"""
        with patch('builtins.open', side_effect=FileNotFoundError):
            with pytest.raises(FileNotFoundError):
                TestAgent("missing_config.json")
    
    def test_prompt_file_not_found(self, mock_config):
        """Test initialization fails when prompt file missing"""
        with patch('builtins.open', mock_open(read_data=json.dumps(mock_config))):
            with patch.object(TestAgent, '_load_prompt', side_effect=FileNotFoundError):
                with pytest.raises(FileNotFoundError):
                    TestAgent("mock_config.json")


class TestOllamaAPICall:
    """Test Ollama API calls"""
    
    @patch('_sub_agents.agents.base_agent.requests.post')
    def test_successful_api_call(self, mock_post, agent):
        """Test successful API call to Ollama"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "Test response from model"
        }
        mock_post.return_value = mock_response
        
        result = agent._call_ollama_api("Test prompt")
        
        assert result == "Test response from model"
        assert mock_post.called
        
        # Verify call parameters
        call_args = mock_post.call_args
        assert call_args[0][0] == "http://localhost:11434/api/generate"
        payload = call_args[1]['json']
        assert payload['model'] == "test-model:1b"
        assert payload['prompt'] == "Test prompt"
        assert payload['stream'] == False
    
    @patch('_sub_agents.agents.base_agent.requests.post')
    def test_api_call_timeout(self, mock_post, agent):
        """Test API call timeout handling"""
        mock_post.side_effect = Exception("Timeout")
        
        with pytest.raises(Exception):
            agent._call_ollama_api("Test prompt")
    
    @patch('_sub_agents.agents.base_agent.requests.post')
    def test_api_call_with_custom_params(self, mock_post, agent):
        """Test API call with custom model parameters"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Test"}
        mock_post.return_value = mock_response
        
        custom_params = {"temperature": 0.5, "top_k": 20}
        agent._call_ollama_api("Test prompt", model_params=custom_params)
        
        payload = mock_post.call_args[1]['json']
        assert payload['options']['temperature'] == 0.5
        assert payload['options']['top_k'] == 20


class TestJSONParsing:
    """Test JSON response parsing"""
    
    def test_parse_valid_json(self, agent):
        """Test parsing valid JSON response"""
        response = '{"key": "value", "number": 42}'
        result = agent._parse_json_response(response)
        
        assert result == {"key": "value", "number": 42}
    
    def test_parse_json_with_markdown(self, agent):
        """Test parsing JSON wrapped in markdown code blocks"""
        response = '```json\n{"key": "value"}\n```'
        result = agent._parse_json_response(response)
        
        assert result == {"key": "value"}
    
    def test_parse_json_with_generic_code_block(self, agent):
        """Test parsing JSON in generic code blocks"""
        response = '```\n{"key": "value"}\n```'
        result = agent._parse_json_response(response)
        
        assert result == {"key": "value"}
    
    def test_parse_invalid_json(self, agent):
        """Test parsing invalid JSON raises error"""
        response = '{"key": invalid}'
        
        with pytest.raises(ValueError):
            agent._parse_json_response(response)


class TestRetryLogic:
    """Test retry mechanism"""
    
    def test_retry_success_on_second_attempt(self, agent):
        """Test function succeeds on retry"""
        mock_func = Mock(side_effect=[Exception("First fail"), "Success"])
        
        result = agent._retry_on_failure(mock_func)
        
        assert result == "Success"
        assert mock_func.call_count == 2
    
    def test_retry_exhausted(self, agent):
        """Test all retries exhausted"""
        mock_func = Mock(side_effect=Exception("Always fails"))
        
        with pytest.raises(Exception):
            agent._retry_on_failure(mock_func)
        
        # Should try max_retries + 1 times (initial + retries)
        assert mock_func.call_count == agent.max_retries + 1
    
    def test_retry_with_arguments(self, agent):
        """Test retry passes arguments correctly"""
        mock_func = Mock(side_effect=[Exception("Fail"), "Success"])
        
        result = agent._retry_on_failure(mock_func, "arg1", kwarg1="kwarg1")
        
        assert result == "Success"
        mock_func.assert_called_with("arg1", kwarg1="kwarg1")


class TestFieldValidation:
    """Test field validation"""
    
    def test_validate_all_fields_present(self, agent):
        """Test validation passes when all fields present"""
        data = {"field1": "value1", "field2": "value2", "field3": "value3"}
        required = ["field1", "field2", "field3"]
        
        assert agent._validate_required_fields(data, required) == True
    
    def test_validate_missing_field(self, agent):
        """Test validation fails when field missing"""
        data = {"field1": "value1", "field2": "value2"}
        required = ["field1", "field2", "field3"]
        
        assert agent._validate_required_fields(data, required) == False
    
    def test_validate_empty_requirements(self, agent):
        """Test validation passes with no requirements"""
        data = {"field1": "value1"}
        required = []
        
        assert agent._validate_required_fields(data, required) == True


class TestAgentInfo:
    """Test agent information methods"""
    
    def test_get_model_info(self, agent):
        """Test getting model information"""
        info = agent.get_model_info()
        
        assert info["agent_id"] == "test-agent"
        assert info["agent_name"] == "Test Agent"
        assert info["model"] == "test-model:1b"
        assert info["ollama_host"] == "http://localhost:11434"
        assert "config" in info


class TestLogging:
    """Test logging functionality"""
    
    def test_logger_setup(self, agent):
        """Test logger is properly configured"""
        assert agent.logger is not None
        assert agent.logger.name == "test-agent"
        assert agent.logger.level == 20  # INFO level
    
    @patch('_sub_agents.agents.base_agent.requests.post')
    def test_logging_enabled(self, mock_post, agent):
        """Test logging when enabled in config"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Test"}
        mock_post.return_value = mock_response
        
        with patch.object(agent.logger, 'info') as mock_log:
            agent._call_ollama_api("Test")
            
            # Should log latency
            assert mock_log.called


@pytest.mark.integration
class TestIntegrationWithRealOllama:
    """Integration tests requiring actual Ollama server"""
    
    @pytest.mark.skipif(
        "not config.getoption('--run-integration')",
        reason="Integration tests only with --run-integration flag"
    )
    def test_real_ollama_call(self, agent):
        """Test with real Ollama server"""
        # This will only run if Ollama is available
        try:
            result = agent._call_ollama_api("Say hello")
            assert isinstance(result, str)
            assert len(result) > 0
        except Exception as e:
            pytest.skip(f"Ollama not available: {e}")


# Pytest configuration
def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="run integration tests"
    )
