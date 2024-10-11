# frontend script

import streamlit as st
import requests
from datetime import datetime
import json
from typing import Dict, Any
import os
from pathlib import Path
from PIL import Image
from streamlit_mermaid import st_mermaid  # Ensure this is installed: pip install streamlit-mermaid

# Helper functions
def handle_api_response(response: requests.Response) -> Dict[str, Any]:
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

def labeled_text_area(label, help_text, key):
    st.markdown(f"""
        <p style="font-weight:bold;">{label} <span style='color:red;'>*</span></p>
    """, unsafe_allow_html=True)
    return st.text_area("", help=help_text, key=key)

def display_product_brief(brief: Dict[str, Any]):
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

def display_market_analysis(analysis: Dict[str, Any]):
    if "error" in analysis:
        st.error(f"Error in market and competitor analysis: {analysis['error']}")
        if "raw_response" in analysis:
            st.code(analysis["raw_response"])
        return
    st.markdown("## Market and Competitor Analysis")
    sections = [
        ("Market Overview", "market_overview"),
        ("Target Market", "target_market"),
        ("Competitive Landscape", "competitive_landscape"),
        ("Opportunities and Threats", "opportunities_and_threats"),
        ("Differentiation", "differentiation")
    ]
    for title, key in sections:
        st.markdown(f"### {title}")
        content = analysis.get(key, "Not available")
        st.markdown(content)

def display_competitor_analysis(analysis: Dict[str, Any]):
    if "error" in analysis:
        st.error(f"Error in market and competitor analysis: {analysis['error']}")
        if "raw_response" in analysis:
            st.code(analysis["raw_response"])
        return

    # Display competitor analysis section
    st.markdown("### Competitor Analysis")
    competitor_analysis = analysis.get("analysis", "No analysis available.")
    st.markdown(f"```\n{competitor_analysis}\n```")


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
if 'market_analysis' not in st.session_state:
    st.session_state.market_analysis = None
if 'competitor_analysis' not in st.session_state:
    st.session_state.competitor_analysis = None
if 'technical_details' not in st.session_state:
    st.session_state.technical_details = None

# Page configuration
st.set_page_config(
    page_title="AI Consultant",
    page_icon="🤖",
    layout="wide"
)

# Create tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "💡 Idea",
    "📋 Project Brief",
    "📈 Market Analysis",
    "📈 Competitor Analysis",
    "📊 Technical Components",
    "📄 Final Report"
])

