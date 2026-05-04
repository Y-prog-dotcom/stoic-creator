import streamlit as st
import os, uuid, time, asyncio, urllib.request
from pathlib import Path
from datetime import datetime

IS_HF = os.getenv("SPACE_ID") is not None
BASE = Path(__file__).parent
DATA_DIR = Path("/data") if Path("/data").exists() else Path("/tmp")
OUT_DIR = DATA_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FONT_PATH = BASE / "assets" / "fonts" / "Montserrat-Bold.ttf"
if not FONT_PATH.exists():
    FONT_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        urllib.request.urlretrieve("https://github.com/JulietaUla/Montserrat/raw/master/fonts/ttf/Montserrat-Bold.ttf", FONT_PATH)
    except:
        pass

st.set_page_config(page_title="Stoic Creator", page_icon="⚔️", layout="wide")

st.markdown("""
<style>
    .stApp {background: linear-gradient(135deg, #0a0a1a, #1a1a2e); color: white;}
    .main-title {font-size: 2.8rem; font-weight: 900; text-align: center; background: linear-gradient(90deg, #FFD700, #FFA500); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
    .stButton>button[kind="primary"] {background: linear-gradient(90deg, #FFD700, #FFA500)!important; color: black!important; font-weight: bold!important; padding: 1.2rem!important; border-radius: 12px!important; width: 100%;}
    .step {background: rgba(255,215,0,0.1); border-left: 5px solid #FFD700; padding: 15px; margin: 10px 0; border-radius: 0 10px 10px 0;}
    .success-box {background: #0f5132; color: #d4edda; padding: 20px; border-radius: 12px; border: 1px solid #00C864;}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">⚔️ STOIC CREATOR</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#aaa;'>Création automatique de vidéos stoïques • Mistral + Edge-TTS + Pexels</p>", unsafe_allow_html=True)

@st.cache_resource
def load_engines():
    from engines.mistral_engine import MistralEngine
    from engines.voice_engine import VoiceEngine
    from engines.video_engine import VideoEngine
    from engines.editor_engine import EditorEngine
    return MistralEngine(), VoiceEngine(), VideoEngine(), EditorEngine()

mistral, voice_engine, video_engine, editor = load_engines()

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("🚀 Nouvelle Vidéo")
    mode = st.radio("Mode", ["🤖 100% Automatique", "✍️ Je donne un thème"], horizontal=True)
    topic = st.text_input("Thème", placeholder="Ex: La puissance de la solitude", disabled=mode == "🤖 100% Automatique")

    if st.button("⚔️ LANCER LA CRÉATION", type="primary", use_container_width=True):
        with st.spinner("Création en cours (2 à 4 minutes)..."):
            try:
                video_id = str(uuid.uuid4())[:8]
                vdir = OUT_DIR / video_id
                vdir.mkdir(parents=True, exist_ok=True)
                cdir = vdir / "clips"
                cdir.mkdir(exist_ok=True)

                idea = mistral.generate_idea(topic if mode == "✍️ Je donne un thème" else "")
                st.success(f"Idée : **{idea['titre']}**")

                script = mistral.generate_script(idea)
                voice_path = str(vdir / "voice.mp3")
                voice_path, subs = voice_engine.generate(script, voice_path)
                duration = voice_engine.get_duration(voice_path)

                clips = video_engine.get_clips(idea.get("keywords", []), str(cdir), max(4, int(duration/8)))
                final_video = str(vdir / "final_video.mp4")
                editor.assemble(clips, voice_path, script, final_video, subs)

                st.markdown('<div class="success-box">✅ VIDÉO CRÉÉE AVEC SUCCÈS !</div>', unsafe_allow_html=True)
                st.video(final_video)

                with open(final_video, "rb") as f:
                    st.download_button("📥 TÉLÉCHARGER LA VIDÉO", f, file_name=f"stoic_{video_id}.mp4", mime="video/mp4", use_container_width=True)

            except Exception as e:
                st.error(f"Erreur : {e}")

with col2:
    st.info("Cette version est optimisée pour **Hugging Face Spaces Gratuit**.\n\nTélécharge la vidéo et publie-la manuellement sur YouTube, TikTok et Facebook.")
