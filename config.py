"""
Configuration settings for the LinkedIn Post Generator
"""
import os
from typing import Dict, Any

# Application Settings
APP_CONFIG = {
    "title": "LinkedIn Post Generator",
    "version": "2.0.0",
    "description": "AI-Powered Content Creation with Few-Shot Learning",
    "author": "Vacant Vectors Team"
}

# Model Settings
MODEL_CONFIG = {
    "default_model": "llama-3.3-70b-versatile",
    "fallback_models": [
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768"
    ],
    "temperature": 0.7,
    "max_tokens": 1000,
    "timeout": 30  # seconds
}

# Generation Settings
GENERATION_CONFIG = {
    "max_examples": 2,
    "min_post_length": 10,
    "max_post_length": 2000,
    "default_language": "English",
    "default_length": "Medium",
    "default_tone": "Professional"
}

# Post Length Definitions
LENGTH_DEFINITIONS = {
    "Short": {
        "lines": "1 to 5 lines",
        "words": "10-50 words",
        "description": "Quick, punchy content"
    },
    "Medium": {
        "lines": "6 to 10 lines", 
        "words": "51-150 words",
        "description": "Balanced, engaging content"
    },
    "Long": {
        "lines": "11 to 15 lines",
        "words": "151-300 words", 
        "description": "Detailed, comprehensive content"
    }
}

# Available Options
OPTIONS_CONFIG = {
    "lengths": ["Short", "Medium", "Long"],
    "languages": ["English", "Hinglish"],
    "tones": ["Professional", "Casual", "Humorous", "Inspirational", "Educational"],
    "audiences": ["Students", "Professionals", "Entrepreneurs", "Job Seekers", "General"],
    "purposes": ["Share Experience", "Give Advice", "Ask Question", "Celebrate Achievement", "Educational"],
    "styles": ["Storytelling", "List Format", "Question-Answer", "Tips & Tricks", "Personal Reflection"]
}

# File Paths
PATHS_CONFIG = {
    "data_dir": "data",
    "main_dataset": "data/processed_posts.json",
    "college_dataset": "data/college_student_posts.json",
    "history_file": "data/generated_posts_history.json",
    "templates_file": "data/prompt_templates.json",
    "log_file": "data/app.log",
    "analytics_dir": "data/analytics",
    "backups_dir": "data/backups"
}

# UI Settings
UI_CONFIG = {
    "page_title": "LinkedIn Post Generator",
    "page_icon": "📝",
    "layout": "wide",
    "sidebar_state": "expanded",
    "theme_color": "#667eea",
    "max_history_display": 20,
    "posts_per_page": 10
}

# Analytics Settings
ANALYTICS_CONFIG = {
    "enable_analytics": True,
    "chart_height": 400,
    "max_tags_display": 20,
    "export_formats": ["JSON", "CSV", "PDF"],
    "refresh_interval": 300  # seconds
}

# Error Messages
ERROR_MESSAGES = {
    "api_key_missing": "❌ API key not configured. Please check your .env file.",
    "api_key_invalid": "❌ Invalid API key. Please check your GROQ_API_KEY.",
    "rate_limit": "⏱️ Rate limit exceeded. Please wait a moment and try again.",
    "network_error": "🌐 Network error. Please check your internet connection.",
    "model_error": "🤖 Model not available. Please try again later.",
    "generation_failed": "❌ Failed to generate content. Please try again.",
    "file_not_found": "📁 File not found. Please check the file path.",
    "invalid_input": "⚠️ Invalid input. Please check your parameters.",
    "dataset_empty": "📊 Dataset is empty. Please load some posts first."
}

# Success Messages
SUCCESS_MESSAGES = {
    "post_generated": "✅ Post generated successfully!",
    "post_saved": "💾 Post saved to history.",
    "dataset_loaded": "📊 Dataset loaded successfully.",
    "template_saved": "📝 Template saved successfully.",
    "export_complete": "📤 Export completed successfully.",
    "backup_created": "🔄 Backup created successfully."
}

