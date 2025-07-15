"""
Test Dataset Statistics Functionality
"""
import sys
import os

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dataset_manager import dataset_manager

def test_dataset_stats():
    """Test the dataset statistics functionality"""
    print("🧪 Testing Dataset Statistics")
    print("=" * 50)
    
    # Check if we can get statistics for raw datasets
    raw_datasets = dataset_manager.get_raw_datasets()
    
    if raw_datasets:
        print(f"📊 Found {len(raw_datasets)} raw datasets")
        
        for name, path in raw_datasets.items():
            print(f"\n📋 Testing stats for: {name}")
            print(f"    File: {path}")
            
            # Test dataset info
            info = dataset_manager.get_dataset_info(path)
            if info:
                print(f"    ✅ Basic info: {info['total_posts']} posts")
            else:
                print(f"    ❌ Could not get basic info")
            
            # Test validation
            valid, message = dataset_manager.validate_dataset(path)
            print(f"    {'✅' if valid else '❌'} Validation: {message}")
            
            # Note: Statistics require processed datasets
            print(f"    ℹ️  Full statistics require processing first")
    
    # Check processed datasets stats
    processed_datasets = dataset_manager.get_available_datasets()
    
    if processed_datasets:
        print(f"\n📈 Found {len(processed_datasets)} processed datasets")
        
        for name, path in processed_datasets.items():
            print(f"\n📊 Testing full stats for: {name}")
            
            stats = dataset_manager.get_dataset_statistics(path)
            if stats:
                print(f"    ✅ Total posts: {stats['total_posts']}")
                print(f"    ✅ Languages: {list(stats['languages'].keys())}")
                print(f"    ✅ Average engagement: {stats.get('avg_engagement', 0):.1f}")
            else:
                print(f"    ❌ Could not get statistics")
    else:
        print("\n📭 No processed datasets found for full statistics")
        print("    💡 Process raw datasets to get detailed analytics")
    
    print("\n🎯 Test Complete!")

if __name__ == "__main__":
    test_dataset_stats()
