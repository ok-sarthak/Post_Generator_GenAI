"""
Centralized Dataset Manager for the LinkedIn Post Generator
Handles all dataset operations and state management
"""
import os
import json
from typing import Dict, List, Optional

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False


class DatasetManager:
    def __init__(self):
        self.data_dir = "data"
        self.ensure_data_directory()
        
    def ensure_data_directory(self):
        """Ensure data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def get_available_datasets(self) -> Dict[str, str]:
        """Get all available datasets with display names - only return processed datasets"""
        datasets = {}
        
        # System files to exclude
        system_files = {
            'dataset_mappings.json',
            'prompt_templates.json', 
            'generated_posts_history.json',
            'analytics_report.json'
        }
        
        if os.path.exists(self.data_dir):
            for file in os.listdir(self.data_dir):
                if (file.endswith('.json') and 
                    not file.endswith('_metadata.json') and 
                    not file.endswith('_history.json') and
                    file not in system_files):
                    
                    file_path = os.path.join(self.data_dir, file)
                    
                    # Check if this is a properly processed dataset
                    if self._is_processed_dataset(file_path):
                        # Create display name from filename
                        display_name = self._create_display_name(file)
                        datasets[display_name] = file_path
        
        return datasets
    
    def get_current_dataset(self) -> str:
        """Get the currently selected dataset path"""
        if STREAMLIT_AVAILABLE and hasattr(st, 'session_state'):
            if 'current_dataset' not in st.session_state:
                # Set default dataset
                available = self.get_available_datasets()
                if available:
                    st.session_state.current_dataset = list(available.values())[0]
                else:
                    st.session_state.current_dataset = "data/processed_posts.json"
            
            return st.session_state.current_dataset
        else:
            # Fallback when streamlit is not available
            available = self.get_available_datasets()
            if available:
                return list(available.values())[0]
            else:
                return "data/processed_posts.json"
    
    def set_current_dataset(self, dataset_path: str):
        """Set the current dataset and update session state"""
        if STREAMLIT_AVAILABLE and hasattr(st, 'session_state'):
            st.session_state.current_dataset = dataset_path
            # Force refresh of dependent components
            if 'dataset_changed' not in st.session_state:
                st.session_state.dataset_changed = 0
            st.session_state.dataset_changed += 1
    
    def get_current_dataset_name(self) -> str:
        """Get the display name of the current dataset"""
        current_path = self.get_current_dataset()
        datasets = self.get_available_datasets()
        
        for name, path in datasets.items():
            if path == current_path:
                return name
        
        return os.path.basename(current_path).replace('.json', '').replace('_', ' ').title()
    
    def dataset_exists(self, dataset_path: str) -> bool:
        """Check if a dataset file exists"""
        return os.path.exists(dataset_path)
    
    def get_dataset_info(self, dataset_path: str) -> Optional[Dict]:
        """Get basic information about a dataset"""
        if not self.dataset_exists(dataset_path):
            return None
        
        try:
            with open(dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not data:
                return {"total_posts": 0, "languages": [], "tags": []}
            
            # Extract basic info
            languages = set()
            tags = set()
            
            for post in data:
                if 'language' in post:
                    languages.add(post['language'])
                if 'tags' in post and isinstance(post['tags'], list):
                    tags.update(post['tags'])
            
            return {
                "total_posts": len(data),
                "languages": list(languages),
                "tags": list(tags),
                "file_size": os.path.getsize(dataset_path)
            }
            
        except Exception as e:
            print(f"Error getting dataset info: {e}")
            return None
    
    def validate_dataset(self, dataset_path: str) -> tuple[bool, str]:
        """Validate if a dataset has the required structure"""
        if not self.dataset_exists(dataset_path):
            return False, "Dataset file not found"
        
        try:
            with open(dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                return False, "Dataset must be a list of posts"
            
            if not data:
                return False, "Dataset is empty"
            
            # Check if posts have required fields
            required_fields = ['text']
            sample_post = data[0]
            
            for field in required_fields:
                if field not in sample_post:
                    return False, f"Posts missing required field: {field}"
            
            return True, "Dataset is valid"
            
        except json.JSONDecodeError:
            return False, "Invalid JSON format"
        except Exception as e:
            return False, f"Error validating dataset: {str(e)}"
    
    def add_processed_dataset(self, file_path: str, display_name: str = None):
        """Add a newly processed dataset to the available datasets"""
        if display_name:
            # Create a mapping file for custom display names
            mapping_file = os.path.join(self.data_dir, "dataset_mappings.json")
            
            if os.path.exists(mapping_file):
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    mappings = json.load(f)
            else:
                mappings = {}
            
            mappings[os.path.basename(file_path)] = display_name
            
            with open(mapping_file, 'w', encoding='utf-8') as f:
                json.dump(mappings, f, indent=2, ensure_ascii=False)
    
    def remove_dataset(self, dataset_path: str) -> bool:
        """Remove a dataset file"""
        try:
            if os.path.exists(dataset_path):
                os.remove(dataset_path)
                
                # If this was the current dataset, switch to another one
                if self.get_current_dataset() == dataset_path:
                    available = self.get_available_datasets()
                    if available:
                        self.set_current_dataset(list(available.values())[0])
                
                return True
        except Exception as e:
            print(f"Error removing dataset: {e}")
        
        return False
    
    def get_dataset_statistics(self, dataset_path: str = None) -> Optional[Dict]:
        """Get detailed statistics for a dataset"""
        if dataset_path is None:
            dataset_path = self.get_current_dataset()
        
        info = self.get_dataset_info(dataset_path)
        if not info:
            return None
        
        try:
            with open(dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Calculate detailed statistics
            stats = {
                "total_posts": len(data),
                "languages": {},
                "lengths": {},
                "tones": {},
                "audiences": {},
                "total_tags": len(info['tags']),
                "avg_engagement": 0
            }
            
            total_engagement = 0
            engagement_count = 0
            
            for post in data:
                # Language distribution
                lang = post.get('language', 'Unknown')
                stats['languages'][lang] = stats['languages'].get(lang, 0) + 1
                
                # Length distribution
                length = post.get('length', 'Unknown')
                stats['lengths'][length] = stats['lengths'].get(length, 0) + 1
                
                # Tone distribution
                tone = post.get('tone', 'Unknown')
                stats['tones'][tone] = stats['tones'].get(tone, 0) + 1
                
                # Audience distribution
                audience = post.get('target_audience', 'Unknown')
                stats['audiences'][audience] = stats['audiences'].get(audience, 0) + 1
                
                # Engagement stats
                if 'engagement' in post and isinstance(post['engagement'], (int, float)):
                    total_engagement += post['engagement']
                    engagement_count += 1
            
            if engagement_count > 0:
                stats['avg_engagement'] = total_engagement / engagement_count
            
            return stats
            
        except Exception as e:
            print(f"Error calculating statistics: {e}")
            return None
    
    def _is_processed_dataset(self, dataset_path: str) -> bool:
        """Check if a dataset is properly processed and ready for few-shot learning"""
        try:
            with open(dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not data or not isinstance(data, list):
                return False
            
            # Check if the first post has required fields for few-shot learning
            sample_post = data[0]
            required_fields = ['text', 'tags']  # Minimum required for post generation
            
            for field in required_fields:
                if field not in sample_post:
                    return False
            
            # Check if tags is a list and not empty
            if not isinstance(sample_post.get('tags'), list) or len(sample_post.get('tags', [])) == 0:
                return False
            
            return True
            
        except Exception as e:
            print(f"Error checking dataset {dataset_path}: {e}")
            return False

    def get_raw_datasets(self) -> Dict[str, str]:
        """Get raw (unprocessed) datasets that can be processed"""
        raw_datasets = {}
        
        # System files to exclude
        system_files = {
            'dataset_mappings.json',
            'prompt_templates.json', 
            'generated_posts_history.json',
            'analytics_report.json'
        }
        
        if os.path.exists(self.data_dir):
            for file in os.listdir(self.data_dir):
                if (file.endswith('.json') and 
                    not file.endswith('_metadata.json') and 
                    not file.endswith('_history.json') and
                    file not in system_files):
                    
                    file_path = os.path.join(self.data_dir, file)
                    
                    # Check if this is a raw dataset (not processed)
                    if not self._is_processed_dataset(file_path):
                        display_name = self._create_display_name(file, is_raw=True)
                        raw_datasets[display_name] = file_path
        
        return raw_datasets

    def _create_display_name(self, filename: str, is_raw: bool = False) -> str:
        """Create a proper display name from filename"""
        # Remove .json extension
        name = filename.replace('.json', '')
        
        # Handle different naming patterns
        if name.startswith('raw_'):
            # raw_tech_students -> Tech Students (Raw)
            base_name = name.replace('raw_', '').replace('_', ' ').title()
            if is_raw:
                return f"{base_name} (Raw)"
            else:
                return base_name
        elif name.startswith('processed_raw_'):
            # processed_raw_tech_students -> Tech Students
            return name.replace('processed_raw_', '').replace('_', ' ').title()
        elif name.startswith('processed_'):
            # processed_something -> Something
            return name.replace('processed_', '').replace('_', ' ').title()
        else:
            # Handle legacy names
            clean_name = name.replace('_', ' ').title()
            
            # Special cases for known datasets
            name_mappings = {
                'College Student Posts': 'College Student Journey',
                'Processed Posts': 'Professional Posts',
                'Sample Raw Dataset': 'Sample Dataset (Raw)' if is_raw else 'Sample Dataset'
            }
            
            return name_mappings.get(clean_name, clean_name)

# Global dataset manager instance
dataset_manager = DatasetManager()
