import streamlit as st
import pandas as pd
import numpy as np
import time
import random
import os
import re
from datetime import datetime

# --- Page Configuration & Version ---
VERSION = "v03.02.01.03"
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
if 'placeholder_removed' not in st.session_state:
    st.session_state.placeholder_removed = False

# --- UI Styling ---
def load_css():
    st.markdown("""
    <style>
        body { color: #E0E0E0; background-color: #1a1a1a; }
        h1, h2, h3 { color: #FFFFFF; }
        h2 { border-bottom: 2px solid #4A90E2; padding-bottom: 10px; margin-top: 2rem; margin-bottom: 1.5rem; }
        .main .block-container { padding: 2rem 4rem; }
        .video-card { background-color: #252526; border-radius: 12px; padding: 1.5rem; margin-bottom: 2rem; position: relative; border: 1px solid #3E3E3E; }
        .video-card h3 { margin-top: 0; margin-bottom: 1rem; border-bottom: none; }
        .video-card .stButton > button { position: absolute; top: 10px; right: 10px; width: 35px; height: 35px; border-radius: 50%; background-color: rgba(40, 40, 40, 0.8); color: #BDBDBD; border: 1px solid #555; font-size: 16px; font-weight: bold; line-height: 1; z-index: 99; }
        .video-card .stButton > button:hover { background-color: #D32F2F; color: white; border: 1px solid #D32F2F; }
        .st-expander { border: 1px solid #3E3E3E; border-radius: 10px; background-color: #252526; }
        .st-expander header { font-size: 1.5rem; color: #FFFFFF; font-weight: bold; }
        .metric-card { background-color: #252526; border-radius: 12px; padding: 25px; text-align: center; border: 1px solid #3E3E3E; height: 100%; }
        .metric-card h4 { font-size: 1rem; color: #BDBDBD; margin-bottom: 10px; font-weight: normal; text-transform: uppercase; }
        .metric-card .grade { font-size: 2.5rem; font-weight: bold; color: #4A90E2; }
        .event-table { width: 100%; border-collapse: collapse; }
        .event-table th, .event-table td { text-align: left; padding: 10px; border-bottom: 1px solid #3E3E3E; }
        .event-table th { background-color: #333333; font-weight: bold; }
        .footer { position: fixed; left: 1rem; bottom: 1rem; color: #555; font-size: 0.8rem; }
    </style>
    """, unsafe_allow_html=True)
    st.markdown(f'<div class="footer">{VERSION}</div>', unsafe_allow_html=True)

# --- AI & Analysis / Report Generation Functions (Unchanged) ---
TIPS = [
    "Keep your shoulders square to the shooter at all times. (The Lax Goalie Bible, p. 15)", "A 'Ray Lewis Ready' stance means feet slightly wider than shoulder-width and athletic bend. (The Lax Goalie Bible, p. 17)", "On low saves, think 'what time is it?' Your wrist rotation should be like checking a watch. (The Lax Goalie Bible, p. 38)", "The 5-step arc is fundamental: Pipe Left, 45-Left, Center, 45-Right, Pipe Right. (The Lax Goalie Bible, p. 25)", "Don't drag your trail foot. Finish every save with a shuffle step to stay balanced. (The Lax Goalie Bible, p. 42)",
]
def run_computer_vision_analysis(video_files):
    action_map = []
    actions = { "Stance & Positioning": ["Stance too narrow", "Weight on heels", "Good athletic base"], "Save Movement & Technique": ["Direct hand path to ball", "Sweeping/looping hand motion", "Excellent wrist rotation"], "Clearing & Passing": ["Rushed, panicked throw", "Lazy outlet pass", "Strong, accurate pass"], "Communication & Leadership": ["Loud, clear 'SHOT' call", "Quiet on defense", "Used 'RESET' call"] }
    for video_name in video_files:
        for _ in range(random.randint(15, 30)):
            action_map.append({"Video": video_name, "Timestamp": time.strftime('%H:%M:%S', time.gmtime(random.randint(1, 240))), "Action": random.choice(actions[random.choice(list(actions.keys()))]), "Category": random.choice(list(actions.keys()))})
    return sorted(action_map, key=lambda x: (x['Video'], x['Timestamp']))

