import streamlit as st
import streamlit.components.v1 as components
import json
import os

# 1. Page Config
st.set_page_config(
    page_title="MBBS PBL Dashboard", 
    page_icon="📚", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 2. Folder Structure Mapping
STRUCTURE = {
    "Locomotion, Back & Integumentary System": "Locomotion",
    "Urinary System": "Urinary system",
    "Reproductive System": "Reproductive"
}

# 3. Clean Display Names Mapping
PBL_NAMES = {
    "Myasthenia_gravis.json": "PBL 1 – Generalized Weakness",
    "Erbs_compartmentsyn_carpaltunnel.json": "PBL 2, 3 & 4 – Upper Limb Injuries",
    "Turner_Syndrome_UI.html": "PBL 1 – Disturbed Married Life (Custom UI)"
}

# 4. Helper Functions
@st.cache_data
def load_json(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error reading {filepath}: {e}")
        return None

@st.cache_data
def load_html(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        st.error(f"Error reading {filepath}: {e}")
        return None

def render_json_block(pbl):
    st.header(pbl.get("title", "Unnamed Case Study"))
    col1, col2 = st.columns([3, 2], gap="large")
    
    with col1:
        if "details" in pbl and pbl["details"]:
            st.markdown("### 🩺 Clinical Presentation")
            st.table(pbl["details"])
            
        if "diagram" in pbl and pbl["diagram"].strip():
            st.markdown("### 🔄 Pathophysiology Map")
            st.graphviz_chart(pbl["diagram"])
            
    with col2:
        st.markdown("### 🧠 Viva Preparation")
        if "viva" in pbl and pbl["viva"]:
            for idx, qa in enumerate(pbl["viva"]):
                with st.expander(f"💬 Q{idx+1}: {qa['q']}", expanded=False):
                    st.markdown(f"**Answer:**\n{qa['a']}")
        else:
            st.write("*No assessment criteria configured for this profile.*")
            
        st.markdown("---")
        if "pearl" in pbl and pbl["pearl"].strip():
            st.warning(f"💡 **Clinical Pearl:**\n\n{pbl['pearl']}")
            
    st.markdown("<br><hr style='border:1px dashed #444;'><br>", unsafe_allowed_html=True)


# 5. Sidebar UI
st.sidebar.title("📚 MBBS PBL Dashboard")
st.sidebar.markdown("---")

selected_module_label = st.sidebar.selectbox("Select Module", list(STRUCTURE.keys()))
target_folder = STRUCTURE[selected_module_label]

# Scan the subfolder for both .json and .html files
folder_path = os.path.join("Data", target_folder)
available_files = []
if os.path.exists(folder_path):
    available_files = [f for f in os.listdir(folder_path) if f.endswith('.json') or f.endswith('.html')]

# 6. Main Routing Logic
if available_files:
    display_options = {f: PBL_NAMES.get(f, f.replace(".json", "").replace(".html", "").replace("_", " ").title()) for f in available_files}
    
    st.sidebar.markdown("### 📑 Case Files Found")
    selected_file = st.sidebar.radio(
        "Go to Case Study:", 
        options=available_files, 
        format_func=lambda x: display_options[x]
    )
    
    filepath = os.path.join(folder_path, selected_file)

    # If the user selects a custom HTML file
    if selected_file.endswith('.html'):
        html_content = load_html(filepath)
        if html_content:
            # Render the custom UI full width
            components.html(html_content, height=1200, scrolling=True)
            
    # If the user selects a standard JSON file
    elif selected_file.endswith('.json'):
        st.title(selected_module_label)
        st.markdown("---")
        
        file_data = load_json(filepath)
        if file_data:
            # Handle files that have multiple PBLs in one JSON array
            if "pbls" in file_data:
                for single_case in file_data["pbls"]:
                    render_json_block(single_case)
            # Handle files that are just a single PBL object
            else:
                render_json_block(file_data)
else:
    st.title(selected_module_label)
    st.markdown("---")
    st.warning(f"No active case files (.json or .html) found inside the directory: `Data/{target_folder}/` yet.")
