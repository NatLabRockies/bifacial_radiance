"""
Project Overview Page - Portfolio dashboard and project management
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_config
from utils.database import get_db, get_all_projects, create_project, get_project
from modules.visualization import SolarVisualizer

st.set_page_config(page_title="Project Overview", page_icon="🏗️", layout="wide")

config = get_config()
visualizer = SolarVisualizer()

st.title("🏗️ Project Portfolio Overview")

# Tabs for different views
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "➕ New Project", "📋 Project List"])

with tab1:
    st.header("Portfolio Dashboard")

    try:
        db = get_db()
        projects = get_all_projects(db)
        db.close()

        if projects:
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Projects", len(projects))

            with col2:
                design_count = sum(1 for p in projects if p.status == 'design')
                st.metric("In Design", design_count)

            with col3:
                construction_count = sum(1 for p in projects if p.status == 'construction')
                st.metric("Under Construction", construction_count)

            with col4:
                operational_count = sum(1 for p in projects if p.status == 'operations')
                st.metric("Operational", operational_count)

            # Project table
            st.subheader("All Projects")

            project_data = []
            for p in projects:
                project_data.append({
                    'Project ID': p.project_id,
                    'Name': p.name,
                    'Location': f"{p.latitude:.4f}, {p.longitude:.4f}",
                    'Capacity (kW)': p.system_capacity_kw or 'N/A',
                    'Type': p.project_type or 'N/A',
                    'Status': p.status,
                    'Created': p.created_at.strftime('%Y-%m-%d') if p.created_at else 'N/A',
                })

            df = pd.DataFrame(project_data)
            st.dataframe(df, use_container_width=True)

            # Map view
            if any(p.latitude and p.longitude for p in projects):
                st.subheader("Project Locations")
                map_data = pd.DataFrame([
                    {
                        'lat': p.latitude,
                        'lon': p.longitude,
                        'name': p.name
                    }
                    for p in projects if p.latitude and p.longitude
                ])
                st.map(map_data)

        else:
            st.info("📝 No projects yet. Create your first project in the 'New Project' tab!")

    except Exception as e:
        st.error(f"Error loading projects: {e}")

with tab2:
    st.header("Create New Project")

    with st.form("new_project_form"):
        col1, col2 = st.columns(2)

        with col1:
            project_id = st.text_input("Project ID *", help="Unique identifier (e.g., SOLAR-001)")
            project_name = st.text_input("Project Name *", help="Full project name")
            project_type = st.selectbox(
                "Project Type *",
                ["fixed-tilt", "single-axis-tracking", "dual-axis-tracking", "agripv", "carport"]
            )
            status = st.selectbox("Status", ["design", "construction", "operations", "completed"])

        with col2:
            latitude = st.number_input("Latitude *", min_value=-90.0, max_value=90.0, value=37.5, format="%.6f")
            longitude = st.number_input("Longitude *", min_value=-180.0, max_value=180.0, value=-77.6, format="%.6f")
            capacity_kw = st.number_input("System Capacity (kW DC)", min_value=0.0, value=5000.0, step=100.0)
            location_name = st.text_input("Location Name", help="e.g., Richmond, VA")

        description = st.text_area("Project Description")

        col3, col4 = st.columns(2)
        with col3:
            planned_start = st.date_input("Planned Start Date")
        with col4:
            planned_completion = st.date_input("Planned Completion Date")

        submitted = st.form_submit_button("Create Project")

        if submitted:
            if not project_id or not project_name:
                st.error("Project ID and Name are required!")
            else:
                try:
                    db = get_db()

                    # Check if project ID already exists
                    existing = get_project(db, project_id)
                    if existing:
                        st.error(f"Project ID '{project_id}' already exists!")
                    else:
                        # Create project
                        project_data = {
                            'project_id': project_id,
                            'name': project_name,
                            'description': description,
                            'latitude': latitude,
                            'longitude': longitude,
                            'location_name': location_name,
                            'system_capacity_kw': capacity_kw,
                            'project_type': project_type,
                            'status': status,
                            'planned_start_date': datetime.combine(planned_start, datetime.min.time()),
                            'planned_completion_date': datetime.combine(planned_completion, datetime.min.time()),
                            'created_by': 'user',  # TODO: Add user authentication
                        }

                        create_project(db, project_data)
                        db.close()

                        st.success(f"✅ Project '{project_name}' created successfully!")
                        st.balloons()

                except Exception as e:
                    st.error(f"Error creating project: {e}")

with tab3:
    st.header("Project Details")

    try:
        db = get_db()
        projects = get_all_projects(db)
        db.close()

        if projects:
            # Select project
            project_names = {p.name: p.project_id for p in projects}
            selected_name = st.selectbox("Select Project", list(project_names.keys()))

            if selected_name:
                selected_id = project_names[selected_name]
                db = get_db()
                project = get_project(db, selected_id)
                db.close()

                if project:
                    # Project details
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.subheader("Basic Information")
                        st.write(f"**Project ID:** {project.project_id}")
                        st.write(f"**Name:** {project.name}")
                        st.write(f"**Type:** {project.project_type or 'N/A'}")
                        st.write(f"**Status:** {project.status}")
                        st.write(f"**Capacity:** {project.system_capacity_kw or 'N/A'} kW")

                    with col2:
                        st.subheader("Location")
                        st.write(f"**Coordinates:** {project.latitude:.6f}, {project.longitude:.6f}")
                        st.write(f"**Location:** {project.location_name or 'N/A'}")

                        # Show map
                        if project.latitude and project.longitude:
                            map_fig = visualizer.plot_site_map(
                                project.latitude, project.longitude, project.name
                            )
                            st.plotly_chart(map_fig, use_container_width=True)

                    with col3:
                        st.subheader("Timeline")
                        if project.planned_start_date:
                            st.write(f"**Planned Start:** {project.planned_start_date.strftime('%Y-%m-%d')}")
                        if project.planned_completion_date:
                            st.write(f"**Planned Completion:** {project.planned_completion_date.strftime('%Y-%m-%d')}")
                        if project.actual_start_date:
                            st.write(f"**Actual Start:** {project.actual_start_date.strftime('%Y-%m-%d')}")

                    if project.description:
                        st.subheader("Description")
                        st.write(project.description)

                    # Actions
                    st.subheader("Actions")
                    action_col1, action_col2, action_col3 = st.columns(3)

                    with action_col1:
                        if st.button("📊 Run Analysis"):
                            st.info("Navigate to 'New Site Analysis' to run performance modeling")

                    with action_col2:
                        if st.button("🏗️ Track Construction"):
                            st.info("Navigate to 'Construction Tracking' to monitor progress")

                    with action_col3:
                        if st.button("⚡ Monitor Operations"):
                            st.info("Navigate to 'Operations Monitor' to track performance")

        else:
            st.info("No projects available. Create a project in the 'New Project' tab.")

    except Exception as e:
        st.error(f"Error loading project details: {e}")

# Sidebar
st.sidebar.header("About")
st.sidebar.info("""
**Project Overview** provides a centralized dashboard for managing your solar project portfolio.

**Features:**
- View all projects at a glance
- Create new projects
- Track project status
- View project locations on map
- Access project details
""")