# Tab 1: Idea Generation
with tab1:
    st.header("💡 Describe your next project")
    st.markdown("""
    Let's start by understanding your business needs.
    """)
    st.markdown("""
    **Note:** Fields marked with <span style='color:red'>*</span> are mandatory.
    """, unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    with col1:
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
        def validate_fields():
            missing_fields = []
            if not st.session_state.project_idea.strip():
                missing_fields.append("Project Idea")
            if not st.session_state.industry.strip():
                missing_fields.append("Industry")
            if not st.session_state.problem_area.strip():
                missing_fields.append("Business Problem")
            return missing_fields
        if st.button("Generate Your Next Project"):
            missing = validate_fields()
            if missing:
                st.error(f"Please fill in the following mandatory fields: {', '.join(missing)}.")
            else:
                with st.spinner("Analyzing your idea and generating product brief..."):
                    data = {
                        "domain": st.session_state.industry,
                        "problem": st.session_state.problem_area,
                        "website": st.session_state.website_url,
                        "mvp": st.session_state.mvp
                    }
                    try:
                        response = requests.post(
                            "https://celebrated-analysis-production.up.railway.app/complete_analysis", 
                            json=data,
                            timeout=60
                        )
                        result = handle_api_response(response)
                        if result:
                            st.session_state.analysis_result = result.get('analysis', {})
                            st.session_state.product_brief = result.get('product_brief', {})
                            st.session_state.requirements.update({
                                'project_name': st.session_state.project_idea,
                                'industry': st.session_state.industry,
                                'problem_statement': st.session_state.problem_area
                            })
                            st.success("Product brief generated successfully! Switch to the 'Project Brief' tab to view it.")
                    except Exception as e:
                        st.error(f"An unexpected error occurred: {str(e)}")
    with col2:
        st.info("""
        ### Tips for Better Results
        - Be specific about your problem
        - Include current pain points
        - Mention any existing solutions
        - Describe desired outcomes
        """)

# Tab 2: Project Brief
with tab2:
    st.header("📋 Project Brief")
    if st.session_state.product_brief:
        with st.expander("View Initial Analysis", expanded=False):
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

# Tab 3: Market & Competitor Analysis
with tab3:
    st.header("📈 Market Analysis")
    if st.session_state.product_brief:
        if st.button("Generate Market Analysis"):
            with st.spinner("Generating market analysis..."):
                try:
                    market_competitor_response = requests.post(
                        "https://celebrated-analysis-production.up.railway.app/generate_market_analysis",
                        json={
                            "context": st.session_state.product_brief,
                            "website_overview": st.session_state.analysis_result.get("website_overview", "")
                        },
                        timeout=60
                    )
                    market_result = handle_api_response(market_competitor_response)
                    print(market_result)
                    if market_result:
                        st.session_state.market_analysis = market_result
                        st.success("Market and competitor analysis generated successfully!")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {str(e)}")
        if st.session_state.market_analysis:
            display_market_analysis(st.session_state.market_analysis)
    else:
        st.info("Please generate the product brief in the Idea Generation tab to see the market and competitor analysis.")

with tab4:
    st.header("📈 Competitor Analysis")
    
    # Check if Product Brief is generated before enabling competitor analysis
    if st.session_state.product_brief:
        if st.button("Generate Competitor Analysis"):
            with st.spinner("Generating competitor analysis..."):
                data = {
                    "domain": st.session_state.industry,
                    "problem": st.session_state.problem_area,
                    "website": st.session_state.website_url,
                    "mvp": st.session_state.mvp
                }
                try:
                    competitor_response = requests.post(
                        "https://celebrated-analysis-production.up.railway.app/competition_research",
                        json=data,
                        timeout=60
                    )
                    competitor_result = handle_api_response(competitor_response)
                    if competitor_result:
                        st.session_state.competitor_analysis = competitor_result
                        st.success("Competitor analysis generated successfully!")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {str(e)}")
        
        # Display competitor analysis results if available
        if st.session_state.competitor_analysis:
            display_competitor_analysis(st.session_state.competitor_analysis)
    else:
        st.info("Please generate the product brief in the Idea Generation tab to see the market and competitor analysis.")

# Tab 4: Technical Components
with tab5:
    st.header("📊 Technical Components")
    if st.session_state.product_brief:
        if st.button("Generate Technical Implementation Details"):
            with st.spinner("Generating technical implementation details..."):
                try:
                    tech_stack_response = requests.post(
                        "https://celebrated-analysis-production.up.railway.app/generate_tech_stack",
                        json={
                            "context": st.session_state.product_brief,
                            "website_overview": st.session_state.analysis_result.get("website_overview", "")
                        },
                        timeout=120  # Increased timeout to handle longer processing times
                    )
                    tech_stack_result = handle_api_response(tech_stack_response)
                    if tech_stack_result and "technical_details" in tech_stack_result:
                        st.session_state.technical_details = tech_stack_result
                        st.success("Technical implementation details generated successfully!")
                    else:
                        st.error("Failed to generate technical implementation details.")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {str(e)}")
        if st.session_state.technical_details:
            st.markdown("### Technical Implementation Details")
            technical_details_md = st.session_state.technical_details.get('technical_details', 'Not available')
            st.markdown(technical_details_md, unsafe_allow_html=True)
            st.markdown("### System Diagram")
            mermaid_diagram = st.session_state.technical_details.get('mermaid_diagram', '')
            if mermaid_diagram:
                # Ensure the diagram uses 'graph LR' for left-to-right layout
                mermaid_diagram_lines = mermaid_diagram.strip().split('\n')
                if mermaid_diagram_lines and not mermaid_diagram_lines[0].startswith('graph'):
                    mermaid_diagram = 'graph LR\n' + '\n'.join(mermaid_diagram_lines)
                elif mermaid_diagram_lines[0].startswith('graph TD'):
                    mermaid_diagram_lines[0] = mermaid_diagram_lines[0].replace('graph TD', 'graph LR', 1)
                    mermaid_diagram = '\n'.join(mermaid_diagram_lines)
                # Optionally, wrap the diagram in a container for horizontal scrolling
                st.markdown('<div style="overflow-x: auto;">', unsafe_allow_html=True)
                st_mermaid(mermaid_diagram, key="mermaid_diagram")
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No diagram available.")
    else:
        st.info("Please generate the product brief in the Idea Generation tab to see the technical components.")



# Tab 5: Final Report
with tab6:
    st.header("📄 Final Report")
    if st.session_state.product_brief:
        st.markdown("## Complete Project Report")
        st.markdown("### Project Brief")
        display_product_brief(st.session_state.product_brief)
        if st.session_state.market_analysis:
            st.markdown("### Market Analysis")
            display_market_analysis(st.session_state.market_analysis)
        if st.session_state.competitor_analysis:
            st.markdown("### Market Analysis")
            display_competitor_analysis(st.session_state.competitor_analysis)
        if st.session_state.technical_details:
            st.markdown("### Technical Implementation Details")
            st.markdown(st.session_state.technical_details.get('technical_details', 'Not available'))
            st.markdown("### System Diagram")
            mermaid_diagram = st.session_state.technical_details.get('mermaid_diagram', '')
            if mermaid_diagram:
                st_mermaid(mermaid_diagram)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Export Report as PDF"):
                st.warning("PDF export functionality to be implemented")
        with col2:
            if st.button("Export Report as Markdown"):
                report_content = ""
                # Concatenate all sections
                report_content += "## Project Brief\n"
                for title, key in [
                    ("Problem Statement", "problem_statement"),
                    ("Target Audience", "target_audience"),
                    ("Why It Matters", "why_it_matters"),
                    ("Proposed Solution", "proposed_solution"),
                    ("Success Criteria", "success_criteria"),
                    ("Risks and Considerations", "risks_and_considerations"),
                    ("Next Steps", "next_steps"),
                    ("Additional Notes", "additional_notes")
                ]:
                    content = st.session_state.product_brief.get(key, "Not available")
                    report_content += f"### {title}\n{content}\n\n"
                if st.session_state.market_competitor_analysis:
                    report_content += "## Market & Competitor Analysis\n"
                    for title, key in [
                        ("Market Overview", "market_overview"),
                        ("Target Market", "target_market"),
                        ("Competitive Landscape", "competitive_landscape"),
                        ("Opportunities and Threats", "opportunities_and_threats"),
                        ("Differentiation", "differentiation")
                    ]:
                        content = st.session_state.market_competitor_analysis.get(key, "Not available")
                        report_content += f"### {title}\n{content}\n\n"
                if st.session_state.technical_details:
                    report_content += "## Technical Implementation Details\n"
                    report_content += f"{st.session_state.technical_details.get('technical_details', '')}\n\n"
                    mermaid_diagram = st.session_state.technical_details.get('mermaid_diagram', '')
                    if mermaid_diagram:
                        report_content += "### System Diagram\n"
                        report_content += f"```mermaid\n{mermaid_diagram}\n```\n\n"
                st.download_button(
                    label="Download Report as Markdown",
                    data=report_content,
                    file_name="complete_project_report.md",
                    mime="text/markdown"
                )
    else:
        st.info("Please complete the previous steps to generate the final report.")

# Sidebar for navigation and settings
with st.sidebar:
    current_file = Path(__file__)
    project_root = current_file.parent.parent
    logo_path = project_root / 'assets' / 'AI_consult_logo.png'
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
    st.title("🤖 Your project name: " + st.session_state.requirements['project_name'] if st.session_state.requirements['project_name'] else "Project Name")
    st.markdown("---")
    st.subheader("Project Progress: ")
    st.subheader("1. Fill the info: " + ("✅" if all([st.session_state.project_idea.strip(), st.session_state.industry.strip(), st.session_state.problem_area.strip()]) else "⏳"))
    st.subheader("2. View project brief: " + ("✅" if st.session_state.product_brief else "⏳"))
    st.subheader("3. Generate market analysis: " + ("✅" if st.session_state.market_analysis else "⏳"))
    st.subheader("4. Generate competitor analysis: " + ("✅" if st.session_state.competitor_analysis else "⏳"))
    st.subheader("5. View technical components: " + ("✅" if st.session_state.technical_details else "⏳"))
    progress = st.progress(0)
    completed_sections = sum([
        bool(st.session_state.project_idea.strip()),
        bool(st.session_state.product_brief),
        bool(st.session_state.market_analysis),
        bool(st.session_state.competitor_analysis),
        bool(st.session_state.technical_details)
    ])
    progress.progress(completed_sections / 5)
