import json
import re
import requests
from google import genai
from google.genai import types

class AIContentGenerator:
    def __init__(self, api_key: str, model_name: str = "gemini-3.6-flash"):
        self.api_key = api_key.strip() if api_key else ""
        raw_model = model_name.strip() if model_name else "gemini-3.6-flash"
        self.model_name = raw_model

    def generate_article(
        self,
        main_keyword: str,
        suggested_keywords: str = "",
        content_type: str = "Standard Article",
        target_audience: str = "General",
        word_count: int = 1500
    ) -> dict:
        """
        Generates SEO & EEAT optimized content following Rank Math best practices.
        Returns a dictionary with title, meta_description, content_html, internal_links, and faq.
        """
        if not self.api_key:
            raise ValueError("❌ Gemini API Key is missing! Please paste your valid API Key in the sidebar and click Save Settings.")

        system_instructions = f"""
You are an expert Anti-AI Detection Copywriter and Veteran SEO Strategist specialized in writing 100% Undetectable, Human-Passed articles that BYPASS AI detectors (ZeroGPT, Originality.ai, CopyLeaks, ContentAtScale) while satisfying Rank Math SEO, EEAT, and GEO (Generative Engine Optimization).

YOUR PRIMARY GOAL: Write content that reads 100% like a authentic human expert wrote it from personal experience—ZERO AI FLAGS.

STRICT ANTI-AI DETECTION & HUMAN WRITING RULES (PERPLEXITY & BURSTINESS):
1. HIGH BURSTINESS (Vary Sentence Lengths Dramatically):
   - Mix short 3-6 word punchy sentences with longer, detailed analytical sentences.
   - Do NOT write paragraphs of equal lengths. Keep paragraph lengths asymmetrical (1 line, then 3 lines, then 2 lines).
2. HIGH PERPLEXITY (Unpredictable, Authentic Vocabulary):
   - ABSOLUTELY BANNED AI CLICHÉS & INTROS: Do NOT use "In today's fast-paced world", "In this comprehensive guide", "Welcome to", "In conclusion", "Delve", "Realm", "Tapestry", "Testament", "Beacon", "Furthermore", "Moreover", "Leverage", "Untangling", "Demystifying".
   - Start line 1 immediately with a strong, opinionated human insight or real-world problem statement.
3. AUTHENTIC HUMAN TONE & EEAT SIGNALS:
   - Use first-person perspective ("In my experience...", "When testing this...", "Let's be honest...").
   - Add real-world Bangladesh & global market nuances (e.g. official warranty vs unofficial market, Star Tech / Ryans BD context, budget realities in BDT).
   - Use active voice, rhetorical questions, bolded key phrases, and direct conversational energy.
4. RANK MATH SEO & STRUCTURE:
   - H1 Title: MUST START EXACTLY with main keyword '{main_keyword}'. Under 60 chars.
   - Meta Description: MUST START EXACTLY with main keyword '{main_keyword}'. 140-155 chars.
   - Word Count: Strictly between 300 and 1500 words (target around {word_count} words).
   - Heading Hierarchy: H1 for title, clean H2s for main sections, and H3s for sub-topics.
   - Table of Contents (TOC): Styled box at the top with clickable `<a href="#section-id">...</a>` links.
   - Key Takeaways Box: Styled summary near top for Google AI Overviews (GEO).
   - FAQ Section: 3-5 high-intent FAQ items with H2 "Frequently Asked Questions" in semantic HTML.

OUTPUT FORMAT REQUIREMENTS (STRICT VALID JSON ONLY):
{{
  "title": "Main Keyword ... Rest of Title",
  "meta_description": "Main Keyword ... Rest of meta description",
  "seo_score": 98,
  "seo_checks": ["Title starts with main keyword", "Meta description starts with keyword", "H1/H2/H3 structure followed", "TOC & FAQ included", "EEAT Signals present"],
  "readability_score": 92,
  "readability_grade": "High Readability (Easy & Conversational)",
  "human_touch_score": 99,
  "ai_detector_bypass_status": "Passed (High Burstiness & Zero AI Clichés)",
  "content_html": "<article>... HTML Content including TOC, Key Takeaways, H2s, H3s, Body, FAQs ...</article>",
  "internal_link_suggestions": [
    {{
      "word_or_phrase": "exact phrase from text",
      "anchor_type": "Main Keyword / LSI Keyword",
      "suggestion": "Link this to your relevant pillar/cluster article about [Topic]"
    }}
  ]
}}
"""

        prompt = f"""
Main Keyword: {main_keyword}
Suggested/LSI Keywords: {suggested_keywords}
Article Type: {content_type}
Target Audience: {target_audience}

Please generate the JSON response strictly adhering to all instructions.
Ensure the title and meta_description strictly START with '{main_keyword}'.
"""

        full_prompt = system_instructions + "\n\n" + prompt
        models_to_try = [self.model_name, "gemini-3.6-flash", "gemini-3.5-flash", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-flash-latest", "gemini-flash-lite-latest"]
        models_to_try = list(dict.fromkeys(models_to_try))

        # Method 1: Try official google-genai SDK
        for model in models_to_try:
            try:
                client = genai.Client(api_key=self.api_key)
                response = client.models.generate_content(
                    model=model,
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.7,
                        response_mime_type="application/json",
                    ),
                )
                if response and response.text:
                    raw_text = response.text
                    cleaned_text = re.sub(r'^```json\s*', '', raw_text.strip(), flags=re.MULTILINE)
                    cleaned_text = re.sub(r'```$', '', cleaned_text.strip(), flags=re.MULTILINE)
                    
                    article_data = json.loads(cleaned_text)
                    
                    if not article_data.get("title", "").strip().lower().startswith(main_keyword.strip().lower()):
                        article_data["title"] = f"{main_keyword}: {article_data.get('title', '')}"
                        
                    if not article_data.get("meta_description", "").strip().lower().startswith(main_keyword.strip().lower()):
                        article_data["meta_description"] = f"{main_keyword} - {article_data.get('meta_description', '')}"[:155]
                        
                    return article_data
            except Exception:
                continue

        # Method 2: Direct REST call fallback across available models
        last_err = None
        for m in models_to_try:
            payload = {
                "contents": [{"parts": [{"text": full_prompt}]}],
                "generationConfig": {"temperature": 0.7, "responseMimeType": "application/json"}
            }
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key
            }

            url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={self.api_key}"
            try:
                res = requests.post(url, headers=headers, json=payload, timeout=60)
                if res.status_code == 200:
                    res_data = res.json()
                    raw_text = res_data['candidates'][0]['content']['parts'][0]['text']
                    cleaned_text = re.sub(r'^```json\s*', '', raw_text.strip(), flags=re.MULTILINE)
                    cleaned_text = re.sub(r'```$', '', cleaned_text.strip(), flags=re.MULTILINE)
                    
                    article_data = json.loads(cleaned_text)
                    
                    if not article_data.get("title", "").strip().lower().startswith(main_keyword.strip().lower()):
                        article_data["title"] = f"{main_keyword}: {article_data.get('title', '')}"
                        
                    if not article_data.get("meta_description", "").strip().lower().startswith(main_keyword.strip().lower()):
                        article_data["meta_description"] = f"{main_keyword} - {article_data.get('meta_description', '')}"[:155]
                        
                    return article_data
                else:
                    last_err = f"HTTP {res.status_code}: {res.text}"
                    if res.status_code in [429, 400, 404]:
                        continue
            except Exception as e:
                last_err = str(e)

        raise Exception(f"⚠️ Google API Quota Exceeded / Rate Limit! আপনার এপিআই কী-টির গুগল ফ্রি টোকেন কোটা সাময়িকভাবে শেষ হয়েছে।\n\n💡 সমাধান:\n১. ১-২ মিনিট অপেক্ষা করে আবার চেষ্টা করুন।\n২. অথবা https://aistudio.google.com/app/apikey থেকে আরেকটি নতুন Free API Key বানিয়ে পেস্ট করে সেভ করুন।\n(গুগল রেসপন্স: {last_err})")

    def list_available_models(self) -> list:
        """
        Dynamically fetches valid models supported for generateContent for the user's API Key.
        """
        if not self.api_key:
            return ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-2.5-flash", "gemini-2.0-flash"]
        try:
            client = genai.Client(api_key=self.api_key)
            models_list = [m.name.replace("models/", "") for m in client.models.list() if "flash" in m.name or "pro" in m.name]
            if models_list:
                return models_list
        except Exception:
            pass
        return ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-2.5-flash", "gemini-2.0-flash"]

    def research_search_questions(self, seed_keyword: str, region: str = "Bangladesh") -> dict:
        """
        Mines real-world search queries, questions (AnswerThePublic style), People Also Ask (PAA),
        and commercial intent searches targeting Bangladesh or Worldwide.
        Returns AT LEAST 10 items per category.
        """
        if not self.api_key:
            raise ValueError("❌ Gemini API Key is missing! Please paste your valid API Key in the sidebar and click Save Settings.")

        system_prompt = f"""
You are an expert Search Engine Data Miner, Keyword Researcher, and Consumer Intent Analyst specializing in search behavior for {region} and Worldwide.

Your task is to analyze real-world search queries that users type into Google, AI Search Assistants (ChatGPT, Gemini, Perplexity), and search engines regarding the topic/keyword: '{seed_keyword}'.

Generate an "Answer The Public" style list of real user queries, categorized logically. You MUST provide AT LEAST 10 items for EACH category.

STRICT JSON OUTPUT FORMAT:
{{
  "seed_keyword": "{seed_keyword}",
  "region": "{region}",
  "questions": [
    {{"prefix": "What", "query": "what is the best {seed_keyword}?"}},
    {{"prefix": "How", "query": "how to choose {seed_keyword}?"}},
    {{"prefix": "Why", "query": "why is {seed_keyword} popular?"}},
    {{"prefix": "Where", "query": "where to buy {seed_keyword}?"}},
    {{"prefix": "Price/Budget", "query": "{seed_keyword} price in BD"}},
    {{"prefix": "Which", "query": "which {seed_keyword} is best for beginners?"}},
    {{"prefix": "Can", "query": "can {seed_keyword} be used for work?"}},
    {{"prefix": "Is", "query": "is {seed_keyword} worth buying in 2026?"}},
    {{"prefix": "Who", "query": "who sells authentic {seed_keyword} in BD?"}},
    {{"prefix": "When", "query": "when is the best time to buy {seed_keyword}?"}}
  ],
  "local_commercial_intent": [
    "top 10 {seed_keyword} in BD",
    "best shop for {seed_keyword} in Dhaka",
    "budget friendly {seed_keyword} options",
    "{seed_keyword} price in bangladesh 2026",
    "buy official {seed_keyword} online BD",
    "cheap {seed_keyword} deals near me",
    "best online store for {seed_keyword}",
    "original vs replica {seed_keyword} price",
    "wholesale {seed_keyword} supplier BD",
    "discount offer on {seed_keyword}"
  ],
  "comparisons": [
    "{seed_keyword} vs alternative",
    "is {seed_keyword} worth buying",
    "{seed_keyword} vs top competitor 2026",
    "pros and cons of {seed_keyword}",
    "best alternatives to {seed_keyword}",
    "{seed_keyword} vs budget version",
    "{seed_keyword} detailed feature comparison",
    "why choose {seed_keyword} over others",
    "{seed_keyword} upgrade comparison 2026",
    "should I buy {seed_keyword} or wait"
  ],
  "people_also_ask": [
    "Frequently asked question 1 about {seed_keyword}",
    "Frequently asked question 2 about {seed_keyword}",
    "Frequently asked question 3 about {seed_keyword}",
    "Frequently asked question 4 about {seed_keyword}",
    "Frequently asked question 5 about {seed_keyword}",
    "Frequently asked question 6 about {seed_keyword}",
    "Frequently asked question 7 about {seed_keyword}",
    "Frequently asked question 8 about {seed_keyword}",
    "Frequently asked question 9 about {seed_keyword}",
    "Frequently asked question 10 about {seed_keyword}"
  ]
}}
"""
        models_to_try = [self.model_name, "gemini-3.6-flash", "gemini-3.5-flash", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-flash-latest", "gemini-flash-lite-latest"]
        models_to_try = list(dict.fromkeys(models_to_try))

        # Method 1: Try official SDK
        for model in models_to_try:
            try:
                client = genai.Client(api_key=self.api_key)
                res = client.models.generate_content(
                    model=model,
                    contents=system_prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.7,
                        response_mime_type="application/json"
                    )
                )
                if res and res.text:
                    raw = res.text.strip()
                    cleaned = re.sub(r'^```json\s*', '', raw, flags=re.MULTILINE)
                    cleaned = re.sub(r'```$', '', cleaned, flags=re.MULTILINE).strip()
                    return json.loads(cleaned)
            except Exception:
                continue

        # Method 2: Direct REST call
        last_err = None
        for m in models_to_try:
            payload = {
                "contents": [{"parts": [{"text": system_prompt}]}],
                "generationConfig": {"temperature": 0.7, "responseMimeType": "application/json"}
            }
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key
            }

            url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={self.api_key}"
            try:
                r = requests.post(url, headers=headers, json=payload, timeout=30)
                if r.status_code == 200:
                    raw = r.json()['candidates'][0]['content']['parts'][0]['text']
                    cleaned = re.sub(r'^```json\s*', '', raw.strip(), flags=re.MULTILINE)
                    cleaned = re.sub(r'```$', '', cleaned, flags=re.MULTILINE).strip()
                    return json.loads(cleaned)
                else:
                    last_err = f"HTTP {r.status_code}: {r.text}"
                    if r.status_code in [429, 400, 404]:
                        continue
            except Exception as e:
                last_err = str(e)
                
        raise Exception(f"⚠️ Google API Quota Exceeded / Rate Limit! আপনার এপিআই কী-টির গুগল ফ্রি টোকেন কোটা সাময়িকভাবে শেষ হয়েছে।\n\n💡 সমাধান:\n১. ১-২ মিনিট অপেক্ষা করে আবার চেষ্টা করুন।\n২. অথবা https://aistudio.google.com/app/apikey থেকে আরেকটি নতুন Free API Key বানিয়ে পেস্ট করে সেভ করুন।\n(গুগল রেসপন্স: {last_err})")

    def research_multi_ai_intent(self, niche_or_topic: str, region: str = "Bangladesh 🇧🇩") -> dict:
        """
        Mines 2026 Niche Trends, Google AI Overviews (GEO), ChatGPT prompts, Perplexity research queries, 
        and Claude technical queries for a given niche/topic.
        Returns AT LEAST 10 items per category.
        """
        if not self.api_key:
            raise ValueError("❌ Gemini API Key is missing! Please paste your valid API Key in the sidebar and click Save Settings.")

        system_prompt = f"""
You are an advanced AI Search Intelligence Analyst and 2026 Niche Research Specialist.

Analyze the niche/topic: '{niche_or_topic}' for target region: '{region}' in the context of year 2026.

Generate comprehensive search intent insights formatted STRICTLY in valid JSON with AT LEAST 10 items per list:

STRICT JSON OUTPUT FORMAT:
{{
  "niche": "{niche_or_topic}",
  "region": "{region}",
  "google_ai_overviews": [
    "Overview query 1 for {niche_or_topic}",
    "Overview query 2 for {niche_or_topic}",
    "Overview query 3 for {niche_or_topic}",
    "Overview query 4 for {niche_or_topic}",
    "Overview query 5 for {niche_or_topic}",
    "Overview query 6 for {niche_or_topic}",
    "Overview query 7 for {niche_or_topic}",
    "Overview query 8 for {niche_or_topic}",
    "Overview query 9 for {niche_or_topic}",
    "Overview query 10 for {niche_or_topic}"
  ],
  "chatgpt_popular_prompts": [
    "ChatGPT prompt 1 for {niche_or_topic}",
    "ChatGPT prompt 2 for {niche_or_topic}",
    "ChatGPT prompt 3 for {niche_or_topic}",
    "ChatGPT prompt 4 for {niche_or_topic}",
    "ChatGPT prompt 5 for {niche_or_topic}",
    "ChatGPT prompt 6 for {niche_or_topic}",
    "ChatGPT prompt 7 for {niche_or_topic}",
    "ChatGPT prompt 8 for {niche_or_topic}",
    "ChatGPT prompt 9 for {niche_or_topic}",
    "ChatGPT prompt 10 for {niche_or_topic}"
  ],
  "perplexity_research_queries": [
    "Perplexity research query 1 for {niche_or_topic}",
    "Perplexity research query 2 for {niche_or_topic}",
    "Perplexity research query 3 for {niche_or_topic}",
    "Perplexity research query 4 for {niche_or_topic}",
    "Perplexity research query 5 for {niche_or_topic}",
    "Perplexity research query 6 for {niche_or_topic}",
    "Perplexity research query 7 for {niche_or_topic}",
    "Perplexity research query 8 for {niche_or_topic}",
    "Perplexity research query 9 for {niche_or_topic}",
    "Perplexity research query 10 for {niche_or_topic}"
  ],
  "claude_deep_dives": [
    "Claude technical query 1 for {niche_or_topic}",
    "Claude technical query 2 for {niche_or_topic}",
    "Claude technical query 3 for {niche_or_topic}",
    "Claude technical query 4 for {niche_or_topic}",
    "Claude technical query 5 for {niche_or_topic}",
    "Claude technical query 6 for {niche_or_topic}",
    "Claude technical query 7 for {niche_or_topic}",
    "Claude technical query 8 for {niche_or_topic}",
    "Claude technical query 9 for {niche_or_topic}",
    "Claude technical query 10 for {niche_or_topic}"
  ],
  "niche_trends_2026": [
    "2026 trend 1 for {niche_or_topic}",
    "2026 trend 2 for {niche_or_topic}",
    "2026 trend 3 for {niche_or_topic}",
    "2026 trend 4 for {niche_or_topic}",
    "2026 trend 5 for {niche_or_topic}",
    "2026 trend 6 for {niche_or_topic}",
    "2026 trend 7 for {niche_or_topic}",
    "2026 trend 8 for {niche_or_topic}",
    "2026 trend 9 for {niche_or_topic}",
    "2026 trend 10 for {niche_or_topic}"
  ]
}}
"""
        models_to_try = [self.model_name, "gemini-3.6-flash", "gemini-3.5-flash", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-flash-latest", "gemini-flash-lite-latest"]
        models_to_try = list(dict.fromkeys(models_to_try))

        # Method 1: Try official SDK
        for model in models_to_try:
            try:
                client = genai.Client(api_key=self.api_key)
                res = client.models.generate_content(
                    model=model,
                    contents=system_prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.7,
                        response_mime_type="application/json"
                    )
                )
                if res and res.text:
                    raw = res.text.strip()
                    cleaned = re.sub(r'^```json\s*', '', raw, flags=re.MULTILINE)
                    cleaned = re.sub(r'```$', '', cleaned, flags=re.MULTILINE).strip()
                    return json.loads(cleaned)
            except Exception:
                continue

        # Method 2: Direct REST call
        last_err = None
        for m in models_to_try:
            payload = {
                "contents": [{"parts": [{"text": system_prompt}]}],
                "generationConfig": {"temperature": 0.7, "responseMimeType": "application/json"}
            }
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key
            }

            url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={self.api_key}"
            try:
                r = requests.post(url, headers=headers, json=payload, timeout=30)
                if r.status_code == 200:
                    raw = r.json()['candidates'][0]['content']['parts'][0]['text']
                    cleaned = re.sub(r'^```json\s*', '', raw.strip(), flags=re.MULTILINE)
                    cleaned = re.sub(r'```$', '', cleaned, flags=re.MULTILINE).strip()
                    return json.loads(cleaned)
                else:
                    last_err = f"HTTP {r.status_code}: {r.text}"
                    if r.status_code in [429, 400, 404]:
                        continue
            except Exception as e:
                last_err = str(e)

        raise Exception(f"⚠️ Google API Quota Exceeded / Rate Limit! আপনার এপিআই কী-টির গুগল ফ্রি টোকেন কোটা সাময়িকভাবে শেষ হয়েছে।\n\n💡 সমাধান:\n১. ১-২ মিনিট অপেক্ষা করে আবার চেষ্টা করুন।\n২. অথবা https://aistudio.google.com/app/apikey থেকে আরেকটি নতুন Free API Key বানিয়ে পেস্ট করে সেভ করুন।\n(গুগল রেসপন্স: {last_err})")
