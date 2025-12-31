import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from urllib.parse import urlparse
import time


def is_valid_url(url):
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https") and "." in parsed.netloc


def scrape(website):
    if not is_valid_url(website):
        print(f"[SCRAPER] ❌ Invalid URL skipped: {website}")
        return "[ERROR] Invalid URL"

    chrome_driver_path = r"C:/Users/Draupadi Dream trust/Desktop/INDICA-main/ai_engine/chromedriver.exe"
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/117 Safari/537.36")

    driver = webdriver.Chrome(service=Service(chrome_driver_path), options=options)

    try:
        print(f"[SCRAPER] Visiting: {website}")
        driver.get(website)
        driver.implicitly_wait(5)
        time.sleep(2)
        html = driver.page_source

        if len(html.strip()) < 500:
            print("[SCRAPER] Warning: Very short page source — might be blocked or JS-heavy.")

        return html

    except Exception as e:
        print(f"[SCRAPER ERROR] Failed to scrape {website}: {e}")
        return f"[ERROR] {e}"

    finally:
        driver.quit()


def extract_research_json(text):
    cleaned = re.sub(r"```(?:json)?", "", text).replace("```", "").strip()
    try:
        parsed = json.loads(cleaned)
        return {
            "should_search": parsed.get("should_search", False),
            "summary": parsed.get("summary", "No summary provided."),
            "filename": parsed.get("filename", "research_output.txt"),
            "raw_text": parsed.get("raw_text", ""),
            "links": parsed.get("links", [])
        }
    except json.JSONDecodeError:
        return {
            "should_search": False,
            "summary": "Gemini could not parse the result.",
            "filename": "invalid_response.txt",
            "raw_text": text,
            "links": []
        }


def run_gemini_research(query):
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)

        prompt = f"""
You are INDICA's smart research agent.

The user has asked: \"{query}\"

Your goal:
1. Give a deep but readable summary of the topic using your knowledge.
2. If the topic needs external sources (gov data, news), include a field 'should_search': true.
3. Suggest a filename like: \"yamuna_flow_distribution.txt\".
4. Include a 'summary' and a 'raw_text' version.
5. In 'links', list only **real, valid URLs** to external government or news websites. No search queries, no text phrases. Example:
   ["https://cpcb.nic.in/uploads/final_reports/Yamuna_2024_quality_report.pdf"]

Format:
{{
  "should_search": true/false,
  "summary": "...",
  "filename": "...",
  "raw_text": "...",
  "links": ["https://...", "https://..."]
}}

NO markdown. NO extra commentary. Plain JSON only.
"""

        response = model.generate_content(prompt)
        parsed = extract_research_json(response.text.strip())
        scraped_data = []

        if parsed["should_search"] and parsed["links"]:
            for url in parsed["links"]:
                try:
                    print(f"[RESEARCH] Scraping {url}...")
                    content = scrape(url)
                    if "[ERROR]" in content:
                        print(f"[RESEARCH] Failed to scrape: {url}")
                    scraped_data.append({"url": url, "content": content[:6000]})
                except Exception as e:
                    print(f"[RESEARCH] Exception: {e}")
                    scraped_data.append({"url": url, "content": f"Error scraping: {e}"})

            html_texts = "\n\n".join([f"URL: {d['url']}\nHTML:\n{d['content']}" for d in scraped_data])

            insight_prompt = f"""
You are INDICA, a smart AI researcher.

The user is investigating: \"{query}\"

Below is HTML content scraped from web pages. Please:
- Extract **numerical data**, **source-wise water flow volumes**, and **agency names**.
- If possible, summarize in a table (e.g., Delhi: glacier=X, rainfall=Y, etc.)
- Merge this with your own knowledge into a refined final summary.
- Omit irrelevant content (e.g., menus, cookie popups).

CONTENT:
{html_texts}

Return in JSON:
{{
  "summary": "Improved summary with combined info",
  "raw_text": "Detailed narrative",
  "table": [{{"state": ..., "glacier": ..., "rainfall": ..., ...}}],
  "agencies": ["CWC", "MoWR", ...]
}}
"""

            insight_response = model.generate_content(insight_prompt)
            try:
                merged = json.loads(re.sub(r"```(?:json)?", "", insight_response.text).replace("```", "").strip())
                parsed["summary"] = merged.get("summary", parsed["summary"])
                parsed["raw_text"] = merged.get("raw_text", parsed["raw_text"])
                parsed["table"] = merged.get("table", [])
                parsed["agencies"] = merged.get("agencies", [])
            except:
                parsed["raw_text"] += "\n\n[WARNING] Could not parse enhanced insight."

        parsed["scraped"] = scraped_data
        return parsed

    except Exception as e:
        return {
            "should_search": True,
            "summary": f"Gemini error: {e}",
            "filename": "gemini_error.txt",
            "raw_text": "",
            "links": [],
            "scraped": []
        }
