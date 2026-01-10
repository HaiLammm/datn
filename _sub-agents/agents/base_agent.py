"""
Base Agent Class for Ollama-based AI Agents
Provides common functionality for all sub-agents
"""

import json
import time
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import requests
from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """
    Base class for all Ollama-based AI agents.
    Handles common operations like API calls, config loading, logging, and error handling.
    """

    def __init__(self, config_path: str):
        """
        Initialize the base agent with configuration.
        
        Args:
            config_path: Path to the JSON configuration file
        """
        self.config = self._load_config(config_path)
        self.logger = self._setup_logger()
        self.prompt_template = self._load_prompt()
        
        # Extract key config values
        self.agent_id = self.config.get("agent_id")
        self.agent_name = self.config.get("agent_name")
        self.model = self.config.get("model")
        self.ollama_host = self.config.get("ollama_settings", {}).get("host", "http://localhost:11434")
        self.timeout = self.config.get("ollama_settings", {}).get("timeout", 30)
        self.max_retries = self.config.get("performance_settings", {}).get("max_retries", 2)
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
    
    def _load_prompt(self) -> str:
        """Load system prompt template from file."""
        prompt_file = self.config.get("prompt_settings", {}).get("prompt_file")
        if not prompt_file:
            raise ValueError("prompt_file not specified in configuration")
        
        # Resolve relative path from config directory
        config_dir = Path(__file__).parent.parent
        prompt_path = config_dir / prompt_file
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger for the agent."""
        log_level = self.config.get("logging", {}).get("log_level", "INFO")
        logger = logging.getLogger(self.config.get("agent_id", "base_agent"))
        logger.setLevel(getattr(logging, log_level))
        
        # Create console handler if not already exists
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _call_ollama_api(self, prompt: str, model_params: Optional[Dict] = None) -> str:
        """
        Make API call to Ollama server.
        
        Args:
            prompt: The complete prompt to send to the model
            model_params: Optional model parameters to override defaults
            
        Returns:
            Raw response text from the model
        """
        url = f"{self.ollama_host}/api/generate"
        
        # Merge default model params with overrides
        params = self.config.get("model_parameters", {}).copy()
        if model_params:
            params.update(model_params)
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": params
        }
        
        # Add keep_alive if specified
        keep_alive = self.config.get("ollama_settings", {}).get("keep_alive")
        if keep_alive:
            payload["keep_alive"] = keep_alive
        
        start_time = time.time()
        
        try:
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            elapsed_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Log performance
            if self.config.get("logging", {}).get("log_latency", True):
                self.logger.info(f"API call completed in {elapsed_time:.0f}ms")
            
            return result.get("response", "")
            
        except requests.exceptions.Timeout:
            raise TimeoutError(f"Ollama API call timed out after {self.timeout}s")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama API call failed: {e}")
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON from model response, handling common formatting issues.
        
        Args:
            response: Raw response text from model
            
        Returns:
            Parsed JSON as dictionary
        """
        # Try to extract JSON from markdown code blocks
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            response = response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            response = response[start:end].strip()
        
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response: {e}")
            self.logger.debug(f"Raw response: {response}")
            raise ValueError(f"Invalid JSON in model response: {e}")
    
    def _retry_on_failure(self, func, *args, **kwargs):
        """
        Retry a function call on failure.
        
        Args:
            func: Function to call
            *args, **kwargs: Arguments to pass to function
            
        Returns:
            Result from successful function call
        """
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < self.max_retries:
                    self.logger.warning(
                        f"Attempt {attempt + 1} failed: {e}. Retrying..."
                    )
                    time.sleep(1 * (attempt + 1))  # Exponential backoff
                else:
                    self.logger.error(f"All {self.max_retries + 1} attempts failed")
        
        raise last_error
    
    def _validate_required_fields(self, data: Dict, required_fields: List[str]) -> bool:
        """
        Validate that all required fields are present in data.
        
        Args:
            data: Dictionary to validate
            required_fields: List of required field names
            
        Returns:
            True if all fields present, False otherwise
        """
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            self.logger.error(f"Missing required fields: {missing_fields}")
            return False
        
        return True
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and return result.
        This method must be implemented by subclasses.
        
        Args:
            input_data: Input data specific to the agent
            
        Returns:
            Processing result as dictionary
        """
        pass
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "model": self.model,
            "ollama_host": self.ollama_host,
            "config": self.config
        }
