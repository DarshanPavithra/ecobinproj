# -*- coding: utf-8 -*-
import base64
import math
import os
import time

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from google.cloud import vision
from tinydb import Query, TinyDB

try:
    from streamlit_js_eval import get_geolocation
except ImportError:
    get_geolocation = None

st.set_page_config(page_title="ECO BIN", layout="wide")

BIN_ORDER = ["Green", "Blue", "Red", "Yellow"]
BIN_CAPACITY_TEMPLATE = {"Green": 0, "Blue": 0, "Red": 0, "Yellow": 0}
BIN_HEX = {
    "Green": "#28a745",
    "Blue": "#2f80ff",
    "Red": "#dc3545",
    "Yellow": "#ffc107",
}

NEAR_FULL_THRESHOLD = 95

BLUE_KEYWORDS = {"plastic", "glass", "paper", "bottle", "can", "book"}
GREEN_KEYWORDS = {"food", "fruit", "vegetable", "plant", "banana", "apple", "orange"}
RED_KEYWORDS = {"electronic", "laptop", "phone", "device", "battery", "mouse", "keyboard"}

BASE_DIR = os.path.dirname(__file__)
INTRO_IMAGE = os.path.join(BASE_DIR, "firstpic.webp")
DB_PATH = os.path.join(BASE_DIR, "db.json")

if not os.path.exists(DB_PATH):
    with open(DB_PATH, "w", encoding="utf-8") as db_file:
        db_file.write("{}")

state_table = TinyDB(DB_PATH)

BIN_IMAGES = {
    "Green": os.path.join(BASE_DIR, "PICS", "green bin close.png"),
    "Blue": os.path.join(BASE_DIR, "PICS", "blue bin close.png"),
    "Red": os.path.join(BASE_DIR, "PICS", "red bin close.avif"),
    "Yellow": os.path.join(BASE_DIR, "PICS", "yellow bin close.png"),
}

def get_bin_image(color: str) -> str | None:
    path = BIN_IMAGES.get(color)
    if path and os.path.exists(path):
        return path
    return None

