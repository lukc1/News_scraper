# RAG Based News Scraper Chatbot
A chatbot that scrapes news articles from websites and answers questions using Retrieval Augmented Generation (RAG) with local ollama models.

Scrapes 10 articles each from sites:
-The Rising Nepal
-The Kathmandu Post
-The Himalayan Times


## Requirements
pip install -r requirements.txt
ollama
Embedding model: nomic-embed-text
llm model: Eg: llama3.2:3b, qwen3:4b


## Usage
git clone https://github.com/lukc1/Rag.git
cd rag
pip install -r requirements.txt
python news_scraper/newsscraper.py

ollama serve ## in another terminal
python chatbot.py
