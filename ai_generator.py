import json
import re
import requests
from google import genai
from google.genai import types

class AIContentGenerator:
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key.strip() if api_key else ""
        raw_model = model_name.strip() if model_name else "gemini-1.5-flash"
        if raw_model in ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp", ""]:
            self.model_name = raw_model
        else:
            self.model_name = "gemini-1.5-flash"

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
You are an expert SEO Content Strategist and Copywriter specialized in EEAT (Experience, Expertise, Authoritativeness, Trustworthiness) and Generative Engine Optimization (GEO).

Your task is to write a comprehensive, highly engaging, and Rank Math SEO-optimized article.

STRICT SEO & STRUCTURE REQUIREMENTS:
1. TITLE: MUST START EXACTLY with the main keyword '{main_keyword}'. Make it compelling, click-worthy, and under 60 characters.
2. META DESCRIPTION: MUST START EXACTLY with the main keyword '{main_keyword}'. Summarize the article persuasively in 140-155 characters.
3. CONTENT TYPE: {content_type}. WORD COUNT: Comprehensive article with a depth strictly between 1000 and 2000 words (around {word_count} words).
4. TABLE OF CONTENTS (TOC): Provide a clear Table of Contents at the beginning of the article body linking to all H2 sections using `<a href="#section-id">...</a>` tags.
5. EEAT & GEO FRIENDLY:
   - Include a "Key Takeaways" box near the top.
   - Use clear formatting, H2, H3 tags with IDs matching the TOC links.
   - Demonstrate first-hand experience, authoritative evidence, and actionable value.
   - Optimize for direct search answers (Generative Engine Optimization).
6. FAQ SECTION: Include 3-5 relevant FAQ items with H2 title "Frequently Asked Questions" at the end, formatted with clean semantic HTML.
7. INTERNAL LINKING SUGGESTIONS: Identify key phrases (including the main keyword '{main_keyword}' and suggested related terms: '{suggested_keywords}') within the text that should be hyperlinked internally.