def inject_app_css() -> None:
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Anton&family=Poppins:wght@300;400;500;600;700&display=swap');

    :root {
        --eco-green: #4fd8a5;
        --eco-teal: #6c9aff;
        --eco-orange: #f3b14f;
        --eco-bg: #08152d;
        --eco-surface: rgba(12, 26, 52, 0.94);
        --eco-text: #eef6ff;
        --eco-muted: #b0c6e3;
        --eco-border: rgba(100, 150, 255, 0.18);
        --eco-shadow: rgba(0, 0, 0, 0.35);
    }

    .stApp {
        background: radial-gradient(circle at top left, rgba(74, 124, 232, 0.18), transparent 30%),
                    linear-gradient(180deg, #071428 0%, #0e203f 100%);
        color: var(--eco-text);
        font-family: 'Poppins', sans-serif;
    }

    .block-container {
        max-width: 1240px;
        margin: 0 auto;
        padding: 1.2rem 1rem 2rem;
        animation: pageFadeSlide 0.42s ease-out;
    }

    .top-nav-shell {
        position: sticky;
        top: 1rem;
        z-index: 120;
        background: rgba(9, 24, 48, 0.96);
        backdrop-filter: blur(18px);
        border: 1px solid rgba(92, 142, 236, 0.18);
        border-radius: 22px;
        padding: 22px 28px;
        margin-bottom: 24px;
        box-shadow: 0 22px 50px var(--eco-shadow);
        color: var(--eco-text);
    }

    .top-nav-shell,
    .top-nav-shell * {
        color: var(--eco-text) !important;
    }

    .brand-header {
        font-family: 'Anton', sans-serif;
        font-size: 1.9rem;
        font-weight: 400;
        color: var(--eco-green);
        margin: 0;
        letter-spacing: 0.9px;
    }

    .brand-tagline {
        margin: 4px 0 0 0;
        color: var(--eco-text);
        font-size: 0.94rem;
        letter-spacing: 0.3px;
    }

    .hero-section {
        background: linear-gradient(160deg, rgba(78, 123, 223, 0.18), rgba(38, 92, 152, 0.22));
        border: 1px solid rgba(81, 122, 212, 0.24);
        border-radius: 24px;
        padding: 34px;
        margin-bottom: 28px;
        box-shadow: 0 18px 44px rgba(0, 0, 0, 0.22);
    }

    .hero-section h1 {
        font-size: 3rem;
        margin-bottom: 14px;
        line-height: 1.06;
    }

    .hero-section p,
    .section-copy,
    .feature-card p,
    .summary-panel p,
    .map-panel p {
        color: var(--eco-muted);
        line-height: 1.7;
    }

    .feature-grid,
    .metric-grid,
    .control-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 22px;
        margin: 24px 0;
    }

    .feature-card,
    .section-card,
    .summary-panel,
    .map-panel,
    .status-card,
    .bin-card,
    .talkback-box {
        background: var(--eco-surface);
        border: 1px solid var(--eco-border);
        border-radius: 22px;
        padding: 24px;
        box-shadow: 0 16px 28px rgba(0, 0, 0, 0.22);
        color: var(--eco-text);
    }

    .feature-card {
        min-height: 190px;
    }

    .bin-title {
        margin: 0;
        font-size: 1.14rem;
        font-weight: 700;
        color: var(--eco-text);
    }

    .bin-fill {
        margin: 0;
        color: var(--eco-text);
    }

    .bin-card img {
        width: 100%;
        height: 260px;
        min-height: 240px;
        border-radius: 18px;
        margin: 18px 0;
        object-fit: contain;
        background: rgba(255, 255, 255, 0.06);
    }

    .feature-card h3,
    .section-card h3,
    .summary-panel h3,
    .map-panel h3 {
        margin-top: 0;
        margin-bottom: 10px;
        color: var(--eco-green);
    }

    .feature-card p {
        margin: 0;
    }

    .status-pill {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border-radius: 999px;
        padding: 7px 14px;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        margin-bottom: 12px;
    }

    .status-open {
        background: rgba(38, 165, 103, 0.16);
        color: #135b36;
    }

    .status-closed {
        background: rgba(107, 114, 128, 0.12);
        color: #374151;
    }

    .metric-card {
        padding: 22px;
        min-height: 132px;
    }

    .metric-card h4 {
        margin: 0 0 10px;
        font-size: 0.95rem;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: var(--eco-muted);
    }

    .metric-card .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--eco-green);
    }

    .summary-panel {
        border-left: 4px solid var(--eco-green);
    }

    .map-panel {
        border-left: 4px solid var(--eco-orange);
    }

    .success-badge {
        background: linear-gradient(135deg, var(--eco-green) 0%, #047748 100%);
        color: #fff;
        padding: 12px 18px;
        border-radius: 999px;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        box-shadow: 0 10px 24px rgba(15, 122, 77, 0.22);
        margin-top: 16px;
    }

    .talkback-box {
        background: linear-gradient(135deg, rgba(15, 122, 77, 0.08), rgba(225, 107, 38, 0.08));
        border-left: 5px solid var(--eco-orange);
        border-radius: 20px;
        padding: 20px 22px;
        margin: 24px 0;
        font-weight: 600;
        color: var(--eco-text);
    }

    .talkback-box span {
        display: inline-flex;
        align-items: center;
        margin-right: 10px;
    }

    .input-section {
        border-radius: 20px;
        padding: 26px;
        margin: 20px 0;
    }

    .section-card h4 {
        margin: 12px 0 10px;
        color: var(--eco-green);
    }

    .section-card ul {
        margin: 0;
        padding-left: 18px;
        color: var(--eco-muted);
    }

    .section-card li {
        margin-bottom: 10px;
    }

    .stButton > button {
        border-radius: 999px;
        border: none;
        background: var(--eco-green);
        color: #fff;
        font-weight: 700;
        padding: 0.95rem 1.6rem;
        box-shadow: 0 10px 28px rgba(15, 122, 77, 0.22);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
        letter-spacing: 0.06em;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 14px 32px rgba(15, 122, 77, 0.28);
    }

    .stButton > button:disabled {
        opacity: 0.55;
        cursor: not-allowed;
        transform: none;
    }

    .stFileUploadDropzone,
    .stCameraInput {
        border-radius: 20px !important;
        box-shadow: inset 0 0 0 1px rgba(15, 122, 77, 0.18) !important;
        background: rgba(15, 122, 77, 0.04) !important;
    }

    .stRadio > div > label {
        font-weight: 700;
    }

    .bin-card {
        min-height: 340px;
        padding: 24px;
        background: var(--eco-surface);
        border-radius: 28px;
        border: 1px solid var(--eco-border);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 20px 36px rgba(15, 122, 77, 0.06);
        transition: none;
    }

    .bin-card img {
        width: 100%;
        border-radius: 18px;
        margin: 18px 0;
        object-fit: cover;
    }

    .status-pill {
        margin-top: 0;
        margin-bottom: 12px;
    }

    .page-section {
        margin-top: 16px;
        margin-bottom: 34px;
    }

    @keyframes pageFadeSlide {
        0% { opacity: 0; transform: translateY(16px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def load_db_state() -> tuple[dict[str, int], dict[str, int]]:
    try:
        record = state_table.get(Query().id == "singleton")
        if not record:
            return {}, BIN_CAPACITY_TEMPLATE.copy()
        data = record.get("data", {})
        users = {str(k): int(v) for k, v in data.get("user_points", {}).items()}
        bins = {key: int(data.get("bin_capacities", {}).get(key, 0)) for key in BIN_ORDER}
        return users, bins
    except Exception:
        return {}, BIN_CAPACITY_TEMPLATE.copy()


def save_db_state() -> None:
    payload = {
        "user_points": st.session_state.user_points,
        "bin_capacities": st.session_state.bin_capacities,
    }
    state_table.upsert({"id": "singleton", "data": payload}, Query().id == "singleton")


def initialize_state() -> None:
    users, bins = load_db_state()
    if "user_points" not in st.session_state:
        st.session_state.user_points = users
    if "bin_capacities" not in st.session_state:
        st.session_state.bin_capacities = bins
    if "unlocked_bin" not in st.session_state:
        st.session_state.unlocked_bin = None
    if "active_page" not in st.session_state:
        st.session_state.active_page = "Home"
    if "intro_done" not in st.session_state:
        st.session_state.intro_done = False
    if "spoken_keys" not in st.session_state:
        st.session_state.spoken_keys = []


def encode_image_to_base64(image_path: str) -> str | None:
    if not image_path or not os.path.exists(image_path):
        return None
    ext = os.path.splitext(image_path)[1].lower().lstrip('.')
    mime = 'image/jpeg' if ext in ('jpg', 'jpeg') else f'image/{ext}'
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def speak_once(text: str, event_key: str) -> None:
    if event_key in st.session_state.spoken_keys:
        return
    safe_text = text.replace("'", "").replace('"', "").replace("\n", " ")
    components.html(
        f"""
        <script>
        const msg = new SpeechSynthesisUtterance('{safe_text}');
        msg.rate = 0.88;
        msg.pitch = 1.0;
        msg.volume = 1.0;
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(msg);
        </script>
        """,
        height=0,
    )
    st.session_state.spoken_keys.append(event_key)


def create_talkback_message(bin_color: str, item: str, reason: str) -> str:
    """Create clear, simple talkback message"""
    return f"Please dispose of the {item} in the {bin_color} bin. {reason}"


def detect_trash(image_bytes: bytes) -> dict[str, str | list[str] | None]:
    try:
        client = vision.ImageAnnotatorClient()
        response = client.label_detection(image=vision.Image(content=image_bytes))
        labels = [label.description.lower() for label in response.label_annotations]
        item = labels[0] if labels else "unknown item"

        selected_bin = "Yellow"
        reason = "It will go to the landfill bin."

        for label in labels:
            matched = next((k for k in BLUE_KEYWORDS if k in label), None)
            if matched:
                selected_bin = "Blue"
                reason = f"It will go to Blue bin for recycling."
                break
            matched = next((k for k in GREEN_KEYWORDS if k in label), None)
            if matched:
                selected_bin = "Green"
                reason = f"It will go to Green bin for composting."
                break
            matched = next((k for k in RED_KEYWORDS if k in label), None)
            if matched:
                selected_bin = "Red"
                reason = f"It will go to Red bin for e-waste disposal."
                break

        return {
            "bin_color": selected_bin,
            "labels": labels[:5],
            "item": item,
            "reason": reason,
            "error": None,
        }
    except Exception as error:
        return {
            "bin_color": None,
            "labels": [],
            "item": "unknown item",
            "reason": "",
            "error": str(error),
        }


def render_all_bins_grid(active_color: str | None = None) -> None:
    """Display all 4 bins in a row using static bin imagery."""
    cols = st.columns(4, gap='large')
    for idx, color in enumerate(BIN_ORDER):
        fill = int(st.session_state.bin_capacities.get(color, 0))
        is_selected = active_color == color
        status_class = 'status-open' if is_selected else 'status-closed'
        status_text = 'SELECTED' if is_selected else 'Closed'
        bin_image_path = get_bin_image(color)
        image_base64 = encode_image_to_base64(bin_image_path) if bin_image_path else None

        with cols[idx]:
            image_html = ''
            if image_base64:
                ext = os.path.splitext(bin_image_path)[1].lower().lstrip('.')
                mime = 'image/jpeg' if ext in ('jpg', 'jpeg') else f'image/{ext}'
                image_html = (
                    f"<img src='data:{mime};base64,{image_base64}' alt='{color} bin' "
                    f"style='width:100%;border-radius:18px;margin:18px 0;display:block;'/>"
                )

            html = (
                f"<div class='bin-card' style='border-top: 4px solid {BIN_HEX[color]};'>"
                f"<div class='status-pill {status_class}'>{status_text}</div>"
                f"<div class='bin-title'>{color} Bin</div>"
                f"{image_html}"
                f"<div class='meter'><div class='meter-fill' style='width:{fill}%;background:{BIN_HEX[color]};'></div></div>"
                f"<p class='bin-fill'><strong>{fill}%</strong> full</p>"
                f"</div>"
            )
            st.markdown(html, unsafe_allow_html=True)


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def render_intro() -> None:
    st.markdown(
        """
        <div class="hero-section">
            <h1>ECO BIN</h1>
            <p>Smart waste sorting, guided disposal, and reward-based recycling in one polished experience.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([2, 1], gap="large")
    with col1:
        st.markdown(
            """
            <div class='section-card'>
                <h3>Welcome to ECO BIN</h3>
                <p class='section-copy'>Use the kiosk to identify the correct bin for your waste, keep community bins healthy, and earn points for responsible recycling.</p>
                <ul>
                    <li>AI object detection for accurate waste sorting</li>
                    <li>Smart bin unlocking when the item is verified</li>
                    <li>Live capacity tracking for safer collection</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class='feature-grid'>
                <div class='feature-card'>
                    <h3>Fast Start</h3>
                    <p>One button entry into the kiosk and dashboard experience.</p>
                </div>
                <div class='feature-card'>
                    <h3>Better Sorting</h3>
                    <p>Smart recommendations help local users dispose waste correctly.</p>
                </div>
                <div class='feature-card'>
                    <h3>Community Impact</h3>
                    <p>Reduce overflow, keep bins clean, and encourage responsible disposal.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        if os.path.exists(INTRO_IMAGE):
            st.image(INTRO_IMAGE, caption="ECO BIN Smart Dustbin", use_container_width=True)
        else:
            st.info("Intro image not found. Place firstpic.webp in project root.")

    if st.button("Enter ECO BIN", use_container_width=True):
        progress = st.progress(0, text="Loading modules...")
        for i in range(1, 21):
            time.sleep(0.03)
            progress.progress(i * 5, text="Loading modules...")
        st.session_state.intro_done = True
        st.rerun()


def render_top_nav() -> None:
    total_users = len(st.session_state.user_points)
    total_points = sum(st.session_state.user_points.values())
    avg_fill = int(sum(st.session_state.bin_capacities.values()) / len(BIN_ORDER))

    st.markdown(
        """
        <div class="top-nav-shell">
            <div>
                <p class="brand-header">ECO BIN</p>
                <p class="brand-tagline">AI Waste Sorting • Smart Bin Control • Community Rewards</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    metrics = st.columns(3)
    metrics[0].metric("Eco Users", total_users or 0)
    metrics[1].metric("Total Points", total_points or 0)
    metrics[2].metric("Avg Bin Fill", f"{avg_fill}%")

    pages = ["Home", "About", "Services", "Kiosk", "Admin Dashboard", "Find a Bin", "Leaderboard"]
    selected = st.radio(
        "Navigation",
        pages,
        index=pages.index(st.session_state.active_page) if st.session_state.active_page in pages else 0,
        horizontal=True,
        label_visibility="collapsed",
    )
    if selected != st.session_state.active_page:
        st.session_state.active_page = selected
        st.rerun()


def render_home() -> None:
    st.markdown(
        """
        <div class="hero-section">
            <h1>Smart Waste Management for Every Community</h1>
            <p>ECO BIN helps users identify the right disposal bin, keeps fill levels under control, and encourages eco-friendly habits.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class='feature-grid'>
            <div class='feature-card'>
                <h3>AI Sorting</h3>
                <p>Automatic waste classification makes recycling fast and accurate.</p>
            </div>
            <div class='feature-card'>
                <h3>Smart Bin Unlock</h3>
                <p>Only the correct bin opens for the detected item.</p>
            </div>
            <div class='feature-card'>
                <h3>Rewards System</h3>
                <p>Earn points for responsible disposal and join the leaderboard.</p>
            </div>
        </div>

        <div class='section-card'>
            <h3>Why ECO BIN Works</h3>
            <p>Keep local waste systems cleaner with smarter sorting, safer disposal, and clear feedback for every user.</p>
            <ul>
                <li>Reduce contamination by placing waste in the right bin every time.</li>
                <li>Prevent overflow with live fill-level monitoring.</li>
                <li>Motivate users through points, progress, and community rankings.</li>
            </ul>
        </div>

        <div class='feature-grid'>
            <div class='feature-card'>
                <h3>Step 1</h3>
                <p>Capture or upload a photo of your waste item.</p>
            </div>
            <div class='feature-card'>
                <h3>Step 2</h3>
                <p>ECO BIN identifies the item and assigns the correct disposal bin.</p>
            </div>
            <div class='feature-card'>
                <h3>Step 3</h3>
                <p>Dispose responsibly, earn points, and help the community stay greener.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_about() -> None:
    st.markdown(
        """
        <div class="hero-section">
            <h1>About ECO BIN</h1>
            <p>ECO BIN combines AI vision, real-time bin monitoring, and user incentives to make waste sorting intuitive and impactful.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class='feature-grid'>
            <div class='feature-card'>
                <h3>What We Do</h3>
                <p>Detects waste items, recommends the proper bin, and unlocks the lid for safe disposal.</p>
            </div>
            <div class='feature-card'>
                <h3>Why It Matters</h3>
                <p>Helps prevent contamination, reduce overflow, and support cleaner neighborhoods.</p>
            </div>
            <div class='feature-card'>
                <h3>How It Works</h3>
                <p>Users scan or upload an image, the system analyzes it, and then the right bin opens.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_services() -> None:
    st.markdown(
        """
        <div class="hero-section">
            <h1>Services</h1>
            <p>ECO BIN brings together waste scanning, bin control, analytics, and navigation to support smart disposal.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class='feature-grid'>
            <div class='feature-card'>
                <h3>Real-Time Classification</h3>
                <p>AI labels waste quickly and recommends the correct bin class.</p>
            </div>
            <div class='feature-card'>
                <h3>Capacity Tracking</h3>
                <p>Monitor bin fill levels and avoid overflow with smart alerts.</p>
            </div>
            <div class='feature-card'>
                <h3>Nearest Bin Finder</h3>
                <p>Locate the closest available smart bin when your local one is full.</p>
            </div>
            <div class='feature-card'>
                <h3>Rewards & Leaderboard</h3>
                <p>Encourage healthy disposal habits with points and community rankings.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_leaderboard() -> None:
    st.markdown(
        """
        <div class="hero-section">
            <h1>Leaderboard</h1>
            <p>See the top eco-heroes and their contribution to smarter waste disposal.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.user_points:
        sorted_users = sorted(st.session_state.user_points.items(), key=lambda x: x[1], reverse=True)
        top_users = sorted_users[:5]
        champion = top_users[0]

        st.markdown(
            f"""
            <div class='summary-panel'>
                <h3>Top Recycler</h3>
                <p><strong>{champion[0]}</strong> leads the board with <strong>{champion[1]} points</strong>.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        leader_df = pd.DataFrame([
            {"Rank": i + 1, "Eco-ID": uid, "Points": pts}
            for i, (uid, pts) in enumerate(sorted_users[:10])
        ])
        st.table(leader_df)
    else:
        st.info("No users yet. Scan waste and earn the first points!")


def render_kiosk() -> None:
    st.markdown(
        """
        <div class="hero-section">
            <h1>Kiosk</h1>
            <p>Scan waste, receive bin guidance, and earn points for responsible disposal.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    user_id = st.text_input("Enter your Eco-ID", placeholder="e.g., USER01").strip()
    if not user_id:
        st.info("Enter Eco-ID to continue.")
        return

    if user_id not in st.session_state.user_points:
        st.session_state.user_points[user_id] = 0
        save_db_state()

    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.metric("Your Points", st.session_state.user_points[user_id])
    with col2:
        avg_fill = int(sum(st.session_state.bin_capacities.values()) / len(BIN_ORDER))
        st.metric("Average Bin Fill", f"{avg_fill}%")

    unlocked = st.session_state.unlocked_bin
    if unlocked:
        color = unlocked["bin_color"]
        labels = unlocked["labels"]
        item = unlocked["item"]
        reason = unlocked["reason"]

        st.markdown(
            f"""
            <div class='summary-panel'>
                <h3>Bin Opened</h3>
                <p>Your item was identified as <strong>{item}</strong> and the <strong>{color} bin</strong> is ready.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        render_all_bins_grid(active_color=color)

        talkback_msg = create_talkback_message(color, item, reason)
        st.markdown(f"<div class='talkback-box'><span class='talkback-icon'>Sound:</span>{talkback_msg}</div>", unsafe_allow_html=True)
        speak_once(talkback_msg, f"detect_{user_id}_{item}_{color}")

        st.markdown("---")
        if st.button("Close Lid & Earn 10 Points", type="primary", use_container_width=True):
            st.session_state.user_points[user_id] += 10
            st.session_state.bin_capacities[color] = min(100, st.session_state.bin_capacities[color] + 5)
            save_db_state()
            thank_you_msg = f"Thank you! {item} accepted. +10 points earned!"
            st.markdown(f"<div class='success-badge'>✓ {thank_you_msg}</div>", unsafe_allow_html=True)
            speak_once(thank_you_msg, f"thanks_{user_id}_{item}_{color}")
            time.sleep(1)
            st.session_state.unlocked_bin = None
            st.rerun()
        return

    st.markdown("<h3>All Bins - Ready for Scanning</h3>", unsafe_allow_html=True)
    render_all_bins_grid(active_color=None)

    st.markdown("---")
    st.markdown("<div class='section-card'><h3>Scan or Upload Waste</h3><p>Choose an image source and submit to identify the correct bin.</p></div>", unsafe_allow_html=True)

    mode = st.radio("Input Method", ["Upload Image", "Live Camera"], horizontal=True, label_visibility="collapsed")
    image_bytes = None
    if mode == "Upload Image":
        uploaded = st.file_uploader("Browse Waste Photo", type=["jpg", "jpeg", "png", "webp"])
        if uploaded is not None:
            image_bytes = uploaded.getvalue()
            st.image(image_bytes, caption="Selected Image", use_container_width=True)
    else:
        camera_file = st.camera_input("Capture Live Waste Photo")
        if camera_file is not None:
            image_bytes = camera_file.getvalue()
            st.image(image_bytes, caption="Captured Image", use_container_width=True)

    if st.button("Process Item", use_container_width=True, disabled=image_bytes is None):
        result = detect_trash(image_bytes)
        if result["error"]:
            st.error(f"Detection failed: {result['error']}")
            return

        target_bin = result["bin_color"]
        target_fill = int(st.session_state.bin_capacities.get(target_bin, 0))
        if target_fill >= NEAR_FULL_THRESHOLD:
            st.warning(
                f"Warning: {target_bin} Bin is at {target_fill}% capacity. Please clear this bin before adding more waste."
            )
            speak_once(
                f"Alert. {target_bin} bin is nearly full. Please take the trash out for this bin.",
                f"near_full_{target_bin}_{target_fill}",
            )
            return

        st.session_state.unlocked_bin = result
        st.rerun()


def render_admin() -> None:
    st.markdown(
        """
        <div class="hero-section">
            <h1>Admin Dashboard</h1>
            <p>Monitor bin fill levels, review status, and clear full bins with confidence.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_all_bins_grid()

    st.markdown("---")
    st.markdown("<div class='section-card'><h3>Dispatch Center</h3><p>Clear full bins quickly and keep your smart ecosystem running smoothly.</p></div>", unsafe_allow_html=True)
    for color in BIN_ORDER:
        fill = st.session_state.bin_capacities[color]
        if fill >= NEAR_FULL_THRESHOLD:
            st.warning(f"Alert: {color} Bin is {fill}% full. Please clear it now.")
            if st.button(f"Clear {color} Bin", key=f"clear_{color}"):
                progress = st.progress(0, text="Truck Emptying...")
                for step in range(1, 31):
                    time.sleep(0.1)
                    progress.progress(int(step / 30 * 100), text="Truck Emptying...")
                st.session_state.bin_capacities[color] = 0
                save_db_state()
                st.success(f"{color} Bin cleared!")
                st.rerun()


def render_find_bin() -> None:
    st.markdown(
        """
        <div class="hero-section">
            <h1>Find a Bin</h1>
            <p>Locate the nearest available smart bin with the most capacity.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    bins = [
        {"name": "Kottackal Store (MC Road)", "lat": 10.1710, "lon": 76.4286, "capacity_key": "Green"},
        {"name": "Reliance Smart Bazaar", "lat": 10.1688, "lon": 76.4338, "capacity_key": "Blue"},
        {"name": "Crystal Hypermarket", "lat": 10.1651, "lon": 76.4366, "capacity_key": "Red"},
    ]

    default_lat, default_lon = 10.1785, 76.4300
    user_lat, user_lon = default_lat, default_lon
    geo = get_geolocation() if get_geolocation is not None else None
    if geo and geo.get("coords"):
        user_lat = geo["coords"].get("latitude", default_lat)
        user_lon = geo["coords"].get("longitude", default_lon)

    st.markdown("<div class='map-panel'><h3>Live bin map</h3><p>Your current position and nearby smart bin locations.</p></div>", unsafe_allow_html=True)
    st.map(pd.DataFrame([{"lat": b["lat"], "lon": b["lon"]} for b in bins] + [{"lat": user_lat, "lon": user_lon}]))
    st.caption(f"Current location: {user_lat:.5f}, {user_lon:.5f}")

    if st.button("Find Nearest Bin"):
        candidates = []
        for b in bins:
            fill = st.session_state.bin_capacities.get(b["capacity_key"], 0)
            if fill < NEAR_FULL_THRESHOLD:
                candidates.append((haversine_km(user_lat, user_lon, b["lat"], b["lon"]), b, fill))
        if not candidates:
            st.error(f"No available bins under {NEAR_FULL_THRESHOLD}% fill.")
        else:
            d, b, fill = min(candidates, key=lambda x: x[0])
            st.success(f"Nearest available bin: {b['name']} | {d:.2f} km | Fill {fill}%")
            maps_url = (
                "https://www.google.com/maps/dir/?api=1"
                f"&origin={user_lat},{user_lon}"
                f"&destination={b['lat']},{b['lon']}"
                "&travelmode=walking"
            )
            st.link_button("Start Google Maps Directions", maps_url, use_container_width=True)


# ============ MAIN APP ============

inject_app_css()
initialize_state()

# Setup Google Cloud credentials
path1 = os.path.join(BASE_DIR, "gcp-key.json")
path2 = os.path.join(BASE_DIR, "gcp-key.json.json")
if os.path.exists(path1):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path1
elif os.path.exists(path2):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path2

# Render app
if not st.session_state.intro_done:
    render_intro()
else:
    render_top_nav()
    page = st.session_state.active_page
    if page == "Home":
        render_home()
    elif page == "About":
        render_about()
    elif page == "Services":
        render_services()
    elif page == "Kiosk":
        render_kiosk()
    elif page == "Admin Dashboard":
        render_admin()
    elif page == "Find a Bin":
        render_find_bin()
    else:
        render_leaderboard()