# Prompt Templates
DEFAULT_PROMPTS = {
    "basic_generation": """
    Generate a LinkedIn post using the below information. No preamble.
    
    1) Topic: {topic}
    2) Length: {length}
    3) Language: {language}
    4) Tone: {tone}
    
    Guidelines:
    - If Language is Hinglish, mix Hindi and English naturally
    - Use appropriate emojis for engagement
    - Include relevant hashtags if requested
    - Make the post authentic and engaging
    """,
    
    "custom_generation": """
    Generate a LinkedIn post with the following specifications. No preamble.
    
    CONTENT SPECIFICATIONS:
    1) Topic: {topic}
    2) Target Audience: {audience}
    3) Post Purpose: {purpose}
    4) Length: {length}
    5) Language: {language}
    6) Writing Style: {style}
    7) Additional Context: {context}
    8) Keywords to Include: {keywords}
    
    Make the post relatable, engaging, and valuable for the target audience.
    """,
    
    "college_student": """
    Generate a LinkedIn post from the perspective of a {year} year Computer Science student.
    
    CONTEXT:
    - Student Year: {year}
    - Event/Experience: {event}
    - Emotional Tone: {emotion}
    - Length: {length}
    - Language: {language}
    
    Make the post authentic and inspiring for fellow students.
    """
}

# Validation Rules
VALIDATION_RULES = {
    "min_topic_length": 3,
    "max_topic_length": 200,
    "min_context_length": 0,
    "max_context_length": 500,
    "max_keywords": 10,
    "min_post_quality_score": 0.5,
    "required_fields": ["text"],
    "optional_fields": ["engagement", "language", "tags", "length"]
}

# Performance Settings
PERFORMANCE_CONFIG = {
    "cache_size": 100,
    "max_concurrent_requests": 5,
    "request_timeout": 30,
    "retry_attempts": 3,
    "retry_delay": 1,  # seconds
    "memory_limit_mb": 500
}

def get_config(section: str) -> Dict[str, Any]:
    """Get configuration for a specific section"""
    configs = {
        "app": APP_CONFIG,
        "model": MODEL_CONFIG,
        "generation": GENERATION_CONFIG,
        "lengths": LENGTH_DEFINITIONS,
        "options": OPTIONS_CONFIG,
        "paths": PATHS_CONFIG,
        "ui": UI_CONFIG,
        "analytics": ANALYTICS_CONFIG,
        "errors": ERROR_MESSAGES,
        "success": SUCCESS_MESSAGES,
        "prompts": DEFAULT_PROMPTS,
        "validation": VALIDATION_RULES,
        "performance": PERFORMANCE_CONFIG
    }
    
    return configs.get(section, {})

def get_model_config() -> Dict[str, Any]:
    """Get model configuration with environment overrides"""
    config = MODEL_CONFIG.copy()
    
    # Override with environment variables if available
    if os.getenv("MODEL_NAME"):
        config["default_model"] = os.getenv("MODEL_NAME")
    
    if os.getenv("MODEL_TEMPERATURE"):
        try:
            config["temperature"] = float(os.getenv("MODEL_TEMPERATURE"))
        except ValueError:
            pass
    
    if os.getenv("MODEL_MAX_TOKENS"):
        try:
            config["max_tokens"] = int(os.getenv("MODEL_MAX_TOKENS"))
        except ValueError:
            pass
    
    return config

def get_file_path(file_key: str) -> str:
    """Get file path from configuration"""
    return PATHS_CONFIG.get(file_key, "")

def validate_config() -> bool:
    """Validate configuration settings"""
    try:
        # Check required directories
        required_dirs = [PATHS_CONFIG["data_dir"]]
        for dir_path in required_dirs:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
        
        # Validate model configuration
        model_config = get_model_config()
        if not model_config.get("default_model"):
            return False
        
        # Validate generation settings
        if GENERATION_CONFIG["max_examples"] < 1:
            return False
        
        return True
        
    except Exception:
        return False

# Initialize configuration on import
if not validate_config():
    print("Warning: Configuration validation failed. Some features may not work correctly.")
