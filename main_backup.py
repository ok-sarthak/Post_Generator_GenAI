import streamlit as st
import json
import os
from few_shot import FewShotPosts
from post_generator import generate_post, generate_custom_post
from datetime import datetim        st.markdown("### 🗄️ Dataset Selection")
        
        # Get available datasets
        available_datasets = dataset_manager.get_available_datasets()
        current_dataset = dataset_manager.get_current_dataset()
        
        # Find current dataset display name
        current_display_name = None
        for display_name, file_path in available_datasets.items():
            if file_path == current_dataset:
                current_display_name = display_name
                break
        
        if not current_display_name and available_datasets:
            current_display_name = list(available_datasets.keys())[0]
            dataset_manager.set_current_dataset(available_datasets[current_display_name])
        
        # Dataset selector
        if available_datasets:
            selected_dataset_name = st.selectbox(
                "Choose Dataset:", 
                list(available_datasets.keys()),
                index=list(available_datasets.keys()).index(current_display_name) if current_display_name else 0,
                key="global_dataset_selector"
            )
            
            selected_dataset_path = available_datasets[selected_dataset_name]
            
            # Update current dataset if changed
            if current_dataset != selected_dataset_path:
                dataset_manager.set_current_dataset(selected_dataset_path)
                st.rerun()
        else:
            st.warning("No datasets found. Please upload a dataset in Dataset Manager.")
            selected_dataset_path = None
        
        # Add refresh button
        if st.button("🔄 Refresh Datasets", help="Refresh the dataset list"):
            st.rerun()pd
from error_handler import (
    validate_post_data, safe_file_operation, handle_llm_error,
    check_api_key, sanitize_input
)
from analytics import show_analytics_dashboard
from dataset_manager import dataset_manager