OUTPUT FORMAT REQUIREMENTS:
You MUST output strictly valid JSON in the following schema:
{{
  "title": "Main Keyword ... Rest of Title",
  "meta_description": "Main Keyword ... Rest of meta description",
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
        model = self.model_name if self.model_name else "gemini-2.5-flash"

        # Method 1: Try official google-genai SDK
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
            pass

        # Method 2: Direct REST call to v1beta
        models_to_try = ["gemini-1.5-flash", "gemini-1.5-pro"]
        models_to_try = list(dict.fromkeys(models_to_try))
        
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
                    last_err = f"Model {m} HTTP {res.status_code}: {res.text}"
                    if res.status_code in [429, 400, 404]:
                        continue
            except Exception as e:
                last_err = str(e)

        raise Exception(f"Google Gemini API Quota Limit. Please retry in a few moments. Details: {last_err}")

    def list_available_models(self) -> list:
        """
        Dynamically fetches valid models supported for generateContent for the user's API Key.
        """
        if not self.api_key:
            return ["gemini-2.5-flash", "gemini-3.5-flash", "gemini-2.5-flash"]
        try:
            client = genai.Client(api_key=self.api_key)
            models_list = [m.name.replace("models/", "") for m in client.models.list() if "flash" in m.name or "pro" in m.name]
            if models_list:
                return models_list
        except Exception:
            pass
        return ["gemini-2.5-flash", "gemini-3.5-flash", "gemini-2.5-flash"]

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

CRITICAL REQUIREMENT: You MUST generate AT LEAST 10 distinct, high-quality results for EVERY SINGLE category array below.

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
    {{"prefix": "Which", "query": "which {seed_keyword} is right for beginners?"}},
    {{"prefix": "Can", "query": "can {seed_keyword} improve productivity?"}},
    {{"prefix": "Is", "query": "is {seed_keyword} safe to use?"}},
    {{"prefix": "Who", "query": "who needs {seed_keyword} in 2026?"}},
    {{"prefix": "When", "query": "when to upgrade {seed_keyword}?"}}
  ],
  "local_commercial_intent": [
    "top 10 {seed_keyword} in BD",
    "best shop for {seed_keyword} in Dhaka",
    "budget friendly {seed_keyword} options",
    "{seed_keyword} price list in Bangladesh 2026",
    "buy official {seed_keyword} with warranty",
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
        model = self.model_name if self.model_name else "gemini-2.5-flash"

        # Method 1: Try official SDK
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
            pass

        # Method 2: Direct REST call
        models_to_try = ["gemini-1.5-flash", "gemini-1.5-pro"]
        # Remove duplicates while preserving order
        models_to_try = list(dict.fromkeys(models_to_try))
        
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
                r = requests.post(url, headers=headers, json=payload, timeout=60)
                if r.status_code == 200:
                    raw = r.json()['candidates'][0]['content']['parts'][0]['text']
                    cleaned = re.sub(r'^```json\s*', '', raw.strip(), flags=re.MULTILINE)
                    cleaned = re.sub(r'```$', '', cleaned, flags=re.MULTILINE).strip()
                    return json.loads(cleaned)
                else:
                    last_err = f"Model {m} HTTP {r.status_code}: {r.text}"
                    # If quota/rate limit error (429 or RESOURCE_EXHAUSTED), continue to next model in loop
                    if r.status_code in [429, 400, 404]:
                        continue
            except Exception as e:
                last_err = str(e)
                
        raise Exception(f"Google Gemini API Quota Limit. Please retry in a few moments. Details: {last_err}")

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

CRITICAL MANDATE: You MUST provide AT LEAST 10 distinct, highly realistic items for EVERY SINGLE category array below (`trending_subtopics_2026`, `google_ai_overview_intent`, `chatgpt_user_prompts`, `perplexity_research_queries`, `claude_analytical_queries`). DO NOT output fewer than 10 items per category.

STRICT JSON OUTPUT FORMAT:
{{
  "niche": "{niche_or_topic}",
  "region": "{region}",
  "year": "2026",
  "niche_overview_2026": "A comprehensive strategic summary of this niche in 2026, audience intent, and high ROI topics.",
  "trending_subtopics_2026": [
    {{"topic": "Subtopic 1", "trend_level": "High Growth", "content_angle": "Pillar Strategy"}},
    {{"topic": "Subtopic 2", "trend_level": "High Volume", "content_angle": "Cluster Review"}},
    {{"topic": "Subtopic 3", "trend_level": "Emerging", "content_angle": "Tutorial"}},
    {{"topic": "Subtopic 4", "trend_level": "Trending 2026", "content_angle": "Buyer Guide"}},
    {{"topic": "Subtopic 5", "trend_level": "High ROI", "content_angle": "Case Study"}},
    {{"topic": "Subtopic 6", "trend_level": "High Volume", "content_angle": "Comparison"}},
    {{"topic": "Subtopic 7", "trend_level": "Emerging", "content_angle": "Troubleshooting"}},
    {{"topic": "Subtopic 8", "trend_level": "High Growth", "content_angle": "Best Practices"}},
    {{"topic": "Subtopic 9", "trend_level": "Trending", "content_angle": "Industry Report"}},
    {{"topic": "Subtopic 10", "trend_level": "High Demand", "content_angle": "Future Outlook"}}
  ],
  "google_ai_overview_intent": [
    {{"query": "google query 1", "ai_overview_summary": "summary 1", "intent_type": "Informational"}},
    {{"query": "google query 2", "ai_overview_summary": "summary 2", "intent_type": "Commercial"}},
    {{"query": "google query 3", "ai_overview_summary": "summary 3", "intent_type": "Transactional"}},
    {{"query": "google query 4", "ai_overview_summary": "summary 4", "intent_type": "Informational"}},
    {{"query": "google query 5", "ai_overview_summary": "summary 5", "intent_type": "Commercial BD"}},
    {{"query": "google query 6", "ai_overview_summary": "summary 6", "intent_type": "Informational"}},
    {{"query": "google query 7", "ai_overview_summary": "summary 7", "intent_type": "Commercial"}},
    {{"query": "google query 8", "ai_overview_summary": "summary 8", "intent_type": "Transactional"}},
    {{"query": "google query 9", "ai_overview_summary": "summary 9", "intent_type": "Informational"}},
    {{"query": "google query 10", "ai_overview_summary": "summary 10", "intent_type": "Commercial"}}
  ],
  "chatgpt_user_prompts": [
    {{"prompt": "ChatGPT prompt 1", "user_goal": "goal 1"}},
    {{"prompt": "ChatGPT prompt 2", "user_goal": "goal 2"}},
    {{"prompt": "ChatGPT prompt 3", "user_goal": "goal 3"}},
    {{"prompt": "ChatGPT prompt 4", "user_goal": "goal 4"}},
    {{"prompt": "ChatGPT prompt 5", "user_goal": "goal 5"}},
    {{"prompt": "ChatGPT prompt 6", "user_goal": "goal 6"}},
    {{"prompt": "ChatGPT prompt 7", "user_goal": "goal 7"}},
    {{"prompt": "ChatGPT prompt 8", "user_goal": "goal 8"}},
    {{"prompt": "ChatGPT prompt 9", "user_goal": "goal 9"}},
    {{"prompt": "ChatGPT prompt 10", "user_goal": "goal 10"}}
  ],
  "perplexity_research_queries": [
    {{"query": "Perplexity query 1", "research_angle": "angle 1"}},
    {{"query": "Perplexity query 2", "research_angle": "angle 2"}},
    {{"query": "Perplexity query 3", "research_angle": "angle 3"}},
    {{"query": "Perplexity query 4", "research_angle": "angle 4"}},
    {{"query": "Perplexity query 5", "research_angle": "angle 5"}},
    {{"query": "Perplexity query 6", "research_angle": "angle 6"}},
    {{"query": "Perplexity query 7", "research_angle": "angle 7"}},
    {{"query": "Perplexity query 8", "research_angle": "angle 8"}},
    {{"query": "Perplexity query 9", "research_angle": "angle 9"}},
    {{"query": "Perplexity query 10", "research_angle": "angle 10"}}
  ],
  "claude_analytical_queries": [
    {{"query": "Claude prompt 1", "focus_area": "focus 1"}},
    {{"query": "Claude prompt 2", "focus_area": "focus 2"}},
    {{"query": "Claude prompt 3", "focus_area": "focus 3"}},
    {{"query": "Claude prompt 4", "focus_area": "focus 4"}},
    {{"query": "Claude prompt 5", "focus_area": "focus 5"}},
    {{"query": "Claude prompt 6", "focus_area": "focus 6"}},
    {{"query": "Claude prompt 7", "focus_area": "focus 7"}},
    {{"query": "Claude prompt 8", "focus_area": "focus 8"}},
    {{"query": "Claude prompt 9", "focus_area": "focus 9"}},
    {{"query": "Claude prompt 10", "focus_area": "focus 10"}}
  ]
}}
"""
        model = self.model_name if self.model_name else "gemini-2.5-flash"

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
            pass

        # Method 2: Direct REST call
        models_to_try = ["gemini-1.5-flash", "gemini-1.5-pro"]
        models_to_try = list(dict.fromkeys(models_to_try))
        
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
                r = requests.post(url, headers=headers, json=payload, timeout=60)
                if r.status_code == 200:
                    raw = r.json()['candidates'][0]['content']['parts'][0]['text']
                    cleaned = re.sub(r'^```json\s*', '', raw.strip(), flags=re.MULTILINE)
                    cleaned = re.sub(r'```$', '', cleaned, flags=re.MULTILINE).strip()
                    return json.loads(cleaned)
                else:
                    last_err = f"Model {m} HTTP {r.status_code}: {r.text}"
                    if r.status_code in [429, 400, 404, 401]:
                        continue
            except Exception as e:
                last_err = str(e)

        raise Exception(f"Google Gemini API Error ({model}): {last_err}")

