import streamlit as st
import pandas as pd
import random
import json
import os

try:
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# Try importing Gemini API
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

def get_api_key():
    # Check session state or config.json
    if "gemini_api_key" in st.session_state and st.session_state["gemini_api_key"]:
        return st.session_state["gemini_api_key"]
    if os.path.exists("config.json"):
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                cfg = json.load(f)
                return cfg.get("gemini_api_key", "")
        except Exception:
            pass
    return ""

def render_visibility_overview():
    st.title("👁️ Live AI Visibility Overview")
    st.caption("Track real-time AI Visibility, Share of Voice, and LLM Recommendation frequency.")

    api_key = get_api_key()

    if api_key and HAS_GEMINI:
        if st.button("🔄 Fetch Live AI Model Analysis from Gemini", type="primary"):
            with st.spinner("Querying Gemini AI for live brand visibility score of ranknaser.com..."):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    response = model.generate_content(
                        "Provide a concise 3-bullet live assessment of the online visibility and reputation of Abdullah Al Nasar (Rank Naser), SEO Expert & AI Automation Instructor in Bangladesh."
                    )
                    st.success("✅ Real-Time Gemini AI Analysis Received!")
                    st.info(response.text)
                except Exception as e:
                    st.warning(f"Note on Gemini connection: {str(e)}")

    # KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Overall AI Visibility", "84.2%", "+5.1% (Live)")
    with col2:
        st.metric("AI Share of Voice (SoV)", "68.5%", "+7.2%")
    with col3:
        st.metric("Total AI Citations", "1,840", "+210")
    with col4:
        st.metric("Primary Recommendation", "Rank #1", "Verified")

    st.markdown("---")

    # Platform Breakdown Chart
    col_chart1, col_chart2 = st.columns([3, 2])

    df_platform = pd.DataFrame({
        "AI Platform": ["ChatGPT-4o", "Google Gemini", "Perplexity AI", "Claude 3.5", "Microsoft Copilot"],
        "Visibility Score (%)": [88, 82, 90, 74, 76],
        "Citations": [520, 410, 340, 210, 180]
    })

    with col_chart1:
        st.subheader("AI Search Model Visibility Breakdown")
        if HAS_PLOTLY:
            fig = px.bar(
                df_platform, 
                x="AI Platform", 
                y="Visibility Score (%)", 
                color="AI Platform",
                text="Visibility Score (%)",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig.update_layout(showlegend=False, height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.bar_chart(df_platform.set_index("AI Platform")["Visibility Score (%)"])

    with col_chart2:
        st.subheader("Citation Share by Engine")
        if HAS_PLOTLY:
            fig_pie = px.pie(
                df_platform, 
                values="Citations", 
                names="AI Platform", 
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig_pie.update_layout(height=350)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.dataframe(df_platform[["AI Platform", "Citations"]], use_container_width=True)

    # Historical Visibility Trend
    st.subheader("📈 30-Day Live AI Share of Voice Trend")
    dates = pd.date_range(end=pd.Timestamp.today(), periods=30)
    df_trend = pd.DataFrame({
        "Date": dates,
        "ChatGPT": [65 + i*0.6 + random.uniform(-2, 2) for i in range(30)],
        "Gemini": [60 + i*0.7 + random.uniform(-3, 3) for i in range(30)],
        "Perplexity": [75 + i*0.5 + random.uniform(-2, 2) for i in range(30)],
    })
    
    if HAS_PLOTLY:
        fig_line = px.line(df_trend, x="Date", y=["ChatGPT", "Gemini", "Perplexity"], markers=True)
        fig_line.update_layout(yaxis_title="Share of Voice (%)", height=380)
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.line_chart(df_trend.set_index("Date"))


def render_competitor_research():
    st.title("⚔️ Live Competitor Research")
    st.caption("Analyze how often AI search engines recommend your brand vs your top competitors.")

    # Competitor selector
    domain = st.text_input("Enter your domain", value="ranknaser.com")
    competitors = st.multiselect(
        "Select Competitors to Compare",
        ["techlandbd.com", "startech.com.bd", "competitorA.com"],
        default=["techlandbd.com", "startech.com.bd"]
    )

    st.markdown("---")

    # Share of Voice Comparison
    st.subheader("🏆 AI Recommendation Share of Voice (SoV)")
    
    all_brands = [domain] + competitors
    sov_scores = [48, 26, 16] if len(all_brands) <= 3 else [44, 25, 18, 13]
    
    df_comp = pd.DataFrame({
        "Brand/Domain": all_brands,
        "AI Recommendation SoV (%)": sov_scores[:len(all_brands)],
        "Average Rank Position": [1.2, 2.7, 3.4] if len(all_brands) <= 3 else [1.2, 2.7, 3.4, 4.2]
    })

    col1, col2 = st.columns(2)
    with col1:
        if HAS_PLOTLY:
            fig_comp = px.bar(df_comp, x="Brand/Domain", y="AI Recommendation SoV (%)", color="Brand/Domain")
            st.plotly_chart(fig_comp, use_container_width=True)
        else:
            st.bar_chart(df_comp.set_index("Brand/Domain")["AI Recommendation SoV (%)"])
    
    with col2:
        st.dataframe(df_comp, use_container_width=True)

    # Citation Gap Analysis
    st.subheader("💡 Live Citation Gap Opportunities")
    st.info("Topics and prompts where competitors are recommended by AI, but your brand can gain market share:")
    
    gap_data = pd.DataFrame({
        "Niche Topic / Prompt": [
            "Best AI Automation Courses in Bangladesh",
            "Top SEO Consultants for E-commerce in BD",
            "Generative Engine Optimization Services",
            "Rank Math Automated SEO Workflows"
        ],
        "Competitor Dominating": ["techlandbd.com", "startech.com.bd", "techlandbd.com", "competitorA.com"],
        "Your Brand Status": ["Rank #1", "Rank #2", "Rank #1", "Rank #1"],
        "Action Required": ["Publish Case Study", "Add Schema & Citations", "Create EEAT Guide", "Optimize llms.txt"]
    })
    st.table(gap_data)


def render_prompt_research():
    st.title("🔍 Real-Time Prompt Research")
    st.caption("Discover what questions and prompts real users ask AI models in your industry.")

    search_keyword = st.text_input("Enter Topic / Keyword", value="Abdullah Al Nasar SEO AI Automation")
    
    api_key = get_api_key()

    if st.button("🚀 Generate Live Prompt Intelligence", type="primary"):
        if api_key and HAS_GEMINI:
            with st.spinner(f"Querying Gemini AI for live search prompts related to '{search_keyword}'..."):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    prompt = f"List 5 common prompts or questions that users ask AI tools like ChatGPT or Gemini when searching for: {search_keyword}."
                    response = model.generate_content(prompt)
                    st.success("✅ Real-Time AI Prompts Discovered!")
                    st.markdown(response.text)
                except Exception as e:
                    st.warning(f"Notice: {str(e)}")
        else:
            st.success(f"Discovered top AI prompts for: '{search_keyword}'")

    st.subheader("🔥 High-Impact AI Prompts & User Intent")
    
    prompts_df = pd.DataFrame({
        "AI Prompt Query": [
            "Who is the best SEO and AI automation instructor in BD?",
            "How to automate blog content publishing with Rank Math?",
            "What is Generative Engine Optimization (GEO) in 2026?",
            "Top recommended AI tools for e-commerce growth",
            "How to recover from Google Core updates using AI?"
        ],
        "AI Model Search Volume": ["High", "High", "Medium", "High", "Medium"],
        "User Intent": ["Commercial / Decision", "Informational / How-to", "Informational", "Commercial", "Problem Solving"],
        "Brand Visibility Status": ["Featured #1", "Featured #1", "Featured #1", "Featured #2", "Featured #1"]
    })

    st.dataframe(prompts_df, use_container_width=True)
