import streamlit as st
import json
import os
import importlib

try:
    import modules.ai_generator
    import modules.wp_publisher
    importlib.reload(modules.ai_generator)
    importlib.reload(modules.wp_publisher)
    from modules.ai_generator import AIContentGenerator
    from modules.wp_publisher import WordPressPublisher
except ImportError:
    import ai_generator
    import wp_publisher
    importlib.reload(ai_generator)
    importlib.reload(wp_publisher)
    from ai_generator import AIContentGenerator
    from wp_publisher import WordPressPublisher

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
    page_title="Research of Ranknaser 2026 Topic & Search Intent on Google",
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

st.markdown('<div class="main-title">🤖 Research of Ranknaser 2026 Topic & Search Intent on Google</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">WordPress AI Content Generator & Auto-Publisher | Rank Math Ready • EEAT & GEO Optimized • 1-Click Publishing</div>', unsafe_allow_html=True)

# Session State Initialization
if "generated_article" not in st.session_state:
    st.session_state["generated_article"] = None
if "preset_keyword" not in st.session_state:
    st.session_state["preset_keyword"] = ""
if "research_results" not in st.session_state:
    st.session_state["research_results"] = None
if "multi_ai_results" not in st.session_state:
    st.session_state["multi_ai_results"] = None
if "is_credentials_unlocked" not in st.session_state:
    st.session_state["is_credentials_unlocked"] = False

# Load Saved Credentials
saved_cfg = load_config()

# Sidebar Configuration
with st.sidebar:
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
                
        # Hidden/Silent read of saved credentials for running app tasks
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

# Main Navigation Tabs
main_tab1, main_tab2, main_tab3 = st.tabs([
    "📝 Write & Auto-Publish Article", 
    "🤖 Multi-AI & 2026 Niche Intent Intelligence", 
    "🔎 AnswerThePublic Search Intent Researcher"
])

