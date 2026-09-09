import streamlit as st
import json
import os
import importlib
import pandas as pd

try:
    import modules.ai_generator
    import modules.wp_publisher
    import modules.ai_analysis
    import modules.brand_performance
    import modules.boost_monitor
    importlib.reload(modules.ai_generator)
    importlib.reload(modules.wp_publisher)
    from modules.ai_generator import AIContentGenerator
    from modules.wp_publisher import WordPressPublisher
    from modules.ai_analysis import render_visibility_overview, render_competitor_research, render_prompt_research
    from modules.brand_performance import render_brand_performance, render_perception, render_narrative_drivers, render_questions
    from modules.boost_monitor import render_site_audit, render_prompt_tracking
except ImportError:
    import ai_generator
    import wp_publisher
    import ai_analysis
    import brand_performance
    import boost_monitor
    importlib.reload(ai_generator)
    importlib.reload(wp_publisher)
    from ai_generator import AIContentGenerator
    from wp_publisher import WordPressPublisher
    from ai_analysis import render_visibility_overview, render_competitor_research, render_prompt_research
    from brand_performance import render_brand_performance, render_perception, render_narrative_drivers, render_questions
    from boost_monitor import render_site_audit, render_prompt_tracking

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
    page_title="Ranknaser 2026 AI Visibility & Search Intelligence",
    page_icon="🚀",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        color: #1E88E5;
        font-size: 2.3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        color: #555;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
    }
    .badge-keyword {
        background-color: #e3f2fd;
        color: #0d47a1;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    .seo-card {
        border-left: 5px solid #4caf50;
        background-color: #f9f9f9;
        padding: 15px;
        border-radius: 4px;
        margin-bottom: 15px;
    }
    .query-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 10px 15px;
        border-radius: 6px;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "generated_article" not in st.session_state:
    st.session_state["generated_article"] = None
if "preset_keyword" not in st.session_state:
    st.session_state["preset_keyword"] = ""
if "research_results" not in st.session_state:
    st.session_state["research_results"] = None
if "multi_ai_results" not in st.session_state:
    st.session_state["multi_ai_results"] = None
if "search_volume_results" not in st.session_state:
    st.session_state["search_volume_results"] = None
if "is_credentials_unlocked" not in st.session_state:
    st.session_state["is_credentials_unlocked"] = False

# Load Saved Credentials
saved_cfg = load_config()

# Sidebar Configuration
with st.sidebar:
    st.markdown('<div style="font-size: 18px; font-weight: 700; color: #1e293b; margin-bottom: 10px;">⚡ AI Visibility</div>', unsafe_allow_html=True)
    
    menu_options = [
        "Visibility Overview",
        "Competitor Research",
        "Prompt Research",
        "Brand Performance",
        "Perception",
        "Narrative Drivers",
        "Questions",
        "Site Audit",
        "Prompt Tracking",
        "Content Creation"
    ]
    
    selected_page = st.radio(
        "Navigation",
        menu_options,
        index=0,
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.header("⚙️ Configuration & Credentials")
    
    if not st.session_state.get("is_credentials_unlocked", False):
        st.warning("🔒 **Settings Locked**")
        st.caption("Please enter password to view or modify API keys & credentials.")
        
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

# Page Routing
if selected_page == "Visibility Overview":
    render_visibility_overview()
elif selected_page == "Competitor Research":
    render_competitor_research()
elif selected_page == "Prompt Research":
    render_prompt_research()
elif selected_page == "Brand Performance":
    render_brand_performance()
elif selected_page == "Perception":
    render_perception()
elif selected_page == "Narrative Drivers":
    render_narrative_drivers()
elif selected_page == "Questions":
    render_questions()
elif selected_page == "Site Audit":
    render_site_audit()
elif selected_page == "Prompt Tracking":
    render_prompt_tracking()
elif selected_page == "Content Creation":
    main_tab1, main_tab2, main_tab3, main_tab4 = st.tabs([
        "📝 Write & Auto-Publish Article", 
        "🤖 Multi-AI & 2026 Niche Intent Intelligence", 
        "🔎 AnswerThePublic Search Intent Researcher",
        "📊 2026 Search Volume & Topic Trends (CSV Export)"
    ])
    
    with main_tab1:
        col1, col2 = st.columns([2, 1])

        with col1:
            default_kw_val = st.session_state.get("preset_keyword", "")
            main_keyword = st.text_input("🎯 Main Keyword (Focus Keyword)", value=default_kw_val, placeholder="e.g. Best Digital Marketing Strategies 2026")
            suggested_keywords = st.text_area("🔗 Suggested / LSI Keywords (Optional)", placeholder="e.g. SEO optimization, social media marketing, content marketing tips", height=80)

        with col2:
            content_type = st.selectbox("📌 Article Type", ["Pillar Content (Comprehensive Guide)", "Cluster / Supporting Article", "Standard Blog Post"])
            word_count = st.slider("📏 Target Word Count", min_value=300, max_value=1500, value=1000, step=50)
            post_status = st.radio("📤 Post Status on WordPress", ["draft", "publish"], format_func=lambda x: "Save as Draft" if x == "draft" else "Publish Immediately")

        if st.button("✨ Generate AI Content", type="primary", use_container_width=True):
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
