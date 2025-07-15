#!/usr/bin/env python3
"""
Test script for dataset detection without Streamlit dependency
"""
import os
import json

def test_dataset_detection():
    print("=== DATASET DETECTION TEST ===")
    
    data_dir = "data"
    if not os.path.exists(data_dir):
        print(f"Data directory {data_dir} not found!")
        return
    
    files = os.listdir(data_dir)
    json_files = [f for f in files if f.endswith('.json') and not f.endswith('_metadata.json') and not f.endswith('_history.json')]
    
    print(f"Found {len(json_files)} JSON files:")
    for file in json_files:
        print(f"  - {file}")
    
    print("\n=== TESTING EACH FILE ===")
    processed_datasets = {}
    raw_datasets = {}
    
    for file in json_files:
        file_path = os.path.join(data_dir, file)
        
        # Check if processed
        is_processed = check_if_processed(file_path)
        
        # Create display name
        if file.startswith('raw_'):
            display_name = file.replace('raw_', '').replace('.json', '').replace('_', ' ').title()
            if is_processed:
                display_name = f"{display_name}"
            else:
                display_name = f"{display_name} (Raw)"
        elif file.startswith('processed_raw_'):
            display_name = file.replace('processed_raw_', '').replace('.json', '').replace('_', ' ').title()
        else:
            display_name = file.replace('.json', '').replace('_', ' ').title()
        
        if is_processed:
            processed_datasets[display_name] = file_path
            print(f"✅ PROCESSED: {display_name} <- {file}")
        else:
            raw_datasets[display_name] = file_path
            print(f"⚠️  RAW: {display_name} <- {file}")
        
        # Show file structure
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if data:
                sample_keys = list(data[0].keys())
                has_tags = 'tags' in data[0]
                print(f"    Posts: {len(data)}, Keys: {sample_keys}, Has tags: {has_tags}")
        except Exception as e:
            print(f"    Error reading file: {e}")
        print()
    
    print("=== FINAL RESULTS ===")
    print(f"Processed datasets ready for generation: {len(processed_datasets)}")
    for name, path in processed_datasets.items():
        print(f"  ✅ {name}")
    
    print(f"\nRaw datasets needing processing: {len(raw_datasets)}")
    for name, path in raw_datasets.items():
        print(f"  ⚠️  {name}")

def check_if_processed(file_path):
    """Check if a dataset is processed"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not data or not isinstance(data, list):
            return False
        
        sample_post = data[0]
        
        # Check required fields
        if 'text' not in sample_post or 'tags' not in sample_post:
            return False
        
        # Check if tags is a list and not empty
        tags = sample_post.get('tags')
        if not isinstance(tags, list) or len(tags) == 0:
            return False
        
        return True
        
    except Exception as e:
        print(f"Error checking {file_path}: {e}")
        return False

if __name__ == "__main__":
    test_dataset_detection()
