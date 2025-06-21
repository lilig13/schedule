import streamlit as st
import datetime

st.set_page_config(page_title="Moving Schedule", layout="centered")
st.title("📋 Moving Schedule")

# --- Initial Data ---
people_list = ["Lulu", "Yeni", "Angelo", "Jeremiah", "Alonso", "Keaneu",
               "Jackson", "Alex", "Walker", "Dayanna", "Sophia"]

materials_list = [
    "1.5 Boxes", "3.0 Boxes", "4.5 Boxes (Tall)", "4.5 Boxes (Long)", "2 PC Mirror",
    "Tape (Pack)", "Stretch wrap (Roll)", "Big Bubble Wrap (Feet)", "Small Bubble Wrap (Feet)",
    "Paper Pad (Brown Paper)", "Mattress Bag", "TV Mount (Small)", "TV Mount (Large)",
    "Felt Pad (Pack)", "Newsprint (White Paper)", "Clear Trash Bags (Box)",
    "Black Trash Bags (Box)", "Rug Gripper Thick Pads"
]

truck_trailer_list = ["10", "11", "30", "31", "32", "33", "50", "51", "52", "53", "54", "55", "56", "57", "59"]

default_time = datetime.time(0, 0)

# --- Utilities ---
def format_materials(material_dict):
    return "\n".join([f"{amt} x {mat}" for mat, amt in material_dict.items()]) if material_dict else "None"

def render_team_section(index):
    team_label = f"Team {index + 1}"
    role_options = ["Project Manager", "Client Manager"]
    people_options = people_list.copy()

    with st.expander(team_label, expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            role_sel = st.multiselect("Role", role_options, default=[], key=f"role_{index}")
            role = ", ".join(role_sel) if role_sel else ""
        with col2:
            name_sel = st.multiselect("Name", people_options, default=[], key=f"name_{index}")
            name = ", ".join(name_sel) if name_sel else ""

        tl_sel = st.multiselect("Team Lead (TL)", people_options, default=[], key=f"tl_{index}")
        tl = ", ".join(tl_sel) if tl_sel else ""

        members = st.multiselect("Team Members", people_list, default=[], key=f"members_{index}")
        trucks = st.multiselect("Trucks & Trailers", truck_trailer_list, default=[], key=f"trucks_{index}")

        move_from = st.text_input("Move From", key=f"from_{index}")
        move_to = st.text_input("Move To", key=f"to_{index}")
        client = st.text_input("Client Name", key=f"client_{index}")
        contact = st.text_input("Point of Contact", key=f"contact_{index}")
        leave_by = st.time_input("Leave By Time", value=default_time, key=f"leave_{index}")

        selected_mats = st.multiselect("Materials", materials_list, key=f"mats_{index}")
        mat_amounts = {
            mat: st.number_input(f"Amount for {mat} ({team_label})", 1, key=f"amt_{mat}_{index}")
            for mat in selected_mats
        }

        notes = st.text_area("Notes", key=f"notes_{index}")

        return {
            "label": team_label,
            "role": role,
            "name": name,
            "tl": tl,
            "members": members,
            "trucks": trucks,
            "from": move_from,
            "to": move_to,
            "client": client,
            "contact": contact,
            "leave_by": leave_by.strftime("%I:%M %p").lstrip("0"),
            "materials": mat_amounts,
            "notes": notes
        }

# --- Session State ---
if "team_count" not in st.session_state:
    st.session_state.team_count = 2

if "intime_count" not in st.session_state:
    st.session_state.intime_count = 2

# --- Date ---
date_input = st.date_input("Date", value=datetime.date.today())
formatted_date = date_input.strftime("%B %d")

# --- In-Times ---
with st.expander("In-Times", expanded=True):
    for i in range(st.session_state.intime_count):
        with st.expander(f"In-Time Team {i + 1}", expanded=True):
            col1, col2 = st.columns([1, 3])
            time = st.time_input(f"Time {i+1}", value=default_time, key=f"time_{i}")
            members = st.multiselect(f"Team Members {i+1}", people_list, default=[], key=f"intime_members_{i}")

    col_add, col_del = st.columns([1, 1])
    with col_add:
        if st.button("➕ Add Another In-Time"):
            st.session_state.intime_count += 1
            st.rerun()
    with col_del:
        if st.session_state.intime_count > 1:
            if st.button("🗑️ Delete Last In-Time"):
                st.session_state.intime_count -= 1
                st.rerun()

# --- Teams Section ---
teams_data = []
for i in range(st.session_state.team_count):
    team_data = render_team_section(i)
    teams_data.append(team_data)

col_add_team, col_del_team = st.columns([1, 1])
with col_add_team:
    if st.button("➕ Add Another Team"):
        st.session_state.team_count += 1
        st.rerun()
with col_del_team:
    if st.session_state.team_count > 1:
        if st.button("🗑️ Delete Last Team"):
            st.session_state.team_count -= 1
            st.rerun()

# --- Generate Schedule ---
if st.button("✅ Generate Schedule"):
    in_times_text = ""
    for i in range(st.session_state.intime_count):
        t = st.session_state[f"time_{i}"].strftime("%I:%M %p").lstrip("0")
        m = ", ".join(st.session_state[f"intime_members_{i}"])
        in_times_text += f"{t} {m}\n"

    schedule = f"{formatted_date}\n\nHi everyone!\nIn times are the following:\n\n{in_times_text.strip()}\n\n"

    for team in teams_data:
        team_section = f"""{team['label']}:
Role: {team['role']}
Name: {team['name']}
Team Lead (TL): {team['tl']}
Team Members: {', '.join(team['members'])}
Trucks & Trailers: {', '.join(team['trucks'])}
Moving From: {team['from']}
Moving To: {team['to']}
Client Name: {team['client']}
Point of Contact: {team['contact'] or 'N/A'}
🚨 Leave by {team['leave_by']} 🚨
Materials:
{format_materials(team['materials'])}
Notes: {team['notes'] or 'N/A'}
"""
        schedule += "—————————\n" + team_section + "\n"

    schedule += "Friendly reminder, please clock in as soon as everyone is in the truck."

    st.code(schedule, language="text")
    st.download_button("📥 Download Schedule", data=schedule, file_name="move_schedule.txt")

