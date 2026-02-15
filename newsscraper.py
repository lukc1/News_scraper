import requests
from bs4 import BeautifulSoup
import time
import json

session = requests.Session()
session.headers.update({"User-Agent" : "Mozilla/5.0"})

def getdata(url):
    response = session.get(url, timeout=10)
    html = response.text
    return BeautifulSoup(html, "html.parser")

def filterlink(url, prefix=""):
    soup = getdata(url)
    filtered = []
    for link in soup.select("a"):
        links = str(link.get("href"))
        if links.startswith(prefix):
            filtered.append(links)

    return list(dict.fromkeys(filtered))

def risingnepal(limit):
    url = "https://risingnepaldaily.com"
    categories = (filterlink(url, f"{url}/categories"))

    newslinks = []
    prefix = f"{url}/news/"
    for url in categories:
        newslinks.extend(filterlink(url, prefix))
    newslinks = list(dict.fromkeys(newslinks))[:limit]

    news = []
    for link in newslinks:
        soup = getdata(link)
        title_tag = soup.select_one("h1")
        date_tag = soup.select_one("span.mr-3.font-size-16")
        content_tag = soup.select("div.blog-details p")

        title = title_tag.get_text(strip=True) if title_tag else ""
        date = date_tag.get_text(strip=True) if date_tag else ""
        content = ""
        for p in content_tag:
            paragraphs = p.get_text(strip= True)
            content += paragraphs + " "
        news.append({
            "title": title, 
            "date": date, 
            "content": content
            })
        
    with open("news.json",'w', encoding= "utf-8") as f:
        json.dump(news, f, indent= 4, ensure_ascii= False)

risingnepal(limit=10)