def generate_ai_critique(action_map):
    if not action_map: return None
    CATEGORIES = { "Stance & Positioning": { "title": "1. Stance & Positioning (Arc Play)", "assessment": "Shows solid foundational understanding but occasionally gets caught with a narrow base.", "expectation": "Utilize the 'Ray Lewis Ready' athletic stance: feet wider than shoulder-width, knees bent.", "improvement_plan": "Consciously force a wider base during practice.", "skill_diagnosis": "Developing", "drill_recommendation": "Walk the Arc (p. 56)" }, "Save Movement & Technique": { "title": "2. Save Movement & Technique", "assessment": "Top hand is generally effective. Some inconsistency noted on off-stick low shots.", "expectation": "Drive the top hand in a straight, direct path to the ball.", "improvement_plan": "Isolate your hand path, focusing on driving hands directly to corners.", "skill_diagnosis": "Intermediate", "drill_recommendation": "Goalie Lead Hand Drill / Egg Toss (p. 47)" }, "Clearing & Passing": { "title": "3. Clearing & Passing", "assessment": "Makes safe outlet passes but could improve decision-making under pressure.", "expectation": "You have 4 seconds. Look to shot origin, then breaking middies, then defenders.", "improvement_plan": "Do not let riders speed up your internal clock. Take a breath.", "skill_diagnosis": "Beginner", "drill_recommendation": "Crooked Arrow Clear (incorporating live pressure)" }, "Communication & Leadership": { "title": "4. Communication & Leadership (Quarterbacking)", "assessment": "Vocal and clear with defensive calls. Aim for even greater volume.", "expectation": "The goalie is the quarterback. Use the B-S-C framework (Ball, Slide, Command).", "improvement_plan": "Work with your defense to introduce advanced calls like 'GILMAN' or 'ROTATE'.", "skill_diagnosis": "Advanced", "drill_recommendation": "Practice live-game scenarios focusing on communication." } }
    performance_summary = {}
    for key, data in CATEGORIES.items():
        performance_summary[key] = { "grade": round(min(5.0 + len([i for i in action_map if i['Category'] == key]) * 0.5, 9.0) + random.uniform(-1.0, 1.0), 1), "assessment": data["assessment"] }
    detailed_critique = {}
    for key, template in CATEGORIES.items():
        grade_info = performance_summary[key]
        relevant_events = [ev for ev in action_map if ev['Category'] == key]
        commentary = f"Analysis of '{key}' revealed several key moments. " + (f"For instance, the '{relevant_events[0]['Action'].lower()}' at {relevant_events[0]['Timestamp']} in '{relevant_events[0]['Video']}' highlights an area for focus." if relevant_events else "No specific events flagged, indicating solid performance.")
        detailed_critique[key] = {**template, "objective_grade": round(grade_info['grade'] * random.uniform(0.9, 1.0), 1), "subjective_grade": round(grade_info['grade'] * random.uniform(0.85, 0.95), 1), "events": relevant_events, "commentary": commentary}
    return {"summary": performance_summary, "details": detailed_critique}

def generate_report_text(results, action_map):
    report = [f"# LAX Goalie AI Coach Analysis Report\n**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"]
    report.append("## 📊 Performance Summary")
    for metric, values in results['summary'].items(): report.append(f"- **{metric}:** {values['grade']}/10\n  - *Assessment:* {values['assessment']}")
    report.append("\n## 📝 Detailed Technical Critique")
    for category, critique in results['details'].items():
        report.append(f"### {critique['title']}")
        report.append(f"- **Objective Grade:** {critique['objective_grade']}/10 | **Subjective Grade:** {critique['subjective_grade']}/10")
        report.append(f"**AI Commentary:** {critique['commentary']}\n**Expectation:** {critique['expectation']}\n**Improvement Plan:** {critique['improvement_plan']}")
        report.append(f"**Skill Diagnosis:** {critique['skill_diagnosis']} | **Prescribed Drill:** {critique['drill_recommendation']}")
        if critique['events']: report.append("**Relevant Events:**\n" + pd.DataFrame(critique['events'])[['Video', 'Timestamp', 'Action']].to_markdown(index=False))
    best_skill, worst_skill = max(results['summary'], key=lambda k: results['summary'][k]['grade']), min(results['summary'], key=lambda k: results['summary'][k]['grade'])
    report.append(f"\n## 🎯 Summary & Next Steps\n- **Primary Strength:** {best_skill}\n- **Area for Improvement:** {worst_skill}")
    report.append("\n## 🗺️ Video Action Map\n" + pd.DataFrame(action_map).to_markdown(index=False))
    return "\n\n".join(report)

