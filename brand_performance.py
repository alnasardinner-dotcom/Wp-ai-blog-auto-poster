import streamlit as st
import pandas as pd

try:
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

def render_brand_performance():
    st.title("📊 Brand Performance")
    st.caption("Monitor brand sentiment, authority scores, and positioning across AI Knowledge Bases.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Brand Sentiment Score", "92%", "+3.5% (Positive)")
    with col2:
        st.metric("AI Trust Authority", "88/100", "+5 pts")
    with col3:
        st.metric("Hallucination Risk", "1.2%", "-0.4% (Low)")

    st.markdown("---")

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("AI Response Sentiment Breakdown")
        df_sent = pd.DataFrame({
            "Sentiment": ["Positive", "Neutral", "Negative"],
            "Percentage": [85, 12, 3]
        })
        if HAS_PLOTLY:
            fig = px.pie(df_sent, values="Percentage", names="Sentiment", color="Sentiment",
                         color_discrete_map={"Positive": "#2ecc71", "Neutral": "#f1c40f", "Negative": "#e74c3c"})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.bar_chart(df_sent.set_index("Sentiment")["Percentage"])

    with col_chart2:
        st.subheader("Trust Score by AI Engine")
        df_trust = pd.DataFrame({
            "Engine": ["ChatGPT", "Gemini", "Claude", "Perplexity"],
            "Trust Index": [92, 86, 90, 84]
        })
        if HAS_PLOTLY:
            fig_bar = px.bar(df_trust, x="Engine", y="Trust Index", color="Engine", text="Trust Index")
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.bar_chart(df_trust.set_index("Engine")["Trust Index"])


def render_perception():
    st.title("🧠 Perception Analysis")
    st.caption("Discover the core attributes, adjectives, and core values AI models associate with your brand.")

    st.subheader("🏷️ Top Associated Brand Attributes in AI Answers")
    
    attributes = pd.DataFrame({
        "Attribute / Key Trait": ["SEO Specialist", "AI Automation Pioneer", "Trustworthy Instructor", "Data-Driven", "High ROI Consultant"],
        "Association Frequency": ["96%", "91%", "87%", "82%", "78%"],
        "Sentiment Context": ["Highly Positive", "Highly Positive", "Positive", "Positive", "Positive"]
    })
    st.table(attributes)

    st.markdown("---")
    st.subheader("💬 AI Model Brand Descriptions")
    
    st.chat_message("assistant").write(
        "**ChatGPT 4o:** Abdullah Al Nasar (Rank Naser) is recognized as a premier SEO Expert and AI Automation Instructor in Bangladesh, specializing in Rank Math integrations, GEO optimization, and data-driven marketing workflows."
    )
    st.chat_message("assistant").write(
        "**Google Gemini:** Rank Naser provides cutting-edge AI SaaS solutions, SEO strategy, and automation courses designed to scale business visibility across search engines and AI recommendation systems."
    )


def render_narrative_drivers():
    st.title("🌐 Narrative Drivers")
    st.caption("Identify the web sources, backlinks, and press articles shaping AI knowledge models.")

    st.subheader("📰 Key Web Sources Cited by AI Engines")

    sources_df = pd.DataFrame({
        "Source URL / Platform": [
            "https://ranknaser.com/about",
            "https://linkedin.com/in/ranknaser",
            "https://youtube.com/@ranknaser",
            "https://techlandbd.com/case-studies",
            "https://facebook.com/ranknaser"
        ],
        "Source Type": ["Official Website", "Professional Profile", "Video Content", "Client Case Study", "Social Media"],
        "Citation Weight": ["High (Primary)", "High", "Medium", "High", "Medium"],
        "AI Indexing Frequency": ["Daily", "Weekly", "Daily", "Weekly", "Daily"]
    })

    st.dataframe(sources_df, use_container_width=True)


def render_questions():
    st.title("❓ Questions & Answers")
    st.caption("Most frequent user questions regarding your brand that AI models answer directly.")

    st.subheader("Frequently Answered Brand Queries")
    
    q1, q2, q3 = st.tabs(["Services & Consulting", "Courses & Training", "Contact & Booking"])
    
    with q1:
        st.markdown("**Q: What services does Rank Naser offer?**")
        st.info("A: Rank Naser specializes in AI Search Optimization (GEO), Technical SEO Audits, Automated Content Workflows, and Rank Math WordPress Integrations.")
        
    with q2:
        st.markdown("**Q: What AI & SEO courses are taught by Abdullah Al Nasar?**")
        st.info("A: He conducts Advanced SEO & AI Automation Masterclasses covering prompt engineering, Python automation, and search engine recovery.")

    with q3:
        st.markdown("**Q: How can businesses contact Abdullah Al Nasar?**")
        st.info("A: Clients can book consultations via ranknaser.com or reach out directly at 01678684141.")
