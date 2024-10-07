import streamlit as st
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Project Requirements Builder",
    page_icon="🤖",
    layout="wide"
)

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Project Requirements",
    "Competitive Analysis",
    "Implementation",
    "Diagram Generation",
    "Technical Difficulties"
])

# Tab 1: Project Requirements
with tab1:
    # Step 1: Basic Project Info
    st.header("Step 1: Basic Project Info")
    product_name = st.text_input("Product Name:")
    description = st.text_input("One-sentence description:")

    # Optional: Company/Project Website
    website = st.text_input("Company/Project Website (optional):")

    # Step 2: Core Problem
    st.header("Step 2: Core Problem")
    problem_statement = st.text_area("What problem are you solving?")
    who_has_problem = st.text_input("Who has this problem?")
    occurrence_frequency = st.selectbox("How often does it occur?", ["Daily", "Weekly", "Monthly", "Yearly"])
    current_solutions = st.text_area("Current solutions/workarounds?")

    # Optional: Tick box to view online competition based on website
    if website:
        view_competition = st.checkbox("View online competition based on your website")
        if view_competition:
            st.write(f"Analyzing competition for: {website}")
            # Placeholder for competition analysis functionality

    # Step 3: Target Users
    st.header("Step 3: Target Users")
    primary_user = st.text_input("Primary user type:")
    main_pain_points = st.text_area("Main pain points:")
    current_process = st.text_area("Current process:")

    # Step 4: Business Goals
    st.header("Step 4: Business Goals")
    primary_goal = st.text_input("Primary goal:")
    timeline = st.date_input("Timeline:")
    key_constraints = st.multiselect("Key constraints:", ["Budget", "Technical resources", "Time", "Regulatory", "Other"])

    # Other constraint input if 'Other' is selected
    if "Other" in key_constraints:
        other_constraint = st.text_input("Specify other constraints:")

    # Step 5: Success Definition
    st.header("Step 5: Success Definition")
    success_metric = st.text_input("Primary success metric:")
    minimum_viable_outcome = st.text_area("Minimum viable outcome:")

    # Optional Summary Sections
    st.header("Optional Summary")
    show_core_problem = st.checkbox("Show Core Problem")
    show_target_users = st.checkbox("Show Target Users")
    show_success_definition = st.checkbox("Show Success Definition")

    if show_core_problem:
        st.subheader("Core Problem Summary")
        st.write(f"Problem: {problem_statement}")
        st.write(f"Who has this problem: {who_has_problem}")
        st.write(f"Occurrence Frequency: {occurrence_frequency}")
        st.write(f"Current Solutions: {current_solutions}")

    if show_target_users:
        st.subheader("Target Users Summary")
        st.write(f"Primary User Type: {primary_user}")
        st.write(f"Main Pain Points: {main_pain_points}")
        st.write(f"Current Process: {current_process}")



    # Button to save project
    if st.button("Save Project Info"):
        st.success("Project information saved successfully!")

# Tab 2: Competitive Analysis
with tab2:
    st.header("Competitive Analysis")
    st.write("Details for competitive analysis will be provided here.")

# Tab 3: Implementation
with tab3:
    st.header("Implementation")
    st.write("Implementation steps and strategies will be provided here.")

# Tab 4: Diagram Generation
with tab4:
    st.header("Diagram Generation")
    st.write("Tools and methods for generating diagrams will be provided here.")

# Tab 5: Technical Difficulties
with tab5:
    st.header("Technical Difficulties")
    st.write("Potential technical challenges and mitigation strategies will be discussed here.")