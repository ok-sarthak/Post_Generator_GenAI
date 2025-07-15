"""
Startup script for LinkedIn Post Generator
Handles initialization, validation, and setup
"""
import os
import sys
import json
import logging
from pathlib import Path

def setup_logging():
    """Setup logging configuration"""
    log_dir = Path("data")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('data/app.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

def check_environment():
    """Check if environment is properly configured"""
    logger = logging.getLogger(__name__)
    
    # Check for .env file
    if not os.path.exists('.env'):
        logger.warning(".env file not found. Please copy .env.example to .env and configure.")
        return False
    
    # Check for API key
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        logger.error("GROQ_API_KEY not found in .env file")
        return False
    
    if len(api_key.strip()) < 10:
        logger.error("GROQ_API_KEY appears to be invalid")
        return False
    
    logger.info("Environment configuration validated")
    return True

def setup_directories():
    """Create necessary directories"""
    logger = logging.getLogger(__name__)
    
    directories = [
        "data",
        "data/analytics",
        "data/backups"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Directory created/verified: {directory}")

def setup_data_files():
    """Initialize necessary data files"""
    logger = logging.getLogger(__name__)
    
    files_to_create = {
        "data/generated_posts_history.json": [],
        "data/prompt_templates.json": [],
        "data/analytics_cache.json": {}
    }
    
    for file_path, default_content in files_to_create.items():
        if not os.path.exists(file_path):
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(default_content, f, indent=2)
                logger.info(f"Created data file: {file_path}")
            except Exception as e:
                logger.error(f"Failed to create {file_path}: {e}")

def validate_datasets():
    """Validate that required datasets exist"""
    logger = logging.getLogger(__name__)
    
    required_datasets = [
        "data/processed_posts.json",
        "data/college_student_posts.json"
    ]
    
    missing_datasets = []
    for dataset in required_datasets:
        if not os.path.exists(dataset):
            missing_datasets.append(dataset)
    
    if missing_datasets:
        logger.warning(f"Missing datasets: {missing_datasets}")
        return False
    
    # Validate dataset format
    for dataset in required_datasets:
        try:
            with open(dataset, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, list):
                    logger.error(f"Invalid dataset format: {dataset}")
                    return False
                logger.info(f"Dataset validated: {dataset} ({len(data)} posts)")
        except Exception as e:
            logger.error(f"Error validating dataset {dataset}: {e}")
            return False
    
    return True

def check_dependencies():
    """Check if all required packages are installed"""
    logger = logging.getLogger(__name__)
    
    required_packages = [
        'streamlit',
        'langchain',
        'langchain_groq',
        'pandas',
        'python-dotenv',
        'plotly'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing required packages: {missing_packages}")
        logger.error("Please run: pip install -r requirements.txt")
        return False
    
    logger.info("All required packages are installed")
    return True

def startup_checks():
    """Run all startup checks"""
    logger = setup_logging()
    logger.info("Starting LinkedIn Post Generator...")
    
    checks = [
        ("Dependencies", check_dependencies),
        ("Environment", check_environment),
        ("Directories", lambda: (setup_directories(), True)[1]),
        ("Data Files", lambda: (setup_data_files(), True)[1]),
        ("Datasets", validate_datasets)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        try:
            if check_func():
                logger.info(f"✅ {check_name} check passed")
            else:
                logger.error(f"❌ {check_name} check failed")
                all_passed = False
        except Exception as e:
            logger.error(f"❌ {check_name} check failed with error: {e}")
            all_passed = False
    
    if all_passed:
        logger.info("🚀 All startup checks passed. Application ready!")
        return True
    else:
        logger.error("⚠️ Some startup checks failed. Please review the issues above.")
        return False

def create_default_prompts():
    """Create default prompt templates"""
    default_templates = [
        {
            "name": "Student Achievement",
            "description": "Template for student achievement posts",
            "prompt": "Generate a LinkedIn post about {achievement} from a {year} year student perspective. Make it inspiring and relatable. Length: {length}, Language: {language}",
            "variables": ["achievement", "year", "length", "language"]
        },
        {
            "name": "Professional Milestone",
            "description": "Template for professional milestone posts",
            "prompt": "Create a professional LinkedIn post about {milestone}. Target audience: {audience}. Tone: {tone}. Include key learnings and insights.",
            "variables": ["milestone", "audience", "tone"]
        },
        {
            "name": "Technical Learning",
            "description": "Template for technical learning posts",
            "prompt": "Write a LinkedIn post about learning {technology}. Share the journey, challenges, and outcomes. Make it educational and engaging.",
            "variables": ["technology"]
        }
    ]
    
    templates_file = "data/prompt_templates.json"
    if os.path.exists(templates_file):
        try:
            with open(templates_file, 'r', encoding='utf-8') as f:
                existing = json.load(f)
                if existing:  # Don't overwrite existing templates
                    return
        except:
            pass
    
    with open(templates_file, 'w', encoding='utf-8') as f:
        json.dump(default_templates, f, indent=2)

def main():
    """Main startup function"""
    if startup_checks():
        create_default_prompts()
        print("\n🎉 LinkedIn Post Generator is ready!")
        print("📝 Run 'streamlit run main.py' to start the application")
        return True
    else:
        print("\n❌ Setup incomplete. Please fix the issues above before running the application.")
        return False

if __name__ == "__main__":
    main()
