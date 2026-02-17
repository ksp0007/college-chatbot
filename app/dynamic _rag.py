# app/dynamic_rag.py
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
import hashlib
import os
import json

class DynamicRAG:
    def __init__(self, persist_dir="./app/vector_db"):
        self.persist_dir = persist_dir
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = Chroma(
            persist_directory=persist_dir, embedding_function=self.embeddings
        )
        self.hash_file = os.path.join(persist_dir, "hashes.json")
        self.hashes = self._load_hashes()

    def _load_hashes(self):
        if os.path.exists(self.hash_file):
            with open(self.hash_file, "r") as f:
                return json.load(f)
        return {}

    def _save_hashes(self):
        with open(self.hash_file, "w") as f:
            json.dump(self.hashes, f, indent=4)

    def _get_hash(self, text):
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    def update_paragraphs(self, data_dict):
        """
        data_dict: dict of {id: text}
        Example: {"p1": "CBIT is in Hyderabad.", "p2": "It offers UG, PG, and PhD programs."}
        """
        for pid, text in data_dict.items():
            new_hash = self._get_hash(text)
            old_hash = self.hashes.get(pid)

            if new_hash != old_hash:
                print(f"[🔄] Updating {pid}...")
                self.vectorstore.delete(ids=[pid])
                self.vectorstore.add_texts(texts=[text], ids=[pid])
                self.hashes[pid] = new_hash

        self.vectorstore.persist()
        self._save_hashes()

    def get_retriever(self, k=3):
        return self.vectorstore.as_retriever(search_kwargs={"k": k})
