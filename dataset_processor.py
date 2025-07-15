"""
Enhanced Dataset Processor for LinkedIn Post Generator
Automatically processes raw datasets into structured format
"""
import json
import os
import pandas as pd
from datetime import datetime
from llm_helper import llm
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
import logging
from typing import List, Dict, Any, Optional
import streamlit as st

logger = logging.getLogger(__name__)

class DatasetProcessor:
    def __init__(self):
        self.processed_datasets = {}
        
    def process_uploaded_dataset(self, uploaded_file, dataset_name: str) -> str:
        """
        Process an uploaded dataset and save both raw and processed versions
        
        Args:
            uploaded_file: Streamlit uploaded file object
            dataset_name: Name for the dataset
            
        Returns:
            str: Path to processed dataset file
        """
        try:
            # Load raw data
            raw_data = json.load(uploaded_file)
            
            # Validate raw data format
            if not isinstance(raw_data, list):
                raise ValueError("Dataset must be a list of posts")
            
            # Save raw dataset first
            if not dataset_name.startswith('raw_'):
                raw_filename = f"data/raw_{dataset_name}.json"
            else:
                raw_filename = f"data/{dataset_name}.json"
            
            # Save the raw dataset
            with open(raw_filename, 'w', encoding='utf-8') as f:
                json.dump(raw_data, f, indent=2, ensure_ascii=False)
            
            st.success(f"✅ Raw dataset saved: {raw_filename}")
            
            # Process each post
            processed_posts = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, post in enumerate(raw_data):
                status_text.text(f"Processing post {i+1}/{len(raw_data)}...")
                progress_bar.progress((i + 1) / len(raw_data))
                
                processed_post = self.process_single_post(post)
                if processed_post:
                    processed_posts.append(processed_post)
            
            # Save processed dataset
            if dataset_name.startswith('raw_'):
                # raw_tech_students -> processed_raw_tech_students
                processed_filename = f"data/processed_{dataset_name}.json"
            else:
                # custom_dataset -> processed_raw_custom_dataset
                processed_filename = f"data/processed_raw_{dataset_name}.json"
            
            self.save_processed_dataset(processed_posts, processed_filename)
            
            status_text.text("✅ Processing completed!")
            st.success(f"✅ Processed dataset saved: {processed_filename}")
            
            return processed_filename
            
        except Exception as e:
            logger.error(f"Error processing dataset: {e}")
            raise
    
    def process_single_post(self, post: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a single post and extract metadata"""
        try:
            # Ensure we have text content
            if 'text' not in post or not post['text']:
                logger.warning("Skipping post without text content")
                return None
            
            text = post['text']
            
            # Extract metadata using AI
            metadata = self.extract_post_metadata(text)
            
            # Combine original post with extracted metadata
            processed_post = {
                'text': text,
                'engagement': post.get('engagement', 0),
                **metadata
            }
            
            return processed_post
            
        except Exception as e:
            logger.error(f"Error processing single post: {e}")
            return None
    
    def extract_post_metadata(self, text: str) -> Dict[str, Any]:
        """Extract metadata from post text using AI"""
        template = '''
        You are an expert at analyzing LinkedIn posts. Extract the following metadata from the given post:
        
        1. line_count: Count the number of lines in the post
        2. language: Determine if the post is in "English" or "Hinglish" (mix of Hindi and English)
        3. tags: Extract 2-4 relevant topic tags that describe the main themes of the post
        4. length_category: Categorize as "Short" (1-5 lines), "Medium" (6-10 lines), or "Long" (11+ lines)
        5. tone: Identify the tone as "Professional", "Casual", "Humorous", "Inspirational", or "Educational"
        6. target_audience: Identify target audience as "Students", "Professionals", "Job Seekers", "Entrepreneurs", or "General"
        
        Return ONLY a valid JSON object with these fields. No additional text.
        
        Post to analyze:
        {post_text}
        '''
        
        try:
            pt = PromptTemplate.from_template(template)
            chain = pt | llm
            response = chain.invoke(input={"post_text": text})
            
            json_parser = JsonOutputParser()
            metadata = json_parser.parse(response.content)
            
            # Validate and normalize the extracted data
            normalized_metadata = self.normalize_metadata(metadata, text)
            
            return normalized_metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            # Return default metadata if AI extraction fails
            return self.get_default_metadata(text)
    
    def normalize_metadata(self, metadata: Dict[str, Any], text: str) -> Dict[str, Any]:
        """Normalize and validate extracted metadata"""
        
        # Calculate line count from actual text
        line_count = len(text.split('\n'))
        
        # Normalize length category based on actual line count
        if line_count <= 5:
            length = "Short"
        elif line_count <= 10:
            length = "Medium"
        else:
            length = "Long"
        
        # Ensure tags is a list
        tags = metadata.get('tags', [])
        if isinstance(tags, str):
            tags = [tags]
        elif not isinstance(tags, list):
            tags = []
        
        # Validate language
        language = metadata.get('language', 'English')
        if language not in ['English', 'Hinglish']:
            language = 'English'
        
        # Validate tone
        valid_tones = ['Professional', 'Casual', 'Humorous', 'Inspirational', 'Educational']
        tone = metadata.get('tone', 'Professional')
        if tone not in valid_tones:
            tone = 'Professional'
        
        # Validate target audience
        valid_audiences = ['Students', 'Professionals', 'Job Seekers', 'Entrepreneurs', 'General']
        target_audience = metadata.get('target_audience', 'General')
        if target_audience not in valid_audiences:
            target_audience = 'General'
        
        return {
            'line_count': line_count,
            'language': language,
            'tags': tags[:4],  # Limit to 4 tags
            'length': length,
            'tone': tone,
            'target_audience': target_audience
        }
    
    def get_default_metadata(self, text: str) -> Dict[str, Any]:
        """Get default metadata when AI extraction fails"""
        line_count = len(text.split('\n'))
        
        if line_count <= 5:
            length = "Short"
        elif line_count <= 10:
            length = "Medium"
        else:
            length = "Long"
        
        return {
            'line_count': line_count,
            'language': 'English',
            'tags': ['General'],
            'length': length,
            'tone': 'Professional',
            'target_audience': 'General'
        }
    
    def save_processed_dataset(self, processed_posts: List[Dict[str, Any]], filename: str):
        """Save processed dataset to file"""
        try:
            # Ensure data directory exists
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Add processing metadata
            dataset_metadata = {
                'processed_at': datetime.now().isoformat(),
                'total_posts': len(processed_posts),
                'processor_version': '2.0.0'
            }
            
            # Save the dataset
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(processed_posts, f, indent=2, ensure_ascii=False)
            
            # Save metadata separately
            metadata_filename = filename.replace('.json', '_metadata.json')
            with open(metadata_filename, 'w', encoding='utf-8') as f:
                json.dump(dataset_metadata, f, indent=2)
            
            # Notify dataset manager about new dataset
            try:
                from dataset_manager import dataset_manager
                dataset_name = os.path.basename(filename).replace('processed_', '').replace('.json', '')
                dataset_manager.add_processed_dataset(filename, dataset_name)
            except ImportError:
                pass  # Dataset manager not available
            
            logger.info(f"Processed dataset saved to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving processed dataset: {e}")
            raise
            raise
    
    def process_existing_raw_dataset(self, raw_file_path: str, processed_file_path: str):
        """Process an existing raw dataset file"""
        try:
            with open(raw_file_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            processed_posts = []
            for post in raw_data:
                processed_post = self.process_single_post(post)
                if processed_post:
                    processed_posts.append(processed_post)
            
            self.save_processed_dataset(processed_posts, processed_file_path)
            return processed_file_path
            
        except Exception as e:
            logger.error(f"Error processing existing dataset: {e}")
            raise
    
    def get_processing_stats(self, processed_file_path: str) -> Dict[str, Any]:
        """Get statistics about a processed dataset"""
        try:
            with open(processed_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            df = pd.DataFrame(data)
            
            stats = {
                'total_posts': len(df),
                'languages': df['language'].value_counts().to_dict() if 'language' in df.columns else {},
                'lengths': df['length'].value_counts().to_dict() if 'length' in df.columns else {},
                'tones': df['tone'].value_counts().to_dict() if 'tone' in df.columns else {},
                'audiences': df['target_audience'].value_counts().to_dict() if 'target_audience' in df.columns else {},
                'avg_engagement': df['engagement'].mean() if 'engagement' in df.columns else 0,
                'total_tags': len(set([tag for tags in df['tags'] for tag in tags])) if 'tags' in df.columns else 0
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting processing stats: {e}")
            return {}

def demo_processing():
    """Demo function to show how processing works"""
    print("🔧 Dataset Processing Demo")
    print("=" * 40)
    
    # Sample raw posts
    sample_raw_posts = [
        {
            "text": "Just completed my first hackathon! 💻\nLearned so much about React and Node.js.\nTeam collaboration was amazing! 🚀",
            "engagement": 45
        },
        {
            "text": "Coding interview tips:\n1. Practice algorithms daily\n2. Understand system design\n3. Be confident\n4. Ask good questions\nYou got this! 💪",
            "engagement": 123
        }
    ]
    
    processor = DatasetProcessor()
    
    # Process sample posts
    processed_posts = []
    for post in sample_raw_posts:
        processed = processor.process_single_post(post)
        if processed:
            processed_posts.append(processed)
    
    print("📊 Processing Results:")
    for i, post in enumerate(processed_posts):
        print(f"\nPost {i+1}:")
        print(f"  Text: {post['text'][:50]}...")
        print(f"  Language: {post['language']}")
        print(f"  Length: {post['length']}")
        print(f"  Tags: {post['tags']}")
        print(f"  Tone: {post['tone']}")
        print(f"  Audience: {post['target_audience']}")

if __name__ == "__main__":
    demo_processing()
