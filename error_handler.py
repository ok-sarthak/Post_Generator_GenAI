"""
Error handling and validation utilities for the LinkedIn Post Generator
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class PostValidationError(Exception):
    """Custom exception for post validation errors"""
    pass


class DatasetError(Exception):
    """Custom exception for dataset-related errors"""
    pass


class LLMError(Exception):
    """Custom exception for LLM-related errors"""
    pass


def validate_post_data(post: Dict[str, Any]) -> bool:
    """
    Validate post data structure
    
    Args:
        post: Dictionary containing post data
        
    Returns:
        bool: True if valid, raises exception if invalid
        
    Raises:
        PostValidationError: If post data is invalid
    """
    required_fields = ['text']
    optional_fields = ['engagement', 'line_count', 'language', 'tags', 'length']
    
    try:
        # Check required fields
        for field in required_fields:
            if field not in post:
                raise PostValidationError(f"Missing required field: {field}")
            
            if not post[field] or (isinstance(post[field], str) and not post[field].strip()):
                raise PostValidationError(f"Field '{field}' cannot be empty")
        
        # Validate field types
        if not isinstance(post['text'], str):
            raise PostValidationError("'text' field must be a string")
        
        if 'engagement' in post and not isinstance(post['engagement'], (int, float)):
            raise PostValidationError("'engagement' field must be a number")
        
        if 'line_count' in post and not isinstance(post['line_count'], int):
            raise PostValidationError("'line_count' field must be an integer")
        
        if 'language' in post and post['language'] not in ['English', 'Hinglish']:
            raise PostValidationError("'language' field must be 'English' or 'Hinglish'")
        
        if 'tags' in post and not isinstance(post['tags'], list):
            raise PostValidationError("'tags' field must be a list")
        
        if 'length' in post and post['length'] not in ['Short', 'Medium', 'Long']:
            raise PostValidationError("'length' field must be 'Short', 'Medium', or 'Long'")
        
        logger.info("Post validation successful")
        return True
        
    except Exception as e:
        logger.error(f"Post validation failed: {e}")
        raise


def validate_dataset_file(file_path: str) -> bool:
    """
    Validate dataset file structure and content
    
    Args:
        file_path: Path to the dataset file
        
    Returns:
        bool: True if valid, raises exception if invalid
        
    Raises:
        DatasetError: If dataset is invalid
    """
    try:
        if not os.path.exists(file_path):
            raise DatasetError(f"Dataset file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            raise DatasetError("Dataset must be a list of posts")
        
        if len(data) == 0:
            logger.warning("Dataset is empty")
            return True
        
        # Validate each post
        for i, post in enumerate(data):
            try:
                validate_post_data(post)
            except PostValidationError as e:
                raise DatasetError(f"Invalid post at index {i}: {e}")
        
        logger.info(f"Dataset validation successful: {len(data)} posts")
        return True
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in dataset file: {e}")
        raise DatasetError(f"Invalid JSON format: {e}")
    except Exception as e:
        logger.error(f"Dataset validation failed: {e}")
        raise


def safe_file_operation(operation_func, *args, **kwargs):
    """
    Safely execute file operations with error handling
    
    Args:
        operation_func: Function to execute
        *args: Arguments for the function
        **kwargs: Keyword arguments for the function
        
    Returns:
        Result of the operation or None if failed
    """
    try:
        return operation_func(*args, **kwargs)
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return None
    except PermissionError as e:
        logger.error(f"Permission denied: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in file operation: {e}")
        return None


def validate_llm_response(response: str) -> bool:
    """
    Validate LLM response
    
    Args:
        response: Response from LLM
        
    Returns:
        bool: True if valid, raises exception if invalid
        
    Raises:
        LLMError: If response is invalid
    """
    try:
        if not response or not response.strip():
            raise LLMError("LLM response is empty")
        
        # Check for common error indicators
        error_indicators = [
            "I cannot",
            "I can't",
            "Error:",
            "Sorry, I",
            "I apologize"
        ]
        
        response_lower = response.lower()
        for indicator in error_indicators:
            if indicator.lower() in response_lower:
                logger.warning(f"Potential error in LLM response: {indicator}")
        
        # Check minimum length
        if len(response.strip()) < 10:
            raise LLMError("LLM response too short")
        
        logger.info("LLM response validation successful")
        return True
        
    except Exception as e:
        logger.error(f"LLM response validation failed: {e}")
        raise


def ensure_data_directory():
    """Ensure data directory exists and create necessary files"""
    try:
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            logger.info("Created data directory")
        
        # Create necessary files if they don't exist
        files_to_create = [
            "data/generated_posts_history.json",
            "data/prompt_templates.json",
            "data/app.log"
        ]
        
        for file_path in files_to_create:
            if not os.path.exists(file_path):
                if file_path.endswith('.json'):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump([], f)
                else:
                    open(file_path, 'a').close()
                logger.info(f"Created file: {file_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error ensuring data directory: {e}")
        return False


def backup_dataset(file_path: str) -> Optional[str]:
    """
    Create a backup of the dataset
    
    Args:
        file_path: Path to the dataset file
        
    Returns:
        str: Path to the backup file or None if failed
    """
    try:
        if not os.path.exists(file_path):
            logger.warning(f"Cannot backup non-existent file: {file_path}")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{file_path}.backup_{timestamp}"
        
        with open(file_path, 'r', encoding='utf-8') as src:
            with open(backup_path, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
        
        logger.info(f"Dataset backed up to: {backup_path}")
        return backup_path
        
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        return None


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        str: Sanitized text
    """
    if not isinstance(text, str):
        return ""
    
    # Remove potentially harmful characters
    sanitized = text.strip()
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
        logger.warning(f"Input truncated to {max_length} characters")
    
    return sanitized


def check_api_key() -> bool:
    """
    Check if API key is configured
    
    Returns:
        bool: True if API key is available
    """
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.error("GROQ_API_KEY not found in environment variables")
            return False
        
        if len(api_key.strip()) < 10:  # Basic length check
            logger.error("GROQ_API_KEY appears to be invalid (too short)")
            return False
        
        logger.info("API key validation successful")
        return True
        
    except Exception as e:
        logger.error(f"Error checking API key: {e}")
        return False


def handle_llm_error(error: Exception) -> str:
    """
    Handle LLM-related errors and provide user-friendly messages
    
    Args:
        error: Exception that occurred
        
    Returns:
        str: User-friendly error message
    """
    error_str = str(error).lower()
    
    if "api key" in error_str or "authentication" in error_str:
        return "❌ API key error. Please check your GROQ_API_KEY in the .env file."
    elif "rate limit" in error_str or "quota" in error_str:
        return "⏱️ Rate limit exceeded. Please wait a moment and try again."
    elif "network" in error_str or "connection" in error_str:
        return "🌐 Network error. Please check your internet connection."
    elif "model" in error_str and "not found" in error_str:
        return "🤖 Model not available. The AI model might be temporarily unavailable."
    elif "timeout" in error_str:
        return "⏰ Request timeout. The service is taking too long to respond."
    else:
        logger.error(f"Unexpected LLM error: {error}")
        return "❌ An unexpected error occurred. Please try again later."


# Initialize data directory on import
ensure_data_directory()
