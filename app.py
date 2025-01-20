# main.py
import streamlit as st
import os
import requests
from PIL import Image
from dotenv import load_dotenv
import time
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
from datetime import datetime
from groq import Groq
from typing import Dict, List
import ast
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import pyrebase
import re
from urllib.parse import urlencode
from urllib.parse import urlparse

os.environ["GROQ_API_KEY"] = "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"

load_dotenv()

# Initialize session states
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'page' not in st.session_state:
    st.session_state.page = "Login"
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        "name": "",
        "email": "",
        "phone": "",
        "bio": "",
        "institution": "",
        "degree": "",
        "branch": "",
        "year_of_joining": datetime.now().year,
        "linkedin": "",
        "github": "",
        "skills": [],
        "is_verified": False,
        "last_updated": ""
    }
if 'prompt' not in st.session_state:
    st.session_state.prompt = ""

if 'recent_activity' not in st.session_state:
    st.session_state.recent_activity = []

# Theme and styling
st.set_page_config(page_title="CodeExe", page_icon="🤖", layout="wide")

def load_lottie_url(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Load animations
coding_animation = load_lottie_url("https://assets2.lottiefiles.com/packages/lf20_xvrofzfk.json")
analysis_animation = load_lottie_url("https://assets5.lottiefiles.com/packages/lf20_bp5lntrf.json")
translation_animation = load_lottie_url("https://assets4.lottiefiles.com/packages/lf20_DMgKk1.json")

class LLMInterface:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.1-70b-versatile"

    def generate_response(self, prompt, max_tokens=1000):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating response: {e}")
            return None
        
firebase_config = {
    "apiKey": "AIzaSyByNgD6Gy0vxkgVZ2oRIiVeKBvyz2Avnhk",
    "authDomain": "codeexe-b1462.firebaseapp.com",
    "databaseURL": "https://codeexe-b1462-default-rtdb.firebaseio.com",
    "projectId": "codeexe-b1462",
    "storageBucket": "codeexe-b1462.appspot.com",  
    "messagingSenderId": "941011777680",
    "appId": "1:941011777680:web:abffc37228d9a45bf34015",
    "measurementId": "G-N1QZMBB1PY"
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database() 

def apply_custom_css():
    st.markdown("""
    <style>
    /* Main theme colors and variables */
    :root {
        --primary-color: #6C63FF;
        --secondary-color: #4CAF50;
        --background-color: #F0F2F6;
        --text-color: #2C3E50;
        --accent-color: #FF6B6B;
    }

    /* Animations */
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
        100% { transform: translateY(0px); }
    }

    @keyframes slideIn {
        from { transform: translateX(-100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }

    /* Navigation Bar */
    .navigation-bar {
        background-color: var(--primary-color);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        animation: slideIn 0.5s ease-out;
    }

    /* Cards and Containers */
    .custom-card {
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        transition: transform 0.3s ease;
    }

    .custom-card:hover {
        transform: translateY(-5px);
    }

    /* Buttons */
    .stButton > button {
        background-color: var(--primary-color);
        color: white;
        border-radius: 25px;
        padding: 10px 25px;
        border: none;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background-color: var(--secondary-color);
        transform: scale(1.05);
    }

    /* Form inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 10px;
        border: 2px solid var(--primary-color);
        padding: 10px;
    }

    /* Profile section */
    .profile-container {
        animation: float 6s ease-in-out infinite;
    }

    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# Custom CSS for styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .stButton > button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        padding: 0.5rem 1rem;
        border: none;
        border-radius: 5px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #45a049;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .auth-container {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-top: 1rem;
    }
    .title-container {
        text-align: center;
        margin-bottom: 2rem;
    }
    .stTextInput > div > div > input {
        border-radius: 5px;
        padding: 0.5rem;
        border: 1px solid #ddd;
    }
    .secondary-button > button {
        background-color: #6c757d;
    }
    .auth-link {
        color: #4CAF50;
        text-align: center;
        cursor: pointer;
        text-decoration: underline;
    }
    .success-container {
        text-align: center;
        padding: 2rem;
    }
    </style>
""", unsafe_allow_html=True)


def is_valid_email(email):
    """
    Validate email format using a comprehensive regex pattern.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def login_page():
    st.markdown("<div class='navigation-bar'>", unsafe_allow_html=True)
    st.title("🚀 CodeExe Login")
    st.markdown("</div>", unsafe_allow_html=True)

    with st.container():
        st_lottie(coding_animation, height=250, key="login_animation")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        
        button_col1, button_col2 = st.columns([1, 1])
        with button_col1:
            if st.button("Login 🚀"):
                try:
                    if 'user_profile' in st.session_state:
                        del st.session_state.user_profile
                    if 'profile_loaded' in st.session_state:
                        del st.session_state.profile_loaded

                    user = auth.sign_in_with_email_and_password(email, password)
                    user_info = auth.get_account_info(user['idToken'])
                    email_verified = user_info['users'][0]['emailVerified']
                    
                    if not email_verified:
                        st.error("⚠️ Please verify your email before logging in.")
                        if st.button("📧 Resend Verification Email"):
                            auth.send_email_verification(user['idToken'])
                            st.success("✅ Verification email sent!")
                    else:
                        st.session_state['user'] = {
                            'idToken': user['idToken'],
                            'localId': user['localId'],
                            'refreshToken': user['refreshToken'],
                            'email': email
                        }
                        st.session_state['logged_in'] = True
                        
                        # Get the requested page from query params or default to home
                        query_params = st.query_params
                        requested_page = query_params.get('page', ['home'])[0]
                        st.query_params['page'] = requested_page
                        st.rerun()
                except Exception as e:
                    st.error("❌ Login failed. Please check your credentials.")
                    print(f"Login error: {str(e)}")

        with button_col2:
            if st.button("Forgot Password? 🔑"):
                st.session_state.page = "Reset Password"

        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.write("New to CodeExe?")
        if st.button("Create Account ✨"):
            st.session_state.page = "Sign Up"
        st.markdown("</div>", unsafe_allow_html=True)

def sign_up_page():
    st.markdown("<div class='navigation-bar'>", unsafe_allow_html=True)
    st.title("✨ Join CodeExe")
    st.markdown("</div>", unsafe_allow_html=True)

    if "account_created" not in st.session_state:
        st.session_state.account_created = False

    if not st.session_state.account_created:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.subheader("Create your account")
            
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")

            if st.button("Sign Up ✨"):
                if not email.strip():
                    st.error("❌ Email required")
                elif not is_valid_email(email):
                    st.error("❌ Invalid email format")
                elif not password:
                    st.error("❌ Password required")
                elif password != confirm_password:
                    st.error("❌ Passwords don't match")
                else:
                    try:
                        user = auth.create_user_with_email_and_password(email, password)
                        auth.send_email_verification(user['idToken'])
                        st.session_state.account_created = True
                        st.session_state.verification_email_sent = email
                        st.rerun()
                    except Exception as e:
                        st.error("❌ Sign-up failed")
                        print(f"Sign-up error: {e}")

            st.markdown("<div style='text-align: center; margin-top: 1rem;'>", unsafe_allow_html=True)
            st.write("Already have an account?")
            if st.button("Sign In 🚀"):
                st.session_state.page = "Login"
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        
        st.success("🎉 Account created successfully!")
        st.info("📧 Please check your email for verification.")
        if st.button("Go to Login 🚀"):
            st.session_state.page = "Login"
            st.session_state.account_created = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

def reset_password_page():
    st.markdown("<div class='navigation-bar'>", unsafe_allow_html=True)
    st.title("🔑 Reset Password")
    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("Forgot your password?")
        st.write("Enter your email address and we'll send you a reset link.")
        
        email = st.text_input("Email", placeholder="Enter your email")

        if st.button("Send Reset Link 📧"):
            try:
                auth.send_password_reset_email(email)
                st.success("✅ Reset link sent! Check your email.")
            except Exception as e:
                st.error("❌ Failed to send reset email")

        st.markdown("<div style='text-align: center; margin-top: 1rem;'>", unsafe_allow_html=True)
        if st.button("Back to Login 🔙"):
            st.session_state.page = "Login"
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

def navigation_bar():
    selected = option_menu(
        menu_title=None,
        options=["Home", "Code Analysis", "Image Processing", "Translator", 
                 "Error Detection", "Learning Hub", "Code Generator",
                 "Code Execution", "Community", "Profile", "About","FAQ","Logout"],  
        icons=["house", "code-square", "image", "translate", "bug", 
               "book", "gear", "code-square", "people", "person", "info-circle","question-circle","box-arrow-right"],  
        orientation="horizontal",
    )
    return selected

def home_page():
    # Navigation bar at the top
    st.markdown("""
        <div class='navigation-bar'>
            <style>
                .activity-card {
                    border-left: 3px solid #ff4b4b;
                    padding-left: 10px;
                    margin: 10px 0;
                }
            </style>
        </div>
    """, unsafe_allow_html=True)
    
    st.title("🏠 Welcome to CodeExe")
    
    # Simple greeting based on time
    current_hour = datetime.now().hour
    greeting = "Good morning" if 5 <= current_hour < 12 else "Good afternoon" if 12 <= current_hour < 18 else "Good evening"
    st.write(f"### {greeting}! 👋")
    
    st_lottie(coding_animation, height=300, key="welcome_animation")
    
    col1, col2 = st.columns(2)

    # Recent Activity Section
    with col1:
        st.subheader("📊 Recent Activity")
        
        if "recent_activity" in st.session_state and st.session_state.recent_activity:
            for activity in st.session_state.recent_activity:
                st.markdown(f"""
                    <div class="activity-card">
                        <small>{activity['timestamp']}</small><br>
                        {activity['description']}
                    </div>
                """, unsafe_allow_html=True)
                
        else:
            st.write("No recent activity. Start exploring our features!")

    with col2:
        st.subheader("🎯 Quick Actions")

        # Buttons for quick navigation
        if st.button("🚀 New Code Analysis", help="Start a new code analysis task"):
            st.session_state.page = code_analysis_page() 
        if st.button("📸 Start Image Processing", help="Begin processing images for code extraction"):
            st.session_state.page = image_processing_page()

        st.markdown("</div>", unsafe_allow_html=True)

def add_to_recent_activity(activity_type, description):
    """
    Add a new activity to the recent activity list with basic metadata.
    
    Args:
        activity_type (str): Type of activity (e.g., "analysis", "processing")
        description (str): Description of the activity
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    activity = {
        "type": activity_type,
        "description": description,
        "timestamp": timestamp
    }
    
    if "recent_activity" not in st.session_state:
        st.session_state.recent_activity = []
    
    # Add to the beginning of the list and maintain last 10 activities
    st.session_state.recent_activity.insert(0, activity)
    st.session_state.recent_activity = st.session_state.recent_activity[:10]

class CodeAnalyzer:
    def __init__(self):
        self.llm = LLMInterface()

    def explain_code(self, code_snippet):
        prompt = f"Explain the following code snippet in simple terms:\n\n{code_snippet}\n\nExplanation:"
        return self.llm.generate_response(prompt)

class BugDetector:
    def __init__(self):
        self.llm = LLMInterface()

    def detect_bugs(self, code_snippet):
        prompt = f"Identify potential bugs or issues in the following code snippet:\n\n{code_snippet}\n\nPotential bugs or issues:"
        return self.llm.generate_response(prompt)

class Optimizer:
    def __init__(self):
        self.llm = LLMInterface()

    def optimize_code(self, code_snippet):
        prompt = f"Optimize the following code snippet for better performance and readability:\n\n{code_snippet}\n\nOptimized code:"
        return self.llm.generate_response(prompt)

def process_code(code, action, language=None):
    """
    Process code based on the selected action and language.
    
    Args:
        code (str): The code snippet to process
        action (str): The type of analysis to perform ("Explain", "Detect Bugs", or "Optimize")
        language (str, optional): Programming language of the code
    
    Returns:
        str: Analysis result
    """
    try:
        # Format the prompt with language if provided
        if language is None:
            prompt = code
        else:
            prompt = f"Language: {language}\n\nCode:\n{code}"
        
        # Perform the requested analysis
        if action == "Explain":
            analyzer = CodeAnalyzer()
            return analyzer.explain_code(prompt)
        elif action == "Detect Bugs":
            detector = BugDetector()
            return detector.detect_bugs(prompt)
        elif action == "Optimize":
            optimizer = Optimizer()
            return optimizer.optimize_code(prompt)
        else:
            return "Invalid action specified. Please choose 'Explain', 'Detect Bugs', or 'Optimize'."
            
    except Exception as e:
        return f"Error processing code: {str(e)}"

class CodeExecutor:
    def __init__(self):
        self.jdoodle_endpoint = "https://api.jdoodle.com/v1/execute"
        self.client_id = "3c4fb59a8a02dc00ab802d11675fca85"
        self.client_secret = "3d123a4e7ced42b684c4bb180b8983ed8d1758c2ac41e9f6c320dea06c665100"
        
        self.language_mapping = {
            "Python": "python3",
            "JavaScript": "nodejs",
            "Java": "java",
            "C++": "cpp17",
            "Ruby": "ruby",
            "Go": "go"
        }

    def execute_code(self, code, language, input_data=""):
        try:
            headers = {
                "Content-Type": "application/json"
            }
            
            jdoodle_language = self.language_mapping.get(language, "python3")
            
            payload = {
                "clientId": self.client_id,
                "clientSecret": self.client_secret,
                "script": code,
                "language": jdoodle_language,
                "versionIndex": "0",
                "stdin": input_data
            }
            
            response = requests.post(
                self.jdoodle_endpoint,
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "output": result.get("output", ""),
                    "memory": result.get("memory", ""),
                    "cpu_time": result.get("cpuTime", "")
                }
            else:
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        
def code_analysis_page():
    st.markdown("<div class='navigation-bar'>", unsafe_allow_html=True)
    st.title("🔍 Code Analysis")
    st.markdown("</div>", unsafe_allow_html=True)

    # Display analysis animation
    st_lottie(analysis_animation, height=200, key="analysis_animation")

    # Language selection
    language = st.selectbox("Select Language:", 
                             ["Python", "JavaScript", "Java", "C++", "Ruby", "Go"])

    # File upload for code
    uploaded_file = st.file_uploader("Upload your code file:", 
                                     type=["py", "java", "cpp", "js", "rb", "go"],
                                     help="Upload a file to analyze its code.")
    if uploaded_file is not None:
        code = uploaded_file.read().decode("utf-8")
        st.text_area("Uploaded Code", code, height=200)
    else:
        # Manual code input
        code = st.text_area("Enter your code manually", height=200)

    # Optional input data
    input_data = st.text_area("Input (optional):", 
                              help="Enter input data for your code", height=100)

    # Analysis type dropdown spanning both columns
    st.markdown("<b>Analysis Type:</b>", unsafe_allow_html=True)
    analysis_type = st.selectbox("", ["Explain", "Detect Bugs", "Optimize"], key="analysis_type_full")

    # Action buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Analyze Code"):
            with st.spinner("Analyzing..."):
                try:
                    # Perform detailed analysis
                    result = process_code(code, analysis_type, language)
                    if result:
                        st.subheader("Analysis Results")
                        st.write(result)
                        add_to_recent_activity("analysis", f"Code analysis performed: {analysis_type}")
                    else:
                        st.error("Analysis failed. Please try again.")
                except Exception as e:
                    st.error(f"Error during analysis: {str(e)}")

    with col2:
        # Shared Execute button
        if st.button("Execute Code"):
            with st.spinner("Executing..."):
                try:
                    executor = CodeExecutor()
                    result = executor.execute_code(code, language, input_data)

                    if result['success']:
                        st.subheader("Execution Results")
                        st.code(result['output'])
                        st.markdown(f"""
                            **Memory Used:** {result['memory']}  
                            **CPU Time:** {result['cpu_time']}
                        """)
                        add_to_recent_activity("execution", "Code execution completed")
                    else:
                        st.error(result['error'])
                except Exception as e:
                    st.error(f"Error during execution: {str(e)}")

    # Additional section for file details and working
    if uploaded_file:
        st.subheader("File Details and Analysis")
        st.markdown(f"""
            **File Name:** {uploaded_file.name}  
            **File Type:** {uploaded_file.type}  
            **File Size:** {len(uploaded_file.getvalue())} bytes
        """)

        st.markdown("""
            **How it Works:**  
            1. The uploaded file is read and analyzed based on the selected language and analysis type.  
            2. The analysis may include explaining the code logic, detecting potential bugs, optimizing code structure, and providing complexity analysis.  
            3. Execution allows you to run the uploaded code and see the results dynamically.
        """)

class CodeImageProcessor:
    def __init__(self):
        self.llm = LLMInterface()

    def detect_language(self, text):
        """
        Enhanced language detection with support for Ruby, C, and Go.
        """
        # Dictionary of language patterns with weighted scores
        language_patterns = {
            'Python': {
                'keywords': ['def ', 'class ', 'import ', 'from ', 'if __name__', 'print(', 
                           'return', 'self.', 'True', 'False', 'None', 'try:', 'except:',
                           'elif ', 'async ', 'await ', 'with '],
                'weight': 1.5
            },
            'JavaScript': {
                'keywords': ['function', 'const ', 'let ', 'var ', 'console.log', '=> {', 
                           'return', 'this.', 'true', 'false', 'null', 'undefined',
                           'async ', 'await ', 'import ', 'export '],
                'weight': 1.2
            },
            'Java': {
                'keywords': ['public class', 'private ', 'protected ', 'void ', 'System.out', 
                           'String[]', 'extends', 'implements', 'new ', 'interface ',
                           'abstract ', 'final ', 'static '],
                'weight': 1.3
            },
            'C++': {
                'keywords': ['#include', 'using namespace', 'std::', 'cout <<', 'cin >>', 
                           'int main(', 'void', 'class ', 'template<', 'vector<',
                           'public:', 'private:', 'protected:'],
                'weight': 1.4
            },
            'Ruby': {
                'keywords': ['def ', 'class ', 'module ', 'require ', 'attr_', 'puts ',
                           'yield ', 'super', 'initialize', '@', '@@', 'end\n',
                           'do |', 'rescue ', 'raise '],
                'weight': 1.3
            },
            'C': {
                'keywords': ['#include', 'int main(', 'void', 'printf(', 'scanf(',
                           'malloc(', 'free(', 'struct ', 'typedef ', '#define ',
                           'char *', 'return 0;', 'const '],
                'weight': 1.4
            },
            'Go': {
                'keywords': ['package ', 'func ', 'import (', 'type ', 'struct {',
                           'interface {', 'go ', 'chan ', 'defer ', 'select {',
                           'var ', 'const ', ':= '],
                'weight': 1.3
            }
        }

        # Additional distinguishing patterns
        language_specific_patterns = {
            'Ruby': {
                'symbols': [':', '=>', '@', '@@'],
                'weight': 2.0
            },
            'Go': {
                'patterns': [':=', 'func (', 'package main'],
                'weight': 2.0
            },
            'C': {
                'patterns': ['#include <stdio.h>', 'return 0;'],
                'weight': 2.0
            }
        }

        scores = {lang: 0 for lang in language_patterns}
        
        # Calculate scores based on keywords
        for lang, patterns in language_patterns.items():
            for keyword in patterns['keywords']:
                if keyword in text:
                    scores[lang] += text.count(keyword) * patterns['weight']

        # Add scores from specific patterns
        for lang, patterns in language_specific_patterns.items():
            for pattern_type, pattern_list in patterns.items():
                if pattern_type in ['symbols', 'patterns']:
                    for pattern in pattern_list:
                        if pattern in text:
                            scores[lang] += text.count(pattern) * patterns['weight']

        # Additional heuristics for similar languages
        if 'printf(' in text and '#include' in text:
            # Differentiate between C and C++
            if 'class' in text or 'std::' in text:
                scores['C++'] *= 1.2
            else:
                scores['C'] *= 1.2

        # Get the language with the highest score
        max_score = max(scores.values())
        if max_score > 0:
            detected_lang = max(scores.items(), key=lambda x: x[1])[0]
            confidence = 'High' if max_score > 3 else 'Medium' if max_score > 1 else 'Low'
            return detected_lang, confidence
        
        return "Unknown", "Low"

    def extract_text(self, image):
        """
        Enhanced text extraction with better preprocessing.
        """
        try:
            # Convert to grayscale
            gray_image = image.convert('L')
            
            # Enhanced image preprocessing
            enhanced = ImageEnhance.Contrast(gray_image).enhance(2.0)
            enhanced = enhanced.filter(ImageFilter.SHARPEN)
            enhanced = enhanced.filter(ImageFilter.EDGE_ENHANCE)
            
            # Extract text with improved configuration
            extracted_text = pytesseract.image_to_string(
                enhanced,
                config='--oem 3 --psm 6 -c preserve_interword_spaces=1'
            )
            
            if not extracted_text.strip():
                return {
                    'success': False,
                    'error': 'No text detected in the image'
                }
            
            # Improved language detection with confidence
            detected_lang, confidence = self.detect_language(extracted_text)
            
            return {
                'success': True,
                'text': extracted_text,
                'language': detected_lang,
                'confidence': confidence
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def analyze_text(self, text, language):
        """
        Enhanced code analysis with language-specific considerations.
        """
        try:
            language_specific_prompts = {
                'Ruby': "\n- Ruby-specific idioms and conventions\n- Gem usage and compatibility\n- Ruby version considerations",
                'C': "\n- Memory management analysis\n- Pointer usage safety\n- Buffer overflow risks\n- Standard library usage",
                'Go': "\n- Goroutine and channel usage\n- Error handling patterns\n- Package organization\n- Concurrency best practices"
            }

            base_prompt = f"""
                Analyze this {language} code and provide:
                1. Code Structure Analysis:
                    - Main components and their purposes
                    - Code organization and flow
                2. Code Quality Assessment:
                    - Best practices adherence
                    - Readability and maintainability
                3. Potential Issues:
                    - Bug risks
                    - Performance concerns
                    - Security considerations
                4. Specific Recommendations:
                    - Concrete improvement suggestions
                    - Alternative approaches
            {language_specific_prompts.get(language, '')}

            Code to analyze:
            {text}
            """
            return self.llm.generate_response(prompt=base_prompt)
        except Exception as e:
            return f"Analysis failed: {str(e)}"

    def explain_text(self, text, language):
        """
        Enhanced code explanation with language-specific contexts.
        """
        try:
            language_specific_prompts = {
                'Ruby': "\n- Ruby idioms and conventions used\n- Gem dependencies and requirements\n- Ruby-specific features utilized",
                'C': "\n- Memory management approach\n- Pointer usage and management\n- Standard library functions used",
                'Go': "\n- Concurrency patterns used\n- Error handling approach\n- Package organization and dependencies"
            }

            base_prompt = f"""
                    Explain this {language} code in detail:
                    1. Purpose and Functionality:
                    - What does this code do?
                    - What problem does it solve?
                    2. Implementation Breakdown:
                    - Step-by-step explanation
                    - Key algorithms and methods
                    3. Technical Details:
                    - Important variables and their roles
                    - Control flow and logic
                    4. Usage Context:
                    - When to use this code
                    - Potential applications
                    {language_specific_prompts.get(language, '')}

                    Code to explain:
                    {text}
                    """
            return self.llm.generate_response(prompt=base_prompt)
        except Exception as e:
            return f"Explanation failed: {str(e)}"
        
def image_processing_page():
    st.markdown("<div class='navigation-bar'>", unsafe_allow_html=True)
    st.title("📸 Code Image to Text Analyzer")
    st.markdown("</div>", unsafe_allow_html=True)

    # Initialize processor
    processor = CodeImageProcessor()

    # File upload
    uploaded_file = st.file_uploader("Upload an image containing code", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file:
        # Load and display original image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)
        
        # Create three columns for buttons
        col1, col2, col3 = st.columns(3)
        
        # Extract Text button
        if col1.button("Extract Text"):
            with st.spinner("Extracting text from image..."):
                try:
                    result = processor.extract_text(image)
                    if result['success']:
                        st.session_state.extracted_text = result['text']
                        st.session_state.detected_language = result['language']
                        
                        # Display extracted text in an editable text area
                        st.subheader("📝 Extracted Text")
                        st.session_state.edited_text = st.text_area(
                            "Edit extracted text if needed:",
                            value=result['text'],
                            height=200,
                            key="extracted_text_area"
                        )
                        
                        # Display language detection info
                        st.info(f"Detected Language: {result['language']} (Confidence: {result['confidence']})")

                    else:
                        st.error(f"Failed to extract text: {result.get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Error processing image: {str(e)}")

        # Rest of the buttons and functionality remains the same
        if col2.button("Analyze"):
            if 'extracted_text' in st.session_state:
                with st.spinner("Analyzing text..."):
                    analysis = processor.analyze_text(
                        st.session_state.edited_text,
                        st.session_state.detected_language
                    )
                    st.subheader("Analysis Results")
                    st.write(analysis)
                    add_to_recent_activity(
                        "analysis",
                        f"Analyzed {st.session_state.detected_language} code from image"
                    )
            else:
                st.warning("Please extract text from the image first")

        if col3.button("Explain"):
            if 'extracted_text' in st.session_state:
                with st.spinner("Generating explanation..."):
                    explanation = processor.explain_text(
                        st.session_state.edited_text,
                        st.session_state.detected_language
                    )
                    st.subheader("Code Explanation")
                    st.write(explanation)
                    add_to_recent_activity(
                        "explanation",
                        f"Generated explanation for {st.session_state.detected_language} code"
                    )
            else:
                st.warning("Please extract text from the image first")

    # Help section remains the same
    with st.expander("ℹ️ Usage Guide"):
        st.markdown("""
        ### How to Use:
        1. Upload an image containing code (screenshot, photo, etc.)
        2. Click "Extract Text" to get the code from the image
        3. Edit the extracted text if needed
        4. Use the copy button to copy the text
        5. Use the buttons to:
           - Analyze the code for insights
           - Get a detailed explanation
        
        ### Tips for Best Results:
        - Use clear, high-resolution images
        - Ensure the code is well-lit and in focus
        - Avoid glare or shadows on the code
        - Make sure the code is properly formatted in the image
        - Use images with good contrast between text and background
        """)
        
class CodeTranslator:
    def __init__(self):
        self.llm = LLMInterface()

    def translate_code(self, code, source_lang, target_lang):
        """
        Translate code from one programming language to another.
        
        Args:
            code (str): Source code to translate
            source_lang (str): Source programming language
            target_lang (str): Target programming language
            
        Returns:
            str: Translated code
        """
        prompt = f"""
Translate the following {source_lang} code to {target_lang}.
Maintain the same functionality and include comments explaining the translation.
Only respond with the translated code, no explanations outside the code comments.

Original code:
{code}

Translated {target_lang} code:"""
        
        try:
            translated_code = self.llm.generate_response(prompt)
            return translated_code
        except Exception as e:
            return f"Translation error: {str(e)}"
        
# First, add this helper function at the top level of your code, near your other utility functions
def get_file_extension(language):
    """
    Get the appropriate file extension for a programming language.
    """
    extensions = {
        "Python": "py",
        "Java": "java",
        "JavaScript": "js",
        "C++": "cpp",
        "Ruby": "rb",
        "Go": "go"
    }
    return extensions.get(language, "txt")

# Replace your existing translator_page() function with this updated version
def translator_page():
    st.markdown("<div class='navigation-bar'>", unsafe_allow_html=True)
    st.title("🌐 Code Translator")
    st.markdown("</div>", unsafe_allow_html=True)

    # Display translation animation
    st_lottie(translation_animation, height=200, key="translation_animation")

    source_lang = st.selectbox("Source Language",
        ["Python", "Java", "JavaScript", "C++", "Ruby", "Go"])
    
    code_input = st.text_area("Enter your code", height=300)
    st.markdown("</div>", unsafe_allow_html=True)

    target_lang = st.selectbox("Target Language",
        ["Python", "Java", "JavaScript", "C++", "Ruby", "Go"],
        index=1)  # Default to a different language than source

    if st.button("Translate Code"):
        if not code_input:
            st.error("Please enter some code to translate.")
        elif source_lang == target_lang:
            st.warning("Source and target languages are the same. Please select different languages.")
        else:
            with st.spinner("Translating your code..."):
                try:
                    translator = CodeTranslator()
                    translated_code = translator.translate_code(
                        code_input, source_lang, target_lang)

                    if translated_code:
                        st.code(translated_code, language=target_lang.lower())
                        add_to_recent_activity(
                            "translation",
                            f"Translated code from {source_lang} to {target_lang}")

                        # Download functionality
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        extension = get_file_extension(target_lang)
                        filename = f"translated_code_{timestamp}.{extension}"
                        st.download_button(
                            label="Download Translated Code",
                            data=translated_code,
                            file_name=filename,
                            mime="text/plain"
                        )
                    else:
                        st.error("Translation failed. Please try again.")
                except Exception as e:
                    st.error(f"Translation error: {str(e)}")
    st.markdown("</div>", unsafe_allow_html=True)

    # Tips section
    
    st.subheader("📝 Translation Tips")
    st.markdown("""
    - Ensure your code is syntactically correct in the source language
    - Include comments to explain complex logic
    - Some language-specific features may not have direct translations
    - Review the translated code for necessary adjustments
    """)
    st.markdown("</div>", unsafe_allow_html=True)


class RealTimeErrorDetector:
    def __init__(self):
        self.llm = LLMInterface()

    def analyze_code(self, code, language):
        """
        Analyze code for syntax errors, linting issues, and provide LLM suggestions.

        Args:
            code (str): The source code to analyze.
            language (str): The programming language of the code.

        Returns:
            Dict: A dictionary with syntax errors and LLM suggestions.
        """
        errors = []
        suggestions = []

        if language == "Python":
            # Syntax error check for Python
            try:
                ast.parse(code)
            except SyntaxError as e:
                errors.append({
                    "line": e.lineno,
                    "col": e.offset,
                    "type": "SyntaxError",
                    "message": str(e)
                })

        # Use LLM for suggestions
        try:
            prompt = f"""
                Analyze the following {language} code and suggest improvements:
                {code}

                Focus on:
                1. Best practices
                2. Performance optimization
                3. Code readability
                4. Potential bugs
                """
            suggestions = self.llm.generate_response(prompt)
        except Exception as e:
            suggestions = [f"Failed to generate suggestions: {str(e)}"]

        return {
            "errors": errors,
            "suggestions": suggestions
        }


def error_detection_page():
    """
    Streamlit page for real-time error detection and code analysis.
    """
    st.markdown("<div class='navigation-bar'>", unsafe_allow_html=True)
    st.title("🐛 Real-Time Error Detection")
    st.markdown("</div>", unsafe_allow_html=True)

    # Initialize error detector
    if 'error_detector' not in st.session_state:
        st.session_state.error_detector = RealTimeErrorDetector()

    # Code input and language selection
    language = st.selectbox("Select Language", ["Python", "JavaScript", "Java"])
    code_input = st.text_area("Write or paste your code", height=300)

    if code_input:
        col1, col2 = st.columns([2, 1])

        with col1:
            
            st.subheader("Code Analysis")

            analysis = st.session_state.error_detector.analyze_code(code_input, language)

            # Display errors with line highlighting
            if analysis["errors"]:
                st.error("Found the following issues:")
                for error in analysis["errors"]:
                    st.write(f"""
                    Line {error['line']}: {error['message']}
                    Type: {error['type']}
                    """)
            else:
                st.success("No syntax errors found!")

            st.markdown("</div>", unsafe_allow_html=True)

        with col2:

            st.subheader("Suggestions")
            if analysis["suggestions"]:
                st.write((analysis["suggestions"]))
            else:
                st.info("No suggestions generated.")
            st.markdown("</div>", unsafe_allow_html=True)


def learning_hub_page():
    """
    Displays a learning hub page with working buttons and improved interaction.
    """
    # Styling remains the same
    st.markdown("<div class='navigation-bar'>", unsafe_allow_html=True)
    
    st.title("📚 Learning Hub")
    
    # Search section
    with st.container():
        st.subheader("🔍 Explore Topics")
        col1, col2 = st.columns([2, 1])
        with col1:
            topic = st.text_input("Search for programming topics", 
                                value=st.session_state.get("topic", ""))
        with col2:
            category = st.selectbox(
                "Category",
                ["All", "Programming Basics", "Web Development", "Data Science", "DevOps"]
            )

    # Featured paths with working buttons
    st.subheader("📌 Learning Paths")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class='featured-card'>
                <div class='card-title'>🌟 Python Mastery</div>
                <div class='card-subtitle'>From basics to advanced concepts</div>
                <ul class='feature-list'>
                    <li>Core Python fundamentals</li>
                    <li>Object-oriented programming</li>
                    <li>Advanced Python features</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Start Python Path", key="python_path"):
            st.session_state.topic = "Python Programming"
            st.rerun()
    
    with col2:
        st.markdown("""
            <div class='featured-card'>
                <div class='card-title'>🚀 Web Development</div>
                <div class='card-subtitle'>Build modern web applications</div>
                <ul class='feature-list'>
                    <li>HTML/CSS mastery</li>
                    <li>JavaScript essentials</li>
                    <li>React development</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Start Web Dev Path", key="web_path"):
            st.session_state.topic = "Web Development"
            st.rerun()
    
    with col3:
        st.markdown("""
            <div class='featured-card'>
                <div class='card-title'>📊 Data Science</div>
                <div class='card-subtitle'>Master data analysis</div>
                <ul class='feature-list'>
                    <li>Data analysis tools</li>
                    <li>Visualization techniques</li>
                    <li>Machine learning basics</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Start Data Science Path", key="data_path"):
            st.session_state.topic = "Data Science"
            st.rerun()

    # Related topics with working buttons
    if topic:
        st.markdown("### 💡 Related Topics")
        suggestions = generate_suggestions(topic)
        cols = st.columns(len(suggestions))
        for i, suggestion in enumerate(suggestions):
            with cols[i]:
                if st.button(f"📚 {suggestion}", key=f"topic_{i}"):
                    st.session_state.topic = suggestion
                    st.rerun()

    if topic:
        # Topic header with bookmark option
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(f"Topic: {topic}")

        # Learning preferences
        col1, col2 = st.columns(2)
        with col1:
            explanation_level = st.selectbox(
                "Explanation Level",
                ["Basic Overview", "Standard Explanation", "Detailed Explanation"]
            )
        with col2:
            learning_style = st.selectbox(
                "Learning Style",
                ["Text", "Interactive", "Visual"]
            )

        # Initialize LLM interface with retry mechanism
        llm = LLMInterface()
        max_retries = 3
        
        try:
            # Generate dynamic prompt based on user preferences
            prompt = generate_prompt(topic, explanation_level, learning_style, category)
            
            # Fetch explanation with retry mechanism
            for attempt in range(max_retries):
                try:
                    explanation = llm.generate_response(prompt)
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    time.sleep(1)

            with st.expander("📝 Explanation", expanded=True):
                st.write(explanation)


            if learning_style == "Visual":
                with st.expander("📊 Visual Examples"):
                    display_visual_examples(topic)
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.button("🔄 Retry")

        st.markdown("</div>", unsafe_allow_html=True)

def generate_suggestions(topic: str) -> List[str]:
    """Generate related topic suggestions based on the search query."""
    # This would ideally use a more sophisticated recommendation system
    topic_map = {
        "python": ["Python OOP", "Python Libraries", "Python Testing", "Python Web Frameworks"],
        "javascript": ["React.js", "Node.js", "TypeScript", "JavaScript ES6+"],
        "data": ["SQL Basics", "Data Visualization", "pandas", "Data Cleaning"],
        "web": ["HTML/CSS", "JavaScript", "React", "Backend Development"],
    }
    
    # Find matching suggestions
    suggestions = []
    for key, values in topic_map.items():
        if key in topic.lower():
            suggestions.extend(values)
    
    # If no specific matches, return general suggestions
    if not suggestions:
        suggestions = [
            "Programming Fundamentals",
            "Web Development Basics",
            "Data Structures",
            "Algorithms"
        ]
    
    return suggestions[:4]  # Return top 4 suggestions

def generate_prompt(topic, level, style, category):
    """Generate contextual prompt based on user preferences."""
    prompts = {
        "Basic Overview": f"Provide a beginner-friendly overview of {topic}",
        "Standard Explanation": f"Explain {topic} with key concepts and examples",
        "Detailed Explanation": f"Provide comprehensive coverage of {topic} with advanced examples"
    }
    base_prompt = prompts[level]
    
    if style == "Interactive":
        base_prompt += " Include practical examples and exercises."
    elif style == "Visual":
        base_prompt += " Focus on visual explanations and diagrams."
        
    if category != "All":
        base_prompt += f" Focus on {category} context."
        
    return base_prompt

def display_visual_examples(topic):
    """Display visual examples and diagrams."""
    examples = generate_visual_examples(topic)
    for example in examples:
        st.image(example['image'])
        st.write(example['description'])

def generate_visual_examples(topic: str) -> List[Dict]:
    """Generate visual examples for a topic."""
    return [
        {
            "image": "placeholder.png",
            "description": f"Visual representation of {topic}"
        }
    ]
       
class CodeGenerator:
    def __init__(self):
        self.llm = LLMInterface()

    def generate_code(self, prompt, language, code_type="script"):
        """
        Generate code based on the prompt and specified language.
        
        Args:
            prompt (str): Description of what the code should do
            language (str): Target programming language
            code_type (str): Type of code (script, class, function, etc.)
            
        Returns:
            str: Generated code
        """
        template = f"""
            Generate {language} code that does the following:
            {prompt}

            Requirements:
            1. Include proper imports and dependencies
            2. Add comprehensive comments explaining the code
            3. Follow {language} best practices and conventions
            4. Include error handling where appropriate
            5. Make the code modular and reusable
            6. Include example usage if applicable

            Generate complete, working code that can be run directly.
            Only provide the code, no additional explanations.
            """
        try:
            return self.llm.generate_response(template, max_tokens=2000)
        except Exception as e:
            return f"Generation error: {str(e)}"

def code_generator_page():
    st.markdown("<div class='navigation-bar'>", unsafe_allow_html=True)
    st.title("⚙️ Code Generator")
    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        prompt = st.text_area(
            "Describe what you want to create",
            value=st.session_state.prompt,  # Use the updated session state value
            height=150,
            placeholder="Example: Create a function that takes a list of numbers and returns the average, median, and mode. Include error handling for empty lists and non-numeric values."
        )


        language = st.selectbox(
            "Select Language",
            ["Python", "Java", "JavaScript", "C++", "Ruby", "Go"]
        )

        code_type = st.selectbox(
            "Code Type",
            ["Script", "Function", "Class", "API Endpoint", "Database Operation", "Data Structure"]
        )

        additional_options = st.expander("Additional Options")
        with additional_options:
            include_comments = st.checkbox("Include Comments", value=True)
            include_tests = st.checkbox("Include Unit Tests", value=False)
            include_documentation = st.checkbox("Include Documentation", value=True)
            optimization_level = st.slider("Optimization Level", 1, 3, 2)

        if st.button("Generate Code"):
            if not prompt:
                st.error("Please provide a description of what you want to generate.")
            else:
                with st.spinner("Generating your code..."):
                    try:
                        generator = CodeGenerator()
                        
                        # Enhance prompt based on options
                        enhanced_prompt = f"""{prompt}

                            Additional requirements:
                            {'- Add detailed comments and documentation' if include_comments else ''}
                            {'- Include unit tests' if include_tests else ''}
                            {'- Include function/class documentation' if include_documentation else ''}
                            - Optimize code for {'speed' if optimization_level == 3 else 'readability' if optimization_level == 1 else 'balance of speed and readability'}
                            - Code type: {code_type}
                            """
                                                    
                        generated_code = generator.generate_code(
                            enhanced_prompt,
                            language,
                            code_type.lower()
                        )
                        
                        if generated_code:
                            # Display generated code
                            st.code(generated_code, language=language.lower())
                            
                            # Add to recent activity
                            add_to_recent_activity(
                                "generation",
                                f"Generated {code_type.lower()} in {language}"
                            )
                            
                            # Download button
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            extension = get_file_extension(language)
                            filename = f"generated_code_{timestamp}.{extension}"
                            st.download_button(
                                label="Download Generated Code",
                                data=generated_code,
                                file_name=filename,
                                mime="text/plain"
                            )
                        else:
                            st.error("Code generation failed. Please try again.")
                    except Exception as e:
                        st.error(f"Generation error: {str(e)}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        
        st.subheader("🎯 Quick Templates")
        templates = {
            "CRUD Operations": "Create CRUD operations for a user management system with name, email, and age fields.",
            "Data Processing": "Create a script to read a CSV file, process its data, and generate summary statistics.",
            "API Client": "Create an API client to fetch and process weather data from a REST API.",
            "Sort Algorithm": "Implement a sorting algorithm with time complexity analysis.",
            "File Handler": "Create a file handling utility to process text files and perform operations like search and replace."
        }

        for template_name, template_prompt in templates.items():
            if st.button(template_name):
                st.session_state.prompt = template_prompt  # Update session state
                st.rerun()  
                st.markdown("</div>", unsafe_allow_html=True)

    
        st.subheader("💡 Tips")
        st.markdown("""
        - Be specific about input/output requirements
        - Mention error cases to handle
        - Specify performance requirements
        - Include example scenarios
        - Mention any specific libraries to use
        """)
        st.markdown("</div>", unsafe_allow_html=True)

                        
def code_execution_page():
    st.markdown("<div class='navigation-bar'>", unsafe_allow_html=True)
    st.title("💻 Code Execution")
    st.markdown("</div>", unsafe_allow_html=True)

    # Language selection
    language = st.selectbox(
        "Select Programming Language:",
        ["Python", "JavaScript", "Java", "C++", "Ruby", "Go"]
    )

    # Code input area
    code = st.text_area("Enter your code here:", height=200)

    # Input data (optional)
    input_data = st.text_area("Input data (optional):", height=100)

    # Action selection
    action = st.radio(
        "Choose action:",
        ["Execute", "Analyze", "Explain"]
    )

    if st.button(f"{action} Code"):
        if not code:
            st.error("Please enter some code first!")
            return

        with st.spinner(f"{action}ing your code..."):
            try:
                if action == "Execute":
                    # Execute the code
                    executor = CodeExecutor()
                    result = executor.execute_code(code, language, input_data)
                    
                    if result['success']:
                        st.success("Code executed successfully!")
                        
                        # Display output in a formatted way
                        st.subheader("Output:")
                        st.code(result['output'])
                        
                        # Display execution metrics
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Memory Used", result['memory'])
                        with col2:
                            st.metric("CPU Time", result['cpu_time'])
                            
                    else:
                        st.error(f"Execution failed: {result.get('error', 'Unknown error')}")

                elif action == "Analyze":
                    # Initialize LLM interface for analysis
                    llm = LLMInterface()
                    prompt = f"""
                    Analyze this {language} code for:
                    1. Code quality and best practices
                    2. Potential bugs or issues
                    3. Performance considerations
                    4. Security concerns (if any)
                    
                    Code:
                    {code}
                    """
                    analysis = llm.generate_response(prompt)
                    
                    st.subheader("Code Analysis Results")
                    st.write(analysis)

                elif action == "Explain":
                    # Initialize LLM interface for explanation
                    llm = LLMInterface()
                    prompt = f"""
                    Explain this {language} code in detail:
                    1. Overall purpose and functionality
                    2. Step-by-step breakdown
                    3. Key components and their roles
                    4. Important variables and functions
                    
                    Code:
                    {code}
                    """
                    explanation = llm.generate_response(prompt)
                    
                    st.subheader("Code Explanation")
                    st.write(explanation)

                # Add to recent activity
                add_to_recent_activity(
                    action.lower(),
                    f"{action}ed {language} code"
                )

            except Exception as e:
                st.error(f"Error during {action.lower()}: {str(e)}")

    # Tips and documentation section
    with st.expander("📚 Tips & Documentation"):
        st.markdown("""
        ### How to use this tool:
        1. **Execute**: Runs your code and shows the output
            - Add input data if your code needs it
            - See memory usage and execution time
        
        2. **Analyze**: Examines your code for:
            - Code quality and best practices
            - Potential bugs or issues
            - Performance considerations
            - Security concerns
        
        3. **Explain**: Provides detailed explanation of:
            - Overall purpose and functionality
            - Step-by-step breakdown
            - Key components and their roles
            - Important variables and functions
        """)

def community_page():
    """
    Modern Streamlit page for community interactions with horizontal navigation and cards.
    """
    # Initialize session state for community type if not exists
    if 'community_type' not in st.session_state:
        st.session_state.community_type = "College"

    # Custom CSS for better styling
    st.markdown("""
        <style>
        .community-header {
            padding: 2rem 0;
            text-align: center;
            background: linear-gradient(135deg, #6B46C1 0%, #9F7AEA 100%);
            color: white;
            border-radius: 15px;
            margin-bottom: 2rem;
        }
        .card {
            border-radius: 15px;
            padding: 1.5rem;
            background: white;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
        }
        .community-type-btn {
            background-color: #ffffff;
            border: 2px solid #E2E8F0;
            border-radius: 10px;
            padding: 1rem;
            text-align: center;
            margin: 0.5rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .community-type-btn:hover {
            border-color: #9F7AEA;
            transform: translateY(-2px);
        }
        .community-type-btn.active {
            border-color: #6B46C1;
            background-color: #F3E8FF;
        }
        .chat-message {
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 10px;
            background: #F7FAFC;
        }
        .send-button {
            background-color: #6B46C1;
            color: white;
            padding: 0.5rem 2rem;
            border-radius: 20px;
            border: none;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header Section
    st.markdown("""
        <div class="community-header">
            <h1>🌐 Community Hub</h1>
            <p>Connect, Share, and Grow Together</p>
        </div>
    """, unsafe_allow_html=True)

    # Horizontal Community Type Selection
    st.markdown("### Choose Your Community")
    col1, col2, col3 = st.columns(3)
    
    def get_button_style(button_type):
        active_class = " active" if st.session_state.community_type == button_type else ""
        return f'<div class="community-type-btn{active_class}">'

    with col1:
        if st.button("🏫 College Communities", key="college_btn", use_container_width=True):
            st.session_state.community_type = "College"
            st.rerun()
    
    with col2:
        if st.button("📚 Department Groups", key="dept_btn", use_container_width=True):
            st.session_state.community_type = "Department"
            st.rerun()
        
    with col3:
        if st.button("💻 Domain-Specific", key="domain_btn", use_container_width=True):
            st.session_state.community_type = "Domain"
            st.rerun()

    # Community Selection Area
    st.markdown("### 🎯 Select Your Community")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.session_state.community_type == "College":
            selected_community = st.selectbox(
                "Select Your College",
                ["Sri Manakula Vinayagar Engineering College", 
                 "Pondicherry University",
                 "Puducherry Technological University"],
                key="college_select"
            )
        elif st.session_state.community_type == "Department":
            selected_community = st.selectbox(
                "Select Your Department",
                ["Computer Science", "Mechanical", "Electrical", "AI/ML"],
                key="dept_select"
            )
        else:
            selected_community = st.selectbox(
                "Select Your Domain",
                ["AI/ML", "Web Development", "Cybersecurity", "Robotics",
                 "Blockchain (Web3)", "Quantum Computing", "Post Quantum Cryptography"],
                key="domain_select"
            )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Join Community", use_container_width=True):
            st.success(f"Successfully joined {selected_community}!")

    # [Rest of the code remains the same...]
    # Community Interaction Area
    st.markdown("### 💭 Community Discussion")
    
    # Initialize chat messages
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"user": "Community Bot", "content": "Welcome to the community! Feel free to start a discussion or ask questions."},
            {"user": "Sarah", "content": "Hey everyone! Anyone interested in working on a project together?"},
            {"user": "Alex", "content": "I'd love to collaborate! What kind of project did you have in mind?"}
        ]

    # Chat display
    for msg in st.session_state.messages:
        st.markdown(f"""
            <div class="chat-message">
                <strong>{msg['user']}</strong><br>
                {msg['content']}
            </div>
        """, unsafe_allow_html=True)

    # Message input
    col1, col2 = st.columns([4, 1])
    with col1:
        user_message = st.text_input("Share your thoughts...", key="message_input")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Send", use_container_width=True):
            if user_message:
                st.session_state.messages.append({"user": "You", "content": user_message})
                st.rerun()
            else:
                st.warning("Please enter a message!")

    # Community Stats
    st.markdown("### 📊 Community Stats")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Members", "1,234")
    with col2:
        st.metric("Active Now", "56")
    with col3:
        st.metric("Posts Today", "89")
    with col4:
        st.metric("Projects", "23")

    # Tips and Guidelines
    st.markdown("""
        <div class="card">
            <h4>🌟 Community Guidelines</h4>
            <ul>
                <li>Be respectful and inclusive</li>
                <li>Share knowledge and resources</li>
                <li>Help others learn and grow</li>
                <li>Organize and participate in events</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

def save_profile_data(profile_data, section="all"):
    """
    Save profile data to Firebase for the currently authenticated user.
    
    Args:
        profile_data (dict): The profile data to save
        section (str): The section of the profile to update (default: "all")
    """
    try:
        # Check if user is authenticated
        if 'user' not in st.session_state or not st.session_state['user'].get('localId'):
            raise Exception("User not authenticated")

        # Refresh token before saving
        refresh_token()

        user_id = st.session_state['user']['localId']
        
        # Ensure email is included
        if 'email' not in profile_data and 'user' in st.session_state:
            profile_data['email'] = st.session_state['user'].get('email', '')

        if section == "all":
            # Save entire profile
            db.child("users").child(user_id).set(profile_data, token=st.session_state['user']['idToken'])
            st.session_state.user_profile = profile_data
        else:
            # Update only specific section
            current_data = st.session_state.user_profile or {}
            current_data[section] = profile_data[section]
            db.child("users").child(user_id).update({section: profile_data[section]}, 
                                                   token=st.session_state['user']['idToken'])
            st.session_state.user_profile = current_data
        
        return True, "Profile updated successfully!"
        
    except Exception as e:
        print(f"Error saving profile: {str(e)}")  # For debugging
        return False, f"Failed to save profile: {str(e)}"

def load_profile_data():
    """
    Load profile data from Firebase for the currently authenticated user.
    Returns True if successful, False otherwise.
    """
    try:
        # Clear existing profile data first
        st.session_state.user_profile = {}
        
        # Check if user is authenticated
        if 'user' not in st.session_state or not st.session_state['user'].get('localId'):
            st.warning("Please log in to view your profile.")
            return False

        # Refresh token before making the request
        refresh_token()

        # Get the current user's ID
        user_id = st.session_state['user']['localId']
        
        # Fetch user data from Firebase
        user_data = db.child("users").child(user_id).get(token=st.session_state['user']['idToken'])
        
        if user_data.val():
            # Store the data in session state
            st.session_state.user_profile = user_data.val()
            return True
        else:
            # Initialize empty profile for new users
            st.session_state.user_profile = {
                'email': st.session_state['user'].get('email', ''),
                'name': '',
                'year_of_joining': '',
                'institution': '',
                'degree': '',
                'branch': '',
                'linkedin': ''
            }
            return True
            
    except Exception as e:
        print(f"Error loading profile: {str(e)}")  # For debugging
        st.error(f"Failed to load profile data: {str(e)}")
        return False


def refresh_token():
    try:
        user = auth.refresh(st.session_state['user']['refreshToken'])
        st.session_state['user']['idToken'] = user['idToken']
    except Exception as e:
        st.error(f"Session expired: {e}")
        st.session_state.logged_in = False
        st.session_state.page = "Login"
        st.rerun()

def profile_page():
    # Enhanced CSS with animations and better visual hierarchy
    st.markdown("""
        <style>
        /* Modern Color Palette */
        :root {
            --primary: #6B46C1;
            --primary-light: #9F7AEA;
            --secondary: #48BB78;
            --background: #F7FAFC;
            --card-bg: #FFFFFF;
            --text: #2D3748;
            --text-light: #718096;
            --error: #E53E3E;
            --success: #38A169;
        }

        /* Animations */
        @keyframes slideIn {
            from { transform: translateX(-10px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        .profile-header {
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
            color: white;
            padding: 2.5rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 10px 30px rgba(107, 70, 193, 0.2);
            animation: fadeIn 0.5s ease-out;
        }

        .profile-header h1 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }

        .profile-container {
            background: var(--card-bg);
            border-radius: 20px;
            padding: 2.5rem;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
            margin: 1rem 0;
            animation: slideIn 0.5s ease-out;
        }

        .profile-field {
            background: var(--background);
            padding: 1.2rem;
            border-radius: 12px;
            margin: 1rem 0;
            transition: all 0.3s ease;
            animation: slideIn 0.5s ease-out;
        }

        .profile-field:hover {
            transform: translateX(5px);
            box-shadow: 0 4px 12px rgba(107, 70, 193, 0.1);
        }

        .profile-label {
            color: var(--text-light);
            font-size: 1rem;
            font-weight: 500;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .profile-value {
            color: var(--text);
            font-size: 1.2rem;
            font-weight: 500;
            padding: 0.5rem 0;
        }

        .verification-badge {
            background: var(--success);
            color: white;
            padding: 0.2rem 0.5rem;
            border-radius: 12px;
            font-size: 0.8rem;
            margin-left: 0.5rem;
        }

        .profile-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 1.5rem 0;
        }

        .stat-card {
            background: var(--background);
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            transition: all 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 12px rgba(107, 70, 193, 0.1);
        }

        .required-field::after {
            content: " *";
            color: var(--error);
        }

        /* Form styling improvements */
        .stTextInput > div > div {
            border-radius: 12px !important;
        }

        .stSelectbox > div > div {
            border-radius: 12px !important;
        }

        .stTextArea > div > div {
            border-radius: 12px !important;
        }

        .profile-actions {
            display: flex;
            gap: 1rem;
            margin-top: 2rem;
        }

        .action-button {
            padding: 0.8rem 2rem;
            border-radius: 12px;
            border: none;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 500;
            text-align: center;
        }

        .primary-button {
            background: var(--primary);
            color: white;
        }

        .secondary-button {
            background: var(--background);
            color: var(--text);
            border: 1px solid var(--text-light);
        }
        </style>
    """, unsafe_allow_html=True)

    # Initialize session state variables
    if 'profile_loaded' not in st.session_state:
        st.session_state.profile_loaded = False
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {}
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False

    # Load profile data
    if not st.session_state.profile_loaded:
        success = load_profile_data()
        if success:
            st.session_state.profile_loaded = True
        else:
            st.error("Failed to load profile data. Please try again.")
            return
    st.markdown("<div class='navigation-bar'>", unsafe_allow_html=True)


    # Additional profile options
    branch_options = ["Computer Science", "Indormation Technology", "Mechanical", "Electrical", "Civil", "Electronics", "AI/ML", "Data Science", "Other"]
    degree_options = ["B.Tech", "B.E", "M.Tech", "M.E", "PhD", "Other"]
    year_options = list(range(2000, datetime.now().year + 1))
    
    # New fields for enhanced profile
    skill_options = [
        "Python", "Java", "JavaScript", "C++", "HTML/CSS",
        "React", "Angular", "Vue.js", "Node.js", "Django",
        "Machine Learning", "Data Science", "Cloud Computing",
        "DevOps", "Cybersecurity", "Mobile Development"
    ]

    if st.session_state.edit_mode:
        st.markdown("<div class='profile-container'>", unsafe_allow_html=True)
        st.subheader("✏️ Edit Profile")
        
        with st.form("edit_profile_form"):
            # Personal Information Section
            st.subheader("📋 Personal Information")
            
            name = st.text_input(
                "Full Name",
                value=st.session_state.user_profile.get('name', ''),
                help="Enter your full name as you'd like it to appear"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                current_year = st.session_state.user_profile.get('year_of_joining')
                if isinstance(current_year, str):
                    try:
                        current_year = int(current_year)
                    except ValueError:
                        current_year = year_options[0]
                
                year_index = year_options.index(current_year) if current_year in year_options else 0
                year_of_joining = st.selectbox(
                    "Year of Joining",
                    year_options,
                    index=year_index
                )
            
            with col2:
                phone = st.text_input(
                    "Phone Number (optional)",
                    value=st.session_state.user_profile.get('phone', ''),
                    help="Enter your contact number"
                )

            # Academic Information Section
            st.subheader("🎓 Academic Information")
            
            institution = st.text_input(
                "Institution Name",
                value=st.session_state.user_profile.get('institution', ''),
                help="Enter your college/university name"
            )

            col3, col4 = st.columns(2)
            with col3:
                degree_index = degree_options.index(st.session_state.user_profile.get('degree', degree_options[0])) if st.session_state.user_profile.get('degree') in degree_options else 0
                degree = st.selectbox(
                    "Degree",
                    degree_options,
                    index=degree_index
                )
            
            with col4:
                branch_index = branch_options.index(st.session_state.user_profile.get('branch', branch_options[0])) if st.session_state.user_profile.get('branch') in branch_options else 0
                branch = st.selectbox(
                    "Branch",
                    branch_options,
                    index=branch_index
                )

            # Skills Section
            st.subheader("🛠️ Skills & Expertise")
            
            selected_skills = st.multiselect(
                "Select your skills",
                options=skill_options,
                default=st.session_state.user_profile.get('skills', []),
                help="Choose your technical skills"
            )

            # Professional Links Section
            st.subheader("🔗 Professional Links")
            
            col5, col6 = st.columns(2)
            with col5:
                linkedin = st.text_input(
                    "LinkedIn Profile",
                    value=st.session_state.user_profile.get('linkedin', ''),
                    help="Enter your LinkedIn profile URL"
                )
            
            with col6:
                github = st.text_input(
                    "GitHub Profile",
                    value=st.session_state.user_profile.get('github', ''),
                    help="Enter your GitHub profile URL"
                )

            # Bio Section
            st.subheader("📝 Bio")
            bio = st.text_area(
                "About Me",
                value=st.session_state.user_profile.get('bio', ''),
                help="Write a brief introduction about yourself",
                max_chars=500
            )

            # Form Buttons
            col7, col8 = st.columns([1, 1])
            with col7:
                save_button = st.form_submit_button("💾 Save Changes", use_container_width=True)
            with col8:
                back_button = st.form_submit_button("↩️ Back to Profile", use_container_width=True)

        if save_button:
            if not name.strip():
                st.error("Name is required!")
            else:
                # Update profile with new fields
                updated_profile = {
                    "name": name.strip(),
                    "year_of_joining": year_of_joining,
                    "phone": phone.strip(),
                    "institution": institution.strip(),
                    "degree": degree,
                    "branch": branch,
                    "email": st.session_state.user_profile.get('email', ''),
                    "linkedin": linkedin.strip(),
                    "github": github.strip(),
                    "bio": bio.strip(),
                    "skills": selected_skills,
                    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                success, message = save_profile_data(updated_profile)
                if success:
                    st.success("✅ Profile updated successfully!")
                    st.session_state.user_profile = updated_profile
                    st.session_state.edit_mode = False
                    
                else:
                    st.error(f"❌ {message}")

        if back_button:
            st.session_state.edit_mode = False
            st.rerun()

    else:
        
        if not st.session_state.user_profile:
            st.warning("No profile data available. Please edit your profile.")
        else:
            # Personal Information Section
            st.subheader("👤 Personal Information")
            personal_fields = [
                ("👤", "Full Name", 'name'),
                ("📅", "Year of Joining", 'year_of_joining'),
                ("📞", "Phone", 'phone'),
                ("📧", "Email", 'email')
            ]

            for icon, label, key in personal_fields:
                value = st.session_state.user_profile.get(key, 'Not set')
                st.markdown(f"""
                    <div class="profile-field">
                        <div class="profile-label">{icon} {label}</div>
                        <div class="profile-value">{value}</div>
                    </div>
                """, unsafe_allow_html=True)

            # Academic Information Section
            st.subheader("🎓 Academic Information")
            academic_fields = [
                ("🏛️", "Institution", 'institution'),
                ("📚", "Degree", 'degree'),
                ("🔬", "Branch", 'branch')
            ]

            for icon, label, key in academic_fields:
                value = st.session_state.user_profile.get(key, 'Not set')
                st.markdown(f"""
                    <div class="profile-field">
                        <div class="profile-label">{icon} {label}</div>
                        <div class="profile-value">{value}</div>
                    </div>
                """, unsafe_allow_html=True)

            # Skills Section
            st.subheader("🛠️ Skills & Expertise")
            skills = st.session_state.user_profile.get('skills', [])
            if skills:
                st.markdown(f"""
                    <div class="profile-field">
                        <div class="profile-value">
                            {', '.join(skills)}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div class="profile-field">
                        <div class="profile-value">No skills added yet</div>
                    </div>
                """, unsafe_allow_html=True)

            # Professional Links Section
            st.subheader("🔗 Professional Links")
            links_fields = [
                ("🔗", "LinkedIn Profile", 'linkedin'),
                ("🐱", "GitHub Profile", 'github')
            ]

            for icon, label, key in links_fields:
                value = st.session_state.user_profile.get(key, 'Not set')
                if value != 'Not set' and value.strip():
                    display_value = f"<a href='{value}' target='_blank'>{value}</a>"
                else:
                    display_value = 'Not set'
                st.markdown(f"""
                    <div class="profile-field">
                        <div class="profile-label">{icon} {label}</div>
                        <div class="profile-value">{display_value}</div>
                    </div>
                """, unsafe_allow_html=True)

            # Bio Section
            st.subheader("📝 About Me")
            bio = st.session_state.user_profile.get('bio', 'No bio added yet')
            st.markdown(f"""
                <div class="profile-field">
                    <div class="profile-value">{bio}</div>
                </div>
            """, unsafe_allow_html=True)

            # Last Updated Information
            last_updated = st.session_state.user_profile.get('last_updated', 'Never')
            st.markdown(f"""
                <div style='text-align: right; color: var(--text-light); font-size: 0.8rem; margin-top: 1rem;'>
                    Last updated: {last_updated}
                </div>
            """, unsafe_allow_html=True)

            # Profile Statistics
            st.markdown("""
                <div class='profile-stats'>
                    <div class='stat-card'>
                        <h3>Skills</h3>
                        <p>{}</p>
                    </div>
                </div>
            """.format(
                len(st.session_state.user_profile.get('skills', [])),
            ), unsafe_allow_html=True)

            # Action Button Without Columns
            if st.button("✏️ Edit Profile", use_container_width=True):
                st.session_state.edit_mode = True
                st.rerun()
    
            # Profile Verification Status
            if st.session_state.user_profile.get('is_verified'):
                st.markdown("""
                    <div style='background: var(--success); color: white; padding: 1rem; border-radius: 12px; margin-top: 1rem;'>
                        ✅ Your profile is verified
                    </div>
                """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

def is_valid_url(url):
    """Validate URL format"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def validate_phone_number(phone):
    """Validate phone number format"""
    pattern = re.compile(r'^\+?1?\d{9,15}$')
    return bool(pattern.match(phone))

def about_page():
    st.markdown("<div class='navigation-bar'>", unsafe_allow_html=True)
    st.title("About Us")
    st.markdown("</div>", unsafe_allow_html=True)

    # Developer 1: Abishek Palani S
    st.markdown("## Abishek Palani S")
    col1, col2 = st.columns([1, 3])

    with col1:
        st.image("Abishek palani.jpg",width=200)

    with col2:
        st.markdown("""
        - **Role:** Lead Developer
        - **Expertise:** Artificial Intelligence, Blockchain, and Decentralized Systems
        - **Key Achievements:**
            - Developed a decentralized government job portal integrating blockchain and Aadhaar verification.
            - Created intelligent document processing solutions for RAC under DRDO.
            - Worked on cryptographic algorithm identification using AI/ML.
        - **Contact Details:**
            - [LinkedIn Profile](www.linkedin.com/in/ap9505)
            - Email: abishekpalanisivashanmugam@gmail.com
        """)

    st.markdown("---")  # Divider

    # Developer 2: Nandhini
    st.markdown("## Nandhini S")
    col3, col4 = st.columns([1, 3])

    with col3:
        st.image("Nandhini.jpg",width=200)

    with col4:
        st.markdown("""
        - **Role:** Full-Stack Developer
        - **Expertise:** Web Development, UI/UX Design, and API Integration
        - **Key Achievements:**
            - Designed user-centric interfaces for DRDO's recruitment portal.
            - Developed secure web applications integrating Aadhaar and DigiLocker.
            - Worked on public transportation data analysis apps with predictive insights.
        - **Contact Details:**
            - [LinkedIn Profile](https://www.linkedin.com/in/nandhini3)
            - Email: nandhinisaravanane@gmail.com
        """)

    st.markdown("---")  # Divider

    # Closing Section
    st.markdown("""
    We are a passionate team committed to developing innovative solutions for real-world problems. 
    Feel free to connect with us on LinkedIn or reach out via email for any collaborations or inquiries.
    """)

def faq_page():
    st.markdown("<div class='navigation-bar'>", unsafe_allow_html=True)
    st.title("📖 User Guide & FAQ")
    st.markdown("</div>", unsafe_allow_html=True)

    # User Guide Section
    st.subheader("📝 User Guide")
    st.markdown("""
    Welcome to **CodeExe**, your all-in-one platform for code analysis, optimization, execution, and learning. This guide will help you get started and make the most of its features.

    ### Getting Started
    1. **Login**  
       - Navigate to the login page and enter your credentials to access the platform.
    2. **Explore Features**  
       - Use the navigation bar at the top to explore features such as:
         - **Code Analysis**: Analyze, optimize, or debug your code.
         - **Code Execution**: Run your code and view the results.
         - **Learning Hub**: Learn programming concepts with guided explanations.
         - **Translator**: Convert code between programming languages.
         - **Community**: Connect with peers to collaborate and discuss topics.
    3. **Upload Code or Images**  
       - Use the file uploader in respective pages (e.g., Code Analysis or Image Processing) to provide your input.

    ### Step-by-Step Guide
    #### Code Analysis
    - Navigate to the **Code Analysis** page.
    - Upload your code file or paste it into the provided text area.
    - Select the analysis type (e.g., Explain, Detect Bugs, Optimize).
    - Click "Analyze Code" to view insights and suggestions.

    #### Code Execution
    - Go to the **Code Execution** page.
    - Choose your programming language.
    - Paste your code and optional input data.
    - Click "Execute Code" to run your program and see the output.

    #### Learning Hub
    - Visit the **Learning Hub** to search for programming topics.
    - Select the explanation level (Basic, Standard, Detailed).
    - Read the explanation, examples, and use cases.

    #### Translator
    - Navigate to the **Translator** page.
    - Enter your source code, choose source and target languages.
    - Click "Translate Code" to see the translated code with comments.

    #### Community
    - Join communities based on your college, department, or domain.
    - Interact with other members via the Community Wall.

    ### Tips
    - Use **high-quality images** for the Image Processing feature.
    - Save frequently used code snippets in your profile.
    - Explore **Quick Templates** under Code Generator for common tasks.
    """)

    # FAQ Section
    st.subheader("❓ Frequently Asked Questions (FAQs)")
    st.markdown("""
    ### General
    **Q: What is CodeExe?**  
    A: CodeExe is a platform that combines AI-driven code analysis, execution, and learning tools to help developers improve their coding skills and productivity.

    **Q: What programming languages are supported?**  
    A: CodeExe supports popular languages like Python, JavaScript, Java, C++, Ruby, and Go.

    ### Features
    **Q: How do I analyze my code?**  
    A: Go to the **Code Analysis** page, upload your code, choose an analysis type, and click "Analyze Code."

    **Q: Can I run my code directly on this platform?**  
    A: Yes, visit the **Code Execution** page to run your code in various supported languages.

    **Q: What can I learn in the Learning Hub?**  
    A: The **Learning Hub** offers explanations of programming topics, including examples and use cases, tailored to your skill level.

    ### Technical
    **Q: Is my code stored on the platform?**  
    A: No, CodeExe does not store your code. It is processed temporarily and securely during analysis or execution.

    **Q: How accurate is the Image Processing feature?**  
    A: The accuracy depends on the quality of the uploaded image. Ensure the image is clear, well-lit, and in focus.

    ### Community
    **Q: How do I join a community?**  
    A: Go to the **Community** page, select a college, department, or domain, and click "Join Community."

    **Q: Can I interact with other members?**  
    A: Yes, use the **Community Wall** to chat, share resources, and collaborate.

    ### Troubleshooting
    **Q: I encountered an error during analysis. What should I do?**  
    A: Ensure your code is properly formatted and supported. If the issue persists, contact support.

    **Q: Why is my code not running as expected?**  
    A: Check the input data, language selection, and ensure there are no syntax errors in your code.

    **Q: How do I report a bug?**  
    A: Use the **Contact Us** section on the profile page or email our support team.
    """)

    st.info("📧 For further questions or feedback, reach out to our support team.")

def add_footer():
    # Add custom CSS with light, modern styling (CSS remains the same as before)
    st.markdown("""
        <style>
        .footer {
            position: relative;
            padding: 4rem 2rem;
            background: rgba(248, 249, 250, 0.9);
            color: #333;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            border-top: 1px solid rgba(0, 0, 0, 0.1);
        }
        
        .footer-grid {
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 3rem;
        }
        
        .footer-section h3 {
            color: #6C63FF;
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            position: relative;
            display: inline-block;
        }
        
        .footer-section h3::after {
            content: '';
            position: absolute;
            left: 0;
            bottom: -5px;
            width: 50px;
            height: 4px;
            background: #6C63FF;
            border-radius: 2px;
        }
        
        .footer-section ul {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        
        .footer-section li {
            margin-bottom: 1rem;
            transition: transform 0.3s ease;
            display: flex;
            align-items: center;
            color: #555;
            cursor: pointer;
        }
        
        .footer-section li:hover {
            transform: translateX(10px);
            color: #6C63FF;
        }
        
        .footer-section li i {
            margin-right: 10px;
            font-size: 0.8rem;
            color: #6C63FF;
        }
        
        .footer-section a {
            color: inherit;
            text-decoration: none;
            position: relative;
            transition: color 0.3s ease;
        }
        
        .footer-section a:hover {
            color: #6C63FF;
        }
        
        .footer-bottom {
            margin-top: 4rem;
            padding-top: 2rem;
            border-top: 1px solid rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        
        .social-links {
            display: flex;
            justify-content: center;
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .social-link {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #f0f0f0;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            text-decoration: none;
        }
        
        .social-link:hover {
            background: #6C63FF;
            transform: translateY(-5px);
        }
        
        .social-link:hover i {
            color: white;
        }
        
        .social-link i {
            color: #666;
            font-size: 1.2rem;
            transition: color 0.3s ease;
        }
        
        .footer-bottom p {
            color: #666;
            font-size: 0.9rem;
        }
        
        .footer-logo {
            text-align: center;
            margin-bottom: 3rem;
        }
        
        .footer-logo h1 {
            color: #6C63FF;
            font-size: 2.5rem;
            margin: 0;
        }
        
        @media (max-width: 768px) {
            .footer {
                padding: 3rem 1rem;
            }
            
            .footer-grid {
                grid-template-columns: 1fr;
                gap: 2rem;
            }
        }
        </style>
    """, unsafe_allow_html=True)

    # Add Font Awesome
    st.markdown("""
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    """, unsafe_allow_html=True)

    # Create a dictionary of external links
    external_links = {
        'github': 'https://github.com/your-repo',
        'discord': 'https://discord.com/invite/your-discord',
        'twitter': 'https://twitter.com/your-twitter',
        'linkedin': 'https://linkedin.com/company/your-company'
    }

    # Function to create Streamlit-compatible links
    def create_link(text, url, icon_class, is_external=False):
        if is_external:
            return f'<a href="{url}" target="_blank"><i class="{icon_class}"></i>{text}</a>'
        else:
            params = urlencode({'page': url})
            return f'<a href="?{params}" target="_self"><i class="{icon_class}"></i>{text}</a>'

    # Footer content with working links
    footer_content = f"""
        <div class="footer">
            <div class="footer-grid">
                <div class="footer-section">
                    <h3>Quick Links</h3>
                    <ul>
                        <li>{create_link('Home', 'home', 'fas fa-chevron-right')}</li>
                        <li>{create_link('Code Analysis', 'code-analysis', 'fas fa-chevron-right')}</li>
                        <li>{create_link('Image Processing', 'image-processing', 'fas fa-chevron-right')}</li>
                        <li>{create_link('Code Translation', 'code-translation', 'fas fa-chevron-right')}</li>
                        <li>{create_link('Error Detection', 'error-detection', 'fas fa-chevron-right')}</li>
                    </ul>
                </div>
                <div class="footer-section">
                    <h3>Documentation</h3>
                    <ul>
                        <li>{create_link('API Reference', 'api-reference', 'fas fa-book')}</li>
                        <li>{create_link('Getting Started', 'getting-started', 'fas fa-play')}</li>
                        <li>{create_link('User Guide', 'user-guide', 'fas fa-user')}</li>
                        <li>{create_link('Changelog', 'changelog', 'fas fa-clipboard-list')}</li>
                    </ul>
                </div>
                <div class="footer-section">
                    <h3>Resources</h3>
                    <ul>
                        <li>{create_link('GitHub Repository', external_links['github'], 'fab fa-github', True)}</li>
                        <li>{create_link('Release Notes', 'release-notes', 'fas fa-rocket')}</li>
                        <li>{create_link('Community', 'community', 'fas fa-users')}</li>
                        <li>{create_link('Report Issues', 'report-issues', 'fas fa-bug')}</li>
                    </ul>
                </div>
                <div class="footer-section">
                    <h3>Contact</h3>
                    <ul>
                        <li>{create_link('Support', 'support', 'fas fa-headset')}</li>
                        <li>{create_link('Feedback', 'feedback', 'fas fa-comment')}</li>
                        <li>{create_link('Join Discord', external_links['discord'], 'fab fa-discord', True)}</li>
                        <li>{create_link('Newsletter', 'newsletter', 'fas fa-envelope')}</li>
                    </ul>
                </div>
            </div>
            <div class="footer-bottom">
                <div class="social-links">
                    <a href="{external_links['github']}" class="social-link" target="_blank"><i class="fab fa-github"></i></a>
                    <a href="{external_links['discord']}" class="social-link" target="_blank"><i class="fab fa-discord"></i></a>
                    <a href="{external_links['twitter']}" class="social-link" target="_blank"><i class="fab fa-twitter"></i></a>
                    <a href="{external_links['linkedin']}" class="social-link" target="_blank"><i class="fab fa-linkedin"></i></a>
                </div>
                <p>© 2024 CodeExe. All rights reserved.</p>
            </div>
        </div>
    """
    
    st.markdown(footer_content, unsafe_allow_html=True)

    # Add the page handler to your main Streamlit app
    query_params = st.query_params
    if 'page' in query_params:
        current_page = query_params['page'][0]
        # Handle the page navigation here
        st.session_state['current_page'] = current_page

        
def api_reference_page():
   st.title("API Reference")
   st.markdown("""
       ## API Endpoints
       
       ### Code Analysis API
       - POST /analyze: Submit code for analysis
       - GET /analysis/{id}: Retrieve analysis results
       
       ### Image Processing API  
       - POST /process-image: Process an image
       - GET /image/{id}: Get processed image
       
       ### Code Translation API
       - POST /translate: Translate code between languages
       
       [View full API documentation](https://docs.example.com)
   """)

def getting_started_page():
   st.title("Getting Started")
   st.markdown("""
       ## Quick Start Guide
       1. Install the library: pip install codeexe
       2. Import and initialize
       3. Start using core features
       
       ## Basic Examples
       python
       import codeexe
       
       # Analyze code
       result = codeexe.analyze(code)
       
       # Process image 
       processed = codeexe.process_image(image)
       
   """)

def user_guide_page():
   st.title("User Guide")
   st.markdown("""
       ## Features
       - Code Analysis
       - Image Processing 
       - Code Translation
       
       ## Usage Examples
       - How to analyze code
       - How to process images
       - Common workflows
       
       ## Best Practices
       - Performance optimization
       - Error handling
       - Security considerations
   """)

def changelog_page():
   st.title("Changelog")
   st.markdown("""
       ## Version 2.0.0
       - Added image processing
       - Improved code analysis
       - Bug fixes
       
       ## Version 1.5.0
       - Added code translation
       - Performance improvements
       
       ## Version 1.0.0
       - Initial release
       - Basic code analysis
   """)

def release_notes_page():
   st.title("Release Notes") 
   st.markdown("""
       ## Latest Release (v2.0.0)
       
       ### New Features
       - Image processing capabilities
       - Enhanced code analysis
       
       ### Improvements
       - 50% faster processing
       - Better error handling
       
       ### Bug Fixes
       - Fixed memory leak
       - Resolved UI glitches
   """)

def report_issues_page():
   st.title("Report Issues")
   
   issue_type = st.selectbox(
       "Issue Type",
       ["Bug", "Feature Request", "Documentation", "Other"]
   )
   
   st.text_area("Describe the issue")
   st.text_area("Steps to reproduce")
   st.text_input("System details")
   st.button("Submit Issue")

def support_page():
   st.title("Support")
   st.markdown("""
       ## Get Help
       
       - Documentation
       - FAQs
       - Community Forums
       
       ## Contact Support
       Email: support@example.com
       Response time: 24-48 hours
   """)
   
   st.text_area("Message")
   st.button("Send Message")

def feedback_page():
   st.title("Feedback")
   
   feedback_type = st.selectbox(
       "Feedback Type",
       ["General", "Bug Report", "Feature Request", "Other"]
   )
   
   st.text_area("Your feedback")
   st.slider("Rating", 1, 5, 3)
   st.button("Submit Feedback")

def newsletter_page():
   st.title("Newsletter")
   
   st.markdown("Stay updated with latest features and updates!")
   
   st.text_input("Email")
   preferences = st.multiselect(
       "Preferences",
       ["Product Updates", "Tutorials", "Community News"]
   )
   st.button("Subscribe")

def handle_page_navigation():
    query_params = st.query_params
    if 'page' in query_params:
        page = query_params['page']
        if page != 'home':
            st.query_params['page'] = 'home'
            st.rerun()
            
        pages = {
            'code-analysis': code_analysis_page,
            'image-processing': image_processing_page,
            'code-translation': translator_page,
            'error-detection': error_detection_page,
            'api-reference': api_reference_page,
            'getting-started': getting_started_page,
            'user-guide': user_guide_page,
            'changelog': changelog_page,
            'release-notes': release_notes_page,
            'report-issues': report_issues_page,
            'community': community_page,
            'support': support_page,
            'feedback': feedback_page,
            'newsletter': newsletter_page
        }
        
        if page in pages:
            pages[page]()
            return True
    return False

def main():
    apply_custom_css()

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "page" not in st.session_state:
        st.session_state.page = "Login"

    # Handle authentication
    if not st.session_state.logged_in:
        if st.session_state.page == "Login":
            login_page()
        elif st.session_state.page == "Sign Up":
            sign_up_page()
        elif st.session_state.page == "Reset Password":
            reset_password_page()
        return

    # Handle page navigation from footer
    if handle_page_navigation():
        add_footer()
        return

    # Handle main navigation
    selected_page = navigation_bar()
    
    if selected_page == "Home":
        home_page()
    elif selected_page == "Code Analysis":
        code_analysis_page()
    elif selected_page == "Image Processing":
        image_processing_page()
    elif selected_page == "Translator":
        translator_page()
    elif selected_page == "Error Detection":
        error_detection_page()
    elif selected_page == "Learning Hub":
        learning_hub_page()
    elif selected_page == "Code Generator":
        code_generator_page()
    elif selected_page == "Community":
        community_page()
    elif selected_page == "Code Execution":
        code_execution_page()
    elif selected_page == "Profile":
        profile_page()
    elif selected_page == "About":
        about_page()
    elif selected_page == "FAQ":
        faq_page()
    elif selected_page == "Logout":
        st.session_state.logged_in = False
        st.session_state.page = "Login"
        st.rerun()

    add_footer()
if __name__ == "__main__":
    main()