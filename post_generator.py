from llm_helper import llm
from few_shot import FewShotPosts
from error_handler import validate_llm_response, LLMError
from config import get_config, LENGTH_DEFINITIONS
import logging

logger = logging.getLogger(__name__)

# Initialize with default, but allow override
few_shot = None

def get_few_shot_instance(dataset_path=None):
    """Get FewShotPosts instance with optional dataset override"""
    global few_shot
    if dataset_path:
        return FewShotPosts(dataset_path)
    if few_shot is None:
        few_shot = FewShotPosts()
    return few_shot


def get_length_str(length):
    """Get length description from config"""
    length_config = LENGTH_DEFINITIONS.get(length, {})
    return length_config.get("lines", "1 to 5 lines")


def generate_post(length, language, tag, tone="Professional", include_hashtags=True, 
                 include_emojis=True, add_cta=False, professional=False, dataset_path=None):
    """Generate a post with error handling"""
    try:
        fs = get_few_shot_instance(dataset_path)
        prompt = get_prompt(length, language, tag, tone, include_hashtags, 
                           include_emojis, add_cta, professional, fs)
        
        response = llm.invoke(prompt)
        
        if response and hasattr(response, 'content'):
            content = response.content
            validate_llm_response(content)
            logger.info("Post generated successfully")
            return content
        else:
            raise LLMError("Empty response from LLM")
            
    except Exception as e:
        logger.error(f"Error generating post: {e}")
        raise


def generate_custom_post(topic, audience, purpose, length, language, style, 
                        context="", keywords=None):
    """Generate a custom post with specific parameters and error handling"""
    try:
        if keywords is None:
            keywords = []
        
        prompt = get_custom_prompt(topic, audience, purpose, length, language, 
                                  style, context, keywords)
        response = llm.invoke(prompt)
        
        if response and hasattr(response, 'content'):
            content = response.content
            validate_llm_response(content)
            logger.info("Custom post generated successfully")
            return content
        else:
            raise LLMError("Empty response from LLM")
            
    except Exception as e:
        logger.error(f"Error generating custom post: {e}")
        raise


def get_prompt(length, language, tag, tone="Professional", include_hashtags=True, 
               include_emojis=True, add_cta=False, professional=False, fs=None):
    if fs is None:
        fs = get_few_shot_instance()
        
    length_str = get_length_str(length)

    prompt = f'''
    Generate a LinkedIn post using the below information. No preamble.

    1) Topic: {tag}
    2) Length: {length_str}
    3) Language: {language}
    4) Tone: {tone}
    5) Include Hashtags: {include_hashtags}
    6) Include Emojis: {include_emojis}
    7) Add Call-to-Action: {add_cta}
    8) Professional Format: {professional}
    
    If Language is Hinglish then it means it is a mix of Hindi and English. 
    The script for the generated post should always be English.
    
    Additional Guidelines:
    - If tone is "Humorous", include light jokes or witty observations
    - If tone is "Inspirational", focus on motivation and positive messaging
    - If tone is "Educational", provide valuable insights or tips
    - If tone is "Casual", use conversational language and personal anecdotes
    - If include_hashtags is True, add 3-5 relevant hashtags at the end
    - If include_emojis is True, use appropriate emojis throughout the post
    - If add_cta is True, include a call-to-action like "What's your experience?" or "Share your thoughts"
    - If professional is True, maintain formal business language
    '''

    examples = fs.get_filtered_posts(length, language, tag)

    if len(examples) > 0:
        prompt += "\n\n9) Use the writing style as per the following examples:"

    for i, post in enumerate(examples):
        post_text = post['text']
        prompt += f'\n\n Example {i+1}: \n\n {post_text}'

        if i == 1:  # Use max two samples
            break

    return prompt


