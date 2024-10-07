import streamlit as st
import requests
from datetime import datetime
import json
from typing import Dict, Any

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

# Page configuration
st.set_page_config(
    page_title="AI Requirements Analyst",
    page_icon="🤖",
    layout="wide"
)

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
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        project_idea = st.text_area(
            "What is your project idea?",
            help="Define a type of product you would like to build eg. chatbot, predictive algorithm, etc"
        )
        
        industry = st.text_area(
            "What industry are you in?",
            help="Eg. Automotive, Marketing, Sales"
        )
        
        problem_area = st.text_area(
            "Describe the business problem you're trying to solve:",
            help="Be as specific as possible about the challenges you're facing."
        )
        
        website_url = st.text_area(
            "Provide your website url",
            help="What is the website of the business?"
        )
        
        mvp = st.text_area(
            "What is the minimum viable product?",
            help="Define the minimum requirement for this project to succeed"
        )
        
        if st.button("Generate Product Brief"):
            if not all([industry, problem_area, website_url, mvp]):
                st.error("Please fill in all fields before generating the brief.")
            else:
                with st.spinner("Analyzing your idea and generating product brief..."):
                    data = {
                        "domain": industry,
                        "problem": problem_area,
                        "website": website_url,
                        "mvp": mvp,
                        "problem_area": problem_area
                    }

                    try:
                        response = requests.post(
                            "http://localhost:8000/complete_analysis", 
                            json=data,
                            timeout=30
                        )
                        
                        result = handle_api_response(response)
                        if result:
                            st.session_state.analysis_result = result['analysis']
                            st.session_state.product_brief = result['product_brief']
                            # Update the requirements state
                            st.session_state.requirements.update({
                                'project_name': project_idea,
                                'industry': industry,
                                'problem_statement': problem_area
                            })
                            st.success("Product brief generated successfully! Switch to the 'Requirements Gathering' tab to view it.")
                            tab2.click()

                    except Exception as e:
                        st.error(f"An unexpected error occurred: {str(e)}")
    
    with col2:
        st.info("""
        ### Tips for Better Results
        - Be specific about your problem
        - Include current pain points
        - Mention any existing solutions
        - Describe desired outcomes
        - Consider using tools such as NotebookLM to answer your questions on youtube videos, web links and pdf files for further research
        """)

# Tab 2: Requirements Gathering
with tab2:
    st.header("📋 Project Brief")
    
    if st.session_state.product_brief:
        with st.expander("View Initial Analysis", expanded=True):
            st.json(st.session_state.analysis_result)
        
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
        st.info("Please fill out the project details in the Idea Generation tab to generate a product brief.")

# [Rest of the tabs remain unchanged]
with tab3:
    st.header("📊 Diagram Generation")
    # [Previous diagram generation code remains the same]

with tab4:
    st.header("🔍 AI Feasibility Analysis")
    # [Previous AI feasibility analysis code remains the same]

with tab5:
    st.header("📄 Final Report")
    # [Previous final report code remains the same]

# Sidebar for navigation and settings
with st.sidebar:
    st.title("🤖 Your project name: " + st.session_state.requirements['project_name'] if st.session_state.requirements['project_name'] else "XXX")
    st.markdown("---")
    
    st.subheader("Project Progress: ")
    st.subheader("1. Fill the info: " + ("✅" if all([industry, problem_area, website_url, mvp]) else "⏳"))
    st.subheader("2. View project brief: " + ("✅" if st.session_state.product_brief else "⏳"))
    st.subheader("3. View your step by step guide: " + ("✅" if st.session_state.generated_diagrams else "⏳"))
    st.subheader("4. Research tools required: " + ("✅" if st.session_state.ai_analysis else "⏳"))
    progress = st.progress(0)
    
    # Update progress based on completed sections
    completed_sections = sum([
        bool(st.session_state.requirements['project_name']),
        bool(st.session_state.requirements['industry']),
        bool(st.session_state.requirements['problem_statement']),
        bool(st.session_state.generated_diagrams),
        bool(st.session_state.ai_analysis)
    ])
    progress.progress(completed_sections / 5)
    
    st.markdown("---")
    
    if st.button("Save Project"):
        st.success("Project saved successfully!")
    
    if st.button("Load Project"):
        st.info("Select a project to load...")