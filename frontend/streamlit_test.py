import streamlit as st
import requests
from datetime import datetime
import json
from typing import Dict, Any
import os
from pathlib import Path
from PIL import Image

# Helper functions
def handle_api_response(response: requests.Response) -> Dict[str, Any]:
    """Helper function to handle API responses and errors."""
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 500:
            try:
                error_detail = response.json().get('detail', str(e))
                st.error(f"Server error: {error_detail}")
            except:
                st.error(f"Server error: {str(e)}")
        else:
            st.error(f"HTTP error: {str(e)}")
    except requests.exceptions.RequestException as e:
        st.error(f"Request error: {str(e)}")
    except json.JSONDecodeError as e:
        st.error(f"Error parsing response: {str(e)}")
        st.code(response.text)
    return None

def display_product_brief(brief: Dict[str, Any]):
    """Helper function to display the product brief."""
    if "error" in brief:
        st.error(f"Error in product brief: {brief['error']}")
        if "raw_response" in brief:
            st.code(brief["raw_response"])
        return

    st.markdown("## 1-Pager: Project Brief")
    
    sections = [
        ("Problem Statement", "problem_statement"),
        ("Target Audience", "target_audience"),
        ("Why It Matters", "why_it_matters"),
        ("Proposed Solution", "proposed_solution"),
        ("Success Criteria", "success_criteria"),
        ("Risks and Considerations", "risks_and_considerations"),
        ("Next Steps", "next_steps"),
        ("Additional Notes", "additional_notes")
    ]
    
    for title, key in sections:
        st.markdown(f"### {title}")
        content = brief.get(key, "Not available")
        st.markdown(content)

def labeled_text_area(label, help_text, key):
    """
    Renders a labeled text area with a red asterisk to indicate it's mandatory.

    Parameters:
    - label (str): The label for the text area.
    - help_text (str): Help text for the text area.
    - key (str): The unique key for the Streamlit widget.

    Returns:
    - str: The user input from the text area.
    """
    st.markdown(f"""
        <p style="font-weight:bold;">{label} <span style='color:red;'>*</span></p>
    """, unsafe_allow_html=True)
    return st.text_area("", help=help_text, key=key)