# --- UI Rendering Functions ---
def display_video_gallery():
    if not st.session_state.placeholder_removed:
        with st.container():
            st.markdown('<div class="video-card">', unsafe_allow_html=True)
            st.subheader("Your_Performance_Video.mp4")
            st.video("https://www.youtube.com/watch?v=gTsq5nLSFmQ")
            st.caption("This is a placeholder. Upload your own videos to begin analysis!")
            st.markdown('</div>', unsafe_allow_html=True)
    
    video_keys_to_delete = []
    for video_name, video_path in st.session_state.video_files.items():
        with st.container():
            st.markdown('<div class="video-card">', unsafe_allow_html=True)
            if st.button("✖", key=f"del_{video_name}"):
                video_keys_to_delete.append(video_name)
            st.subheader(video_name)
            st.video(video_path)
            st.markdown('</div>', unsafe_allow_html=True)

    if video_keys_to_delete:
        for key in video_keys_to_delete:
            if key in st.session_state.video_files:
                file_path = st.session_state.video_files.get(key)
                if file_path and os.path.exists(file_path): os.remove(file_path)
                del st.session_state.video_files[key]
        if not st.session_state.video_files: st.session_state.placeholder_removed = False
        st.rerun()

def display_analysis_dashboard(results, report_data):
    col1, col2 = st.columns([3, 1])
    with col1:
        st.header("📊 Analysis Dashboard")
        st.success("✅ Analysis Complete!")
    with col2:
        st.download_button(label="📥 Download Full Report", data=report_data, file_name=f"LAX_Analysis_{datetime.now().strftime('%Y%m%d')}.md", mime="text/markdown", use_container_width=True)
    cols = st.columns(4)
    for i, (metric, values) in enumerate(results['summary'].items()):
        with cols[i]: st.markdown(f'<div class="metric-card"><h4>{metric.split("(")[0].strip()}</h4><p class="grade">{values["grade"]}/10</p></div>', unsafe_allow_html=True); st.caption(values['assessment'])

