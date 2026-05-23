import streamlit as st
import pandas as pd
import numpy as np
import os
import json
import requests
import joblib
import time
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity

# Set Page Config
st.set_page_config(
    page_title="RAG AI Teaching Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom Fonts & Styling (Glassmorphism, Neon Cyan, Modern Dark Slate)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Main Background & Fonts */
    .stApp {
        background-color: #0B0F19;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #E2E8F0;
    }
    
    /* Custom Title Style */
    .app-title {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        font-size: 3rem;
        background: linear-gradient(135deg, #FFFFFF 30%, #0EA5E9 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        letter-spacing: -0.05em;
    }
    
    .app-subtitle {
        color: #94A3B8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Glassmorphic Side Bar */
    [data-testid="stSidebar"] {
        background-color: #0F172A;
        border-right: 1px solid #1E293B;
    }
    
    /* Beautiful Widgets & Metric Cards */
    div[data-testid="metric-container"] {
        background: rgba(15, 23, 42, 0.6);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(14, 165, 233, 0.2);
        padding: 1.25rem;
        border-radius: 16px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.4);
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-4px);
        border-color: rgba(14, 165, 233, 0.6);
        box-shadow: 0 10px 30px rgba(14, 165, 233, 0.1);
    }
    
    /* Custom Glassmorphic Card class */
    .glass-card {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(226, 232, 240, 0.08);
        padding: 1.5rem;
        border-radius: 20px;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    
    .glass-card-cyan {
        background: rgba(14, 165, 233, 0.03);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(14, 165, 233, 0.15);
        padding: 1.5rem;
        border-radius: 20px;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    
    /* Interactive Citation Box */
    .citation-card {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid #1E293B;
        border-left: 4px solid #0EA5E9;
        padding: 1rem 1.2rem;
        border-radius: 12px;
        margin-top: 0.75rem;
        margin-bottom: 0.75rem;
        transition: all 0.2s ease;
    }
    
    .citation-card:hover {
        border-color: #0EA5E9;
        background: rgba(15, 23, 42, 0.95);
        box-shadow: 0 5px 15px rgba(14, 165, 233, 0.15);
        transform: translateX(4px);
    }
    
    .citation-header {
        font-weight: 700;
        color: #F8FAFC;
        font-size: 0.95rem;
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.4rem;
    }
    
    .citation-tag {
        background: rgba(14, 165, 233, 0.15);
        color: #38BDF8;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    
    .citation-text {
        font-style: italic;
        color: #94A3B8;
        font-size: 0.88rem;
        line-height: 1.4;
    }
    
    /* Pulse Animation for Online Health Status */
    .pulse-green {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #10B981;
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
        animation: pulse-green-anim 1.5s infinite;
        vertical-align: middle;
        margin-right: 8px;
    }
    @keyframes pulse-green-anim {
        0% {
            transform: scale(0.95);
            box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
        }
        70% {
            transform: scale(1);
            box-shadow: 0 0 0 8px rgba(16, 185, 129, 0);
        }
        100% {
            transform: scale(0.95);
            box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
        }
    }
    
    .pulse-red {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #EF4444;
        box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
        animation: pulse-red-anim 1.5s infinite;
        vertical-align: middle;
        margin-right: 8px;
    }
    @keyframes pulse-red-anim {
        0% {
            transform: scale(0.95);
            box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
        }
        70% {
            transform: scale(1);
            box-shadow: 0 0 0 8px rgba(239, 68, 68, 0);
        }
        100% {
            transform: scale(0.95);
            box-shadow: 0 0 0 0 rgba(239, 68, 68, 0);
        }
    }
    
    /* Sleek Chat bubbles styling */
    .chat-bubble-user {
        background: #1E293B;
        border: 1px solid rgba(226, 232, 240, 0.06);
        padding: 1rem 1.25rem;
        border-radius: 16px 16px 4px 16px;
        color: #F1F5F9;
        margin-bottom: 1rem;
        max-width: 85%;
        margin-left: auto;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
    }
    
    .chat-bubble-assistant {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.8) 100%);
        border: 1px solid rgba(14, 165, 233, 0.15);
        padding: 1.25rem 1.5rem;
        border-radius: 16px 16px 16px 4px;
        color: #F8FAFC;
        margin-bottom: 1rem;
        max-width: 85%;
        margin-right: auto;
        box-shadow: 0 6px 20px rgba(14, 165, 233, 0.05);
    }

    /* Tabs Styling override */
    button[data-baseweb="tab"] {
        font-family: 'Inter', sans-serif !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        color: #94A3B8 !important;
        border-bottom-width: 2px !important;
        border-bottom-color: transparent !important;
        transition: all 0.25s ease !important;
    }
    button[aria-selected="true"] {
        color: #0EA5E9 !important;
        border-bottom-color: #0EA5E9 !important;
    }
    button[data-baseweb="tab"]:hover {
        color: #38BDF8 !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# Constants & Directory Verification
# ----------------------------------------------------
DB_PATH = 'embeddings.joblib'
OLLAMA_BASE_URL = "http://localhost:11434"
YOUTUBE_PLAYLIST_ID = "PLu0W_TkAOddqgT1QAiC5C9efBwzRYL5Ib" # Sigma Web Dev Course Playlist ID

# Create directory structures if absent
os.makedirs("videos", exist_ok=True)
os.makedirs("audios", exist_ok=True)
os.makedirs("jsons", exist_ok=True)

# ----------------------------------------------------
# Helper Functions
# ----------------------------------------------------
def format_time(seconds):
    """Converts seconds float to MM:SS string representation."""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"

@st.cache_resource(show_spinner=False)
def check_ollama():
    """Validates if the local Ollama backend is accessible."""
    try:
        r = requests.get(OLLAMA_BASE_URL, timeout=2)
        return r.status_code == 200
    except requests.exceptions.RequestException:
        return False

def check_model_available(model_name):
    """Verifies if a specific model is pulled in Ollama."""
    try:
        r = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
        if r.status_code == 200:
            models = [m['name'] for m in r.json().get('models', [])]
            # Match both tag-less and tagged model names
            return any(model_name in m for m in models)
        return False
    except Exception:
        return False

def get_db_stats():
    """Compiles statistics about local ingested dataset."""
    num_videos = len([f for f in os.listdir("videos") if f.lower().endswith(('.mp4', '.mkv', '.webm'))])
    num_audios = len([f for f in os.listdir("audios") if f.lower().endswith('.mp3')])
    num_jsons = len([f for f in os.listdir("jsons") if f.lower().endswith('.json')])
    
    total_chunks = 0
    if os.path.exists(DB_PATH):
        try:
            df = joblib.load(DB_PATH)
            total_chunks = len(df)
        except Exception:
            pass
            
    return num_videos, num_audios, num_jsons, total_chunks

@st.cache_data(show_spinner=False)
def load_database():
    """Loads vectorized Pandas DataFrame from joblib file."""
    if os.path.exists(DB_PATH):
        try:
            return joblib.load(DB_PATH)
        except Exception as e:
            st.error(f"Error reading vector database: {e}")
            return None
    return None

def create_query_embedding(query):
    """Fetches embedding for user query from BGE-M3."""
    r = requests.post(f"{OLLAMA_BASE_URL}/api/embed", json={
        "model": "bge-m3",
        "input": [query]
    }, timeout=15)
    if r.status_code == 200:
        return r.json()["embeddings"][0]
    else:
        raise Exception(f"Embedding request failed with status {r.status_code}")

def generate_rag_response(prompt):
    """Streams RAG generation from Ollama Llama3.2."""
    r = requests.post(f"{OLLAMA_BASE_URL}/api/generate", json={
        "model": "llama3.2",
        "prompt": prompt,
        "stream": False
    }, timeout=60)
    if r.status_code == 200:
        return r.json().get("response", "")
    else:
        raise Exception(f"Generation request failed: {r.text}")

# ----------------------------------------------------
# Main Layout Setup
# ----------------------------------------------------
col_title, col_status = st.columns([4, 1])

with col_title:
    st.markdown('<div class="app-title">🎓 Sigma Course AI Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-subtitle">RAG-Based AI Teaching Assistant for your video tutorials, powered by local AI.</div>', unsafe_allow_html=True)

with col_status:
    is_ollama_alive = check_ollama()
    has_bge_m3 = check_model_available("bge-m3") if is_ollama_alive else False
    has_llama32 = check_model_available("llama3.2") if is_ollama_alive else False
    
    if is_ollama_alive:
        st.markdown(
            '<div style="text-align: right; margin-top: 15px;">'
            '<span class="pulse-green"></span>'
            '<span style="font-weight:600; color:#10B981; font-size: 0.9rem;">OLLAMA ONLINE</span>'
            '</div>', 
            unsafe_allow_html=True
        )
        # Display pulled models checklist in sub-status
        models_subtext = []
        if has_bge_m3: models_subtext.append("BGE-M3")
        if has_llama32: models_subtext.append("Llama3.2")
        st.markdown(f"<div style='text-align: right; color:#64748B; font-size:0.75rem; font-weight:500;'>Models: {', '.join(models_subtext) if models_subtext else 'None'}</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            '<div style="text-align: right; margin-top: 15px;">'
            '<span class="pulse-red"></span>'
            '<span style="font-weight:600; color:#EF4444; font-size: 0.9rem;">OLLAMA OFFLINE</span>'
            '</div>', 
            unsafe_allow_html=True
        )

# Initialize Session States for Chat Interface
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar Navigation Panel
with st.sidebar:
    st.image("https://img.icons8.com/nolan/96/artificial-intelligence.png", width=70)
    st.markdown("<h3 style='color:#FFFFFF; font-weight:700; margin-top: 5px; margin-bottom: 2px;'>System Hub</h3>", unsafe_allow_html=True)
    st.markdown("<div style='color:#64748B; font-size:0.8rem; margin-bottom:15px;'>RAG Status Console</div>", unsafe_allow_html=True)
    
    # Retrieve & Draw Directory Stats
    v_cnt, a_cnt, j_cnt, c_cnt = get_db_stats()
    
    st.markdown("#### Indexed Assets")
    st.metric("Videos Ingested", f"{v_cnt}", help="MP4 video files located in the 'videos/' directory.")
    st.metric("Audios Extracted", f"{a_cnt}", help="MP3 audio extracted files located in the 'audios/' directory.")
    st.metric("JSON Transcripts", f"{j_cnt}", help="Whisper structured transcripts located in the 'jsons/' directory.")
    st.metric("Vector Text Chunks", f"{c_cnt:,}", help="Dense vectors saved in the 'embeddings.joblib' database.")
    
    st.markdown("---")
    st.markdown("#### Setup Quicklinks")
    st.info("Ensure Ollama models are pulled and running:\n"
            "- `ollama run llama3.2`\n"
            "- `ollama run bge-m3` ")

# ----------------------------------------------------
# Main Interactive Tabs Setup
# ----------------------------------------------------
tab_chat, tab_catalog, tab_pipeline = st.tabs([
    "💬 AI Teaching Assistant", 
    "📚 Lecture Transcripts", 
    "⚙️ Pipeline Management"
])

# ----------------------------------------------------
# TAB 1: Chat Dashboard (RAG Interface)
# ----------------------------------------------------
with tab_chat:
    if not is_ollama_alive:
        st.warning("⚠️ Local Ollama API is not running at http://localhost:11434. Please start Ollama locally to enable RAG functionality!")
        st.markdown("""
        <div class="glass-card-cyan">
            <h4 style="color:#0EA5E9; font-weight:700;">Steps to startup local Ollama backend:</h4>
            <ol style="margin-left: 1.5rem; color:#94A3B8; font-size: 0.9rem;">
                <li>Download Ollama from <a href="https://ollama.com" target="_blank" style="color:#38BDF8;">ollama.com</a> and install it.</li>
                <li>Open a command prompt/powershell and verify it starts.</li>
                <li>Pull the semantic embedding model: <code>ollama pull bge-m3</code></li>
                <li>Pull the conversational model: <code>ollama pull llama3.2</code></li>
                <li>Refresh this webpage dashboard.</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
    df_db = load_database()
    
    if df_db is None or len(df_db) == 0:
        st.info("💡 Your RAG Vector Database (`embeddings.joblib`) is currently empty. Please go to the **Pipeline Management** or **Lecture Transcripts** tab to parse your transcripts first!")
    else:
        st.markdown("<p style='font-size: 0.95rem; color:#94A3B8; margin-top: -10px; margin-bottom: 20px;'>Ask your question about HTML, CSS, JavaScript, SEO or any topic in the Sigma Web Development course. The assistant will answer using context and provide clickable timeline links.</p>", unsafe_allow_html=True)
        
        # Draw Existing Chat History
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f'<div class="chat-bubble-user"><b>You:</b><br>{message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-bubble-assistant"><b>🎓 Teaching Assistant:</b><br>{message["content"]}</div>', unsafe_allow_html=True)
                
                # Check if this assistant response had references/citations and render them beautifully
                if "citations" in message and message["citations"]:
                    st.markdown("<p style='font-size:0.8rem; font-weight:600; color:#38BDF8; margin-top:-8px; margin-bottom:2px; margin-left: 10px;'>📚 SOURCE CITATIONS USED FOR ANSWER:</p>", unsafe_allow_html=True)
                    cols_cit = st.columns(2)
                    for idx, cit in enumerate(message["citations"]):
                        col_idx = idx % 2
                        with cols_cit[col_idx]:
                            # Parse timestamp
                            start_str = format_time(cit['start'])
                            end_str = format_time(cit['end'])
                            
                            # Construct video catalog link or search query
                            st.markdown(f"""
                            <div class="citation-card">
                                <div class="citation-header">
                                    <span>📹 Video {cit['number']}: {cit['title']}</span>
                                    <span class="citation-tag">🕒 {start_str} - {end_str}</span>
                                </div>
                                <div class="citation-text">"{cit['text'].strip()}"</div>
                            </div>
                            """, unsafe_allow_html=True)
        
        # User input field
        query = st.chat_input("Ask a question about the course materials (e.g., 'What is semantic tags and its benefits?')")
        
        if query:
            # Render user bubble immediately
            st.markdown(f'<div class="chat-bubble-user"><b>You:</b><br>{query}</div>', unsafe_allow_html=True)
            st.session_state.chat_history.append({"role": "user", "content": query})
            
            with st.spinner("Analyzing vector database and generating grounded response..."):
                try:
                    # 1. Generate query embedding
                    q_embedding = create_query_embedding(query)
                    
                    # 2. Retrieve top matching segments using Cosine Similarity
                    db_embeddings = np.vstack(df_db['embedding'].values)
                    similarities = cosine_similarity(db_embeddings, [q_embedding]).flatten()
                    
                    # Get top 5 matches
                    top_matches = 5
                    top_indices = similarities.argsort()[::-1][:top_matches]
                    ref_df = df_db.loc[top_indices]
                    
                    # Create structured citations to display to the user
                    citations = []
                    for _, row in ref_df.iterrows():
                        citations.append({
                            "number": row.get("number", "00"),
                            "title": row.get("title", "Unknown Video"),
                            "start": row.get("start", 0.0),
                            "end": row.get("end", 0.0),
                            "text": row.get("text", "")
                        })
                    
                    # 3. Inject strict system prompt with extracted JSON segments
                    context_json = ref_df[["title", "number", "start", "end", "text"]].to_json(orient="records")
                    
                    rag_prompt = f"""I am teaching web development in my Sigma web development course. Here are video subtitle chunks containing video title, video number, start time in seconds, end time in seconds, the text at that time:

{context_json}
---------------------------------
"{query}"
User asked this question related to the video chunks, you have to answer in a human way (dont mention the above format, its just for you) where and how much content is taught in which video (in which video and at what timestamp) and guide the user to go to that particular video. If user asks unrelated question, tell him that you can only answer questions related to the course.
"""
                    # 4. Perform LLM inference
                    llm_response = generate_rag_response(rag_prompt)
                    
                    # Render Assistant Response
                    st.markdown(f'<div class="chat-bubble-assistant"><b>🎓 Teaching Assistant:</b><br>{llm_response}</div>', unsafe_allow_html=True)
                    
                    # Render Citations
                    st.markdown("<p style='font-size:0.8rem; font-weight:600; color:#38BDF8; margin-top:-8px; margin-bottom:2px; margin-left: 10px;'>📚 SOURCE CITATIONS USED FOR ANSWER:</p>", unsafe_allow_html=True)
                    cols_cit = st.columns(2)
                    for idx, cit in enumerate(citations):
                        col_idx = idx % 2
                        with cols_cit[col_idx]:
                            start_str = format_time(cit['start'])
                            end_str = format_time(cit['end'])
                            st.markdown(f"""
                            <div class="citation-card">
                                <div class="citation-header">
                                    <span>📹 Video {cit['number']}: {cit['title']}</span>
                                    <span class="citation-tag">🕒 {start_str} - {end_str}</span>
                                </div>
                                <div class="citation-text">"{cit['text'].strip()}"</div>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Append response to history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": llm_response,
                        "citations": citations
                    })
                except Exception as e:
                    st.error(f"Failed to process query: {e}")

        # Clear Chat Button
        st.markdown("<div style='margin-top:2rem;'></div>", unsafe_allow_html=True)
        if st.button("🧹 Clear Chat History", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

# ----------------------------------------------------
# TAB 2: Lecture Transcripts Browser
# ----------------------------------------------------
with tab_catalog:
    st.markdown("<p style='font-size: 0.95rem; color:#94A3B8; margin-top: -10px; margin-bottom: 20px;'>Browse through the indexed course curriculum, read the English translations, and execute direct text-based keyword matching.</p>", unsafe_allow_html=True)
    
    jsons_dir = "jsons"
    available_jsons = [f for f in os.listdir(jsons_dir) if f.lower().endswith('.json')]
    
    if not available_jsons:
        st.info("📂 No structured JSON transcripts found in the 'jsons/' folder yet. Please run the conversion in the **Pipeline Management** tab.")
    else:
        # Load all structured items
        transcripts = {}
        for js_file in available_jsons:
            with open(os.path.join(jsons_dir, js_file), "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    if "chunks" in data and len(data["chunks"]) > 0:
                        first_chunk = data["chunks"][0]
                        num = first_chunk.get("number", "00")
                        title = first_chunk.get("title", "Unknown")
                        transcripts[f"Video {num}: {title}"] = {
                            "chunks": data["chunks"],
                            "full_text": data.get("text", ""),
                            "filename": js_file
                        }
                except Exception:
                    pass
                    
        if not transcripts:
            st.warning("Could not read any formatted JSON transcript metadata.")
        else:
            sorted_keys = sorted(list(transcripts.keys()), key=lambda x: int(x.split(":")[0].split(" ")[1]) if x.split(":")[0].split(" ")[1].isdigit() else 999)
            
            # Select Video to Browse
            col_sel, col_src = st.columns([1, 1])
            with col_sel:
                selected_video_name = st.selectbox("📂 Select a lecture from the curriculum:", sorted_keys)
            
            with col_src:
                search_term = st.text_input("🔍 Search keyword inside this video transcript:")
                
            selected_video = transcripts[selected_video_name]
            
            st.markdown(f"### 📹 {selected_video_name}")
            
            if search_term:
                st.markdown(f"<p style='color:#38BDF8; font-weight:600;'>SEARCH RESULTS FOR: '{search_term}'</p>", unsafe_allow_html=True)
                term = search_term.lower()
                found_match = False
                
                for chunk in selected_video["chunks"]:
                    if term in chunk["text"].lower():
                        found_match = True
                        start_time = format_time(chunk["start"])
                        end_time = format_time(chunk["end"])
                        
                        # Highlight search word
                        highlighted_text = chunk["text"].replace(
                            search_term, 
                            f"<span style='background:rgba(14, 165, 233, 0.4); color:#FFFFFF; padding: 2px 4px; border-radius: 4px; font-weight:700;'>{search_term}</span>"
                        )
                        
                        st.markdown(f"""
                        <div class="citation-card">
                            <div class="citation-header">
                                <span>Timeline Match</span>
                                <span class="citation-tag">🕒 {start_time} - {end_time}</span>
                            </div>
                            <div class="citation-text">"... {highlighted_text} ..."</div>
                        </div>
                        """, unsafe_allow_html=True)
                if not found_match:
                    st.info(f"No timeline matches containing '{search_term}' were found inside this video.")
            else:
                # Browse regular transcript timeline chunks
                st.markdown("<p style='color:#64748B; font-weight:500; font-size:0.85rem;'>FULL TIMELINE SEGMENTS:</p>", unsafe_allow_html=True)
                
                # Render in an elegant scrollable box
                timeline_html = "<div style='max-height: 400px; overflow-y: scroll; border: 1px solid #1E293B; border-radius:12px; padding: 15px; background: rgba(15,23,42,0.4);'>"
                for chunk in selected_video["chunks"]:
                    start_str = format_time(chunk["start"])
                    end_str = format_time(chunk["end"])
                    timeline_html += f"""
                    <div style='margin-bottom: 12px; border-bottom: 1px solid rgba(226,232,240,0.03); padding-bottom: 8px;'>
                        <span style='color:#0EA5E9; font-weight: 700; font-family:"JetBrains Mono", monospace; font-size:0.85rem;'>[{start_str} - {end_str}]</span>
                        <span style='color:#E2E8F0; font-size: 0.9rem; margin-left: 10px;'>{chunk['text']}</span>
                    </div>
                    """
                timeline_html += "</div>"
                st.markdown(timeline_html, unsafe_allow_html=True)
                
                # Show Collapsible full raw translated text block
                with st.expander("📝 View Full concatenated translated English script"):
                    st.write(selected_video["full_text"])

# ----------------------------------------------------
# TAB 3: Pipeline Management Tab
# ----------------------------------------------------
with tab_pipeline:
    st.markdown("<p style='font-size: 0.95rem; color:#94A3B8; margin-top: -10px; margin-bottom: 20px;'>Control center to scan directories, check system prerequisites, and execute pipeline conversions directly from the web app interface.</p>", unsafe_allow_html=True)
    
    col_pre, col_ctrl = st.columns(2)
    
    with col_pre:
        st.markdown("""
        <div class="glass-card">
            <h4 style="color:#0EA5E9; margin-top:0; font-weight:700;">📂 Directory Ingestion Inspector</h4>
            <p style="color:#94A3B8; font-size:0.9rem;">Below is the current directory structures and contents of your project workspace:</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display folder list in beautiful tables
        video_files = [f for f in os.listdir("videos") if f.lower().endswith(('.mp4', '.mkv', '.webm'))]
        audio_files = [f for f in os.listdir("audios") if f.lower().endswith('.mp3')]
        json_files = [f for f in os.listdir("jsons") if f.lower().endswith('.json')]
        
        tab_v, tab_a, tab_j = st.tabs(["📹 Videos", "🎵 Audios", "📝 JSONs"])
        
        with tab_v:
            if video_files:
                df_v = pd.DataFrame(video_files, columns=["Video Filename"])
                st.dataframe(df_v, use_container_width=True, height=200)
            else:
                st.info("No raw video files found in the 'videos/' folder yet.")
                
        with tab_a:
            if audio_files:
                df_a = pd.DataFrame(audio_files, columns=["Audio Filename"])
                st.dataframe(df_a, use_container_width=True, height=200)
            else:
                st.info("No audio tracks found in the 'audios/' folder yet.")
                
        with tab_j:
            if json_files:
                df_j = pd.DataFrame(json_files, columns=["JSON Transcripts"])
                st.dataframe(df_j, use_container_width=True, height=200)
            else:
                st.info("No JSON structured transcripts found in the 'jsons/' folder yet.")
                
    with col_ctrl:
        st.markdown("""
        <div class="glass-card">
            <h4 style="color:#0EA5E9; margin-top:0; font-weight:700;">⚙️ Pipeline Operation Panel</h4>
            <p style="color:#94A3B8; font-size:0.9rem;">Trigger pipeline scripts incrementally. The scripts will automatically skip already processed media to save significant CPU/GPU time.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("---")
        
        # Button: Convert Videos to MP3
        if st.button("🎵 Run Video-to-MP3 extraction", use_container_width=True, help="Converts .mp4 files in 'videos/' into .mp3 files in 'audios/'. skips existing."):
            with st.spinner("Extracting audio tracks..."):
                import subprocess
                try:
                    # Run the modified video_to_mp3 script using python
                    result = subprocess.run(["python", "video_to_mp3.py"], capture_output=True, text=True)
                    st.success("Video-to-MP3 operation completed!")
                    with st.expander("Output Logs"):
                        st.code(result.stdout)
                except Exception as e:
                    st.error(f"Execution failed: {e}")
                    
        # Button: MP3 to JSON Transcription (Whisper)
        if st.button("📝 Run Whisper Speech-to-Text translation", use_container_width=True, help="Transcribes audio tracks inside 'audios/' into structured JSON transcripts. skips existing."):
            with st.spinner("Launching Whisper transcription... This could take a while if using heavy models on CPU..."):
                import subprocess
                try:
                    result = subprocess.run(["python", "mp3_to_json.py"], capture_output=True, text=True)
                    st.success("Whisper Speech-to-Text operation completed!")
                    with st.expander("Output Logs"):
                        st.code(result.stdout)
                except Exception as e:
                    st.error(f"Execution failed: {e}")
                    
        # Button: Preprocess JSON to Embeddings (Ollama)
        if st.button("⚡ Run Ollama Vector Indexing", use_container_width=True, help="Generates dense vectors via BGE-M3 for newly processed JSON files and updates your embeddings database."):
            with st.spinner("Generating embeddings via Ollama..."):
                import subprocess
                try:
                    result = subprocess.run(["python", "preprocess_json.py"], capture_output=True, text=True)
                    st.success("Ollama vector database updated successfully!")
                    with st.expander("Output Logs"):
                        st.code(result.stdout)
                except Exception as e:
                    st.error(f"Execution failed: {e}")
                    
        # Re-check database stats after actions
        if st.button("🔄 Refresh Application Dashboard", use_container_width=True):
            st.rerun()
