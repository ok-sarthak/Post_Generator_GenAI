"""
Test script to verify the LinkedIn Post Generator functionality
"""
import sys
import os
sys.path.append('.')

from few_shot import FewShotPosts
from post_generator import generate_post

def test_dataset_loading():
    """Test loading both datasets"""
    print("🧪 Testing Dataset Loading...")
    
    # Test professional posts
    try:
        fs_pro = FewShotPosts("data/processed_posts.json")
        print(f"✅ Professional posts loaded: {len(fs_pro.df)} posts")
        print(f"📊 Professional tags: {fs_pro.get_tags()[:5]}...")
    except Exception as e:
        print(f"❌ Error loading professional posts: {e}")
    
    # Test college student posts
    try:
        fs_college = FewShotPosts("data/college_student_posts.json")
        print(f"✅ College posts loaded: {len(fs_college.df)} posts")
        print(f"📊 College tags: {fs_college.get_tags()[:5]}...")
    except Exception as e:
        print(f"❌ Error loading college posts: {e}")

def test_few_shot_learning():
    """Test few-shot learning functionality"""
    print("\n🎯 Testing Few-Shot Learning...")
    
    # Test with college dataset
    try:
        fs = FewShotPosts("data/college_student_posts.json")
        
        # Find posts for college life
        college_posts = fs.get_filtered_posts("Medium", "English", "College Life")
        print(f"✅ Found {len(college_posts)} college life posts for few-shot learning")
        
        if college_posts:
            print("📝 Sample reference post:")
            print(f"   {college_posts[0]['text'][:100]}...")
        
    except Exception as e:
        print(f"❌ Error in few-shot learning: {e}")

def test_post_generation():
    """Test post generation with college dataset"""
    print("\n🚀 Testing Post Generation...")
    
    try:
        # Test generation with college dataset
        post = generate_post(
            length="Medium",
            language="English", 
            tag="College Life",
            tone="Casual",
            dataset_path="data/college_student_posts.json"
        )
        
        print("✅ Post generated successfully!")
        print("📝 Generated post:")
        print(f"   {post}")
        
    except Exception as e:
        print(f"❌ Error generating post: {e}")

def main():
    """Run all tests"""
    print("🔧 Vacant Vectors LinkedIn Post Generator - Test Suite")
    print("=" * 60)
    
    test_dataset_loading()
    test_few_shot_learning()
    
    # Only test generation if we have API key
    if os.getenv('GROQ_API_KEY'):
        test_post_generation()
    else:
        print("\n⚠️ Skipping post generation test - GROQ_API_KEY not found")
    
    print("\n✨ Test suite completed!")

if __name__ == "__main__":
    main()