# Configure the page
st.set_page_config(
    page_title="LinkedIn Post Generator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .feature-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
        color: #2c3e50;
    }
    .generated-post {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #b3d9ff;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        color: white;
        margin: 0.5rem 0;
    }
    .stats-card h3 {
        color: white;
        margin: 0;
        font-size: 1.5rem;
    }
    .stats-card p {
        color: #e8f4fd;
        margin: 0;
    }
    .sidebar .element-container {
        background: #f8f9fa;
        border-radius: 5px;
        padding: 0.5rem;
        margin: 0.25rem 0;
    }
    .stSelectbox > div > div {
        background: white;
        color: #2c3e50;
    }
    .stSelectbox > div > div > div {
        color: #2c3e50;
    }
    .stSelectbox svg {
        fill: #2c3e50 !important;
    }
    .stTextInput > div > div > input {
        background: white;
        color: #2c3e50;
    }
    .stTextArea > div > div > textarea {
        background: white;
        color: #2c3e50;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .expander-content {
        background: #f8f9fa;
        color: #2c3e50;
        padding: 1rem;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Options for length and language
length_options = ["Short", "Medium", "Long"]
language_options = ["English", "Hinglish"]
post_types = ["General", "College Student Journey", "Professional", "Technical"]
tones = ["Professional", "Casual", "Humorous", "Inspirational", "Educational"]

def load_dataset_stats():
    """Load and display dataset statistics"""
    try:
        fs = FewShotPosts()
        df = fs.df
        return {
            "total_posts": len(df),
            "languages": df['language'].value_counts().to_dict(),
            "length_distribution": df['length'].value_counts().to_dict(),
            "top_tags": df.explode('tags')['tags'].value_counts().head(5).to_dict()
        }
    except:
        return None

def save_generated_post(post_content, metadata):
    """Save generated posts to history"""
    history_file = "data/generated_posts_history.json"
    
    if os.path.exists(history_file):
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
    else:
        history = []
    
    new_entry = {
        "timestamp": datetime.now().isoformat(),
        "content": post_content,
        "metadata": metadata
    }
    
    history.append(new_entry)
    
    # Keep only last 100 posts
    if len(history) > 100:
        history = history[-100:]
    
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 LinkedIn Post Generator</h1>
        <p>AI-Powered Content Creation with Few-Shot Learning by Vacant Vectors</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar for navigation
    with st.sidebar:
        st.title("📊 Navigation")
        page = st.selectbox("Choose a feature:", [
            "🏠 Post Generator", 
            "📈 Analytics", 
            "⚙️ Custom Prompts", 
            "📚 Dataset Manager",
            "📝 Post History"
        ])
        
        st.markdown("---")
        st.markdown("### �️ Dataset Selection")
        dataset_options = {
            "Professional Posts": "data/processed_posts.json",
            "College Student Journey": "data/college_student_posts.json"
        }
        
        selected_dataset_name = st.selectbox(
            "Choose Dataset:", 
            list(dataset_options.keys()),
            key="dataset_selector"
        )
        
        selected_dataset_path = dataset_options[selected_dataset_name]
        
        # Store in session state
        if 'current_dataset' not in st.session_state:
            st.session_state.current_dataset = selected_dataset_path
        
        if st.session_state.current_dataset != selected_dataset_path:
            st.session_state.current_dataset = selected_dataset_path
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📋 Quick Stats")
        try:
            fs = FewShotPosts(st.session_state.current_dataset)
            stats = fs.get_statistics()
            if stats:
                st.metric("Total Posts", stats.get("total_posts", 0))
                st.metric("Languages", len(stats.get("languages", {})))
                st.metric("Categories", len(stats.get("length_distribution", {})))
        except Exception as e:
            st.error(f"Error loading stats: {e}")

    if page == "🏠 Post Generator":
        show_post_generator()
    elif page == "📈 Analytics":
        show_analytics()
    elif page == "⚙️ Custom Prompts":
        show_custom_prompts()
    elif page == "📚 Dataset Manager":
        show_dataset_manager()
    elif page == "📝 Post History":
        show_post_history()

def show_post_generator():
    st.header("🎯 Generate LinkedIn Posts")
    
    # Load few shot posts with selected dataset
    try:
        current_dataset = st.session_state.get('current_dataset', 'data/processed_posts.json')
        fs = FewShotPosts(current_dataset)
        tags = fs.get_tags()
        
        if not tags:
            st.warning(f"No tags found in the selected dataset. Please check the dataset: {current_dataset}")
            return
            
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        return
    
    # Create tabs for different generation modes
    tab1, tab2 = st.tabs(["🎪 Quick Generate", "🎨 Advanced Customization"])
    
    with tab1:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            selected_tag = st.selectbox("📌 Topic", options=tags, key="quick_tag")
        
        with col2:
            selected_length = st.selectbox("📏 Length", options=length_options, key="quick_length")
        
        with col3:
            selected_language = st.selectbox("🌐 Language", options=language_options, key="quick_lang")
        
        with col4:
            selected_tone = st.selectbox("🎭 Tone", options=tones, key="quick_tone")
        
        # Additional options
        col5, col6 = st.columns(2)
        with col5:
            include_hashtags = st.checkbox("Include Hashtags", value=True)
            include_emojis = st.checkbox("Include Emojis", value=True)
        
        with col6:
            add_call_to_action = st.checkbox("Add Call-to-Action", value=False)
            professional_format = st.checkbox("Professional Format", value=False)
        
        if st.button("🚀 Generate Post", type="primary"):
            # Check API key first
            if not check_api_key():
                st.error("❌ API key not configured. Please check your .env file.")
                return
            
            with st.spinner("Generating your post..."):
                try:
                    metadata = {
                        "tag": selected_tag,
                        "length": selected_length,
                        "language": selected_language,
                        "tone": selected_tone,
                        "include_hashtags": include_hashtags,
                        "include_emojis": include_emojis,
                        "add_cta": add_call_to_action,
                        "professional": professional_format
                    }
                    
                    post = generate_post(selected_length, selected_language, selected_tag, 
                                       tone=selected_tone, include_hashtags=include_hashtags,
                                       include_emojis=include_emojis, add_cta=add_call_to_action,
                                       professional=professional_format, 
                                       dataset_path=st.session_state.current_dataset)
                    
                    if post:
                        st.markdown(f"""
                        <div class="generated-post">
                            <h4>📝 Generated Post:</h4>
                            <p>{post}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Save to history
                        save_generated_post(post, metadata)
                        
                        # Show related posts used for generation
                        examples = fs.get_filtered_posts(selected_length, selected_language, selected_tag)
                        if examples:
                            with st.expander(f"📚 Reference Posts Used ({len(examples)} found)"):
                                for i, example in enumerate(examples[:3]):
                                    st.write(f"**Example {i+1}:**")
                                    st.write(example['text'])
                                    st.write(f"*Engagement: {example.get('engagement', 'N/A')}*")
                                    st.markdown("---")
                    else:
                        st.error("Failed to generate post. Please try again.")
                        
                except Exception as e:
                    error_message = handle_llm_error(e)
                    st.error(error_message)
    
    with tab2:
        st.subheader("🎨 Custom Post Generation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            custom_topic = st.text_input("Custom Topic", placeholder="e.g., My first day at Google")
            custom_topic = sanitize_input(custom_topic, 200)
            target_audience = st.selectbox("Target Audience", 
                                         ["Students", "Professionals", "Entrepreneurs", "Job Seekers", "General"])
            post_purpose = st.selectbox("Post Purpose", 
                                      ["Share Experience", "Give Advice", "Ask Question", "Celebrate Achievement", "Educational"])
        
        with col2:
            custom_length = st.selectbox("Length", options=length_options, key="custom_length")
            custom_language = st.selectbox("Language", options=language_options, key="custom_language")
            writing_style = st.selectbox("Writing Style", 
                                       ["Storytelling", "List Format", "Question-Answer", "Tips & Tricks", "Personal Reflection"])
        
        additional_context = st.text_area("Additional Context (Optional)", 
                                        placeholder="Any specific details you want to include...")
        additional_context = sanitize_input(additional_context, 500)
        
        keywords = st.text_input("Keywords to Include", 
                                placeholder="Separate with commas: coding, internship, learning")
        keywords = sanitize_input(keywords, 200)
        
        if st.button("🎨 Generate Custom Post", type="primary"):
            if not custom_topic.strip():
                st.warning("Please enter a custom topic.")
                return
                
            if not check_api_key():
                st.error("❌ API key not configured. Please check your .env file.")
                return
                
            with st.spinner("Creating your custom post..."):
                try:
                    custom_metadata = {
                        "topic": custom_topic,
                        "audience": target_audience,
                        "purpose": post_purpose,
                        "length": custom_length,
                        "language": custom_language,
                        "style": writing_style,
                        "context": additional_context,
                        "keywords": keywords
                    }
                    
                    custom_post = generate_custom_post(
                        topic=custom_topic,
                        audience=target_audience,
                        purpose=post_purpose,
                        length=custom_length,
                        language=custom_language,
                        style=writing_style,
                        context=additional_context,
                        keywords=keywords.split(',') if keywords else []
                    )
                    
                    if custom_post:
                        st.markdown(f"""
                        <div class="generated-post">
                            <h4>📝 Your Custom Post:</h4>
                            <p>{custom_post}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        save_generated_post(custom_post, custom_metadata)
                    else:
                        st.error("Failed to generate custom post. Please try again.")
                        
                except Exception as e:
                    error_message = handle_llm_error(e)
                    st.error(error_message)

def show_analytics():
    st.header("📊 Dataset Analytics")
    
    try:
        fs = FewShotPosts()
        df = fs.df
        
        if df.empty:
            st.warning("No data available for analytics. Please load a dataset first.")
            return
        
        show_analytics_dashboard(df)
        
    except Exception as e:
        st.error(f"Error loading analytics: {handle_llm_error(e)}")

def show_custom_prompts():
    st.header("⚙️ Custom Prompt Templates")
    
    st.markdown("""
    <div class="feature-box">
        <h4>📝 Create Your Own Prompt Templates</h4>
        <p>Design custom prompts for specific use cases and save them for future use.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load existing templates
    templates_file = "data/prompt_templates.json"
    if os.path.exists(templates_file):
        with open(templates_file, 'r', encoding='utf-8') as f:
            templates = json.load(f)
    else:
        templates = []
    
    # Create new template
    with st.expander("➕ Create New Template"):
        template_name = st.text_input("Template Name")
        template_description = st.text_area("Description")
        template_prompt = st.text_area("Prompt Template", 
                                     placeholder="Use variables like {topic}, {length}, {tone}, etc.")
        
        if st.button("Save Template"):
            if template_name and template_prompt:
                new_template = {
                    "name": template_name,
                    "description": template_description,
                    "prompt": template_prompt,
                    "created_at": datetime.now().isoformat()
                }
                templates.append(new_template)
                
                with open(templates_file, 'w', encoding='utf-8') as f:
                    json.dump(templates, f, indent=2, ensure_ascii=False)
                
                st.success("Template saved successfully!")
                st.experimental_rerun()
    
    # Display existing templates
    st.subheader("📚 Saved Templates")
    for i, template in enumerate(templates):
        with st.expander(f"{template['name']} - {template['description'][:50]}..."):
            st.write(f"**Description:** {template['description']}")
            st.code(template['prompt'])
            if st.button(f"Delete", key=f"delete_{i}"):
                templates.pop(i)
                with open(templates_file, 'w', encoding='utf-8') as f:
                    json.dump(templates, f, indent=2, ensure_ascii=False)
                st.experimental_rerun()

def show_dataset_manager():
    st.header("📚 Dataset Management")
    
    tab1, tab2, tab3 = st.tabs(["📤 Upload & Process", "🔄 Switch Dataset", "📊 Dataset Stats"])
    
    with tab1:
        st.subheader("📤 Upload New Dataset")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose a JSON file", 
            type="json",
            help="Upload a JSON file containing LinkedIn posts"
        )
        
        if uploaded_file is not None:
            try:
                # Preview the uploaded data
                uploaded_data = json.load(uploaded_file)
                uploaded_file.seek(0)  # Reset file pointer
                
                st.success(f"✅ File loaded successfully! Found {len(uploaded_data)} posts")
                
                # Show preview
                with st.expander("👀 Preview Data"):
                    st.json(uploaded_data[:2])  # Show first 2 posts
                
                # Dataset naming
                col1, col2 = st.columns(2)
                with col1:
                    dataset_name = st.text_input(
                        "Dataset Name", 
                        value="my_dataset",
                        help="Name for your processed dataset"
                    )
                
                with col2:
                    auto_switch = st.checkbox(
                        "Auto-switch to this dataset after processing", 
                        value=True
                    )
                
                # Process button
                if st.button("🚀 Process Dataset", type="primary"):
                    if not dataset_name.strip():
                        st.error("Please provide a dataset name")
                    else:
                        with st.spinner("Processing dataset... This may take a few minutes."):
                            try:
                                from dataset_processor import DatasetProcessor
                                processor = DatasetProcessor()
                                
                                processed_file_path = processor.process_uploaded_dataset(
                                    uploaded_file, 
                                    dataset_name
                                )
                                
                                st.success(f"✅ Dataset processed successfully!")
                                st.info(f"📁 Processed dataset saved as: {processed_file_path}")
                                
                                # Show processing stats
                                stats = processor.get_processing_stats(processed_file_path)
                                if stats:
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric("Total Posts", stats['total_posts'])
                                    with col2:
                                        st.metric("Languages", len(stats['languages']))
                                    with col3:
                                        st.metric("Unique Tags", stats['total_tags'])
                                
                                # Auto-switch dataset
                                if auto_switch:
                                    st.session_state.current_dataset = processed_file_path
                                    st.success("🔄 Switched to new dataset!")
                                    st.rerun()
                                
                            except Exception as e:
                                st.error(f"❌ Error processing dataset: {e}")
                                
            except json.JSONDecodeError:
                st.error("❌ Invalid JSON file. Please check your file format.")
            except Exception as e:
                st.error(f"❌ Error loading file: {e}")
    
    with tab2:
        st.subheader("🔄 Switch Dataset")
        
        # List available datasets
        data_dir = "data"
        available_datasets = {}
        
        if os.path.exists(data_dir):
            for file in os.listdir(data_dir):
                if file.endswith('.json') and not file.endswith('_metadata.json'):
                    display_name = file.replace('.json', '').replace('_', ' ').title()
                    file_path = os.path.join(data_dir, file)
                    available_datasets[display_name] = file_path
        
        if available_datasets:
            current_dataset = st.session_state.get('current_dataset', 'data/processed_posts.json')
            current_display_name = None
            
            for display_name, file_path in available_datasets.items():
                if file_path == current_dataset:
                    current_display_name = display_name
                    break
            
            selected_dataset = st.selectbox(
                "Select Dataset:",
                list(available_datasets.keys()),
                index=list(available_datasets.keys()).index(current_display_name) if current_display_name else 0
            )
            
            if st.button("🔄 Switch Dataset"):
                new_dataset_path = available_datasets[selected_dataset]
                st.session_state.current_dataset = new_dataset_path
                st.success(f"✅ Switched to: {selected_dataset}")
                st.rerun()
        else:
            st.warning("No datasets found in the data directory.")
    
    with tab3:
        st.subheader("📊 Dataset Statistics")
        
        current_dataset = st.session_state.get('current_dataset', 'data/processed_posts.json')
        
        try:
            from dataset_processor import DatasetProcessor
            processor = DatasetProcessor()
            stats = processor.get_processing_stats(current_dataset)
            
            if stats:
                st.write(f"**Current Dataset:** {os.path.basename(current_dataset)}")
                
                # Overview metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Posts", stats['total_posts'])
                with col2:
                    st.metric("Languages", len(stats['languages']))
                with col3:
                    st.metric("Avg Engagement", f"{stats['avg_engagement']:.1f}")
                with col4:
                    st.metric("Unique Tags", stats['total_tags'])
                
                # Detailed breakdowns
                col1, col2 = st.columns(2)
                
                with col1:
                    if stats['languages']:
                        st.write("**Language Distribution:**")
                        for lang, count in stats['languages'].items():
                            st.write(f"- {lang}: {count} posts")
                    
                    if stats['lengths']:
                        st.write("**Length Distribution:**")
                        for length, count in stats['lengths'].items():
                            st.write(f"- {length}: {count} posts")
                
                with col2:
                    if stats['tones']:
                        st.write("**Tone Distribution:**")
                        for tone, count in stats['tones'].items():
                            st.write(f"- {tone}: {count} posts")
                    
                    if stats['audiences']:
                        st.write("**Target Audience:**")
                        for audience, count in stats['audiences'].items():
                            st.write(f"- {audience}: {count} posts")
            else:
                st.warning("Unable to load dataset statistics.")
                
        except Exception as e:
            st.error(f"Error loading statistics: {e}")

def show_post_history():
    st.header("📝 Generated Posts History")
    
    history_file = "data/generated_posts_history.json"
    
    if os.path.exists(history_file):
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        if history:
            st.write(f"📊 Total posts generated: {len(history)}")
            
            # Filter options
            col1, col2 = st.columns(2)
            with col1:
                filter_language = st.selectbox("Filter by Language", 
                                             ["All"] + language_options)
            with col2:
                filter_length = st.selectbox("Filter by Length", 
                                           ["All"] + length_options)
            
            # Display history
            filtered_history = history
            if filter_language != "All":
                filtered_history = [h for h in filtered_history 
                                  if h.get('metadata', {}).get('language') == filter_language]
            if filter_length != "All":
                filtered_history = [h for h in filtered_history 
                                  if h.get('metadata', {}).get('length') == filter_length]
            
            for i, entry in enumerate(reversed(filtered_history[-20:])):  # Show last 20
                timestamp = datetime.fromisoformat(entry['timestamp']).strftime("%Y-%m-%d %H:%M")
                with st.expander(f"Post {len(filtered_history)-i} - {timestamp}"):
                    st.write(entry['content'])
                    if 'metadata' in entry:
                        st.json(entry['metadata'])
        else:
            st.info("No posts generated yet. Start creating some posts!")
    else:
        st.info("No history found. Generate some posts to see them here!")

if __name__ == "__main__":
    main()
