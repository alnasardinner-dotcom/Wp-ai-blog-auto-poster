import streamlit as st
import json
import os
import importlib
import pandas as pd
import requests
import time
from bs4 import BeautifulSoup

try:
    import modules.ai_generator
    import modules.wp_publisher
    import modules.ai_analysis
    import modules.brand_performance
    import modules.boost_monitor
    import modules.competitor_intelligence
    import modules.semrush_engine
    importlib.reload(modules.ai_generator)
    importlib.reload(modules.wp_publisher)
    importlib.reload(modules.ai_analysis)
    importlib.reload(modules.brand_performance)
    importlib.reload(modules.boost_monitor)
    importlib.reload(modules.competitor_intelligence)
    importlib.reload(modules.semrush_engine)
    from modules.ai_generator import AIContentGenerator
    from modules.wp_publisher import WordPressPublisher
    from modules.ai_analysis import render_visibility_overview, render_competitor_research, render_prompt_research
    from modules.brand_performance import render_brand_performance, render_perception, render_narrative_drivers, render_questions
    from modules.boost_monitor import render_site_audit, render_prompt_tracking
    from modules.competitor_intelligence import render_competitor_intelligence_tab
    from modules.semrush_engine import generate_semrush_50_keywords, generate_answerthepublic_50_questions
except ImportError:
    import ai_generator
    import wp_publisher
    import ai_analysis
    import brand_performance
    import boost_monitor
    import competitor_intelligence
    import semrush_engine
    importlib.reload(ai_generator)
    importlib.reload(wp_publisher)
    importlib.reload(ai_analysis)
    importlib.reload(brand_performance)
    importlib.reload(boost_monitor)
    importlib.reload(competitor_intelligence)
    importlib.reload(semrush_engine)
    from ai_generator import AIContentGenerator
    from wp_publisher import WordPressPublisher
    from ai_analysis import render_visibility_overview, render_competitor_research, render_prompt_research
    from brand_performance import render_brand_performance, render_perception, render_narrative_drivers, render_questions
    from boost_monitor import render_site_audit, render_prompt_tracking
    from competitor_intelligence import render_competitor_intelligence_tab
    from semrush_engine import generate_semrush_50_keywords, generate_answerthepublic_50_questions

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