# --- TAB 1: ARTICLE GENERATOR ---
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

    # Generate Action
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

    # Display Generated Results
    if st.session_state["generated_article"]:
        article = st.session_state["generated_article"]
        target_kw = st.session_state.get("target_keyword", "")
        
        st.markdown("---")
        st.header("📊 Generated Content Preview")
        
        # Title & Meta Card
        st.markdown(f"""
        <div class="seo-card">
            <h4>🏷️ SEO Title (Starts with Main Keyword)</h4>
            <p><strong>{article.get('title')}</strong></p>
            <hr>
            <h4>📝 Rank Math Meta Description (Starts with Main Keyword)</h4>
            <p><em>{article.get('meta_description')}</em></p>
        </div>
        """, unsafe_allow_html=True)

        # Interactive Score Cards Section
        score_col1, score_col2, score_col3 = st.columns(3)
        
        seo_val = article.get("seo_score", 95)
        readability_val = article.get("readability_score", 88)
        human_val = article.get("human_touch_score", 96)
        readability_grade = article.get("readability_grade", "High Readability (Easy & Conversational)")
        
        with score_col1:
            st.metric(label="📈 Rank Math SEO Score", value=f"{seo_val}/100", delta="Rank Math Ready")
            st.progress(min(int(seo_val), 100))
            
        with score_col2:
            st.metric(label="📖 Readability Score", value=f"{readability_val}/100", delta=readability_grade)
            st.progress(min(int(readability_val), 100))
            
        with score_col3:
            st.metric(label="👤 Human-Touch Score", value=f"{human_val}/100", delta="Zero AI Clichés")
            st.progress(min(int(human_val), 100))
            
        if article.get("seo_checks"):
            with st.expander("✅ Rank Math SEO Checklist & Audits"):
                for check in article.get("seo_checks", []):
                    st.write(f"✔️ {check}")
        
        # Tabs for different components
        tab1, tab2, tab3 = st.tabs(["📄 Article HTML Body", "🔗 Internal Linking Suggestions", "📋 Raw Data / JSON"])
        
        with tab1:
            st.caption("Includes Table of Contents (TOC), EEAT Signals, Key Takeaways & FAQ Section")
            st.components.v1.html(article.get("content_html", ""), height=500, scrolling=True)
            with st.expander("Show HTML Code"):
                st.code(article.get("content_html", ""), language="html")
                
        with tab2:
            st.subheader("💡 Suggestions for Internal Linking")
            st.write("Target keywords and phrases found in the article text for internal links:")
            suggestions = article.get("internal_link_suggestions", [])
            if suggestions:
                for item in suggestions:
                    st.markdown(f"""
                    - **Anchor Phrase**: `{item.get('word_or_phrase')}` ({item.get('anchor_type')})  
                      👉 *Suggestion*: {item.get('suggestion')}
                    """)
            else:
                st.info("No explicit internal linking anchors highlighted.")
                
        with tab3:
            st.json(article)
            
        st.markdown("---")
        
        # Publishing Section
        st.header("🚀 1-Click WordPress Publishing")
        
        pub_col1, pub_col2 = st.columns([3, 1])
        with pub_col1:
            st.write(f"Target WordPress Site: `{wp_url if wp_url else 'Not Configured'}`")
            st.write(f"Post Status: **{post_status.upper()}** | Focus Keyword: **{target_kw}**")
            
        with pub_col2:
            if st.button("📤 Push to WordPress Now", type="primary", use_container_width=True):
                if not wp_url or not wp_user or not wp_app_pass:
                    st.error("❌ Please fill in WordPress URL, Username, and Application Password in sidebar.")
                else:
                    with st.spinner("Posting to WordPress REST API..."):
                        publisher = WordPressPublisher(wp_url, wp_user, wp_app_pass)
                        result = publisher.publish_post(
                            title=article.get("title"),
                            content_html=article.get("content_html"),
                            meta_description=article.get("meta_description"),
                            focus_keyword=target_kw,
                            status=post_status
                        )
                        
                        if result["success"]:
                            st.balloons()
                            st.success(f"🎉 {result['message']}")
                            st.markdown(f"👉 **[Edit Post in WP Admin]({result['edit_link']})**")
                            if result.get("post_link"):
                                st.markdown(f"🔗 **[View Published Post]({result['post_link']})**")
                        else:
                            st.error(f"❌ {result['message']}")

