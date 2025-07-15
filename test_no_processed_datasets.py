"""
Test the app behavior when no processed datasets are available
"""
import sys
import os

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dataset_manager import dataset_manager

def test_no_processed_datasets():
    """Test app behavior when only raw datasets exist"""
    print("🧪 Testing No Processed Datasets Scenario")
    print("=" * 50)
    
    # Get current datasets
    available_datasets = dataset_manager.get_available_datasets()
    raw_datasets = dataset_manager.get_raw_datasets()
    
    print(f"📊 **Dataset Status:**")
    print(f"   ✅ Processed datasets: {len(available_datasets)}")
    print(f"   ⚠️  Raw datasets: {len(raw_datasets)}")
    print()
    
    if not available_datasets:
        print("✅ **Scenario Confirmed:** No processed datasets available")
        print("📥 **Expected behavior:** App should show welcome screen with guidance")
        print()
        
        if raw_datasets:
            print("📋 **Available Raw Datasets:**")
            for i, (display_name, file_path) in enumerate(raw_datasets.items(), 1):
                print(f"   {i}. {display_name}")
                # Check file exists
                if os.path.exists(file_path):
                    print(f"      ✅ File exists: {file_path}")
                else:
                    print(f"      ❌ File missing: {file_path}")
            print()
            print("💡 **Recommendation:** Process these raw datasets in Dataset Manager")
        else:
            print("📭 **No raw datasets found either**")
            print("💡 **Recommendation:** Upload datasets in Dataset Manager")
    else:
        print("ℹ️  **Scenario:** Processed datasets are available")
        print("📋 **Available Processed Datasets:**")
        for i, (display_name, file_path) in enumerate(available_datasets.items(), 1):
            print(f"   {i}. {display_name}")
    
    print()
    print("🎯 **Test Complete!**")

if __name__ == "__main__":
    test_no_processed_datasets()