# Config File Management
CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_config(data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception:
        return False

# Page Configuration
st.set_page_config(
    page_title="RankNaser Semrush & Ahrefs Keyword Intelligence Console",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Off-White & Light Gray Professional Theme Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    .stApp {
        background-color: #f8fafc !important;
        color: #0f172a !important;
    }

    .search-box-card {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        padding: 24px 30px;
        border-radius: 16px;
        box-shadow: 0 4px 12px 0 rgba(0, 0, 0, 0.05);
        margin-bottom: 25px;
    }

    .search-title {
        font-size: 1.8rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 6px;
        letter-spacing: -0.5px;
    }

    .search-subtitle {
        color: #64748b;
        font-size: 0.95rem;
        font-weight: 500;
        margin-bottom: 16px;
    }

    div[data-testid="stMetric"] {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 16px 20px !important;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05) !important;
    }

    div[data-testid="stMetric"] label {
        color: #64748b !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
    }

    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #0f172a !important;
        font-size: 1.6rem !important;
        font-weight: 800 !important;
    }

    .stButton>button[kind="primary"] {
        background: #4f46e5 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        border: 1px solid #4338ca !important;
        padding: 10px 24px !important;
        box-shadow: 0 2px 4px 0 rgba(79, 70, 229, 0.2) !important;
    }

    .stButton>button[kind="primary"]:hover {
        background: #4338ca !important;
    }

    button[data-baseweb="tab"] {
        font-weight: 700 !important;
        color: #475569 !important;
        font-size: 0.95rem !important;
    }

    button[aria-selected="true"] {
        color: #4f46e5 !important;
        border-bottom: 3px solid #4f46e5 !important;
    }

    [data-testid="stSidebar"] {
        background-color: #f1f5f9 !important;
        border-right: 1px solid #e2e8f0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "generated_article" not in st.session_state:
    st.session_state["generated_article"] = None
if "preset_keyword" not in st.session_state:
    st.session_state["preset_keyword"] = "SEO Expert BD"
if "search_query" not in st.session_state:
    st.session_state["search_query"] = "SEO Expert BD"
if "is_credentials_unlocked" not in st.session_state:
    st.session_state["is_credentials_unlocked"] = False

# Load Saved Credentials
saved_cfg = load_config()

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Settings & Credentials")
    
    if not st.session_state.get("is_credentials_unlocked", False):
        st.warning("🔒 **Settings Locked**")
        st.caption("Enter password to view or edit API keys & WP credentials.")
        
        pwd_input = st.text_input("🔑 Password", type="password", key="pwd_credentials_input")
        if st.button("🔓 Unlock Credentials", use_container_width=True):
            if pwd_input == "ranknaser011":
                st.session_state["is_credentials_unlocked"] = True
                st.success("✅ Unlocked Successfully!")
                st.rerun()
            else:
                st.error("❌ Incorrect Password!")
                
        gemini_api_key = saved_cfg.get("gemini_api_key", "")
        selected_model = saved_cfg.get("selected_model", "gemini-3.6-flash")
        wp_url = saved_cfg.get("wp_url", "")
        wp_user = saved_cfg.get("wp_user", "")
        wp_app_pass = saved_cfg.get("wp_app_pass", "")
    else:
        col_lock_hdr, col_lock_btn = st.columns([2, 1])
        with col_lock_hdr:
            st.success("🔓 **Unlocked**")
        with col_lock_btn:
            if st.button("🔒 Lock", help="Lock credentials again"):
                st.session_state["is_credentials_unlocked"] = False
                st.rerun()
                
        st.markdown("---")
        
        gemini_api_key = st.text_input("Gemini API Key", value=saved_cfg.get("gemini_api_key", ""), type="password", help="Enter your Google Gemini API key")
        
        if gemini_api_key:
            cleaned_key = gemini_api_key.strip()
            if len(cleaned_key) > 20:
                st.success("✅ **API Key Provided**")
            else:
                st.warning("⚠️ Please enter a complete API Key.")
        
        if "fetched_models" not in st.session_state:
            st.session_state["fetched_models"] = ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-flash-latest", "gemini-flash-lite-latest"]

        col_m1, col_m2 = st.columns([3, 1])
        with col_m1:
            saved_model = saved_cfg.get("selected_model", "gemini-3.6-flash")
            default_model_idx = st.session_state["fetched_models"].index(saved_model) if saved_model in st.session_state["fetched_models"] else 0
            selected_model = st.selectbox("AI Model", st.session_state["fetched_models"], index=default_model_idx)
        with col_m2:
            st.write("")
            st.write("")
            if st.button("🔄", help="Fetch active models enabled for your API Key"):
                if gemini_api_key:
                    gen = AIContentGenerator(api_key=gemini_api_key)
                    active_list = gen.list_available_models()
                    st.session_state["fetched_models"] = active_list
                    st.success("Updated!")
                else:
                    st.error("Key needed")
        
        st.subheader("🌐 WordPress REST API")
        wp_url = st.text_input("Site URL", value=saved_cfg.get("wp_url", ""), placeholder="https://myblogsite.com")
        wp_user = st.text_input("WP Username", value=saved_cfg.get("wp_user", ""), placeholder="admin")
        wp_app_pass = st.text_input("Application Password", value=saved_cfg.get("wp_app_pass", ""), type="password", help="Create an Application Password in WP Dashboard -> Users -> Profile")
        
        col_save, col_test = st.columns([1, 1])
        with col_save:
            if st.button("💾 Save Settings", use_container_width=True):
                new_cfg = {
                    "gemini_api_key": gemini_api_key.strip(),
                    "selected_model": selected_model,
                    "wp_url": wp_url.strip(),
                    "wp_user": wp_user.strip(),
                    "wp_app_pass": wp_app_pass.strip()
                }
                if save_config(new_cfg):
                    st.success("✅ Settings Saved!")
                else:
                    st.error("❌ Save Failed.")
                    
        with col_test:
            if st.button("🔌 Test WP", use_container_width=True):
                if not wp_url or not wp_user or not wp_app_pass:
                    st.error("Fill WP credentials first.")
                else:
                    publisher = WordPressPublisher(wp_url, wp_user, wp_app_pass)
                    res = publisher.test_connection()
                    if res["success"]:
                        st.success(res["message"])
                    else:
                        st.error(res["message"])

        st.markdown("---")
        st.info("💡 **Tip**: Click **💾 Save Settings** to automatically remember your API keys & WP credentials.")


# TOP LIVE RESEARCH & SEARCH CONSOLE
st.markdown("""
<div class="search-box-card">
    <div class="search-title">🔎 Semrush & Ahrefs Style Keyword Magic Intelligence Console</div>
    <div class="search-subtitle">Search ANY Keyword, Topic, or Domain to get 50+ Deduplicated Keywords, Search Intent, Competitor Ranks & 1-Click Publishing.</div>
</div>
""", unsafe_allow_html=True)

col_s1, col_s2 = st.columns([4, 1])
with col_s1:
    user_search_input = st.text_input(
        "Enter Target Keyword or Topic to Research 50+ Results:",
        value=st.session_state.get("search_query", "SEO Expert BD"),
        placeholder="e.g. Laptop Price in BD, Portable Monitor, techlandbd.com, Gaming PC 2026",
        key="main_search_console_input"
    )

with col_s2:
    st.write("")
    st.write("")
    run_research = st.button("🔍 Search 50+ Results", type="primary", use_container_width=True)

if run_research or user_search_input:
    st.session_state["search_query"] = user_search_input
    st.session_state["preset_keyword"] = user_search_input

target_kw = st.session_state.get("search_query", "SEO Expert BD")

st.markdown(f"### 📊 Live Semrush/Ahrefs Keyword Analytics for: **`{target_kw}`**")

# Generate 50+ unique deduplicated keywords dataframe
df_50_kws = generate_semrush_50_keywords(target_kw)
df_50_questions = generate_answerthepublic_50_questions(target_kw)

# Top KPI Summary Cards
total_vol = df_50_kws["BD Google Vol"].sum() if "BD Google Vol" in df_50_kws.columns else 45000
avg_kd = int(df_50_kws["KD %"].mean()) if "KD %" in df_50_kws.columns else 42

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.metric("Total Keywords Found", f"{len(df_50_kws)} Unique", "Deduplicated ✅")
with col_m2:
    st.metric("Total Potential Traffic", f"{total_vol:,} / mo", "+14% Growth")
with col_m3:
    st.metric("Average KD %", f"{avg_kd}%", "Medium Difficulty")
with col_m4:
    st.metric("Primary Intent", "Commercial / Transactional", "High Conversion")

st.markdown("---")

# MAIN WORKSPACE TABS
tab_semrush, tab_answerthepublic, tab_competitors, tab_article, tab_audit = st.tabs([
    f"📊 1. Semrush 50+ Keywords Table ({len(df_50_kws)} Unique Results)",
    "🔎 2. AnswerThePublic Questions & Comparisons",
    "🕵️ 3. Competitor 360° Intelligence & Spy",
    "📝 4. Write & Auto-Publish Article (1-Click)",
    "⚡ 5. Live Site Audit & GEO Readiness"
])


# --- TAB 1: SEMRUSH 50+ KEYWORDS TABLE ---
with tab_semrush:
    st.subheader(f"📊 Semrush/Ahrefs Keyword Explorer: {len(df_50_kws)} Deduplicated Results for '{target_kw}'")
    st.caption("Clean, non-duplicate keyword variations sorted by search volume, KD%, CPC, and SERP features.")

    # Search / Filter within the 50 keywords
    filter_txt = st.text_input("🔎 Filter within 50+ Keywords:", placeholder="Filter by word (e.g. price, best, startech)...")
    
    filtered_df = df_50_kws
    if filter_txt:
        filtered_df = df_50_kws[df_50_kws["Keyword / Query"].str.contains(filter_txt, case=False, na=False)]

    st.dataframe(filtered_df, use_container_width=True, height=450)

    col_d1, col_d2 = st.columns([3, 1])
    with col_d1:
        csv_data = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label=f"📥 Download All {len(filtered_df)} Keywords Report (CSV)",
            data=csv_data,
            file_name=f"semrush_keywords_{target_kw.lower().replace(' ', '_')}.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True
        )

    st.markdown("---")
    st.subheader("⚡ 1-Click Article Generator from Selected Keyword")
    selected_kw = st.selectbox("Select ANY keyword from the 50+ results to generate article:", filtered_df["Keyword / Query"])
    if st.button("🚀 Write Article for Selected Keyword", type="primary"):
        st.session_state["preset_keyword"] = selected_kw
        st.success(f"✅ Selected '{selected_kw}'! Click Tab 4 ('📝 Write & Auto-Publish Article') to generate.")


