# 🚀 LinkedIn Post Generator - AI-Powered Content Creation

<div align="center">

![LinkedIn Post Generator](resources/tool.jpg)

**An advanced AI-powered tool that generates LinkedIn posts using Few-Shot Learning techniques**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-0.1+-green.svg)](https://langchain.com)
[![Groq](https://img.shields.io/badge/Groq-API-purple.svg)](https://groq.com)

</div>

## 📋 Table of Contents

- [🌟 Features](#-features)
- [🏗️ Architecture](#️-architecture)
- [🚀 Quick Start](#-quick-start)
- [📦 Installation](#-installation)
- [⚙️ Configuration](#️-configuration)
- [🎯 Usage Guide](#-usage-guide)
- [📊 Datasets](#-datasets)
- [🔧 Development](#-development)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

## 🌟 Features

### 🎯 **Intelligent Post Generation**
- **Few-Shot Learning**: Learns from existing posts to match unique writing styles
- **Multi-language Support**: Generate posts in English and Hinglish
- **Customizable Length**: Short (1-5 lines), Medium (6-10 lines), Long (11-15 lines)
- **Tone Variations**: Professional, Casual, Humorous, Inspirational, Educational
- **Smart Context**: AI analyzes your dataset to understand patterns and preferences

### 🎨 **Advanced Customization**
- **Custom Prompts**: Create and save your own prompt templates
- **Target Audience**: Tailor content for Students, Professionals, Entrepreneurs, Job Seekers
- **Writing Styles**: Storytelling, List Format, Question-Answer, Tips & Tricks, Personal Reflection
- **Smart Features**: Hashtag inclusion, emoji integration, call-to-action generation
- **Professional Formatting**: Structured layouts for business communications

### 📊 **Comprehensive Analytics**
- **Engagement Analysis**: Track performance metrics and engagement trends
- **Content Insights**: Word count, readability scores, hashtag analysis, sentiment analysis
- **Visual Dashboard**: Interactive charts with Plotly visualizations
- **Performance Recommendations**: AI-driven insights for better engagement
- **Dataset Comparison**: Compare performance across different datasets

### 🗄️ **Dataset Management**
- **Multiple Datasets**: Switch between different post collections seamlessly
- **Auto-Processing**: Upload raw JSON files and automatically extract metadata
- **Smart Categorization**: AI-powered tagging, tone detection, and audience classification
- **Real-time Stats**: Live statistics and insights about your datasets
- **Export/Import**: Easy dataset sharing and backup functionality

#### 📁 **Dataset File Naming Convention**

The system uses a specific naming convention to organize datasets:

**Raw Datasets** (need processing):
```
raw_[category].json
```
Examples: `raw_tech_students.json`, `raw_professionals.json`, `raw_entrepreneurs.json`

**Processed Datasets** (ready for generation):
```
processed_raw_[category].json
```  
Examples: `processed_raw_tech_students.json`, `processed_raw_professionals.json`

**Structure Comparison:**
- **Raw**: Basic posts with `text` and `engagement` only
- **Processed**: Enhanced with AI-extracted `tags`, `tone`, `target_audience`, `language`, `length`, `line_count`

### 🎓 **College Student Journey Posts**
- **Specialized Dataset**: 1000+ posts covering the complete college experience
- **Year-wise Content**: First year to final year journey posts
- **Technical Events**: Hackathons, coding competitions, tech workshops
- **Academic Milestones**: Assignments, projects, internships, placements
- **Personal Growth**: Learning experiences, challenges, achievements

## 🏗️ Technical Architecture

<img src="resources/architecture.jpg" alt="System Architecture" style="width: 100%; max-width: 600px;"/>

### 🔧 **System Components**

#### **Stage 1: Data Processing & Analysis**
```
Raw Posts → Preprocessing → Feature Extraction → Dataset Creation
     ↓              ↓              ↓              ↓
Text Content → Topic/Language → Tags/Metadata → Structured Data
```

#### **Stage 2: Few-Shot Learning & Generation**
```
User Input → Few-Shot Selection → Prompt Engineering → LLM Generation → Post Output
     ↓              ↓                    ↓                ↓              ↓
Query Params → Similar Posts → Context Prompt → AI Model → Generated Content
```

### 🧠 **How AI & Few-Shot Learning Works**

#### **1. Few-Shot Learning Mechanism**
```python
# The system identifies similar posts based on:
- Topic/Tag matching
- Language preference  
- Length category
- Writing style patterns

# Example: For "Internship" + "Medium" + "English"
selected_examples = filter_posts(
    topic="Internship",
    length="Medium", 
    language="English"
)
```

#### **2. Prompt Engineering**
The system creates intelligent prompts by combining:
- **User Requirements**: Topic, length, language, tone
- **Context Examples**: 1-2 most relevant posts from dataset
- **Style Guidelines**: Specific instructions for writing style
- **Formatting Rules**: Hashtags, emojis, structure preferences

```python
# Prompt Structure:
"""
Generate a LinkedIn post using the below information.

1) Topic: {user_topic}
2) Length: {desired_length} 
3) Language: {language_preference}
4) Tone: {selected_tone}

Use the writing style as per the following examples:
Example 1: {similar_post_1}
Example 2: {similar_post_2}
"""
```

#### **3. LLM Integration**
- **Model**: Llama 3.1 70B Versatile (via Groq API)
- **Temperature**: Optimized for creative yet consistent output
- **Context Window**: Efficiently manages prompt length and examples
- **Error Handling**: Robust validation and fallback mechanisms

## 🚀 Quick Start Guide

### **Prerequisites**
- Python 3.8+
- Groq API Key ([Get yours here](https://console.groq.com/keys))

### **Installation**

1. **Clone the repository**
   ```bash
   git clone https://github.com/vacantvectors/project-genai-post-generator.git
   cd project-genai-post-generator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Key**
   Create a `.env` file in the project root:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

4. **Run the application**
   ```bash
   streamlit run main.py
   ```

5. **Access the app**
   Open your browser and navigate to `http://localhost:8501`

## 📚 Dataset Information

### **Primary Dataset (`processed_posts.json`)**
- **Size**: Professional LinkedIn posts with engagement metrics
- **Features**: Text content, engagement data, topics, language classification
- **Use Case**: General professional content generation

### **College Student Dataset (`college_student_posts.json`)**
- **Size**: 1000+ posts covering 4-year college journey
- **Coverage**: 
  - **First Year**: Orientation, first coding classes, basic programming
  - **Second Year**: OOP concepts, internship applications, technical workshops
  - **Third Year**: Advanced algorithms, first internships, open source contributions
  - **Fourth Year**: Final projects, placement preparation, graduation

#### **Sample College Journey Posts**
```json
{
  "text": "Day 1 of college! 🎓\nFeeling excited and nervous at the same time...",
  "tags": ["College Life", "First Year", "Computer Science"],
  "language": "English",
  "engagement": 45
}
```

## 🎮 Using the Application

### **1. Quick Generate Mode**
Perfect for fast content creation:
- Select topic from dropdown
- Choose length and language
- Pick tone and formatting options
- Click "Generate Post"

### **2. Advanced Customization**
For specific requirements:
- Enter custom topic
- Define target audience
- Specify post purpose
- Add context and keywords
- Generate tailored content

### **3. Analytics Dashboard**
Monitor your content performance:
- Engagement metrics
- Content analysis
- Tag performance
- Performance insights

### **4. Dataset Management**
- Upload new posts
- Switch between datasets
- Merge datasets
- Export analytics

## 🔍 Feature Deep Dive

### **Smart Post Generation**
```python
# Example generation process:
1. User selects: Topic="Hackathon", Length="Medium", Language="English"
2. System finds similar posts in dataset
3. Creates context-aware prompt with examples
4. LLM generates new post matching style
5. Post validation and formatting
6. Output delivered to user
```

### **Error Handling & Validation**
- **Input Validation**: Sanitizes user inputs
- **API Error Handling**: Graceful degradation for API issues
- **Data Validation**: Ensures dataset integrity
- **Logging**: Comprehensive error tracking

### **Performance Optimization**
- **Caching**: Intelligent caching of API responses
- **Batch Processing**: Efficient handling of multiple requests
- **Memory Management**: Optimized data loading and processing

## 📊 Analytics & Insights

### **Available Metrics**
- **Engagement Analytics**: Total, average, median engagement
- **Content Metrics**: Word count, hashtags, emojis, readability
- **Performance Insights**: Best performing topics, optimal length
- **Trend Analysis**: Language preferences, tag popularity

### **Visualization Features**
- Interactive charts with Plotly
- Word clouds for content analysis
- Performance comparison graphs
- Exportable analytics reports

## 🛠️ Advanced Configuration

### **Custom Prompt Templates**
Create reusable templates for specific use cases:
```python
template = {
    "name": "Tech Achievement Post",
    "prompt": "Generate a post about {achievement} for {audience}...",
    "variables": ["achievement", "audience"]
}
```

### **Dataset Customization**
Add your own posts to improve generation:
```json
{
    "text": "Your post content here...",
    "engagement": 150,
    "language": "English",
    "tags": ["Your", "Tags"],
    "line_count": 5
}
```

## 🔧 Project Structure
```
project-genai-post-generator/
├── main.py                     # Main Streamlit application
├── post_generator.py           # Core generation logic
├── few_shot.py                # Few-shot learning implementation
├── llm_helper.py              # LLM integration
├── analytics.py               # Analytics and insights
├── error_handler.py           # Error handling utilities
├── preprocess.py              # Data preprocessing
├── requirements.txt           # Dependencies
├── README.md                  # Documentation
├── data/
│   ├── processed_posts.json   # Main dataset
│   ├── college_student_posts.json  # Student-specific dataset
│   ├── generated_posts_history.json  # Generation history
│   └── prompt_templates.json # Custom templates
└── resources/
    ├── architecture.jpg       # Architecture diagram
    └── tool.jpg              # Tool screenshot
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Add tests if applicable**
5. **Commit your changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```
6. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

### **Areas for Contribution**
- Additional datasets (industry-specific posts)
- New generation algorithms
- Enhanced analytics features
- UI/UX improvements
- Performance optimizations

## 🐛 Troubleshooting

### **Common Issues**

#### **API Key Errors**
```
❌ Error: GROQ_API_KEY not found
Solution: Ensure .env file contains valid GROQ_API_KEY
```

#### **Module Import Errors**
```
❌ Error: ModuleNotFoundError
Solution: Run 'pip install -r requirements.txt'
```

#### **Generation Failures**
```
❌ Error: Model not responding
Solution: Check internet connection and API key validity
```

### **Performance Issues**
- Clear browser cache
- Restart Streamlit server
- Check system memory usage
- Verify API rate limits

## 📈 Roadmap

### **Upcoming Features**
- [ ] **Multi-platform Support**: Twitter, Facebook post generation
- [ ] **Advanced AI Models**: Integration with GPT-4, Claude
- [ ] **Real-time Analytics**: Live performance tracking
- [ ] **Collaborative Features**: Team workspaces
- [ ] **API Integration**: REST API for external applications
- [ ] **Mobile App**: Native mobile application

### **Enhanced Analytics**
- [ ] **Sentiment Analysis**: Post emotion tracking
- [ ] **Competitor Analysis**: Benchmark against industry standards
- [ ] **Optimal Timing**: Best posting time recommendations
- [ ] **A/B Testing**: Content variation testing

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Groq** for providing excellent LLM API services
- **Streamlit** for the amazing web app framework
- **LangChain** for LLM integration capabilities
- **Plotly** for interactive visualization tools
- **Open Source Community** for various libraries and tools

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/vacantvectors/project-genai-post-generator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/vacantvectors/project-genai-post-generator/discussions)
- **Email**: support@vacantvectors.io

## 🌟 Show Your Support

If this project helps you, please consider:
- ⭐ Starring the repository
- 🐛 Reporting bugs
- 💡 Suggesting new features
- 📢 Sharing with others

---

<div align="center">
  <p><strong>Made with ❤️ by the Vacant Vectors Team</strong></p>
  <p>Empowering creators with AI-driven content generation</p>
</div>
