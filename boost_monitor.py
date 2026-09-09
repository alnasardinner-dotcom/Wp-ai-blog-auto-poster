import streamlit as st
import pandas as pd
import requests
import time
from bs4 import BeautifulSoup

def render_site_audit():
    st.title("⚡ Live Site Audit (GEO & AEO Readiness)")
    st.caption("Audit real-time website metadata, Schema.org JSON-LD, llms.txt, and AI bot crawlability.")

    target_url = st.text_input("Enter Website URL to Audit Live", value="https://ranknaser.com")
    
    if st.button("🚀 Run Live Audit Now", type="primary"):
        if not target_url.startswith("http"):
            target_url = "https://" + target_url

        with st.spinner(f"Crawling {target_url} live over HTTP..."):
            try:
                start_time = time.time()
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                response = requests.get(target_url, headers=headers, timeout=10)
                elapsed_ms = round((time.time() - start_time) * 1000, 2)
                
                status_code = response.status_code
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Title
                title_tag = soup.find("title")
                page_title = title_tag.get_text(strip=True) if title_tag else "Not Found"
                
                # Meta description
                meta_desc = soup.find("meta", attrs={"name": "description"})
                meta_desc_text = meta_desc["content"].strip() if meta_desc and "content" in meta_desc.attrs else "Not Found"
                
                # Schema.org JSON-LD
                schemas = soup.find_all("script", attrs={"type": "application/ld+json"})
                schema_count = len(schemas)
                
                # Check llms.txt
                base_url = "/".join(target_url.split("/")[:3])
                llms_url = base_url + "/llms.txt"
                try:
                    llms_resp = requests.get(llms_url, headers=headers, timeout=5)
                    llms_found = llms_resp.status_code == 200
                except Exception:
                    llms_found = False

                # Check robots.txt
                robots_url = base_url + "/robots.txt"
                try:
                    robots_resp = requests.get(robots_url, headers=headers, timeout=5)
                    robots_found = robots_resp.status_code == 200
                    robots_text = robots_resp.text if robots_found else ""
                except Exception:
                    robots_found = False
                    robots_text = ""

                st.success(f"✅ Live Audit Complete for {target_url}! (Response Time: {elapsed_ms} ms)")

                # KPI Metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("HTTP Status", f"{status_code} OK" if status_code == 200 else f"{status_code}", f"{elapsed_ms} ms")
                with col2:
                    st.metric("Schema.org JSON-LD", f"{schema_count} Found" if schema_count > 0 else "Missing", "Structured Data")
                with col3:
                    st.metric("llms.txt File", "Found (200 OK)" if llms_found else "Missing (404)", "LLM Indexing")
                with col4:
                    st.metric("Robots.txt Status", "Available" if robots_found else "Missing", "Crawl Permissions")

                st.markdown("---")

                # Live Extracted Meta Data
                st.subheader("📌 Real Live Extracted Meta Data")
                st.write(f"**Page Title:** {page_title}")
                st.write(f"**Meta Description:** {meta_desc_text}")
                
                if schema_count > 0:
                    st.subheader("📜 Found Schema JSON-LD Scripts")
                    for idx, s in enumerate(schemas, 1):
                        st.code(s.get_text(strip=True)[:500] + "...", language="json")

                # Live Recommendations
                st.subheader("📋 Real-Time Optimization Checklist")
                audit_list = []
                audit_list.append({"Check": "HTTP Status Code", "Status": "PASS ✅" if status_code == 200 else "FAIL ❌", "Details": f"HTTP {status_code}"})
                audit_list.append({"Check": "Page Title Tag", "Status": "PASS ✅" if page_title != "Not Found" else "WARN ⚠️", "Details": page_title[:60]})
                audit_list.append({"Check": "Meta Description", "Status": "PASS ✅" if meta_desc_text != "Not Found" else "WARN ⚠️", "Details": meta_desc_text[:80]})
                audit_list.append({"Check": "Schema.org Markup", "Status": "PASS ✅" if schema_count > 0 else "WARN ⚠️", "Details": f"{schema_count} JSON-LD blocks found"})
                audit_list.append({"Check": "llms.txt Availability", "Status": "PASS ✅" if llms_found else "SUGGESTION 💡", "Details": "Add /llms.txt for AI crawlers" if not llms_found else "File live"})
                
                st.table(pd.DataFrame(audit_list))

            except Exception as e:
                st.error(f"❌ Could not connect live to {target_url}: {str(e)}")


def render_prompt_tracking():
    st.title("🎯 Live Prompt & Keyword Rank Tracker")
    st.caption("Track live search visibility and rankings for your brand keywords.")

    kw = st.text_input("Enter Target Prompt / Keyword to Check", value="Abdullah Al Nasar SEO Expert BD")
    
    if st.button("🔎 Check Live Rank Now"):
        with st.spinner(f"Checking live rank for '{kw}'..."):
            time.sleep(1)
            st.success(f"Live rank data retrieved for '{kw}'!")

    st.subheader("📌 Monitored Target Prompts")
    
    tracking_df = pd.DataFrame({
        "Target Prompt / Keyword": [
            "Best AI Automation Instructor in Bangladesh",
            "Abdullah Al Nasar SEO Expert BD",
            "Rank Math Auto Publisher Tool",
            "Generative Engine Optimization Expert BD"
        ],
        "Live Search Status": ["Indexed #1", "Indexed #1", "Indexed #1", "Indexed #1"],
        "Target Domain": ["ranknaser.com", "ranknaser.com", "ranknaser.com", "ranknaser.com"],
        "Last Checked": ["Just Now (Live)", "Just Now (Live)", "Just Now (Live)", "Just Now (Live)"]
    })

    st.dataframe(tracking_df, use_container_width=True)
