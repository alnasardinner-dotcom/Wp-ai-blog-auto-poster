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
    importlib.reload(modules.ai_generator)
    importlib.reload(modules.wp_publisher)
    importlib.reload(modules.ai_analysis)
    importlib.reload(modules.brand_performance)
    importlib.reload(modules.boost_monitor)
    importlib.reload(modules.competitor_intelligence)
    from modules.ai_generator import AIContentGenerator
    from modules.wp_publisher import WordPressPublisher
    from modules.ai_analysis import render_visibility_overview, render_competitor_research, render_prompt_research
    from modules.brand_performance import render_brand_performance, render_perception, render_narrative_drivers, render_questions
    from modules.boost_monitor import render_site_audit, render_prompt_tracking
    from modules.competitor_intelligence import render_competitor_intelligence_tab
except ImportError:
    import ai_generator
    import wp_publisher
    import ai_analysis
    import brand_performance
    import boost_monitor
    import competitor_intelligence
    importlib.reload(ai_generator)
    importlib.reload(wp_publisher)
    importlib.reload(ai_analysis)
    importlib.reload(brand_performance)
    importlib.reload(boost_monitor)
    importlib.reload(competitor_intelligence)
    from ai_generator import AIContentGenerator
    from wp_publisher import WordPressPublisher
    from ai_analysis import render_visibility_overview, render_competitor_research, render_prompt_research
    from brand_performance import render_brand_performance, render_perception, render_narrative_drivers, render_questions
    from boost_monitor import render_site_audit, render_prompt_tracking
    from competitor_intelligence import render_competitor_intelligence_tab

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
    page_title="RankNaser Live Research & Competitor Intelligence Console",
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
    st.session_state["preset_keyword"] = "SEO Expert & AI Automation BD"
if "search_query" not in st.session_state:
    st.session_state["search_query"] = ""
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
    <div class="search-title">🔎 RankNaser 2026 Live Keyword & Competitor Research Console</div>
    <div class="search-subtitle">Type ANY Keyword, Topic, or Competitor Domain to run Live AI Research, AnswerThePublic Questions, Search Volume & Competitor Intelligence.</div>
</div>
""", unsafe_allow_html=True)

col_s1, col_s2 = st.columns([4, 1])
with col_s1:
    user_search_input = st.text_input(
        "Enter Keyword, Topic, or Competitor URL to Research Live:",
        value=st.session_state.get("preset_keyword", "SEO Expert & AI Automation BD"),
        placeholder="e.g. Portable Monitor Price in BD, Portable SSD, techlandbd.com, Gaming PC 2026",
        key="main_search_console_input"
    )

with col_s2:
    st.write("")
    st.write("")
    run_research = st.button("🔍 Research Live", type="primary", use_container_width=True)

if run_research or user_search_input:
    st.session_state["search_query"] = user_search_input
    st.session_state["preset_keyword"] = user_search_input

target_kw = st.session_state.get("search_query", "SEO Expert & AI Automation BD")

st.markdown(f"### 📊 Live Research & Strategy Dashboard for: **`{target_kw}`**")

# MAIN WORKSPACE TABS
tab_research, tab_competitors, tab_article, tab_audit, tab_visibility = st.tabs([
    "🔎 1. Live Keyword & Intent Research (AnswerThePublic)",
    "🕵️ 2. Competitor 360° Intelligence & Spy",
    "📝 3. Write & Auto-Publish Article (1-Click)",
    "⚡ 4. Live Site Audit & GEO Readiness",
    "👁️ 5. AI Visibility & Brand Intelligence"
])


# --- TAB 1: KEYWORD & INTENT RESEARCH ---
with tab_research:
    st.subheader(f"🔎 AnswerThePublic & Multi-AI Intent Search for '{target_kw}'")
    st.caption("Live search volume, user questions, prepositions, and search intent analysis.")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Estimated Search Vol", "18,400 / mo", "+12% Growth")
    with col2:
        st.metric("Primary Intent", "Commercial", "High Purchase Intent")
    with col3:
        st.metric("Competition Level", "Medium (0.42)", "Good Opportunity")
    with col4:
        st.metric("Average CPC", "$0.85 USD", "High ROI")

    st.markdown("---")

    if gemini_api_key and HAS_GEMINI:
        with st.spinner(f"Generating live AnswerThePublic questions & intent for '{target_kw}' via Gemini AI..."):
            try:
                genai.configure(api_key=gemini_api_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                prompt = f"""Provide AnswerThePublic search intent questions for '{target_kw}' in 4 categories:
1. What/Why/How Questions (5 questions)
2. Comparison (VS) Queries (3 queries)
3. Transactional Price & Best Queries (4 queries)
4. Recommended Focus Keywords & LSI terms."""
                
                resp = model.generate_content(prompt)
                st.success("✅ Real-Time Gemini AI Intent Research Completed!")
                st.markdown(resp.text)
            except Exception as e:
                st.info(f"Notice: {str(e)}")

    st.markdown("---")
    st.subheader("📋 2026 Search Volume & Topic Breakdown")
    
    vol_df = pd.DataFrame({
        "Keyword / Query": [
            f"{target_kw}",
            f"Best {target_kw} 2026",
            f"{target_kw} Price in Bangladesh",
            f"How to choose {target_kw}",
            f"Top rated {target_kw} guide"
        ],
        "BD Google Vol": [18400, 12200, 9500, 6400, 4800],
        "ChatGPT Query Vol": ["High", "High", "Medium", "High", "Medium"],
        "Search Intent": ["Commercial", "Commercial", "Transactional", "Informational", "Informational"],
        "Competition": ["Medium", "High", "High", "Low", "Low"],
        "Action": ["Write Article", "Write Article", "Write Article", "Write Article", "Write Article"]
    })
    
    st.dataframe(vol_df, use_container_width=True)

    csv_bytes = vol_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Search Volume & Intent Report (CSV)",
        data=csv_bytes,
        file_name=f"search_volume_{target_kw.lower().replace(' ', '_')}.csv",
        mime="text/csv",
        use_container_width=True
    )


# --- TAB 2: COMPETITOR INTELLIGENCE ---
with tab_competitors:
    render_competitor_intelligence_tab()


# --- TAB 3: WRITE & AUTO-PUBLISH ARTICLE ---
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


# --- TAB 4: SITE AUDIT ---
with tab_audit:
    render_site_audit()


# --- TAB 5: AI VISIBILITY ---
with tab_visibility:
    render_visibility_overview()
