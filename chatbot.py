from ollama import Client
import json
import os
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter


class rag:
    def __init__(self):
        self.embed_model = "nomic-embed-text"
        self.llm_model = "llama3.2:3b" ## change this to local ollama model
        self.client = chromadb.PersistentClient()
        self.remote_client = Client(host=f"http://localhost:11434")
        self.collection = self.client.get_or_create_collection(name="articles_demo")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=600, chunk_overlap=100, separators=[".", " "]
        )
        self.file_path = "news.jsonl"
        self.counter_file = "counter.txt"
        self.counter = self._load_counter()

    def _load_counter(self):
        try:
            with open(self.counter_file) as f:
                return int(f.read().strip())
        except FileNotFoundError:
            with open(self.counter_file, "w") as f:
                f.write("0")
            return 0

    def _save_counter(self):
        with open(self.counter_file, "w") as f:
            f.write(str(self.counter))

    def build_database(self):
        print("Reading news.jsonl and generating embeddings...")
        with open(self.file_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i < self.counter:
                    print("Skipping already processed article:", i)
                    continue
                article = json.loads(line)
                content = article["content"]
                sentences = self.text_splitter.split_text(content)
                for j, each_sentence in enumerate(sentences):
                    response = self.remote_client.embed(
                        model="nomic-embed-text",
                        input=f"search_document: {each_sentence}",
                    )
                    embedding = response["embeddings"][0]

                    self.collection.add(
                        ids=[f"article_{i}_chunk_{j}"],
                        embeddings=[embedding],
                        documents=[each_sentence],
                        metadatas=[{"title": article["title"]}],
                    )
                self.counter += 1
                self._save_counter()
        print("Database built successfully!")

    def chat_loop(self):
        print("-" * os.get_terminal_size().columns)
        while True:
            query = input("\nHow may I help you? \nQuery: ")
            if query.lower() in ("bye", "exit"):
                print("Bye")
                break

            query_embed = self.remote_client.embed(
                model=self.embed_model, input=f"query: {query}"
            )["embeddings"][0]

            results = self.collection.query(query_embeddings=[query_embed], n_results=5)
            retrieved_data = results["documents"]
            context = "\n\n".join(retrieved_data[0]) if retrieved_data else " "

            prompt = f"""
            You are a question answering assistant.
            Rules:
            - Only use the information present in the context.
            - If the context does not contain enough information, respond with "I don't know."
            - Dont mention context in your answer.
            - Keep your answer relevant and informative.            

            Context: {context}

            Question: {query}

            Answer:"""

            response = self.remote_client.generate(
                model=self.llm_model, prompt=prompt, options={"temperature": 0.2}
            )
            answer = response["response"]
            print(f"{answer}\n")
            print("-" * os.get_terminal_size().columns)


if __name__ == "__main__":
    chatbot = rag()
    chatbot.build_database()
    chatbot.chat_loop()