# --- TAB 2: MULTI-AI & 2026 NICHE INTENT INTELLIGENCE ---
with main_tab2:
    st.subheader("🌐 2026 Niche Topics & Multi-AI Search Intent Intelligence")
    st.write("Analyze 2026 trending sub-topics, Google AI Overviews (GEO), ChatGPT user prompts, Perplexity research queries, and Claude queries.")

    mai_col1, mai_col2 = st.columns([3, 1])
    with mai_col1:
        niche_input = st.text_input("🎯 Target Niche / Seed Topic (2026)", placeholder="e.g. Ranknaser, Laptop Price in BD, AI SEO Tools, Electric Vehicles")
    with mai_col2:
        mai_region = st.selectbox("🌐 Region Target", ["Bangladesh 🇧🇩", "Worldwide 🌐", "USA 🇺🇸", "India 🇮🇳"], key="mai_region_select")

    if st.button("🚀 Analyze 2026 Niche Trends & Multi-AI Intent", type="primary", use_container_width=True):
        if not gemini_api_key:
            st.error("❌ Please enter your Gemini API Key in the sidebar first.")
        elif not niche_input:
            st.error("❌ Please enter a Niche or Seed Topic.")
        else:
            with st.spinner("🧠 Analyzing 2026 Niche Trends, Google GEO, ChatGPT, Perplexity & Claude search patterns..."):
                try:
                    generator = AIContentGenerator(api_key=gemini_api_key, model_name=selected_model)
                    mai_data = generator.research_multi_ai_intent(niche_or_topic=niche_input, region=mai_region)
                    st.session_state["multi_ai_results"] = mai_data
                    st.success("✅ Multi-AI & 2026 Intent Analysis completed!")
                except Exception as e:
                    st.error(f"❌ Error during multi-AI analysis: {str(e)}")

    if st.session_state["multi_ai_results"]:
        res_ai = st.session_state["multi_ai_results"]
        st.markdown("---")
        
        # Niche 2026 Overview Card
        st.markdown(f"""
        <div class="seo-card">
            <h3>📈 2026 Niche Intelligence: <u>{res_ai.get('niche')}</u> ({res_ai.get('region')})</h3>
            <p><strong>Strategic 2026 Overview:</strong> {res_ai.get('niche_overview_2026')}</p>
        </div>
        """, unsafe_allow_html=True)

        st_tab1, st_tab2, st_tab3, st_tab4, st_tab5 = st.tabs([
            "🚀 2026 Trending Sub-Topics",
            "🔍 Google & AI Overviews (GEO)",
            "💬 ChatGPT User Prompts",
            "🧠 Perplexity Research Queries",
            "🤖 Claude & LLM Queries"
        ])

        # Sub-tab 1: 2026 Trending Sub-topics
        with st_tab1:
            st.write("#### 🎯 High ROI 2026 Sub-Topics & Content Angles")
            subtopics = res_ai.get("niche_trends_2026", []) or res_ai.get("trending_subtopics_2026", [])
            for idx, sub in enumerate(subtopics):
                s_topic = sub.get('topic', str(sub)) if isinstance(sub, dict) else str(sub)
                s_level = sub.get('trend_level', 'High ROI 2026') if isinstance(sub, dict) else 'High ROI 2026'
                s_angle = sub.get('content_angle', 'Search Intent Optimization') if isinstance(sub, dict) else 'Search Intent Optimization'
                c_s1, c_s2 = st.columns([4, 1])
                with c_s1:
                    st.markdown(f"🔥 **{s_topic}**  \n📌 *Trend Level*: `{s_level}` | 💡 *Strategy*: {s_angle}")
                with c_s2:
                    if st.button("📝 Write Article", key=f"btn_sub_{idx}"):
                        st.session_state["preset_keyword"] = s_topic
                        st.success(f"Selected '{s_topic}'. Switch to 'Write & Auto-Publish Article' tab!")

        # Sub-tab 2: Google Search & AI Overviews (GEO)
        with st_tab2:
            st.write("#### 🔍 Google Search Queries & Expected AI Overview (GEO) Answers")
            g_queries = res_ai.get("google_ai_overviews", []) or res_ai.get("google_ai_overview_intent", [])
            for idx, gq in enumerate(g_queries):
                g_text = gq.get('query', str(gq)) if isinstance(gq, dict) else str(gq)
                g_type = gq.get('intent_type', 'GEO Overview') if isinstance(gq, dict) else 'GEO Overview'
                g_sum = gq.get('ai_overview_summary', 'Generative Search Intent Answer') if isinstance(gq, dict) else 'Generative Search Intent Answer'
                c_g1, c_g2 = st.columns([4, 1])
                with c_g1:
                    st.markdown(f"""
                    <div class="query-card">
                        <strong>🔍 Search Query:</strong> {g_text} <span class="badge-keyword">{g_type}</span><br>
                        <em>🤖 Google AI Overview Result:</em> {g_sum}
                    </div>
                    """, unsafe_allow_html=True)
                with c_g2:
                    if st.button("📝 Write Article", key=f"btn_gq_{idx}"):
                        st.session_state["preset_keyword"] = g_text
                        st.success(f"Selected '{g_text}'. Switch to 'Write & Auto-Publish Article' tab!")

        # Sub-tab 3: ChatGPT User Prompts
        with st_tab3:
            st.write("#### 💬 Exact Prompts & Questions Real Users Ask ChatGPT")
            gpt_prompts = res_ai.get("chatgpt_popular_prompts", []) or res_ai.get("chatgpt_user_prompts", [])
            for idx, gpt in enumerate(gpt_prompts):
                gpt_text = gpt.get('prompt', str(gpt)) if isinstance(gpt, dict) else str(gpt)
                gpt_goal = gpt.get('user_goal', 'User Prompt Intent') if isinstance(gpt, dict) else 'User Prompt Intent'
                c_gp1, c_gp2 = st.columns([4, 1])
                with c_gp1:
                    st.markdown(f"""
                    <div class="query-card">
                        💬 <strong>ChatGPT User Prompt:</strong> "{gpt_text}"<br>
                        🎯 <em>User Goal:</em> {gpt_goal}
                    </div>
                    """, unsafe_allow_html=True)
                with c_gp2:
                    if st.button("📝 Write Article", key=f"btn_gpt_{idx}"):
                        st.session_state["preset_keyword"] = gpt_text
                        st.success(f"Selected '{gpt_text}'. Switch to 'Write & Auto-Publish Article' tab!")

        # Sub-tab 4: Perplexity Research Queries
        with st_tab4:
            st.write("#### 🧠 Deep Research Queries Users Ask on Perplexity.ai")
            px_queries = res_ai.get("perplexity_research_queries", [])
            for idx, px in enumerate(px_queries):
                px_text = px.get('query', str(px)) if isinstance(px, dict) else str(px)
                px_angle = px.get('research_angle', 'Deep Research Query') if isinstance(px, dict) else 'Deep Research Query'
                c_px1, c_px2 = st.columns([4, 1])
                with c_px1:
                    st.markdown(f"""
                    <div class="query-card">
                        🧠 <strong>Perplexity Query:</strong> "{px_text}"<br>
                        📊 <em>Research Angle:</em> {px_angle}
                    </div>
                    """, unsafe_allow_html=True)
                with c_px2:
                    if st.button("📝 Write Article", key=f"btn_px_{idx}"):
                        st.session_state["preset_keyword"] = px_text
                        st.success(f"Selected '{px_text}'. Switch to 'Write & Auto-Publish Article' tab!")

        # Sub-tab 5: Claude & LLM Queries
        with st_tab5:
            st.write("#### 🤖 Technical & Analytical Prompts Asked on Claude & LLMs")
            cl_queries = res_ai.get("claude_deep_dives", []) or res_ai.get("claude_analytical_queries", [])
            for idx, cl in enumerate(cl_queries):
                cl_text = cl.get('query', str(cl)) if isinstance(cl, dict) else str(cl)
                cl_focus = cl.get('focus_area', 'Deep Analytical Focus') if isinstance(cl, dict) else 'Deep Analytical Focus'
                c_cl1, c_cl2 = st.columns([4, 1])
                with c_cl1:
                    st.markdown(f"""
                    <div class="query-card">
                        🤖 <strong>Claude AI Prompt:</strong> "{cl_text}"<br>
                        🔬 <em>Focus Area:</em> {cl_focus}
                    </div>
                    """, unsafe_allow_html=True)
                with c_cl2:
                    if st.button("📝 Write Article", key=f"btn_cl_{idx}"):
                        st.session_state["preset_keyword"] = cl_text
                        st.success(f"Selected '{cl_text}'. Switch to 'Write & Auto-Publish Article' tab!")


