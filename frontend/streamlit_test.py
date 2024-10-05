import streamlit as st
import requests
from datetime import datetime
import json

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

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💡 Idea Generation",
    "📋 Requirements Gathering",
    "📊 Diagram Generation",
    "🔍 AI Feasibility Analysis",
    "📄 Final Report"
])

# Tab 1: Idea Generation
with tab1:
    st.header("💡 AI Project Idea Generation")
    st.markdown("""
    Let's start by understanding your business needs and generating potential AI solutions.
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        industry = st.selectbox(
            "What industry are you in?",
            ["Select Industry", "Healthcare", "Finance", "Retail", "Manufacturing", "Technology", "Other"]
        )
        
        problem_area = st.text_area(
            "Describe the business problem you're trying to solve:",
            help="Be as specific as possible about the challenges you're facing."
        )
        
        if st.button("Analyze my idea"):
            with st.spinner("Analyzing your idea, existing solutions, and current pain points..."):
                # Check that valid data is provided
                if industry == "Select Industry" or not problem_area.strip():
                    st.error("Please select a valid industry and provide a problem description.")
                else:
                    # Prepare the data to send to the backend
                    data = {
                        "domain": industry,
                        "problem": problem_area
                    }

                    try:
                        # Send a request to the FastAPI backend
                        response = requests.post("http://localhost:8000/analyze", json=data)
                        response.raise_for_status()  # Raise an error for bad status codes
                        
                        # Parse the response from the backend
                        analysis_result = response.json()

                        # If the response is a JSON string, ensure it's parsed correctly
                        if isinstance(analysis_result, str):
                            # Replace escaped newlines with actual newlines
                            analysis_result = analysis_result.replace("\\n", "\n")

                        # Display the result in the UI
                        st.success("Idea analyzed successfully!")
                        st.markdown(analysis_result, unsafe_allow_html=True)

                    except requests.exceptions.RequestException as e:
                        st.error(f"An error occurred while contacting the backend: {e}")
    
    with col2:
        st.info("""
        ### Tips for Better Results
        - Be specific about your problem
        - Include current pain points
        - Mention any existing solutions
        - Describe desired outcomes
        """)

# Tab 2: Requirements Gathering
with tab2:
    st.header("📋 Requirements Gathering")
    
    project_name = st.text_input("Project Name", key="project_name")
    
    st.subheader("Business Requirements")
    business_objective = st.text_area("What is the main business objective?")
    target_users = st.text_input("Who are the target users?")
    success_metrics = st.text_area("How will success be measured?")
    
    st.subheader("Technical Requirements")
    data_sources = st.multiselect(
        "What data sources will be needed?",
        ["Internal Databases", "External APIs", "User Input", "Sensors", "Documents", "Images", "Other"]
    )
    
    integration_needs = st.multiselect(
        "Required system integrations:",
        ["CRM", "ERP", "Legacy Systems", "Cloud Services", "APIs", "Other"]
    )
    
    if st.button("Save Requirements"):
        st.success("Requirements saved successfully!")

# Tab 3: Diagram Generation
with tab3:
    st.header("📊 Diagram Generation")
    
    diagram_type = st.selectbox(
        "Select diagram type:",
        ["System Architecture", "Data Flow", "User Journey", "Process Flow"]
    )
    
    st.markdown("### Diagram Specifications")
    col1, col2 = st.columns(2)
    
    with col1:
        components = st.multiselect(
            "Select components to include:",
            ["Frontend", "Backend", "Database", "API", "External Systems", "AI Models"]
        )
    
    with col2:
        detail_level = st.slider("Level of detail", 1, 5, 3)
    
    if st.button("Generate Diagram"):
        with st.spinner("Generating diagram..."):
            st.success("Diagram generated!")
            st.image("/api/placeholder/800/400", caption="Generated System Diagram")

# Tab 4: AI Feasibility Analysis
with tab4:
    st.header("🔍 AI Feasibility Analysis")
    
    st.subheader("Project Assessment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("AI Suitability Score", "85%")
        st.metric("Implementation Complexity", "Medium")
        st.metric("Data Readiness", "High")
    
    with col2:
        st.metric("Resource Requirements", "Medium")
        st.metric("Time to Value", "3-6 months")
        st.metric("ROI Potential", "High")
    
    st.subheader("Detailed Analysis")
    st.write("""
    ### Strengths
    - Clear business objective
    - Sufficient data available
    - Strong integration possibilities
    
    ### Challenges
    - Data quality needs improvement
    - Training requirements for users
    - Integration complexity
    """)

# Tab 5: Final Report
with tab5:
    st.header("📄 Final Report")
    
    st.markdown("### Project Summary")
    if st.session_state.requirements['project_name']:
        st.write(f"**Project Name:** {st.session_state.requirements['project_name']}")
    
    report_sections = st.multiselect(
        "Select sections to include in the report:",
        ["Executive Summary", "Requirements Analysis", "Technical Specifications",
         "Implementation Plan", "Risk Assessment", "Cost Estimation"]
    )
    
    report_format = st.radio(
        "Choose report format:",
        ["PDF", "Word Document", "HTML", "Markdown"]
    )
    
    if st.button("Generate Report"):
        with st.spinner("Generating comprehensive report..."):
            st.success("Report generated successfully!")
            
            st.download_button(
                label="Download Report",
                data="Report content here",
                file_name=f"AI_Requirements_Analysis_{datetime.now().strftime('%Y%m%d')}.{report_format.lower()}",
                mime="text/plain"
            )

# Sidebar for navigation and settings
with st.sidebar:
    st.title("🤖 AI Requirements Analyst")
    st.markdown("---")
    
    st.subheader("Project Progress")
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