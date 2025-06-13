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

def fetch_article_content(url, selector):
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        content = soup.select_one(selector)
        return content.get_text(separator=" ", strip=True) if content else ""
    except Exception as e:
        print(f"Error fetching content from {url}: {e}")
        return ""

def scrape_qiita():
    print("Scraping Qiita...")
    for keyword in KEYWORDS:
        search_url = f"https://qiita.com/search?q={keyword.replace(' ', '+')}"
        try:
            res = requests.get(search_url)
            soup = BeautifulSoup(res.text, "html.parser")
            articles_list = soup.select("div.searchResult_item")
            for article in articles_list:
                title_tag = article.select_one("h2.searchResult_itemTitle a")
                if title_tag:
                    title = title_tag.text.strip()
                    link = f"https://qiita.com{title_tag['href']}"
                    if match_keywords(title):
                        content = fetch_article_content(link, "div[class*='articleBody']")
                        summary = summarize_text(content)
                        articles.append(("Qiita", keyword, title, link, summary))
        except Exception as e:
            print(f"Error scraping Qiita for keyword '{keyword}': {e}")

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
                content = fetch_article_content(full_url, "main")
                summary = summarize_text(content)
                articles.append(("Zenn", "N/A", title, full_url, summary))
    except Exception as e:
        print(f"Error scraping Zenn: {e}")

def scrape_note():
    print("Scraping Note...")
    url = "https://note.com/"
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        articles_list = soup.select("a")
        for a in articles_list:
            title = a.text.strip()
            link = a.get("href")
            full_url = f"https://note.com{link}" if link and link.startswith("/") else ""
            if match_keywords(title) and full_url:
                content = fetch_article_content(full_url, "div.o-noteContent")
                summary = summarize_text(content)
                articles.append(("Note", "N/A", title, full_url, summary))
    except Exception as e:
        print(f"Error scraping Note: {e}")

# 実行
scrape_qiita()
scrape_zenn()
scrape_note()

# Markdown保存
with open(md_filename, "w", encoding="utf-8") as f:
    f.write(f"# Articles Collected on {today}\n\n")
    for source, keyword, title, url, summary in articles:
        f.write(f"## {title}\n")
        f.write(f"**Source**: {source}\n\n")
        f.write(f"**Keyword**: {keyword}\n\n")
        f.write(f"**Summary**:\n{summary}\n\n")
        f.write("---\n\n")

print(f"Saved {len(articles)} articles to {md_filename}")
