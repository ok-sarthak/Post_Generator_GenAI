import pandas as pd
import json
import os


class FewShotPosts:
    def __init__(self, file_path="data/processed_posts.json"):
        self.df = None
        self.unique_tags = None
        self.file_path = file_path
        self.load_posts(file_path)

    def load_posts(self, file_path):
        """Load posts from JSON file and process them"""
        try:
            with open(file_path, encoding="utf-8") as f:
                posts = json.load(f)
                self.df = pd.json_normalize(posts)
                
                # Ensure required columns exist
                if 'line_count' not in self.df.columns:
                    self.df['line_count'] = self.df['text'].apply(lambda x: len(x.split('\n')))
                
                if 'length' not in self.df.columns:
                    self.df['length'] = self.df['line_count'].apply(self.categorize_length)
                
                if 'engagement' not in self.df.columns:
                    self.df['engagement'] = 0  # Default engagement
                
                # Process tags - handle both formats properly
                if 'tags' in self.df.columns:
                    self.df['tags'] = self.df['tags'].apply(self.ensure_list)
                    all_tags = []
                    for tags_list in self.df['tags']:
                        if isinstance(tags_list, list):
                            all_tags.extend(tags_list)
                    self.unique_tags = list(set(all_tags))
                else:
                    self.unique_tags = []
                    
                print(f"✅ Loaded {len(self.df)} posts from {file_path}")
                print(f"📊 Found {len(self.unique_tags)} unique tags")
                    
        except FileNotFoundError:
            print(f"❌ File {file_path} not found. Creating empty dataset.")
            self.df = pd.DataFrame(columns=['text', 'engagement', 'line_count', 'language', 'tags', 'length'])
            self.unique_tags = []
        except Exception as e:
            print(f"❌ Error loading posts: {e}")
            self.df = pd.DataFrame()
            self.unique_tags = []

    def ensure_list(self, tags):
        """Ensure tags is always a list"""
        if isinstance(tags, str):
            return [tags]
        elif isinstance(tags, list):
            return tags
        else:
            return []

    def get_filtered_posts(self, length, language, tag):
        """Get posts filtered by length, language, and tag"""
        try:
            if self.df.empty:
                return []
                
            df_filtered = self.df[
                (self.df['tags'].apply(lambda tags: tag in tags if isinstance(tags, list) else False)) &
                (self.df['language'] == language) &
                (self.df['length'] == length)
            ]
            return df_filtered.to_dict(orient='records')
        except Exception as e:
            print(f"Error filtering posts: {e}")
            return []

    def categorize_length(self, line_count):
        """Categorize post length based on line count"""
        if line_count < 5:
            return "Short"
        elif 5 <= line_count <= 10:
            return "Medium"
        else:
            return "Long"

    def get_tags(self):
        """Get all unique tags"""
        return self.unique_tags if self.unique_tags else []

    def add_posts(self, new_posts):
        """Add new posts to the dataset"""
        try:
            for post in new_posts:
                # Ensure required fields
                if 'line_count' not in post:
                    post['line_count'] = len(post.get('text', '').split('\n'))
                if 'length' not in post:
                    post['length'] = self.categorize_length(post['line_count'])
                if 'engagement' not in post:
                    post['engagement'] = 0
                if 'tags' not in post:
                    post['tags'] = []
            
            # Add to DataFrame
            new_df = pd.json_normalize(new_posts)
            self.df = pd.concat([self.df, new_df], ignore_index=True)
            
            # Update tags
            all_tags = self.df['tags'].apply(lambda x: x if isinstance(x, list) else []).sum()
            self.unique_tags = list(set(all_tags))
            
            return True
        except Exception as e:
            print(f"Error adding posts: {e}")
            return False

    def save_posts(self, file_path=None):
        """Save current dataset to file"""
        if file_path is None:
            file_path = self.file_path
        
        try:
            posts = self.df.to_dict(orient='records')
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(posts, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving posts: {e}")
            return False

    def get_statistics(self):
        """Get dataset statistics"""
        if self.df.empty:
            return {}
        
        try:
            stats = {
                'total_posts': len(self.df),
                'languages': self.df['language'].value_counts().to_dict() if 'language' in self.df.columns else {},
                'length_distribution': self.df['length'].value_counts().to_dict() if 'length' in self.df.columns else {},
                'avg_engagement': self.df['engagement'].mean() if 'engagement' in self.df.columns else 0,
                'total_tags': len(self.unique_tags),
                'top_tags': {}
            }
            
            # Get top tags
            if 'tags' in self.df.columns:
                all_tags = self.df['tags'].apply(lambda x: x if isinstance(x, list) else []).sum()
                tag_counts = pd.Series(all_tags).value_counts()
                stats['top_tags'] = tag_counts.head(10).to_dict()
            
            # Add tone statistics if available
            if 'tone' in self.df.columns:
                stats['tones'] = self.df['tone'].value_counts().to_dict()
            
            # Add audience statistics if available
            if 'target_audience' in self.df.columns:
                stats['audiences'] = self.df['target_audience'].value_counts().to_dict()
            
            return stats
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {}

    def search_posts(self, query, field='text'):
        """Search posts by text content"""
        try:
            if field not in self.df.columns:
                return []
            
            mask = self.df[field].str.contains(query, case=False, na=False)
            return self.df[mask].to_dict(orient='records')
        except Exception as e:
            print(f"Error searching posts: {e}")
            return []

    def get_posts_by_engagement(self, min_engagement=0, max_engagement=float('inf')):
        """Get posts filtered by engagement range"""
        try:
            if 'engagement' not in self.df.columns:
                return []
            
            mask = (self.df['engagement'] >= min_engagement) & (self.df['engagement'] <= max_engagement)
            return self.df[mask].to_dict(orient='records')
        except Exception as e:
            print(f"Error filtering by engagement: {e}")
            return []

    def merge_datasets(self, other_file_path):
        """Merge with another dataset"""
        try:
            other_fs = FewShotPosts(other_file_path)
            if not other_fs.df.empty:
                # Combine DataFrames
                self.df = pd.concat([self.df, other_fs.df], ignore_index=True)
                
                # Remove duplicates based on text content
                self.df = self.df.drop_duplicates(subset=['text'], keep='first')
                
                # Update tags
                all_tags = self.df['tags'].apply(lambda x: x if isinstance(x, list) else []).sum()
                self.unique_tags = list(set(all_tags))
                
                return True
            return False
        except Exception as e:
            print(f"Error merging datasets: {e}")
            return False


if __name__ == "__main__":
    # Test with college student posts
    fs = FewShotPosts("data/college_student_posts.json")
    print("Tags:", fs.get_tags())
    print("Statistics:", fs.get_statistics())
    
    # Test filtering
    posts = fs.get_filtered_posts("Medium", "English", "College Life")
    print(f"Found {len(posts)} posts for 'College Life'")
    
    if posts:
        print("Sample post:", posts[0]['text'][:100] + "...")