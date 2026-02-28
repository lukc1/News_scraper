import json

def load(filename="news.jsonl"):
    try:
        with open(filename,'r',encoding= 'utf-8') as f:
            return [json.loads(line) for line in f if line.strip()]
    except FileNotFoundError:
        return []
    
def store(data, filename='news.jsonl'):
    with open(filename, 'a', encoding='utf-8') as f:
        for article in data:
            f.write(json.dumps(article, ensure_ascii=False) + '\n')