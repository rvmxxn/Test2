

import streamlit as st
import json
import os

# Page Config for clean layout
st.set_page_config(
    page_title="MBBS PBL Dashboard", 
    page_icon="📚", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Structure mapping folder display names to actual directory names
STRUCTURE = {
    "Locomotion, Back & Integumentary System": "Locomotion",
    "Urinary System": "Urinary system",
    "Reproductive System": "Reproductive"
}

# Mapping exact file names to your dashboard listing names
PBL_NAMES = {
    # Locomotion
    "Myasthenia_gravis.json": "PBL 1 – Generalized Weakness",
    "Erbs_compartmentsyn_carpaltunnel.json": "PBL 2 – I Can't Start My Day / Arm Injuries",
    "Colles_humeralfrac.json": "PBL 3 – The Wrist in a Twist / Fractures",
    "Disc_herniation.json": "PBL 5 – Severe Pain in the Back and Leg",
    "Acute_om.json": "PBL 7 – When a Simple Slip Becomes Serious",
    "Ra_gout.json": "PBL 4 – OMG My Knees!",
    "Oa.json": "PBL 6 – Osteoarthritis Profile",
    # Urinary
    "Apsg.json": "PBL 1 – Facial Swelling with Frothy Urine",
    "Mcd.json": "PBL 2 – Minimal Change Disease Profile",
    "Aki.json": "PBL 3 – Why Is My Urine Output So Low?",
    "Urolithiasis.json": "PBL 4 – Why Is My Urine Red?",
    # Reproductive
    "Aub_endometriosis.json": "PBL 1 – Disturbed Married Life",
    "Turner_syndrome.json": "PBL 2 – Turner Syndrome Case"
}

@st.cache_data
def load_single_pbl(folder, filename):
    filepath = os.path.join("Data", folder, filename)
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error reading {filename}: {e}")
        return None

# --- Layout Rendering Helper ---
def render_pbl_block(pbl):
    st.header(pbl.get("title", "Unnamed Case Study"))
    col1, col2 = st.columns([3, 2], gap="large")
    
    with col1:
        if "details" in pbl and pbl["details"]:
            st.markdown("### 🩺 Clinical Presentation")
            st.table(pbl["details"])
            
        if "diagram" in pbl and pbl["diagram"].strip():
            st.markdown("### 🔄 Pathophysiology / Management Map")
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

# --- Sidebar UI ---
st.sidebar.title("📚 MBBS PBL Dashboard")
st.sidebar.markdown("---")

selected_module_label = st.sidebar.selectbox("Select Module", list(STRUCTURE.keys()))
target_folder = STRUCTURE[selected_module_label]

# Scan the subfolder for available JSON files
folder_path = os.path.join("Data", target_folder)
available_files = []
if os.path.exists(folder_path):
    available_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]

# Build option lists for navigation based on files physically present
if available_files:
    # Use the mapping array for clean UI names, fallback to raw filename if unmapped
    display_options = {f: PBL_NAMES.get(f, f.replace(".json", "").replace("_", " ").title()) for f in available_files}
    
    st.sidebar.markdown("### 📑 Case Files Found")
    selected_file = st.sidebar.radio(
        "Go to Case Study:", 
        options=available_files, 
        format_func=lambda x: display_options[x]
    )
    
    # Global Search Input
    search_query = st.sidebar.text_input("🔍 Search within this module", "").strip().lower()
    
    # --- Data Processing and Display Engine ---
    st.title(selected_module_label)
    st.caption(f"Current Directory: Data/{target_folder}/")
    st.markdown("---")

    if search_query:
        # Loop through all files in the active folder to execute deep text search
        matched_any = False
        for file in available_files:
            pbl_data = load_single_pbl(target_folder, file)
            if pbl_data:
                # Text aggregation for searching
                viva_text = " ".join([qa["q"] + " " + qa["a"] for qa in pbl_data.get("viva", [])]).lower()
                combined_content = (pbl_data.get("title", "") + " " + pbl_data.get("pearl", "") + " " + viva_text).lower()
                
                if search_query in combined_content:
                    render_pbl_block(pbl_data)
                    matched_any = True
        if not matched_any:
            st.info("No matching content found for your query in this module.")
    else:
        # Load and render just the one selected file
        active_pbl = load_single_pbl(target_folder, selected_file)
        if active_pbl:
            render_pbl_block(active_pbl)
else:
    st.title(selected_module_label)
    st.markdown("---")
    st.warning(f"No active case JSON files found inside the directory: `Data/{target_folder}/` yet.")


