import requests
from bs4 import BeautifulSoup
from storage import load, store
from urllib.parse import urljoin

session = requests.Session()
session.headers.update({"User-Agent": "NewsScraper/1.0"})

def getdata(url):
    response = session.get(url, timeout=10)
    return BeautifulSoup(response.text, "html.parser")

def fetch_articles(links, select_title, select_content, limit):
    data = load()
    existing_titles = {d["title"] for d in data} 
    articles = []

    for link in list(dict.fromkeys(links)):
        if len(articles) >= limit:
            break     

        soup = getdata(link)    
        if not soup: 
            continue 
        
        title_tag = soup.select(select_title)
        content_tag = soup.select(select_content)
        
        title = "".join(t.get_text(strip=True) for t in title_tag)    
        content = " ".join(t.get_text(strip=True) for t in content_tag)    
        
        if content and title not in existing_titles:
            articles.append({"title": title, "content": content})
            existing_titles.add(title)
    
    store(articles)

def risingnepal(limit, url = "https://risingnepaldaily.com/"):
    soup = getdata(url)
    if not soup: return
    cats = []
    for a in soup.select("a[href*='/categories/']"):
        href = str(a.get("href"))
        cats.append(urljoin(url, href))
    
    links = []
    for cat in list(dict.fromkeys(cats)):
        cat_soup = getdata(cat)
        for a in cat_soup.select("a[href*='/news/']"):
            href = str(a.get("href"))
            links.append(href)
    
    fetch_articles(links, "h1", "div.blog-details p", limit)

def kathmandupost(limit, url = "https://kathmandupost.com/"):
    soup = getdata(url)    
    if not soup: return
    links = []
    for a in soup.select("a[href]"):
        href = str(a.get("href"))
        if "20" in href:
            links.append(urljoin(url, href))
            
    fetch_articles(links, "title", "p", limit)

def himalayantimes(limit, url = "https://thehimalayantimes.com/"):
    soup = getdata(url)
    if not soup: return
    cats = []
    for a in soup.select("a.menu-item"):
        href = str(a.get("href"))
        cats.append(href + "/")
    
    links = []
    for cat in list(dict.fromkeys(cats)):
        cat_soup = getdata(cat)
        if not cat_soup: return
        for a in cat_soup.find_all("a"):
            href = str(a.get("href"))
            if href.startswith(cat):
                links.append(href)
     
    fetch_articles(links, "h1", "div.ht-article-details article div.post-content p", limit)

if __name__== "__main__":
    scrapers = [risingnepal, kathmandupost, himalayantimes]
    limit_per_site = 10
    for s in scrapers:
        print(f"Scraping {s.__name__}")
        s(limit_per_site)
    print("Completed")