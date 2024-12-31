import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Initialize session state
def init_session_state():
    if "teams" not in st.session_state:
        st.session_state.teams = {}


# Default skills for each category
DEFAULT_SKILLS = {
    "Technical": ["Databricks", "Python", "NodeJS", "SQL", "Gitlab"],
    "Domain": ["LM", "SM", "in vitro", "in vivo", "target"],
    "Operational": ["SAFe", "Collab", "Comms", "SNOW", "Monitoring and Tracking"]
}

# Add a new team
def add_team():
    team_name = st.text_input("Enter team name:", key="add_team")
    if st.button("Add Team"):
        if team_name and team_name not in st.session_state.teams:
            st.session_state.teams[team_name] = {
                "members": {},
                "skills": {
                    category: skills.copy() for category, skills in DEFAULT_SKILLS.items()
                }
            }
            st.success(f"Team '{team_name}' added with default skills.")
        elif team_name in st.session_state.teams:
            st.warning(f"Team '{team_name}' already exists.")
        else:
            st.error("Please enter a valid team name.")

# Add multiple members to a team
def add_members(team_name):
    members_input = st.text_area("Enter member names (comma or line separated):", key=f"add_members_{team_name}")
    if st.button(f"Add Members to {team_name}"):
        if members_input:
            members = [m.strip() for m in members_input.replace("\n", ",").split(",") if m.strip()]
            for member_name in members:
                if member_name and member_name not in st.session_state.teams[team_name]["members"]:
                    st.session_state.teams[team_name]["members"][member_name] = {}
            st.success(f"Members added to team '{team_name}': {', '.join(members)}")
        else:
            st.error("Please enter valid member names.")

# Add multiple skills to a team under categories
def add_skills(team_name):
    for category in ["Technical", "Domain", "Operational"]:
        skills_input = st.text_area(f"Enter {category} skill names (comma or line separated):", key=f"add_skills_{team_name}_{category}")
        if st.button(f"Add {category} Skills to {team_name}"):
            if skills_input:
                skills = [s.strip() for s in skills_input.replace("\n", ",").split(",") if s.strip()]
                for skill_name in skills:
                    if skill_name and skill_name not in st.session_state.teams[team_name]["skills"][category]:
                        st.session_state.teams[team_name]["skills"][category].append(skill_name)
                st.success(f"{category} Skills added to team '{team_name}': {', '.join(skills)}")
            else:
                st.error(f"Please enter valid {category} skill names.")

# Assign competency levels for each skill in a team
def assign_competency(team_name):
    if not any(st.session_state.teams[team_name]["skills"].values()):
        st.warning(f"No skills added to team '{team_name}'. Please add skills first.")
        return

    for category, skills in st.session_state.teams[team_name]["skills"].items():
        for skill in skills:
            st.subheader(f"Competency Levels for {category} Skill: {skill}")
            for member_name in st.session_state.teams[team_name]["members"]:
                level = st.slider(
                    f"{skill} competency for {member_name}",
                    min_value=0,
                    max_value=10,
                    key=f"{team_name}_{member_name}_{skill}",
                )
                st.session_state.teams[team_name]["members"][member_name][skill] = level

# Display radar chart for a team category
def display_category_radar_chart(team_name, category):
    team_data = st.session_state.teams[team_name]
    skills = team_data["skills"].get(category, [])

    if not skills or not team_data["members"]:
        st.warning(f"Cannot create radar chart for category '{category}' in team '{team_name}'. Add skills and members first.")
        return

    skill_stats = {"Skill": [], "Min": [], "Max": [], "Average": []}
    for skill in skills:
        competencies = [
            team_data["members"][member][skill]
            for member in team_data["members"]
            if skill in team_data["members"][member]
        ]
        if competencies:
            skill_stats["Skill"].append(skill)
            skill_stats["Min"].append(min(competencies))
            skill_stats["Max"].append(max(competencies))
            skill_stats["Average"].append(sum(competencies) / len(competencies))

    if len(skill_stats["Skill"]) < 5 or len(skill_stats["Skill"]) > 8:
        st.warning(f"Radar chart for category '{category}' can only be displayed if there are between 5 and 8 skills. Current count: {len(skill_stats['Skill'])}.")
        return

    df = pd.DataFrame(skill_stats)

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=df["Min"], theta=df["Skill"], fill="toself", name="Min"))
    fig.add_trace(go.Scatterpolar(r=df["Max"], theta=df["Skill"], fill="toself", name="Max"))
    fig.add_trace(go.Scatterpolar(r=df["Average"], theta=df["Skill"], fill="toself", name="Average"))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        showlegend=True,
        title=f"{category} Competency Radar Chart for Team: {team_name}"
    )

    return fig

# Display and manage teams
def manage_teams():
    if not st.session_state.teams:
        st.warning("No teams added yet. Please add a team first.")
        return

    for team_name, team_data in st.session_state.teams.items():
        st.subheader(f"Team: {team_name}")

        # Display members and skills
        st.write("**Members:**", list(team_data["members"].keys()))
        for category, skills in team_data["skills"].items():
            st.write(f"**{category} Skills:**", skills)

        # Add members and skills
        with st.expander(f"Manage {team_name}"):
            add_members(team_name)
            add_skills(team_name)
            assign_competency(team_name)

        # Display radar charts for each category
        with st.expander(f"Radar Charts for {team_name}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.plotly_chart(display_category_radar_chart(team_name, "Technical"), use_container_width=True)
            with col2:
                st.plotly_chart(display_category_radar_chart(team_name, "Domain"), use_container_width=True)
            with col3:
                st.plotly_chart(display_category_radar_chart(team_name, "Operational"), use_container_width=True)

        # Delete team
        if st.button(f"Delete {team_name}"):
            del st.session_state.teams[team_name]
            st.success(f"Team '{team_name}' deleted.")
            st.rerun()
# Main app
st.title("Team and Skill Management App")
init_session_state()

st.sidebar.header("Add Team")
add_team()

st.sidebar.header("Manage Teams")
manage_teams()

# Export data
def export_data():
    all_data = []
    for team_name, team_data in st.session_state.teams.items():
        for member_name, skills in team_data["members"].items():
            for skill, level in skills.items():
                all_data.append({
                    "Team": team_name,
                    "Member": member_name,
                    "Skill": skill,
                    "Competency Level": level,
                })
    return pd.DataFrame(all_data)

if st.button("Export Data"):
    data = export_data()
    if not data.empty:
        st.download_button(
            label="Download CSV",
            data=data.to_csv(index=False),
            file_name="team_data.csv",
            mime="text/csv",
        )
    else:
        st.warning("No data to export.")