# --- TAB 2: ANSWER THE PUBLIC QUESTIONS ---
with tab_answerthepublic:
    st.subheader(f"🔎 AnswerThePublic Questions & Intent Queries for '{target_kw}'")
    st.dataframe(df_50_questions, use_container_width=True)


# --- TAB 3: COMPETITOR INTELLIGENCE ---
with tab_competitors:
    render_competitor_intelligence_tab()


# --- TAB 4: WRITE & AUTO-PUBLISH ARTICLE ---
with tab_article:
    st.subheader("📝 AI Content Generator & WordPress Auto-Publisher")
    st.caption("Generate EEAT & GEO optimized articles with Rank Math rules and push to WordPress in 1 click.")

    col1, col2 = st.columns([2, 1])

    with col1:
        main_keyword = st.text_input("🎯 Main Keyword (Focus Keyword)", value=st.session_state.get("preset_keyword", target_kw), placeholder="e.g. Best Digital Marketing Strategies 2026")
        suggested_keywords = st.text_area("🔗 Suggested / LSI Keywords (Optional)", placeholder="e.g. SEO optimization, social media marketing, content marketing tips", height=80)

    with col2:
        content_type = st.selectbox("📌 Article Type", ["Pillar Content (Comprehensive Guide)", "Cluster / Supporting Article", "Standard Blog Post"])
        word_count = st.slider("📏 Target Word Count", min_value=300, max_value=1500, value=1000, step=50)
        post_status = st.radio("📤 Post Status on WordPress", ["draft", "publish"], format_func=lambda x: "Save as Draft" if x == "draft" else "Publish Immediately")

    if st.button("✨ Generate AI Content Now", type="primary", use_container_width=True):
        if not gemini_api_key:
            st.error("❌ Please provide a valid Gemini API Key in the sidebar.")
        elif not main_keyword:
            st.error("❌ Please enter a Main Keyword.")
        else:
            with st.spinner("🧠 Generating EEAT & GEO optimized content with Rank Math rules..."):
                try:
                    generator = AIContentGenerator(api_key=gemini_api_key, model_name=selected_model)
                    article_data = generator.generate_article(
                        main_keyword=main_keyword,
                        suggested_keywords=suggested_keywords,
                        content_type=content_type,
                        word_count=word_count
                    )
                    st.session_state["generated_article"] = article_data
                    st.session_state["target_keyword"] = main_keyword
                    st.success("✅ Content generated successfully!")
                except Exception as e:
                    st.error(f"❌ Error generating content: {str(e)}")

    if st.session_state.get("generated_article"):
        art = st.session_state["generated_article"]
        st.markdown("---")
        st.subheader("📰 Generated Article Preview")
        st.markdown(art.get("content_html", ""), unsafe_allow_html=True)
        
        col_pub, col_copy = st.columns([1, 1])
        with col_pub:
            if st.button("🚀 Push to WordPress Now", use_container_width=True):
                if not wp_url or not wp_user or not wp_app_pass:
                    st.error("Provide WordPress credentials in sidebar first.")
                else:
                    publisher = WordPressPublisher(wp_url, wp_user, wp_app_pass)
                    res = publisher.publish_post(
                        title=art.get("title", ""),
                        content=art.get("content_html", ""),
                        status=post_status,
                        focus_keyword=st.session_state.get("target_keyword", ""),
                        meta_title=art.get("meta_title", ""),
                        meta_desc=art.get("meta_desc", "")
                    )
                    if res["success"]:
                        st.success(f"✅ Published to WordPress! Post ID: {res.get('post_id')}")
                    else:
                        st.error(f"❌ Publishing Failed: {res.get('message')}")


# --- TAB 5: SITE AUDIT ---
with tab_audit:
    render_site_audit()
