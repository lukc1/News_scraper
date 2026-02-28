from ollama import Client
import json
import os
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter

client = chromadb.PersistentClient()
remote_client = Client(host=f"http://localhost:11434")
collection = client.get_or_create_collection(name="articles_demo")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200, chunk_overlap=20, separators=["."]
)

with open("counter.txt", "r") as f:
    counter = int(f.read().strip())

print("Reading articles.jsonl and generating embeddings...")
with open("articles.jsonl", "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if i < counter:
            print("Skipping already processed article:", i)
            continue
        article = json.loads(line)
        content = article["content"]
        sentences = text_splitter.split_text(content)
        # print(sentences)
        # print("-------------")
        for each_sentence in sentences:
            response = remote_client.embed(
                model="nomic-embed-text", input=f"search_document: {content}"
            )
            embedding = response["embeddings"][0]

            collection.add(
                ids=[f"article_{i}"],
                embeddings=[embedding],
                documents=[each_sentence],
                metadatas=[{"title": article["title"]}],
            )
        counter += 1

print("Database built successfully!")
with open("counter.txt", "w") as f:
    f.write(str(counter))


while True:
    query = input("\nHow may I help you? \nQuery: ")

    if query == "bye":
        break
    query_embed = remote_client.embed(
        model="nomic-embed-text", input=f"query: {query}"
    )["embeddings"][0]
    results = collection.query(query_embeddings=[query_embed], n_results=1)

    retrieved_data = results["documents"]
    context = "\n\n".join(retrieved_data[0]) if retrieved_data else " "

    prompt = f"""You are a helpful assistant. Answer the question based on the context provided. Use the information in the context to form your answer. If context does not have enough information just say "There is no mention of the query in given context"

    Context: {context}

    Question: {query}

    Answer:"""

    response = remote_client.generate(
        model="llama3.2:3b", prompt=prompt, options={"temperature": 0.1}
    )

    answer = response["response"]
    print(f"{answer}\n")
    print("-" * os.get_terminal_size().columns)