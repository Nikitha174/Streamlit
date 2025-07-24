import streamlit as st
from googleapiclient.discovery import build
from urllib.parse import urlparse
import google.generativeai as genai

# ----------------- CONFIG -----------------
st.set_page_config(page_title="📊 YouTube Analytics & Insights", layout="centered")

st.markdown("""
    <style>
    .title {text-align: center; font-size: 2rem; font-weight: bold; color: #ff4b4b;}
    .video-list {margin-top: 20px;}
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">📺 YouTube Channel Insights + AI Suggestions</div>', unsafe_allow_html=True)

# ----------------- API Keys -----------------
YOUTUBE_API_KEY = "AIzaSyDyildv6VT-GMhHQvRyw5_jTbyNG0iaQMc"       # 🔑 Replace with actual YouTube Data API v3 key
GEMINI_API_KEY = "AIzaSyA8VuHfXaj_HZ5-kHxk94vCf4r07X4lfoo"         # 🔐 Replace with your Gemini API key

genai.configure(api_key=GEMINI_API_KEY)

# ----------------- YouTube Client -----------------
@st.cache_resource
def get_youtube_service():
    return build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

youtube = get_youtube_service()

# ----------------- Helper Functions -----------------
def extract_channel_id(url):
    parsed = urlparse(url)
    path = parsed.path

    if "/channel/" in path:
        return path.split("/channel/")[1]
    elif "/@" in path:
        username = path.split("/@")[1].split("?")[0]
        return get_channel_id_by_query(username)
    elif "/c/" in path:
        custom = path.split("/c/")[1].split("?")[0]
        return get_channel_id_by_query(custom)
    return None

def get_channel_id_by_query(query):
    search = youtube.search().list(part="snippet", q=query, type="channel", maxResults=1).execute()
    items = search.get("items", [])
    if items:
        return items[0]["snippet"]["channelId"]
    return None

def get_channel_stats(channel_id):
    response = youtube.channels().list(
        part="snippet,statistics,contentDetails",
        id=channel_id
    ).execute()
    
    items = response.get("items", [])
    if not items:
        return None

    data = items[0]
    stats = data["statistics"]
    snippet = data["snippet"]

    return {
        "id": channel_id,
        "title": snippet["title"],
        "description": snippet["description"],
        "subscribers": f'{int(stats.get("subscriberCount", 0)):,}',
        "views": f'{int(stats.get("viewCount", 0)):,}',
        "videos": stats.get("videoCount", "0"),
        "thumbnail": snippet["thumbnails"]["high"]["url"],
        "uploads_playlist": data["contentDetails"]["relatedPlaylists"]["uploads"]
    }

def get_recent_videos(playlist_id, count=5):
    response = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=count
    ).execute()

    videos = []
    for item in response.get("items", []):
        title = item["snippet"]["title"]
        date = item["snippet"]["publishedAt"].split("T")[0]
        videos.append((title, date))
    return videos

def generate_channel_summary(title, desc, videos):
    video_titles = "\n".join(f"- {v[0]}" for v in videos)
    prompt = f"""
You are an expert YouTube content analyst.

Here is a YouTube channel:
Title: {title}
Description: {desc}

Recent Videos:
{video_titles}

1. Provide a 4-5 line summary of this channel's content style.
2. Suggest 3 areas where this channel could improve based on its public data (e.g., video variety, description detail, engagement ideas).
    """.strip()

    model = genai.GenerativeModel("gemini-1.5-flash")  # Or "gemini-1.5-pro"
    response = model.generate_content(prompt)
    return response.text

# ----------------- Streamlit UI -----------------
url_input = st.text_input("🔗 Paste YouTube Channel URL")

if st.button("📊 Analyze Channel"):
    if not url_input:
        st.warning("Please enter a valid YouTube channel URL.")
    else:
        with st.spinner("Analyzing channel..."):
            try:
                channel_id = extract_channel_id(url_input)
                if channel_id:
                    stats = get_channel_stats(channel_id)
                    if stats:
                        st.image(stats["thumbnail"], width=180)
                        st.subheader(stats["title"])
                        st.write(stats["description"])

                        col1, col2, col3 = st.columns(3)
                        col1.metric("👥 Subscribers", stats["subscribers"])
                        col2.metric("🎬 Videos", stats["videos"])
                        col3.metric("👁️ Views", stats["views"])

                        # Show recent videos
                        st.markdown("### 🆕 Recent Uploads")
                        recent = get_recent_videos(stats["uploads_playlist"])
                        for title, date in recent:
                            st.markdown(f"- **{title}** *(📅 {date})*")

                        # Generate summary + suggestions
                        st.markdown("---")
                        st.markdown("### 💡 AI-Generated Summary & Improvements")
                        summary = generate_channel_summary(stats["title"], stats["description"], recent)
                        st.markdown(summary)
                    else:
                        st.error("⚠️ Channel found but stats unavailable.")
                else:
                    st.error("⚠️ Could not resolve channel ID.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
