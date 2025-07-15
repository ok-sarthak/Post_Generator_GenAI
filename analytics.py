"""
Analytics module for the LinkedIn Post Generator
Provides detailed analytics and insights about the posts
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from collections import Counter
import re
from datetime import datetime, timedelta
import json
import os
from typing import List, Dict, Any
try:
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt
    WORDCLOUD_AVAILABLE = True
except ImportError:
    WORDCLOUD_AVAILABLE = False

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    # Download required NLTK data
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('punkt')
        nltk.download('stopwords')
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

try:
    import textstat
    TEXTSTAT_AVAILABLE = True
except ImportError:
    TEXTSTAT_AVAILABLE = False


class PostAnalytics:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.processed_df = self._preprocess_data()
    
    def _preprocess_data(self):
        """Preprocess the dataframe for analytics"""
        df = self.df.copy()
        
        # Calculate additional metrics
        if 'text' in df.columns:
            df['word_count'] = df['text'].apply(lambda x: len(str(x).split()))
            df['char_count'] = df['text'].apply(lambda x: len(str(x)))
            df['hashtag_count'] = df['text'].apply(self._count_hashtags)
            df['emoji_count'] = df['text'].apply(self._count_emojis)
            df['mention_count'] = df['text'].apply(self._count_mentions)
            
            if TEXTSTAT_AVAILABLE:
                df['readability_score'] = df['text'].apply(textstat.flesch_reading_ease)
                df['reading_time'] = df['word_count'] / 200  # Average reading speed
        
        # Ensure engagement is numeric
        if 'engagement' in df.columns:
            df['engagement'] = pd.to_numeric(df['engagement'], errors='coerce').fillna(0)
            
            # Calculate engagement rates
            if len(df) > 0:
                df['engagement_rate'] = df['engagement'] / df['engagement'].max() * 100
        
        return df
    
    def _count_hashtags(self, text: str) -> int:
        """Count hashtags in text"""
        return len(re.findall(r'#\w+', str(text)))
    
    def _count_emojis(self, text: str) -> int:
        """Count emojis in text (simplified)"""
        emoji_pattern = re.compile("["
                                   u"\U0001F600-\U0001F64F"  # emoticons
                                   u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                   u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                   u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                   "]+", flags=re.UNICODE)
        return len(emoji_pattern.findall(str(text)))
    
    def _count_mentions(self, text: str) -> int:
        """Count mentions in text"""
        return len(re.findall(r'@\w+', str(text)))
    
    def get_engagement_analytics(self):
        """Get engagement analytics"""
        if 'engagement' not in self.processed_df.columns:
            return None
        
        analytics = {
            'total_engagement': self.processed_df['engagement'].sum(),
            'avg_engagement': self.processed_df['engagement'].mean(),
            'median_engagement': self.processed_df['engagement'].median(),
            'max_engagement': self.processed_df['engagement'].max(),
            'min_engagement': self.processed_df['engagement'].min(),
            'std_engagement': self.processed_df['engagement'].std()
        }
        
        # Top performing posts
        top_posts = self.processed_df.nlargest(5, 'engagement')[['text', 'engagement']]
        analytics['top_posts'] = top_posts.to_dict('records')
        
        return analytics
    
    def get_content_analytics(self):
        """Get content analytics"""
        if 'text' not in self.processed_df.columns:
            return None
        
        analytics = {
            'avg_word_count': self.processed_df['word_count'].mean(),
            'avg_char_count': self.processed_df['char_count'].mean(),
            'avg_hashtags': self.processed_df['hashtag_count'].mean(),
            'avg_emojis': self.processed_df['emoji_count'].mean(),
            'avg_mentions': self.processed_df['mention_count'].mean()
        }
        
        if TEXTSTAT_AVAILABLE and 'readability_score' in self.processed_df.columns:
            analytics['avg_readability'] = self.processed_df['readability_score'].mean()
            analytics['avg_reading_time'] = self.processed_df['reading_time'].mean()
        
        return analytics
    
    def get_language_analytics(self):
        """Get language distribution analytics"""
        if 'language' not in self.processed_df.columns:
            return None
        
        language_dist = self.processed_df['language'].value_counts()
        return language_dist.to_dict()
    
    def get_length_analytics(self):
        """Get length distribution analytics"""
        if 'length' not in self.processed_df.columns:
            return None
        
        length_dist = self.processed_df['length'].value_counts()
        return length_dist.to_dict()
    
    def get_tag_analytics(self):
        """Get tag analytics"""
        if 'tags' not in self.processed_df.columns:
            return None
        
        all_tags = []
        for tags in self.processed_df['tags']:
            if isinstance(tags, list):
                all_tags.extend(tags)
        
        tag_counts = Counter(all_tags)
        return dict(tag_counts.most_common(20))
    
    def create_engagement_chart(self):
        """Create engagement distribution chart"""
        if 'engagement' not in self.processed_df.columns:
            return None
        
        fig = px.histogram(
            self.processed_df, 
            x='engagement',
            title='Engagement Distribution',
            nbins=20,
            color_discrete_sequence=['#2980b9']
        )
        fig.update_layout(
            xaxis_title='Engagement',
            yaxis_title='Number of Posts',
            showlegend=False
        )
        return fig
    
    def create_length_vs_engagement_chart(self):
        """Create length vs engagement chart"""
        if 'length' not in self.processed_df.columns or 'engagement' not in self.processed_df.columns:
            return None
        
        fig = px.box(
            self.processed_df,
            x='length',
            y='engagement',
            title='Engagement by Post Length',
            color='length',
            color_discrete_sequence=['#2980b9', '#27ae60', '#e74c3c']
        )
        fig.update_layout(showlegend=False)
        return fig
    
    def create_language_vs_engagement_chart(self):
        """Create language vs engagement chart"""
        if 'language' not in self.processed_df.columns or 'engagement' not in self.processed_df.columns:
            return None
        
        avg_engagement = self.processed_df.groupby('language')['engagement'].mean().reset_index()
        
        fig = px.bar(
            avg_engagement,
            x='language',
            y='engagement',
            title='Average Engagement by Language',
            color='language',
            color_discrete_sequence=['#2980b9', '#27ae60']
        )
        fig.update_layout(showlegend=False)
        return fig
    
    def create_tag_cloud_chart(self):
        """Create tag frequency chart"""
        tag_analytics = self.get_tag_analytics()
        if not tag_analytics:
            return None
        
        tags = list(tag_analytics.keys())[:15]  # Top 15 tags
        counts = [tag_analytics[tag] for tag in tags]
        
        fig = px.bar(
            x=counts,
            y=tags,
            orientation='h',
            title='Top Tags by Frequency',
            color=counts,
            color_continuous_scale='blues'
        )
        fig.update_layout(
            xaxis_title='Frequency',
            yaxis_title='Tags',
            showlegend=False,
            height=500
        )
        return fig
    
    def create_content_metrics_chart(self):
        """Create content metrics overview chart"""
        content_analytics = self.get_content_analytics()
        if not content_analytics:
            return None
        
        metrics = ['avg_word_count', 'avg_hashtags', 'avg_emojis', 'avg_mentions']
        values = [content_analytics.get(metric, 0) for metric in metrics]
        labels = ['Avg Words', 'Avg Hashtags', 'Avg Emojis', 'Avg Mentions']
        
        fig = px.bar(
            x=labels,
            y=values,
            title='Average Content Metrics',
            color=values,
            color_continuous_scale='greens'
        )
        fig.update_layout(showlegend=False)
        return fig
    
    def create_wordcloud(self):
        """Create word cloud from post content"""
        if not WORDCLOUD_AVAILABLE or 'text' not in self.processed_df.columns:
            return None
        
        # Combine all text
        all_text = ' '.join(self.processed_df['text'].astype(str))
        
        # Remove common stopwords
        if NLTK_AVAILABLE:
            stop_words = set(stopwords.words('english'))
            # Add custom stopwords
            stop_words.update(['linkedin', 'post', 'share', 'like', 'comment', 'follow'])
        else:
            stop_words = set()
        
        # Create word cloud
        wordcloud = WordCloud(
            width=800, 
            height=400, 
            background_color='white',
            stopwords=stop_words,
            colormap='coolwarm'
        ).generate(all_text)
        
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        plt.title('Most Common Words in Posts')
        
        return fig
    
    def get_performance_insights(self):
        """Get performance insights and recommendations"""
        insights = []
        
        if 'engagement' in self.processed_df.columns and len(self.processed_df) > 0:
            # Engagement insights
            avg_engagement = self.processed_df['engagement'].mean()
            high_performers = self.processed_df[self.processed_df['engagement'] > avg_engagement * 1.5]
            
            if len(high_performers) > 0:
                insights.append({
                    'type': 'success',
                    'title': 'High-Performing Content',
                    'message': f'{len(high_performers)} posts have engagement 50% above average'
                })
                
                # Analyze high performers
                if 'hashtag_count' in high_performers.columns:
                    avg_hashtags = high_performers['hashtag_count'].mean()
                    insights.append({
                        'type': 'info',
                        'title': 'Hashtag Strategy',
                        'message': f'High-performing posts average {avg_hashtags:.1f} hashtags'
                    })
        
        # Content length insights
        if 'word_count' in self.processed_df.columns:
            optimal_length = self.processed_df.loc[self.processed_df['engagement'].idxmax(), 'word_count']
            insights.append({
                'type': 'info',
                'title': 'Optimal Length',
                'message': f'Your highest-engaging post had {optimal_length} words'
            })
        
        # Language insights
        if 'language' in self.processed_df.columns:
            lang_performance = self.processed_df.groupby('language')['engagement'].mean()
            best_lang = lang_performance.idxmax()
            insights.append({
                'type': 'tip',
                'title': 'Language Performance',
                'message': f'{best_lang} posts perform better on average'
            })
        
        return insights
    
    def export_analytics_report(self, filename: str = None):
        """Export analytics report to JSON"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/analytics_report_{timestamp}.json"
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'dataset_overview': {
                'total_posts': len(self.processed_df),
                'date_range': 'N/A'  # Would need timestamp data
            },
            'engagement_analytics': self.get_engagement_analytics(),
            'content_analytics': self.get_content_analytics(),
            'language_analytics': self.get_language_analytics(),
            'length_analytics': self.get_length_analytics(),
            'tag_analytics': self.get_tag_analytics(),
            'performance_insights': self.get_performance_insights()
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            return filename
        except Exception as e:
            print(f"Error exporting report: {e}")
            return None


