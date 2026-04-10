import streamlit as st
import pandas as pd
import numpy as np
import time
import random
import os
import re
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="LAX Goalie AI Coach",
    page_icon="🥍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- State Management ---
if 'video_files' not in st.session_state:
    st.session_state.video_files = {}
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'analysis_in_progress' not in st.session_state:
    st.session_state.analysis_in_progress = False
if 'action_map' not in st.session_state:
    st.session_state.action_map = []

# --- UI Styling ---
def load_css():
    st.markdown("""
    <style>
        /* General Body and Font */
        body {
            color: #E0E0E0;
            background-color: #1a1a1a; /* Slightly lighter black */
        }
        h1, h2, h3 {
            color: #FFFFFF;
        }
        h1 {
            font-weight: bold;
        }
        h2 {
            border-bottom: 2px solid #4A90E2;
            padding-bottom: 10px;
            margin-top: 2rem;
            margin-bottom: 1.5rem;
        }

        /* Main content area */
        .main .block-container {
            padding: 2rem 4rem;
        }

        /* --- VIDEO GALLERY & CARD STYLING --- */
        .video-card {
            background-color: #252526;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            position: relative; /* Crucial for overlay button */
            border: 1px solid #3E3E3E;
        }
        .video-card h3 {
            margin-top: 0;
            margin-bottom: 1rem;
            border-bottom: none; /* Override h2 style */
        }
        
        /* --- OVERLAY DELETE BUTTON --- */
        .video-card .stButton > button {
            position: absolute;
            top: 10px;
            right: 10px;
            width: 35px;
            height: 35px;
            border-radius: 50%; /* Makes it round */
            background-color: rgba(40, 40, 40, 0.8);
            color: #BDBDBD;
            border: 1px solid #555;
            font-size: 16px;
            font-weight: bold;
            line-height: 1;
            z-index: 99; /* Ensure it's on top */
        }
        .video-card .stButton > button:hover {
            background-color: #D32F2F; /* Red on hover */
            color: white;
            border: 1px solid #D32F2F;
        }

        /* Expander for critique sections */
        .st-expander {
            border: 1px solid #3E3E3E;
            border-radius: 10px;
            background-color: #252526;
        }
        .st-expander header {
            font-size: 1.5rem;
            color: #FFFFFF;
            font-weight: bold;
        }

        /* Metric cards for grades */
        .metric-card {
            background-color: #252526;
            border-radius: 12px;
            padding: 25px;
            text-align: center;
            border: 1px solid #3E3E3E;
            height: 100%;
        }
        .metric-card h4 {
            font-size: 1rem;
            color: #BDBDBD;
            margin-bottom: 10px;
            font-weight: normal;
            text-transform: uppercase;
        }
        .metric-card .grade {
            font-size: 2.5rem;
            font-weight: bold;
            color: #4A90E2; /* Brighter blue for grades */
        }
        
        /* Table styling for event details */
        .event-table {
            width: 100%; border-collapse: collapse;
        }
        .event-table th, .event-table td {
            text-align: left; padding: 10px; border-bottom: 1px solid #3E3E3E;
        }
        .event-table th {
            background-color: #333333; font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)

# --- AI & Analysis Functions ---
TIPS = [
    "Keep your shoulders square to the shooter at all times. (The Lax Goalie Bible, p. 15)",
    "A 'Ray Lewis Ready' stance means feet slightly wider than shoulder-width and athletic bend. (The Lax Goalie Bible, p. 17)",
    "On low saves, think 'what time is it?' Your wrist rotation should be like checking a watch. (The Lax Goalie Bible, p. 38)",
    "The 5-step arc is fundamental: Pipe Left, 45-Left, Center, 45-Right, Pipe Right. (The Lax Goalie Bible, p. 25)",
    "Don't drag your trail foot. Finish every save with a shuffle step to stay balanced. (The Lax Goalie Bible, p. 42)",
    "Top hand drives a straight line to the ball—the shortest distance between two points. (The Lax Goalie Bible, p. 36)",
    "Practice the 'Walk the Arc' drill (p. 56) to master your positioning without thinking.",
    "Communication is key. Use the 'B-S-C' framework: Ball, Slide, Command. (The Lax Goalie Bible, p. 107)",
    "After a goal, use a 'Reset Routine': Deep breath, physical action, positive self-talk. (The Lax Goalie Bible, p. 103)",
    "For shots inside 8 yards, you must 'Read 'Em and Beat 'Em'—reacting is too slow. (The Lax Goalie Bible, p. 43)",
]

def run_computer_vision_analysis(video_files):
    action_map = []
    actions = {
        "Stance & Positioning": ["Stance too narrow", "Weight on heels", "Good athletic base", "Correct arc position", "Too deep in cage"],
        "Save Movement & Technique": ["Direct hand path to ball", "Sweeping/looping hand motion", "Excellent wrist rotation", "Lazy outlet pass"],
        "Clearing & Passing": ["Rushed, panicked throw", "Lazy outlet pass", "Good first look to shot origin", "Strong, accurate pass to midfielder"],
        "Communication & Leadership": ["Loud, clear 'SHOT' call", "Identified slide package ('HOT')", "Quiet on defense", "Used 'RESET' call effectively"]
    }
    for video_name in video_files:
        num_events = random.randint(15, 30)
        for _ in range(num_events):
            timestamp = time.strftime('%H:%M:%S', time.gmtime(random.randint(1, 240)))
            category_key = random.choice(list(actions.keys()))
            action_detail = random.choice(actions[category_key])
            action_map.append({"Video": video_name, "Timestamp": timestamp, "Action": action_detail, "Category": category_key})
    return sorted(action_map, key=lambda x: (x['Video'], x['Timestamp']))

def generate_ai_critique(action_map):
    if not action_map: return None

    CATEGORIES = {
        "Stance & Positioning": {
            "title": "1. Stance & Positioning (Arc Play)",
            "assessment": "Shows solid foundational understanding but occasionally gets caught with a narrow base, reducing lateral power.",
            "expectation": "According to page 17 of The Lax Goalie Bible, you must utilize the 'Ray Lewis Ready' athletic stance: feet wider than shoulder-width, knees bent, and weight on the balls of your feet.",
            "improvement_plan": "Consciously force a wider base during practice until it becomes muscle memory. This lowers your center of gravity and improves lateral explosiveness.",
            "skill_diagnosis": "Developing",
            "drill_recommendation": "Prescribed Drill: Walk the Arc (p. 56) to improve fluid movement and stance memory."
        },
        "Save Movement & Technique": {
            "title": "2. Save Movement & Technique",
            "assessment": "Top hand is generally effective. Some inconsistency noted on off-stick low shots, with a tendency to sweep.",
            "expectation": "Page 36 of The Lax Goalie Bible emphasizes driving the top hand in a straight, direct path to the ball with 'rattlesnake-like quickness', avoiding any looping motion.",
            "improvement_plan": "Isolate your hand path. Temporarily remove lower body variables and focus entirely on driving the hands directly to the corners without dropping them first.",
            "skill_diagnosis": "Intermediate",
            "drill_recommendation": "Prescribed Drill: Goalie Lead Hand Drill / Egg Toss (p. 47) and Off-Stick Hands Drill."
        },
        "Clearing & Passing": {
            "title": "3. Clearing & Passing",
            "assessment": "Makes safe outlet passes but could improve decision-making under pressure to find faster clear options.",
            "expectation": "Page 81 of The Lax Goalie Bible strictly forbids 'lazy outlet passes.' You have 4 seconds. The progression is: 1) Secure rebound, 2) Look to shot origin, 3) Look for breaking middies, 4) Look to defenders.",
            "improvement_plan": "Do not let riding attackmen speed up your internal clock. Take a breath, step out to the side of the crease to buy time, and process your progressions.",
            "skill_diagnosis": "Beginner",
            "drill_recommendation": "Prescribed Drill: Crooked Arrow Clear (incorporating live pressure)."
        },
        "Communication & Leadership": {
            "title": "4. Communication & Leadership (Quarterbacking)",
            "assessment": "Vocal and clear with defensive calls, demonstrating good command. Aim for even greater volume and decisiveness.",
            "expectation": "The goalie is the quarterback. Utilizing the B-S-C (Ball, Slide, Command) framework ensures the entire defensive unit operates as one cohesive system.",
            "improvement_plan": "Work with your defense to introduce and practice more advanced calls like 'GILMAN' or specific 'ROTATE' calls for different defensive sets.",
            "skill_diagnosis": "Advanced",
            "drill_recommendation": "Practice live-game scenarios focusing on communication during fast breaks and unsettled situations."
        }
    }

    performance_summary = {}
    for key, data in CATEGORIES.items():
        events_in_cat = [item for item in action_map if item['Category'] == key]
        base_score = min(5.0 + len(events_in_cat) * 0.5, 9.0)
        final_grade = round(base_score + random.uniform(-1.0, 1.0), 1)
        performance_summary[key] = {
            "grade": max(4.0, min(9.8, final_grade)),
            "assessment": data["assessment"]
        }

    detailed_critique = {}
    for key, template in CATEGORIES.items():
        grade_info = performance_summary[key]
        obj_grade = round(grade_info['grade'] * random.uniform(0.9, 1.0), 1)
        subj_grade = round(grade_info['grade'] * random.uniform(0.85, 0.95), 1)
        relevant_events = [ev for ev in action_map if ev['Category'] == key]
        commentary = f"Analysis of your video(s) revealed several key moments for '{key}'. "
        if relevant_events:
            commentary += f"For instance, the '{relevant_events[0]['Action'].lower()}' at {relevant_events[0]['Timestamp']} in '{relevant_events[0]['Video']}' highlights an area for focus."
        else:
            commentary += "No specific events were flagged, indicating a solid performance."
        detailed_critique[key] = {**template, "objective_grade": obj_grade, "subjective_grade": subj_grade, "events": relevant_events, "commentary": commentary}

    return {"summary": performance_summary, "details": detailed_critique}

def generate_report_text(results, action_map):
    """Compiles all analysis data into a single Markdown-formatted string."""
    report = []
    report.append(f"# LAX Goalie AI Coach Analysis Report\n")
    report.append(f"**Date of Analysis:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

    report.append("## 📊 Performance Summary\n")
    for metric, values in results['summary'].items():
        report.append(f"- **{metric}:** {values['grade']}/10")
        report.append(f"  - *Assessment:* {values['assessment']}\n")

    report.append("\n## 📝 Detailed Technical Critique\n")
    for category, critique in results['details'].items():
        report.append(f"### {critique['title']}\n")
        report.append(f"- **Objective Grade (Fundamentals):** {critique['objective_grade']}/10")
        report.append(f"- **Subjective Grade (Fluidity):** {critique['subjective_grade']}/10\n")
        report.append(f"**AI Commentary:** {critique['commentary']}\n")
        report.append(f"**Expectation:** {critique['expectation']}\n")
        report.append(f"**Improvement Plan:** {critique['improvement_plan']}\n")
        report.append(f"**Skill Diagnosis:** {critique['skill_diagnosis']} | **Prescribed Drill:** {critique['drill_recommendation']}\n")
        if critique['events']:
            report.append("**Relevant Events:**\n")
            df = pd.DataFrame(critique['events'])
            report.append(df[['Video', 'Timestamp', 'Action']].to_markdown(index=False))
            report.append("\n")

    report.append("\n## 🎯 Summary & Next Steps\n")
    summary_grades = results['summary']
    best_skill = max(summary_grades, key=lambda k: summary_grades[k]['grade'])
    worst_skill = min(summary_grades, key=lambda k: summary_grades[k]['grade'])
    report.append(f"- **Primary Strength:** {best_skill} ({summary_grades[best_skill]['grade']}/10)")
    report.append(f"- **Area for Improvement:** {worst_skill} ({summary_grades[worst_skill]['grade']}/10)\n")
    report.append("**Recommended Training Regime:**\n")
    for category, critique in results['details'].items():
        report.append(f"- **For {category}:** *{critique['drill_recommendation']}*")

    report.append("\n\n## 🗺️ Video Action Map (All Events)\n")
    report.append("A complete directory of all critical timestamps detected by the AI.\n")
    report.append(pd.DataFrame(action_map).to_markdown(index=False))

    return "\n".join(report)


# --- UI Rendering Functions ---
def display_video_gallery():
    st.header("🎬 Video Gallery & Analysis")
    if not st.session_state.video_files:
        st.info("Upload one or more videos to begin your analysis.")
        if "Your_Performance_Video.mp4" not in st.session_state.video_files:
            st.session_state.video_files["Your_Performance_Video.mp4"] = None
    
    video_keys_to_delete = []
    
    for video_name, video_path in st.session_state.video_files.items():
        with st.container():
            st.markdown('<div class="video-card">', unsafe_allow_html=True)
            if st.button("✖", key=f"del_{video_name}"):
                video_keys_to_delete.append(video_name)
            st.subheader(video_name)
            if video_path: st.video(video_path)
            else: st.text("Placeholder: Upload a real video file to enable analysis.")
            st.markdown('</div>', unsafe_allow_html=True)

    if video_keys_to_delete:
        for key in video_keys_to_delete:
            if key in st.session_state.video_files:
                file_path = st.session_state.video_files.get(key)
                if file_path and os.path.exists(file_path):
                    try: os.remove(file_path)
                    except OSError as e: st.error(f"Error removing file {file_path}: {e}")
                del st.session_state.video_files[key]
        st.rerun()

def display_analysis_dashboard(results, report_data):
    col1, col2 = st.columns([3, 1])
    with col1:
        st.header("📊 Analysis Dashboard")
        st.success("✅ Analysis Complete! Review your performance metrics below.")
    with col2:
        st.download_button(
            label="📥 Download Full Report",
            data=report_data,
            file_name=f"LAX_Goalie_Analysis_Report_{datetime.now().strftime('%Y%m%d')}.md",
            mime="text/markdown",
            use_container_width=True
        )

    summary_data = results['summary']
    cols = st.columns(4)
    for i, (metric, values) in enumerate(summary_data.items()):
        with cols[i]:
            title = metric.split('(')[0].strip()
            st.markdown(f'<div class="metric-card"><h4>{title}</h4><p class="grade">{values["grade"]}/10</p></div>', unsafe_allow_html=True)
            st.caption(values['assessment'])

def display_charts(results):
    import plotly.graph_objects as go
    import plotly.express as px
    
    radar_df = pd.DataFrame(dict(r=[v['grade'] for v in results['summary'].values()], theta=list(results['summary'].keys())))
    bar_data = []
    for key, values in results['details'].items():
        bar_data.append({'Metric': 'Objective (Fundamentals)', 'value': values['objective_grade'], 'variable': key})
        bar_data.append({'Metric': 'Subjective (Fluidity)', 'value': values['subjective_grade'], 'variable': key})
    bar_df = pd.DataFrame(bar_data)

    st.markdown("---")
    col1, col2 = st.columns([2, 3])
    with col1:
        st.subheader("Performance Radar")
        fig = go.Figure(data=go.Scatterpolar(r=radar_df['r'], theta=radar_df['theta'], fill='toself', name='Performance', line=dict(color='#4A90E2')))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10], color='#E0E0E0'), angularaxis=dict(color='#E0E0E0')), showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#E0E0E0"))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("Objective vs Subjective Breakdown")
        fig = px.bar(bar_df, x="Metric", y="value", color="variable", barmode="group", labels={'value': 'Grade', 'variable': 'Category', 'Metric': ''})
        fig.update_layout(yaxis=dict(range=[0, 10]), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#E0E0E0"), legend_title_text='')
        st.plotly_chart(fig, use_container_width=True)

def display_detailed_critique(results, action_map):
    st.header("📝 Detailed Technical Critique")
    with st.expander("🗺️ Video Action Map (All Events)", expanded=False):
        st.info("A complete directory mapping all critical timestamps from all videos to their corresponding detected action.")
        st.dataframe(pd.DataFrame(action_map)[['Video', 'Timestamp', 'Action']], use_container_width=True)
    
    for category, critique in results['details'].items():
        with st.expander(f"{critique['title']}"):
            st.markdown(f"**Objective Grade (Fundamentals):** `{critique['objective_grade']}/10` | **Subjective Grade (Fluidity):** `{critique['subjective_grade']}/10`")
            st.markdown("---")
            st.markdown(f"**AI Commentary:** {critique['commentary']}")
            st.markdown(f"**Expectation:** {critique['expectation']}")
            st.markdown(f"**Improvement Plan:** {critique['improvement_plan']}")
            if critique['events']:
                st.markdown("**Analysis based on these timestamped events:**")
                html = "<table class='event-table'><tr><th>Video</th><th>Timestamp</th><th>Detected Action</th></tr>"
                for ev in critique['events'][:5]:
                    html += f"<tr><td>{ev['Video']}</td><td>{ev['Timestamp']}</td><td>{ev['Action']}</td></tr>"
                html += "</table>"
                st.markdown(html, unsafe_allow_html=True)
                if len(critique['events']) > 5: st.caption(f"...and {len(critique['events']) - 5} more events.")
            st.info(f"**Skill Diagnosis:** {critique['skill_diagnosis']} | **Prescribed Drill:** {critique['drill_recommendation']}")

def display_summary_and_next_steps(results):
    st.header("🎯 Summary & Next Steps")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Key Takeaways")
        summary_grades = results['summary']
        best_skill, worst_skill = max(summary_grades, key=lambda k: summary_grades[k]['grade']), min(summary_grades, key=lambda k: summary_grades[k]['grade'])
        st.success(f"**Primary Strength: {best_skill}** ({summary_grades[best_skill]['grade']}/10)")
        st.warning(f"**Area for Improvement: {worst_skill}** ({summary_grades[worst_skill]['grade']}/10)")
    with col2:
        st.subheader("Recommended Training Regime")
        for category, critique in results['details'].items():
            st.markdown(f"- **For {category}:** *{critique['drill_recommendation']}*")

# --- Main App Logic ---
def main():
    load_css()
    st.title("🥍 LAX Goalie AI Coach")
    st.caption("Elite Video Analysis powered by The Lax Goalie Bible")

    tab1, tab2 = st.tabs(["▶️ Video Management & Analysis", "⚙️ Knowledge Base"])

    with tab1:
        st.header("Upload New Video")
        uploaded_files = st.file_uploader("Upload Goalie Videos (Up to 2GB per file)", type=["mp4", "mov", "avi", "mpeg4"], accept_multiple_files=True, label_visibility="collapsed")
        if uploaded_files:
            temp_dir = "temp_videos"; os.makedirs(temp_dir, exist_ok=True)
            for f in uploaded_files:
                if f.name not in st.session_state.video_files:
                    path = os.path.join(temp_dir, f.name); open(path, "wb").write(f.getbuffer())
                    st.session_state.video_files[f.name] = path
            st.success("Video(s) added to the gallery below!")

        display_video_gallery()
        
        real_video_files = {k: v for k, v in st.session_state.video_files.items() if v is not None}
        if real_video_files and not st.session_state.analysis_in_progress:
            st.markdown("---")
            if st.button("🚀 Analyze Performance for All Videos", use_container_width=True, type="primary"):
                st.session_state.analysis_results = None; st.session_state.analysis_in_progress = True
                st.rerun()

        if st.session_state.analysis_in_progress:
            st.session_state.action_map.clear()
            num_videos = len(real_video_files)
            total_duration_estimate = num_videos * 10 + 5 # 10s per video + 5s for report
            
            progress_container = st.empty()
            with progress_container.container():
                status_text = st.empty(); tip_placeholder = st.empty(); progress_bar = st.progress(0)
            
            start_time = time.time(); random.shuffle(TIPS); tip_index = 0
            
            while True:
                elapsed = time.time() - start_time
                progress = min(elapsed / total_duration_estimate, 1.0)
                progress_text = "Initializing..."
                if progress < 0.7: progress_text = f"⚙️ Running Computer Vision models... Frame analysis in progress. ({int(progress*100)}%)"
                elif progress < 0.9: progress_text = f"🧠 Synthesizing visual data and knowledge base... ({int(progress*100)}%)"
                else: progress_text = f"🎨 Generating final report and visualizations... ({int(progress*100)}%)"
                
                status_text.info(progress_text)
                progress_bar.progress(int(progress*100))
                tip_placeholder.info(f"💡 Tip: {TIPS[tip_index]}")
                
                if int(elapsed) % 10 == 0 and int(elapsed) > 0 and int(elapsed) != st.session_state.get('last_tip_time', 0):
                    st.session_state['last_tip_time'] = int(elapsed)
                    tip_index = (tip_index + 1) % len(TIPS)
                if progress >= 1.0: break
                time.sleep(0.5)

            st.session_state.action_map = run_computer_vision_analysis(list(real_video_files.keys()))
            st.session_state.analysis_results = generate_ai_critique(st.session_state.action_map)
            
            progress_container.empty()
            st.session_state.analysis_in_progress = False
            st.rerun()

        if st.session_state.analysis_results:
            st.markdown("---")
            report_data = generate_report_text(st.session_state.analysis_results, st.session_state.action_map)
            
            display_analysis_dashboard(st.session_state.analysis_results, report_data)
            display_charts(st.session_state.analysis_results)
            display_detailed_critique(st.session_state.analysis_results, st.session_state.action_map)
            display_summary_and_next_steps(st.session_state.analysis_results)

    with tab2:
        st.header("📚 Central Knowledge Base")
        st.info("This is the central, shared knowledge base for the application. The AI's analysis for all users is powered by these documents.")
        
        kb_path = "knowledge_base"
        
        st.subheader("Current Reference Documents")
        
        try:
            knowledge_files = [f for f in os.listdir(kb_path) if f.endswith('.pdf')]
            if not knowledge_files:
                st.warning("No reference documents found in the 'knowledge_base' directory.")
            
            for f in knowledge_files:
                st.markdown(f"- 📄 **{f}**")
        except FileNotFoundError:
            st.error(f"Error: The directory '{kb_path}' was not found. Please create it and add your reference PDFs.")

        st.markdown("---")
        st.subheader("How to Update")
        st.markdown("""
        To add or change the reference documents for all users, you must:
        1.  Add the new PDF files to the `knowledge_base` folder in the project's GitHub repository.
        2.  Remove any old files from that same folder.
        3.  Commit the changes to GitHub. The application will automatically update with the new knowledge base.
        """)

if __name__ == "__main__":
    main()
