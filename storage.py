import json
def load(filename="news.json"):
    try:
        with open(filename,'r',encoding= 'utf-8') as f:
            data = json.load(f)
            return data
        
    except FileNotFoundError:
        data = []
        return data
    
def store(data, filename='news.json'):
    with open(filename,'w',encoding = 'utf-8') as f:
        json.dump (data, f, indent=4, ensure_ascii= False)