# Page configuration
st.set_page_config(
    page_title="AI Requirements Analyst",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to set sidebar width and center content
st.markdown("""
    <style>
        /* Color Scheme Variables */
        :root {
            --primary-color: #2E7DAF;
            --secondary-color: #17B890;
            --accent-color: #FF6B6B;
            --background-color: #F8F9FA;
            --text-color: #2C3E50;
            --border-color: #E9ECEF;
            --success-color: #28a745;
            --warning-color: #ffc107;
            --error-color: #dc3545;
        }

        /* Base Styles */
        .stApp {
            background-color: var(--background-color);
            color: var(--text-color);
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid var(--border-color);
            padding: 1rem;
        }

        [data-testid="stSidebar"][aria-expanded="true"] {
            min-width: 300px;
            max-width: 300px;
        }

        /* Progress Indicators */
        .progress-indicator {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin-bottom: 10px;
        }

        .progress-indicator.complete {
            background-color: var(--success-color);
            color: white;
        }

        .progress-indicator.incomplete {
            background-color: var(--border-color);
            color: var(--text-color);
        }

        /* Form Styling */
        .stTextInput input, .stTextArea textarea {
            border-radius: 6px;
            border: 1px solid var(--border-color);
            padding: 8px 12px;
        }

        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 2px rgba(46, 125, 175, 0.2);
        }

        /* Validation Feedback */
        .feedback-message {
            margin-top: 4px;
            font-size: 0.875rem;
        }

        .feedback-message.error {
            color: var(--error-color);
        }

        .feedback-message.success {
            color: var(--success-color);
        }

        /* Button Styling */
        .stButton button {
            background-color: var(--primary-color);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            transition: all 0.3s ease;
        }

        .stButton button:hover {
            background-color: var(--secondary-color);
            transform: translateY(-2px);
        }

        /* Mobile Responsiveness */
        @media (max-width: 768px) {
            [data-testid="stSidebar"][aria-expanded="true"] {
                min-width: 100%;
                max-width: 100%;
                margin-left: -100%;
            }
            
            .stButton button {
                width: 100%;
            }
            
            .row-widget.stSelectbox {
                min-width: 100%;
            }
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'requirements' not in st.session_state:
    st.session_state.requirements = {
        'project_name': '',
        'industry': '',
        'problem_statement': '',
        'current_solutions': '',
        'desired_outcomes': []
    }
if 'generated_diagrams' not in st.session_state:
    st.session_state.generated_diagrams = []
if 'ai_analysis' not in st.session_state:
    st.session_state.ai_analysis = {}
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'product_brief' not in st.session_state:
    st.session_state.product_brief = None

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💡 Idea Generation",
    "📋 Project Brief",
    "📊 Diagram Generation",
    "🔍 AI Feasibility Analysis",
    "📄 Final Report"
])

# Tab 1: Idea Generation
with tab1:
    st.header("💡 Describe your next project")
    st.markdown("""
    Let's start by understanding your business needs.
    """)

    # Optional: Add a legend for mandatory fields
    st.markdown("""
    **Note:** Fields marked with <span style='color:red'>*</span> are mandatory.
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        # Mandatory Fields
        project_idea = labeled_text_area(
            "What is your project idea?",
            help_text="Define a type of product you would like to build e.g., chatbot, predictive algorithm, etc",
            key="project_idea"
        )

        industry = labeled_text_area(
            "What industry are you in?",
            help_text="E.g., Automotive, Marketing, Sales",
            key="industry"
        )

        problem_area = labeled_text_area(
            "Describe the business problem you're trying to solve:",
            help_text="Be as specific as possible about the challenges you're facing.",
            key="problem_area"
        )

        # Optional Fields
        st.markdown("<p style='font-weight:bold;'>Provide your website URL</p>", unsafe_allow_html=True)
        website_url = st.text_area(
            "",
            help="What is the website of the business?",
            key="website_url"
        )

        st.markdown("<p style='font-weight:bold;'>What is the minimum viable product?</p>", unsafe_allow_html=True)
        mvp = st.text_area(
            "",
            help="Define the minimum requirement for this project to succeed",
            key="mvp"
        )

        # Function to check mandatory fields
        def validate_fields():
            missing_fields = []
            if not st.session_state.project_idea.strip():
                missing_fields.append("Project Idea")
            if not st.session_state.industry.strip():
                missing_fields.append("Industry")
            if not st.session_state.problem_area.strip():
                missing_fields.append("Business Problem")
            return missing_fields

        if st.button("Generate Product Brief"):
            missing = validate_fields()
            if missing:
                st.error(f"Please fill in the following mandatory fields: {', '.join(missing)}.")
            else:
                with st.spinner("Analyzing your idea and generating product brief..."):
                    data = {
                        "domain": st.session_state.industry,
                        "problem": st.session_state.problem_area,
                        "website": st.session_state.website_url,
                        "mvp": st.session_state.mvp,
                        "problem_area": st.session_state.problem_area
                    }

                    try:
                        response = requests.post(
                            "http://localhost:8000/complete_analysis", 
                            json=data,
                            timeout=30
                        )
                        
                        result = handle_api_response(response)
                        if result:
                            st.session_state.analysis_result = result.get('analysis', {})
                            st.session_state.product_brief = result.get('product_brief', {})
                            # Update the requirements state
                            st.session_state.requirements.update({
                                'project_name': st.session_state.project_idea,
                                'industry': st.session_state.industry,
                                'problem_statement': st.session_state.problem_area
                            })
                            st.success("Product brief generated successfully! Switch to the 'Project Brief' tab to view it.")
                            tab2.select()
                    except Exception as e:
                        st.error(f"An unexpected error occurred: {str(e)}")

    with col2:
        st.info("""
        ### Tips for Better Results
        - Be specific about your problem
        - Include current pain points
        - Mention any existing solutions
        - Describe desired outcomes
        - Consider using tools such as NotebookLM to answer your questions on YouTube videos, web links, and PDF files for further research
        """)

# Tab 2: Project Brief
with tab2:
    st.header("📋 Project Brief")
    
    if st.session_state.product_brief:
        display_product_brief(st.session_state.product_brief)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Export as PDF"):
                st.warning("PDF export functionality to be implemented")
        with col2:
            if st.button("Export as Markdown"):
                st.download_button(
                    label="Download Markdown",
                    data=json.dumps(st.session_state.product_brief, indent=2),
                    file_name="product_brief.md",
                    mime="text/markdown"
                )
    else:
        st.info("Please fill out the project details in the Idea Generation tab to generate a project brief.")

# Tab 3: Diagram Generation
with tab3:
    st.header("📊 Diagram Generation")
    # Your existing code for Diagram Generation

# Tab 4: AI Feasibility Analysis
with tab4:
    st.header("🔍 AI Feasibility Analysis")
    # Your existing code for AI Feasibility Analysis

# Tab 5: Final Report
with tab5:
    st.header("📄 Final Report")
    # Your existing code for Final Report

# Sidebar with logo and navigation
with st.sidebar:
    # Logo section
    current_file = Path(__file__)
    project_root = current_file.parent.parent
    logo_path = project_root / 'assets' / 'AI_consult_logo.png'

    # Create a container for the logo
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    try:
        if logo_path.exists():
            logo = Image.open(logo_path)
            st.image(logo, width=200)
        else:
            st.warning(f"Logo not found at: {logo_path}")
    except Exception as e:
        st.error(f"Error loading logo: {str(e)}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.title(f"AI consultant")

    # Add a separator
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Project name section
    project_name = st.session_state.requirements.get('project_name', '')
    if project_name:
        st.title(f"🤖 {project_name}")
    else:
        st.title("🤖 New Project")
    
    st.markdown("---")
    
    # Progress section
    st.subheader("Project Progress")
    
    # Define mandatory fields for progress
    has_project_idea = bool(st.session_state.requirements.get('project_name', '').strip())
    has_industry = bool(st.session_state.requirements.get('industry', '').strip())
    has_problem = bool(st.session_state.requirements.get('problem_statement', '').strip())
    has_brief = bool(st.session_state.product_brief)
    has_diagrams = bool(st.session_state.generated_diagrams)
    has_analysis = bool(st.session_state.ai_analysis)
    
    # Display progress items
    progress_items = [
        ("1. Fill your product information", has_project_idea and has_industry and has_problem),
        ("2. View project brief", has_brief),
        ("3. Research tools required", has_analysis),
        ("4. View your step by step guide", has_diagrams)
    ]
    
    for label, is_complete in progress_items:
        st.markdown(
            f"{label}: {('✅' if is_complete else '⏳')}",
            unsafe_allow_html=True
        )
    
    # Progress bar calculation based on mandatory fields and total steps
    total_steps = len(progress_items)
    completed_steps = sum(is_complete for _, is_complete in progress_items)
    progress_percentage = completed_steps / total_steps if total_steps else 0
    st.progress(progress_percentage)
    

    