# --- TAB 3: ANSWER THE PUBLIC INTENT RESEARCHER ---
with main_tab3:
    st.subheader("💡 Discover What People Are Searching (Answer The Public Style)")
    st.write("Analyze real user search intent, questions, PAA (People Also Ask), and commercial searches for Bangladesh & Worldwide.")

    res_col1, res_col2 = st.columns([3, 1])
    with res_col1:
        seed_input = st.text_input("🔍 Topic / Seed Keyword", placeholder="e.g. lenovo laptop, digital marketing, study in bd")
    with res_col2:
        target_region = st.selectbox("🌐 Target Region", ["Bangladesh 🇧🇩", "Worldwide 🌐", "USA 🇺🇸", "India 🇮🇳"])

    if st.button("🚀 Mine Search Intent & Questions", use_container_width=True):
        if not gemini_api_key:
            st.error("❌ Please enter your Gemini API Key in the sidebar first.")
        elif not seed_input:
            st.error("❌ Please enter a Topic or Seed Keyword.")
        else:
            with st.spinner("🔍 Mining Google & AI Search intent data..."):
                try:
                    generator = AIContentGenerator(api_key=gemini_api_key, model_name=selected_model)
                    res_data = generator.research_search_questions(seed_keyword=seed_input, region=target_region)
                    st.session_state["research_results"] = res_data
                    st.success("✅ Research completed successfully!")
                except Exception as e:
                    st.error(f"❌ Error performing research: {str(e)}")

    if st.session_state["research_results"]:
        data = st.session_state["research_results"]
        st.markdown("---")
        st.markdown(f"### 📊 Intent Insights for `{data.get('seed_keyword')}` ({data.get('region')})")

        q_tab1, q_tab2, q_tab3, q_tab4 = st.tabs(["❓ Search Questions", "💰 Local & Commercial Intent", "⚖️ Comparisons", "💡 People Also Ask (PAA)"])

        with q_tab1:
            st.write("#### Real User Search Questions (Answer The Public Style)")
            questions = data.get("questions", [])
            for idx, q in enumerate(questions):
                q_text = q.get("query") if isinstance(q, dict) else str(q)
                prefix = q.get("prefix", "Question") if isinstance(q, dict) else "Query"
                col_q1, col_q2 = st.columns([4, 1])
                with col_q1:
                    st.markdown(f"🔹 **[{prefix}]** {q_text}")
                with col_q2:
                    if st.button("📝 Write Article", key=f"btn_q_{idx}"):
                        st.session_state["preset_keyword"] = q_text
                        st.success(f"Selected '{q_text}'. Switch to 'Write & Auto-Publish Article' tab to generate!")

        with q_tab2:
            st.write("#### Commercial & Local Buyer Searches")
            comms = data.get("local_commercial_intent", [])
            for idx, c in enumerate(comms):
                col_c1, col_c2 = st.columns([4, 1])
                with col_c1:
                    st.markdown(f"🛒 `{c}`")
                with col_c2:
                    if st.button("📝 Write Article", key=f"btn_c_{idx}"):
                        st.session_state["preset_keyword"] = c
                        st.success(f"Selected '{c}'. Switch to 'Write & Auto-Publish Article' tab to generate!")

        with q_tab3:
            st.write("#### Comparison Searches (vs / alternatives)")
            comps = data.get("comparisons", [])
            for idx, comp in enumerate(comps):
                col_m1, col_m2 = st.columns([4, 1])
                with col_m1:
                    st.markdown(f"⚖️ `{comp}`")
                with col_m2:
                    if st.button("📝 Write Article", key=f"btn_m_{idx}"):
                        st.session_state["preset_keyword"] = comp
                        st.success(f"Selected '{comp}'. Switch to 'Write & Auto-Publish Article' tab to generate!")

        with q_tab4:
            st.write("#### People Also Ask (PAA) Topics")
            paas = data.get("people_also_ask", [])
            for idx, paa in enumerate(paas):
                col_p1, col_p2 = st.columns([4, 1])
                with col_p1:
                    st.markdown(f"💡 {paa}")
                with col_p2:
                    if st.button("📝 Write Article", key=f"btn_p_{idx}"):
                        st.session_state["preset_keyword"] = paa
                        st.success(f"Selected '{paa}'. Switch to 'Write & Auto-Publish Article' tab to generate!")

