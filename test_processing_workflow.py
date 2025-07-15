"""
Test the complete dataset processing workflow
"""
import sys
import os
sys.path.append('.')

from dataset_processor import DatasetProcessor
import json

def test_complete_workflow():
    """Test the complete dataset processing workflow"""
    print("🔄 Testing Complete Dataset Processing Workflow")
    print("=" * 60)
    
    # Initialize processor
    processor = DatasetProcessor()
    
    # Load sample raw dataset
    raw_file = "data/sample_raw_dataset.json"
    processed_file = "data/processed_sample_dataset.json"
    
    print(f"📁 Processing raw dataset: {raw_file}")
    
    try:
        # Process the dataset
        processor.process_existing_raw_dataset(raw_file, processed_file)
        print(f"✅ Successfully processed dataset!")
        print(f"📁 Processed file saved as: {processed_file}")
        
        # Get processing statistics
        stats = processor.get_processing_stats(processed_file)
        
        print("\n📊 Processing Statistics:")
        print(f"  Total Posts: {stats['total_posts']}")
        print(f"  Languages: {stats['languages']}")
        print(f"  Lengths: {stats['lengths']}")
        print(f"  Tones: {stats['tones']}")
        print(f"  Audiences: {stats['audiences']}")
        print(f"  Average Engagement: {stats['avg_engagement']:.1f}")
        print(f"  Unique Tags: {stats['total_tags']}")
        
        # Show sample processed post
        with open(processed_file, 'r', encoding='utf-8') as f:
            processed_data = json.load(f)
        
        print("\n📝 Sample Processed Post:")
        sample_post = processed_data[0]
        print(f"  Text: {sample_post['text'][:100]}...")
        print(f"  Language: {sample_post['language']}")
        print(f"  Length: {sample_post['length']}")
        print(f"  Tags: {sample_post['tags']}")
        print(f"  Tone: {sample_post['tone']}")
        print(f"  Audience: {sample_post['target_audience']}")
        print(f"  Engagement: {sample_post['engagement']}")
        
        # Test few-shot learning with processed dataset
        print("\n🎯 Testing Few-Shot Learning with Processed Dataset:")
        from few_shot import FewShotPosts
        fs = FewShotPosts(processed_file)
        print(f"  Loaded dataset: {len(fs.df)} posts")
        print(f"  Available tags: {fs.get_tags()}")
        
        # Test filtering
        if fs.get_tags():
            first_tag = fs.get_tags()[0]
            filtered_posts = fs.get_filtered_posts("Medium", "English", first_tag)
            print(f"  Found {len(filtered_posts)} posts for tag '{first_tag}'")
        
        print("\n✅ Complete workflow test successful!")
        
    except Exception as e:
        print(f"❌ Error in workflow: {e}")

if __name__ == "__main__":
    test_complete_workflow()
