import streamlit as st
import json
import os
from few_shot import FewShotPosts
from post_generator import generate_post, generate_custom_post
from datetime import datetime
import pandas as pd
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
        background: linear-gradient(90deg, #2980b9 0%, #27ae60 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .feature-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2980b9;
        margin: 1rem 0;
        color: #2c3e50;
    }
    .generated-post {
        background: linear-gradient(135deg, #2980b9 0%, #27ae60 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #b3d9ff;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stats-card {
        background: linear-gradient(135deg, #2980b9 0%, #27ae60 100%);
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
        background: linear-gradient(135deg, #2980b9 0%, #27ae60 100%);
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
        st.markdown("### 🗄️ Dataset Selection")
        
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
            st.markdown("""
            <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 1rem; margin: 1rem 0;">
                <h4 style="color: #856404; margin: 0 0 0.5rem 0;">📥 No Processed Datasets</h4>
                <p style="color: #856404; margin: 0; font-size: 0.9em;">
                    Go to <strong>Dataset Manager</strong> to process raw datasets or upload new ones!
                </p>
            </div>
            """, unsafe_allow_html=True)
            selected_dataset_path = None
        
        # Add refresh button
        if st.button("🔄 Refresh Datasets", help="Refresh the dataset list"):
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📋 Quick Stats")
        
        # Show current dataset stats
        if selected_dataset_path and dataset_manager.dataset_exists(selected_dataset_path):
            try:
                stats = dataset_manager.get_dataset_statistics(selected_dataset_path)
                if stats:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Posts", stats.get("total_posts", 0))
                    with col2:
                        st.metric("Languages", len(stats.get("languages", {})))
                    with col3:
                        st.metric("Categories", len(stats.get("lengths", {})))
                    
                    # Show current dataset name
                    st.success(f"📊 **Active:** {dataset_manager.get_current_dataset_name()}")
            except Exception as e:
                st.error(f"Error loading stats: {e}")
        elif available_datasets:
            st.info("📊 Select a dataset above to view statistics")
        else:
            # Check for raw datasets
            raw_datasets = dataset_manager.get_raw_datasets()
            if raw_datasets:
                st.info(f"📥 **{len(raw_datasets)} raw datasets** ready for processing")
                st.markdown("*Process them in Dataset Manager to start generating posts!*")
            else:
                st.info("📥 Upload datasets in **Dataset Manager** to get started")

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
    
    # Check if we have any processed datasets
    available_datasets = dataset_manager.get_available_datasets()
    
    if not available_datasets:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #2980b9 0%, #27ae60 100%); padding: 2rem; border-radius: 15px; text-align: center; color: white; margin: 2rem 0;">
            <h2>🚀 Welcome to Vacant Vectors!</h2>
            <p style="font-size: 1.2em; margin: 1rem 0;">Ready to create amazing LinkedIn posts? Let's get started!</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📥 **Step 1: Get Your Datasets Ready**")
        st.markdown("""
        To generate posts, you need processed datasets. Here are your options:
        
        **🔧 Process Raw Datasets** (Recommended)
        - Go to **📚 Dataset Manager** tab
        - You'll find raw datasets ready for processing
        - Click "🚀 Process Dataset" to convert them with AI enhancement
        
        **📤 Upload Your Own**
        - Upload your JSON file with posts in the Dataset Manager
        - Our AI will automatically add tags, tone analysis, and more
        
        **✨ What happens during processing?**
        - AI extracts topics and tags from your posts
        - Analyzes tone (Professional, Casual, Inspirational, etc.)
        - Identifies target audience (Students, Professionals, etc.)
        - Detects language and writing style
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📚 Go to Dataset Manager", type="primary", use_container_width=True):
                st.session_state.page = "📚 Dataset Manager"
                st.rerun()
        
        with col2:
            st.markdown("**📊 Current Status:**")
            st.error("No processed datasets available")
        
        return
    
    # Load few shot posts with selected dataset
    try:
        current_dataset = dataset_manager.get_current_dataset()
        
        if not current_dataset:
            st.warning("⚠️ No dataset selected. Please select a dataset from the sidebar.")
            return
            
        fs = FewShotPosts(current_dataset)
        tags = fs.get_tags()
        
        if not tags:
            st.warning(f"No tags found in the selected dataset. Please check the dataset: {current_dataset}")
            return
            
    except FileNotFoundError:
        st.error("📁 Selected dataset file not found. Please check if the file exists or select a different dataset.")
        return
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        st.info("💡 **Tip:** Make sure your dataset is properly processed. Go to Dataset Manager to process raw datasets.")
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
                                       dataset_path=current_dataset)
                    
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
    
    # Check if we have any processed datasets
    available_datasets = dataset_manager.get_available_datasets()
    
    if not available_datasets:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #e74c3c 0%, #f39c12 100%); padding: 2rem; border-radius: 15px; text-align: center; color: white; margin: 2rem 0;">
            <h2>📈 Analytics Dashboard</h2>
            <p style="font-size: 1.2em; margin: 1rem 0;">Discover insights from your LinkedIn posts!</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📊 **Analytics Features Available:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **📈 Engagement Analytics**
            - Total and average engagement metrics
            - Top performing posts analysis
            - Engagement distribution charts
            
            **📝 Content Analysis**
            - Word count and readability scores
            - Hashtag and emoji usage patterns
            - Content length optimization insights
            """)
        
        with col2:
            st.markdown("""
            **🏷️ Tag & Topic Analysis**
            - Most popular topics and tags
            - Tag frequency visualization
            - Content categorization insights
            
            **🌍 Language & Audience**
            - Language distribution analysis
            - Target audience identification
            - Performance by demographics
            """)
        
        st.markdown("### 🚀 **Get Started**")
        st.info("📥 **Need datasets first:** Go to Dataset Manager to process your raw datasets or upload new ones!")
        
        if st.button("📚 Go to Dataset Manager", type="primary"):
            st.session_state.page = "📚 Dataset Manager"
            st.rerun()
        
        return
    
    try:
        current_dataset = dataset_manager.get_current_dataset()
        
        if not current_dataset:
            st.warning("⚠️ No dataset selected. Please select a dataset from the sidebar.")
            return
            
        fs = FewShotPosts(current_dataset)
        df = fs.df
        
        if df.empty:
            st.warning("📊 No data available for analytics. The selected dataset appears to be empty.")
            return
        
        # Show current dataset info
        st.info(f"📊 Analyzing: **{dataset_manager.get_current_dataset_name()}** ({len(df)} posts)")
        
        show_analytics_dashboard(df)
        
    except FileNotFoundError:
        st.error("📁 Selected dataset file not found. Please check if the file exists or select a different dataset.")
    except Exception as e:
        st.error(f"Error loading analytics: {handle_llm_error(e)}")
        st.info("💡 **Tip:** Make sure your dataset is properly processed and contains the required fields.")

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
                st.rerun()
    
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
                st.rerun()

def show_dataset_manager():
    st.header("📚 Dataset Management")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload & Process", "🔄 Process Raw Data", "🔄 Switch Dataset", "📊 Dataset Stats"])
    
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
                
            

                # Auto-extract filename for default value
                uploaded_filename = uploaded_file.name
                default_name = uploaded_filename.replace('.json', '').replace('_', '_').lower()
                
                # Dataset naming
                col1, col2 = st.columns(2)
                with col1:
                    dataset_name = st.text_input(
                        "Dataset Name", 
                        value=default_name,
                        help="Name for your processed dataset (auto-filled from uploaded filename)"
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
                                stats = dataset_manager.get_dataset_statistics(processed_file_path)
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
                                    dataset_manager.set_current_dataset(processed_file_path)
                                    st.success("🔄 Switched to new dataset!")
                                    st.rerun()
                                
                            except Exception as e:
                                st.error(f"❌ Error processing dataset: {e}")
                                
            except json.JSONDecodeError:
                st.error("❌ Invalid JSON file. Please check your file format.")
            except Exception as e:
                st.error(f"❌ Error loading file: {e}")
    
    with tab2:
        st.subheader("🔄 Process Raw Datasets")
        
        # Get raw datasets that need processing
        raw_datasets = dataset_manager.get_raw_datasets()
        
        if raw_datasets:
            st.info("💡 **Raw datasets** only have basic fields (text, engagement). Process them to enable AI features like topic selection and smart generation.")
            
            for display_name, file_path in raw_datasets.items():
                with st.expander(f"📄 {display_name}"):
                    # Show dataset info
                    info = dataset_manager.get_dataset_info(file_path)
                    if info:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Posts", info['total_posts'])
                        with col2:
                            st.metric("Status", "⚠️ Raw (Needs Processing)")
                    
                    # Process button
                    if st.button(f"🚀 Process {display_name}", key=f"process_{display_name}"):
                        with st.spinner(f"Processing {display_name}..."):
                            try:
                                from dataset_processor import DatasetProcessor
                                processor = DatasetProcessor()
                                
                                # Process the raw dataset
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    raw_data = json.load(f)
                                
                                processed_posts = []
                                for i, post in enumerate(raw_data):
                                    st.write(f"Processing post {i+1}/{len(raw_data)}...")
                                    processed_post = processor.process_single_post(post)
                                    if processed_post:
                                        processed_posts.append(processed_post)
                                
                                # Save processed version
                                processed_name = f"processed_{display_name.lower().replace(' ', '_')}"
                                processed_path = f"data/{processed_name}.json"
                                processor.save_processed_dataset(processed_posts, processed_path)
                                
                                st.success(f"✅ {display_name} processed successfully!")
                                st.info(f"📁 Saved as: {processed_name}")
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"❌ Error processing {display_name}: {e}")
        else:
            st.success("✅ All datasets are already processed and ready for use!")
    
    with tab3:
        st.subheader("🔄 Switch Dataset")
        
        # List available datasets
        available_datasets = dataset_manager.get_available_datasets()
        current_dataset = dataset_manager.get_current_dataset()
        
        if available_datasets:
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
            
            # Show dataset info
            selected_path = available_datasets[selected_dataset]
            info = dataset_manager.get_dataset_info(selected_path)
            if info:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Posts", info['total_posts'])
                with col2:
                    st.metric("Languages", len(info['languages']))
                with col3:
                    st.metric("Tags", len(info['tags']))
            
            if st.button("🔄 Switch Dataset"):
                new_dataset_path = available_datasets[selected_dataset]
                dataset_manager.set_current_dataset(new_dataset_path)
                st.success(f"✅ Switched to: {selected_dataset}")
                st.rerun()
        else:
            st.warning("No datasets found in the data directory.")
    
    with tab4:
        st.subheader("📊 Dataset Statistics & Analytics")
        
        current_dataset = dataset_manager.get_current_dataset()
        
        if not current_dataset or not dataset_manager.dataset_exists(current_dataset):
            st.warning("No dataset selected or dataset not found.")
            return
        
        try:
            stats = dataset_manager.get_dataset_statistics(current_dataset)
            
            if stats:
                st.success(f"**📊 Analyzing:** {dataset_manager.get_current_dataset_name()}")
                
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
                    st.markdown("### 🌍 Language Distribution")
                    if stats['languages']:
                        for lang, count in stats['languages'].items():
                            percentage = (count / stats['total_posts']) * 100
                            st.write(f"**{lang}:** {count} posts ({percentage:.1f}%)")
                    else:
                        st.info("No language data available")
                    
                    st.markdown("### 📏 Length Distribution")
                    if stats['lengths']:
                        for length, count in stats['lengths'].items():
                            percentage = (count / stats['total_posts']) * 100
                            st.write(f"**{length}:** {count} posts ({percentage:.1f}%)")
                    else:
                        st.info("No length data available")
                
                with col2:
                    st.markdown("### 🎭 Tone Distribution")
                    if stats['tones']:
                        for tone, count in stats['tones'].items():
                            percentage = (count / stats['total_posts']) * 100
                            st.write(f"**{tone}:** {count} posts ({percentage:.1f}%)")
                    else:
                        st.info("No tone data available")
                    
                    st.markdown("### 👥 Target Audience")
                    if stats['audiences']:
                        for audience, count in stats['audiences'].items():
                            percentage = (count / stats['total_posts']) * 100
                            st.write(f"**{audience}:** {count} posts ({percentage:.1f}%)")
                    else:
                        st.info("No audience data available")
                
                # Full analytics if data is available
                if stats['total_posts'] > 0:
                    st.markdown("---")
                    st.markdown("### 📈 Full Analytics")
                    
                    # Load the dataset for full analytics
                    try:
                        from few_shot import FewShotPosts
                        fs = FewShotPosts(current_dataset)
                        
                        if not fs.df.empty:
                            from analytics import show_analytics_dashboard
                            show_analytics_dashboard(fs.df)
                        else:
                            st.warning("Dataset appears to be empty for full analytics.")
                    except Exception as analytics_error:
                        st.warning(f"Full analytics not available: {analytics_error}")
                        st.info("💡 Basic statistics are shown above. For full analytics, ensure the dataset is properly processed.")
                        
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
