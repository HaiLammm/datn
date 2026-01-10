"""
Unit tests for QuestionGeneratorAgent
Tests question generation functionality
"""

import pytest
from unittest.mock import Mock, patch
import json
from _sub_agents.agents.question_generator import QuestionGeneratorAgent


@pytest.fixture
def agent():
    """Create QuestionGeneratorAgent instance with mocked dependencies"""
    with patch.object(QuestionGeneratorAgent, '__init__', lambda x, y=None: None):
        agent = QuestionGeneratorAgent.__new__(QuestionGeneratorAgent)
        agent.agent_id = "question-generator"
        agent.model = "llama3.2:3b-instruct-fp16"
        agent.prompt_template = "Test prompt template"
        agent.quality_settings = {
            "min_questions_per_level": 3,
            "category_distribution": {
                "technical": 0.6,
                "behavioral": 0.2,
                "situational": 0.2
            },
            "required_fields": [
                "question_id", "category", "difficulty", 
                "question_text", "key_points"
            ]
        }
        agent.min_questions = 3
        agent.required_fields = agent.quality_settings["required_fields"]
        agent.category_distribution = agent.quality_settings["category_distribution"]
        agent.config = {"logging": {}}
        agent.logger = Mock()
        return agent


class TestInputValidation:
    """Test input validation"""
    
    def test_valid_input(self, agent, sample_job_description, sample_cv):
        """Test validation passes with valid input"""
        input_data = {
            "job_description": sample_job_description,
            "cv_content": sample_cv,
            "position_level": "middle"
        }
        
        assert agent._validate_input(input_data) == True
    
    def test_missing_job_description(self, agent, sample_cv):
        """Test validation fails without job description"""
        input_data = {
            "cv_content": sample_cv,
            "position_level": "middle"
        }
        
        assert agent._validate_input(input_data) == False
    
    def test_empty_fields(self, agent):
        """Test validation fails with empty fields"""
        input_data = {
            "job_description": "",
            "cv_content": "Some CV",
            "position_level": "middle"
        }
        
        assert agent._validate_input(input_data) == False


class TestPromptBuilding:
    """Test prompt construction"""
    
    def test_basic_prompt_structure(
        self, agent, sample_job_description, sample_cv
    ):
        """Test prompt includes all required elements"""
        input_data = {
            "job_description": sample_job_description,
            "cv_content": sample_cv,
            "position_level": "middle",
            "num_questions": 10
        }
        
        prompt = agent._build_prompt(input_data)
        
        assert "Backend Developer" in prompt
        assert "Nguyễn Văn A" in prompt
        assert "middle" in prompt
        assert "10" in prompt
    
    def test_prompt_with_focus_areas(
        self, agent, sample_job_description, sample_cv
    ):
        """Test prompt includes focus areas when provided"""
        input_data = {
            "job_description": sample_job_description,
            "cv_content": sample_cv,
            "position_level": "middle",
            "num_questions": 10,
            "focus_areas": ["FastAPI", "PostgreSQL"]
        }
        
        prompt = agent._build_prompt(input_data)
        
        assert "FastAPI" in prompt
        assert "PostgreSQL" in prompt


class TestCategoryDistribution:
    """Test question category distribution"""
    
    def test_calculate_distribution(self, agent):
        """Test distribution calculation"""
        questions = [
            {"category": "technical"},
            {"category": "technical"},
            {"category": "technical"},
            {"category": "behavioral"},
            {"category": "situational"}
        ]
        
        distribution = agent._calculate_distribution(questions)
        
        assert distribution["technical"] == 3
        assert distribution["behavioral"] == 1
        assert distribution["situational"] == 1
    
    def test_empty_questions(self, agent):
        """Test distribution with no questions"""
        distribution = agent._calculate_distribution([])
        
        assert distribution["technical"] == 0
        assert distribution["behavioral"] == 0
        assert distribution["situational"] == 0


class TestOutputValidation:
    """Test output validation"""
    
    def test_valid_output(self, agent):
        """Test validation passes with valid output"""
        output = {
            "questions": [
                {
                    "question_id": "Q1",
                    "category": "technical",
                    "difficulty": "middle",
                    "question_text": "Test question?",
                    "key_points": ["point1", "point2"],
                    "ideal_answer_outline": "Test outline",
                    "evaluation_criteria": ["criteria1"]
                },
                {
                    "question_id": "Q2",
                    "category": "behavioral",
                    "difficulty": "middle",
                    "question_text": "Another question?",
                    "key_points": ["point1"],
                    "ideal_answer_outline": "Outline",
                    "evaluation_criteria": ["criteria1"]
                },
                {
                    "question_id": "Q3",
                    "category": "situational",
                    "difficulty": "middle",
                    "question_text": "Third question?",
                    "key_points": ["point1"],
                    "ideal_answer_outline": "Outline",
                    "evaluation_criteria": ["criteria1"]
                }
            ]
        }
        
        assert agent._validate_output(output) == True
    
    def test_missing_questions_field(self, agent):
        """Test validation fails without questions field"""
        output = {"status": "success"}
        
        assert agent._validate_output(output) == False
    
    def test_insufficient_questions(self, agent):
        """Test validation fails with too few questions"""
        output = {
            "questions": [
                {
                    "question_id": "Q1",
                    "category": "technical",
                    "difficulty": "middle",
                    "question_text": "Only one question",
                    "key_points": ["point1"]
                }
            ]
        }
        
        # min_questions is 3
        assert agent._validate_output(output) == False
    
    def test_missing_required_fields(self, agent):
        """Test validation fails with missing required fields"""
        output = {
            "questions": [
                {
                    "question_id": "Q1",
                    "category": "technical"
                    # Missing: difficulty, question_text, key_points
                },
                {"question_id": "Q2", "category": "behavioral"},
                {"question_id": "Q3", "category": "situational"}
            ]
        }
        
        assert agent._validate_output(output) == False


class TestConvenienceMethod:
    """Test generate_questions convenience method"""
    
    @patch.object(QuestionGeneratorAgent, 'process')
    def test_generate_questions_calls_process(
        self, mock_process, agent, sample_job_description, sample_cv
    ):
        """Test convenience method calls process correctly"""
        mock_process.return_value = {"status": "success", "questions": []}
        
        result = agent.generate_questions(
            job_description=sample_job_description,
            cv_content=sample_cv,
            position_level="middle",
            num_questions=5
        )
        
        assert mock_process.called
        call_args = mock_process.call_args[0][0]
        assert call_args["job_description"] == sample_job_description
        assert call_args["cv_content"] == sample_cv
        assert call_args["position_level"] == "middle"
        assert call_args["num_questions"] == 5


# Create placeholder test files for other agents
# These would be expanded similarly