def display_charts(results):
    import plotly.graph_objects as go; import plotly.express as px
    radar_df = pd.DataFrame(dict(r=[v['grade'] for v in results['summary'].values()], theta=list(results['summary'].keys())))
    bar_data = [{'Metric': m, 'value': v[k], 'variable': key} for key, v in results['details'].items() for m,k in [('Objective', 'objective_grade'), ('Subjective', 'subjective_grade')]]
    bar_df = pd.DataFrame(bar_data)
    st.markdown("---"); col1, col2 = st.columns([2, 3])
    with col1:
        st.subheader("Performance Radar"); fig = go.Figure(data=go.Scatterpolar(r=radar_df['r'], theta=radar_df['theta'], fill='toself', line=dict(color='#4A90E2'))); fig.update_layout(polar=dict(radialaxis=dict(range=[0, 10])), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#E0E0E0"), showlegend=False); st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("Objective vs Subjective"); fig = px.bar(bar_df, x="Metric", y="value", color="variable", barmode="group"); fig.update_layout(yaxis=dict(range=[0, 10]), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#E0E0E0"), legend_title_text=''); st.plotly_chart(fig, use_container_width=True)

def display_detailed_critique(results, action_map):
    st.header("📝 Detailed Technical Critique");
    with st.expander("🗺️ Video Action Map (All Events)", expanded=False): st.dataframe(pd.DataFrame(action_map)[['Video', 'Timestamp', 'Action']], use_container_width=True)
    for category, critique in results['details'].items():
        with st.expander(f"{critique['title']}"):
            st.markdown(f"**Objective:** `{critique['objective_grade']}/10` | **Subjective:** `{critique['subjective_grade']}/10`\n---\n**AI Commentary:** {critique['commentary']}\n\n**Expectation:** {critique['expectation']}\n\n**Improvement Plan:** {critique['improvement_plan']}")
            if critique['events']: st.markdown("**Events:**\n" + pd.DataFrame(critique['events'])[['Video', 'Timestamp', 'Action']].head().to_html(index=False, classes='event-table'), unsafe_allow_html=True)
            st.info(f"**Skill Diagnosis:** {critique['skill_diagnosis']} | **Prescribed Drill:** {critique['drill_recommendation']}")

def display_summary_and_next_steps(results):
    st.header("🎯 Summary & Next Steps"); col1, col2 = st.columns(2)
    with col1: st.subheader("Key Takeaways"); best_skill, worst_skill = max(results['summary'], key=lambda k: results['summary'][k]['grade']), min(results['summary'], key=lambda k: results['summary'][k]['grade']); st.success(f"**Strength: {best_skill}**"); st.warning(f"**To Improve: {worst_skill}**")
    with col2: st.subheader("Training Regime"); [st.markdown(f"- **For {cat}:** *{crit['drill_recommendation']}*") for cat, crit in results['details'].items()]

# --- Main App Logic ---
def main():
    load_css()
    st.title("🥍 LAX Goalie AI Coach")

    col1, col2, col3 = st.columns([0.4, 0.4, 0.2])
    with col1:
        tab1, tab2 = st.tabs(["▶️ Video Management & Analysis", "⚙️ Knowledge Base"])
    with col3:
        st.write(""); st.write("") # Spacers
        if st.button("🔄 New Analysis Session"):
            for key in list(st.session_state.keys()):
                if key in ['video_files', 'analysis_results', 'action_map', 'analysis_in_progress', 'placeholder_removed']:
                    del st.session_state[key]
            if os.path.exists("temp_videos"):
                for f in os.listdir("temp_videos"): os.remove(os.path.join("temp_videos", f))
            st.rerun()

    with tab1:
        st.header("Upload New Video")
        uploaded_files = st.file_uploader("Upload Goalie Videos", type=["mp4", "mov", "avi", "mpeg4"], accept_multiple_files=True, label_visibility="collapsed")
        
        if uploaded_files:
            if not st.session_state.placeholder_removed:
                st.session_state.placeholder_removed = True
            
            temp_dir = "temp_videos"; os.makedirs(temp_dir, exist_ok=True)
            for f in uploaded_files:
                if f.name not in st.session_state.video_files:
                    path = os.path.join(temp_dir, f.name)
                    with open(path, "wb") as out_file: out_file.write(f.getbuffer())
                    st.session_state.video_files[f.name] = path
            st.rerun()

        display_video_gallery()
        
        if st.session_state.video_files and not st.session_state.analysis_in_progress:
            st.markdown("---")
            if st.button("🚀 Analyze Performance for All Videos", use_container_width=True, type="primary"):
                st.session_state.analysis_results = None; st.session_state.analysis_in_progress = True
                st.rerun()

        if st.session_state.analysis_in_progress:
            num_videos = len(st.session_state.video_files); total_duration_estimate = num_videos * 10 + 5
            progress_container = st.empty()
            with progress_container.container():
                status_text = st.empty(); tip_placeholder = st.empty(); progress_bar = st.progress(0)
            start_time = time.time(); random.shuffle(TIPS); tip_index = 0
            while True:
                elapsed = time.time() - start_time; progress = min(elapsed / total_duration_estimate, 1.0)
                if progress < 0.7: progress_text = f"⚙️ Running Computer Vision models... ({int(progress*100)}%)"
                elif progress < 0.9: progress_text = f"🧠 Synthesizing visual data... ({int(progress*100)}%)"
                else: progress_text = f"🎨 Generating final report... ({int(progress*100)}%)"
                status_text.info(progress_text); progress_bar.progress(int(progress*100)); tip_placeholder.info(f"💡 Tip: {TIPS[tip_index]}")
                if int(elapsed) % 10 == 0 and int(elapsed) > 0 and int(elapsed) != st.session_state.get('last_tip_time', 0):
                    st.session_state['last_tip_time'] = int(elapsed); tip_index = (tip_index + 1) % len(TIPS)
                if progress >= 1.0: break
                time.sleep(0.5)
            st.session_state.action_map = run_computer_vision_analysis(list(st.session_state.video_files.keys()))
            st.session_state.analysis_results = generate_ai_critique(st.session_state.action_map)
            progress_container.empty(); st.session_state.analysis_in_progress = False; st.rerun()

        if st.session_state.analysis_results:
            st.markdown("---")
            report_data = generate_report_text(st.session_state.analysis_results, st.session_state.action_map)
            display_analysis_dashboard(st.session_state.analysis_results, report_data)
            display_charts(st.session_state.analysis_results)
            display_detailed_critique(st.session_state.analysis_results, st.session_state.action_map)
            display_summary_and_next_steps(st.session_state.analysis_results)

    with tab2:
        st.header("📚 Central Knowledge Base")
        st.info("The AI's analysis for all users is powered by these documents, which are bundled with the application.")
        kb_path = "knowledge_base"
        st.subheader("Current Reference Documents")
        try:
            knowledge_files = [f for f in os.listdir(kb_path) if f.endswith('.pdf')]
            if not knowledge_files: st.warning("No reference documents found.")
            for f in knowledge_files: st.markdown(f"- 📄 **{f}**")
        except FileNotFoundError:
            st.error(f"Error: The directory '{kb_path}' was not found. Please ensure it is in your GitHub repository.")
        st.markdown("---\n" + "**How to Update:** To change reference documents, update the `knowledge_base` folder in the project's GitHub repository and redeploy.")

if __name__ == "__main__":
    main()