def show_analytics_dashboard(df: pd.DataFrame):
    """Show comprehensive analytics dashboard"""
    analytics = PostAnalytics(df)
    
    # Overview metrics
    st.subheader("📊 Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Posts", len(df))
    
    engagement_analytics = analytics.get_engagement_analytics()
    if engagement_analytics:
        with col2:
            st.metric("Total Engagement", f"{engagement_analytics['total_engagement']:,.0f}")
        with col3:
            st.metric("Avg Engagement", f"{engagement_analytics['avg_engagement']:.1f}")
        with col4:
            st.metric("Max Engagement", f"{engagement_analytics['max_engagement']:,.0f}")
    
    # Charts
    st.subheader("📈 Engagement Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        engagement_chart = analytics.create_engagement_chart()
        if engagement_chart:
            st.plotly_chart(engagement_chart, use_container_width=True)
    
    with col2:
        length_engagement_chart = analytics.create_length_vs_engagement_chart()
        if length_engagement_chart:
            st.plotly_chart(length_engagement_chart, use_container_width=True)
    
    # Content analysis
    st.subheader("📝 Content Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        content_metrics_chart = analytics.create_content_metrics_chart()
        if content_metrics_chart:
            st.plotly_chart(content_metrics_chart, use_container_width=True)
    
    with col2:
        tag_chart = analytics.create_tag_cloud_chart()
        if tag_chart:
            st.plotly_chart(tag_chart, use_container_width=True)
    
    # Word cloud
    if WORDCLOUD_AVAILABLE:
        st.subheader("☁️ Word Cloud")
        wordcloud_fig = analytics.create_wordcloud()
        if wordcloud_fig:
            st.pyplot(wordcloud_fig)
    
    # Insights
    st.subheader("💡 Performance Insights")
    insights = analytics.get_performance_insights()
    
    for insight in insights:
        if insight['type'] == 'success':
            st.success(f"**{insight['title']}**: {insight['message']}")
        elif insight['type'] == 'info':
            st.info(f"**{insight['title']}**: {insight['message']}")
        elif insight['type'] == 'tip':
            st.warning(f"**{insight['title']}**: {insight['message']}")
    
    # Export option
    if st.button("📤 Export Analytics Report"):
        filename = analytics.export_analytics_report()
        if filename:
            st.success(f"Report exported to {filename}")
        else:
            st.error("Failed to export report")