def get_custom_prompt(topic, audience, purpose, length, language, style, context, keywords):
    """Generate a custom prompt for specific requirements"""
    length_str = get_length_str(length)
    keywords_str = ", ".join(keywords) if keywords else "None specified"
    
    prompt = f'''
    Generate a LinkedIn post with the following specifications. No preamble.

    CONTENT SPECIFICATIONS:
    1) Topic: {topic}
    2) Target Audience: {audience}
    3) Post Purpose: {purpose}
    4) Length: {length_str}
    5) Language: {language}
    6) Writing Style: {style}
    7) Additional Context: {context}
    8) Keywords to Include: {keywords_str}

    STYLE GUIDELINES:
    - {get_style_guidelines(style)}
    - {get_audience_guidelines(audience)}
    - {get_purpose_guidelines(purpose)}
    
    FORMATTING:
    - Use appropriate emojis for engagement
    - Include relevant hashtags
    - Ensure the post is engaging and authentic
    - If language is Hinglish, mix Hindi and English naturally
    
    Make the post relatable, engaging, and valuable for the target audience.
    '''
    
    return prompt


def get_style_guidelines(style):
    """Get specific guidelines for writing styles"""
    guidelines = {
        "Storytelling": "Structure as a narrative with beginning, middle, and end. Use personal anecdotes.",
        "List Format": "Present information in numbered points or bullet format for easy readability.",
        "Question-Answer": "Start with a compelling question and provide thoughtful answers.",
        "Tips & Tricks": "Focus on actionable advice and practical insights.",
        "Personal Reflection": "Share personal experiences, lessons learned, and honest insights."
    }
    return guidelines.get(style, "Write in an engaging and authentic manner.")


def get_audience_guidelines(audience):
    """Get specific guidelines for target audiences"""
    guidelines = {
        "Students": "Use relatable college/university experiences, learning journey, academic challenges.",
        "Professionals": "Focus on career growth, workplace insights, professional development.",
        "Entrepreneurs": "Emphasize business insights, startup journey, leadership lessons.",
        "Job Seekers": "Address job search challenges, interview tips, career transition advice.",
        "General": "Keep content broadly relatable and universally valuable."
    }
    return guidelines.get(audience, "Keep content relevant and valuable.")


def get_purpose_guidelines(purpose):
    """Get specific guidelines for post purposes"""
    guidelines = {
        "Share Experience": "Be authentic and share genuine personal experiences with lessons learned.",
        "Give Advice": "Provide actionable tips and insights based on experience.",
        "Ask Question": "Engage audience with thought-provoking questions that encourage interaction.",
        "Celebrate Achievement": "Share accomplishments while remaining humble and inspiring others.",
        "Educational": "Focus on teaching something valuable with clear, actionable information."
    }
    return guidelines.get(purpose, "Create valuable and engaging content.")


def generate_college_student_post(year, event_type, subject="Computer Science", 
                                 emotion="excited", length="Medium", language="English"):
    """Generate posts specifically for college students"""
    
    prompt = f'''
    Generate a LinkedIn post from the perspective of a {year} year Computer Science Engineering student.
    
    CONTEXT:
    - Student Year: {year}
    - Event/Experience: {event_type}
    - Subject: {subject}
    - Emotional Tone: {emotion}
    - Length: {get_length_str(length)}
    - Language: {language}
    
    REQUIREMENTS:
    - Write from a genuine student perspective
    - Include relevant technical terms and college experiences
    - Show growth and learning mindset
    - Use appropriate hashtags for students
    - Include emojis for engagement
    - Make it relatable to other students
    
    EXAMPLES OF EVENTS:
    - First coding class, hackathon participation, internship application
    - Project completion, exam stress, placement preparation
    - Technical workshop, coding competition, group project
    - Campus fest, technical presentation, open source contribution
    
    Make the post authentic and inspiring for fellow students.
    '''
    
    response = llm.invoke(prompt)
    return response.content


if __name__ == "__main__":
    print(generate_post("Medium", "English", "Mental Health"))
    print("\n" + "="*50 + "\n")
    print(generate_college_student_post("Second", "First Hackathon", emotion="nervous but excited"))