import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

# キーワード一覧
KEYWORDS = [
    "Claude Code",
    "Vibe Cording",
    "Obsidian",
    "Azure Open AI",
    "Copilot"
]

# 出力フォルダ
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 日付
today = datetime.now().strftime("%Y-%m-%d")

# Markdownファイル名
md_filename = os.path.join(OUTPUT_DIR, f"articles_{today}.md")

# 結果格納リスト
articles = []

def match_keywords(text):
    return any(keyword.lower() in text.lower() for keyword in KEYWORDS)

def summarize_text(text, max_sentences=3):
    sentences = text.split("。")
    summary = "。".join(sentences[:max_sentences]) + "。" if sentences else ""
    return summary.strip()

def fetch_article_content(url, selectors):
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        for selector in selectors:
            content = soup.select_one(selector)
            if content:
                return content.get_text(separator=" ", strip=True)
        return ""
    except Exception as e:
        print(f"Error fetching content from {url}: {e}")
        return ""

def scrape_zenn():
    print("Scraping Zenn...")
    url = "https://zenn.dev/"
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        articles_list = soup.select("article a")
        for a in articles_list:
            title = a.text.strip()
            link = a.get("href")
            full_url = f"https://zenn.dev{link}" if link else ""
            if match_keywords(title) and full_url:
                content = fetch_article_content(full_url, ["div[class*='ArticleContent']", "main"])
                summary = summarize_text(content)
                articles.append(("Zenn", "N/A", title, full_url, summary))
    except Exception as e:
        print(f"Error scraping Zenn: {e}")

# 実行（Zennのみ）
scrape_zenn()

# Markdown保存
with open(md_filename, "w", encoding="utf-8") as f:
    f.write(f"# Articles Collected on {today}\n\n")
    for source, keyword, title, url, summary in articles:
        f.write(f"## {title}\n")
        f.write(f"**Source**: {source}\n\n")
        f.write(f"**Keyword**: {keyword}\n\n")
        f.write(f"**Summary**:\n{summary}\n\n")
        f.write("---\n\n")

print(f"Saved {len(articles)} Zenn articles to {md_filename}")
