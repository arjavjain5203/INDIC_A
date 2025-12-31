# Long Term Memory Module for INDICA
# This module manages a long-term memory system using Sentence Transformers and FAISS for efficient search.


import os
import json
import time
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

LTM_PATH = "logs/LTM.json"
MODEL_NAME = "all-MiniLM-L6-v2"
RELEVANCE_THRESHOLD = 0.4  # L2 similarity threshold (lower is closer)

class LongTermMemory:
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)
        self.last_modified = 0
        self.memory_data = {}
        self.flat_memory = {}
        self.embeddings = None
        self.index = None
        self._load_and_index()

    def _load_and_index(self):
        if not os.path.exists(LTM_PATH):
            print(f"[LTM] File not found at {LTM_PATH}. Starting fresh.")
            self.memory_data = {}
            self.flat_memory = {}
            return

        self.last_modified = os.path.getmtime(LTM_PATH)
        with open(LTM_PATH, "r", encoding="utf-8") as f:
            self.memory_data = json.load(f)

        self.flat_memory = self._flatten(self.memory_data)
        self.embeddings = self.model.encode(list(self.flat_memory.values()))
        dim = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(np.array(self.embeddings).astype("float32"))
        print(f"[LTM] Loaded and indexed {len(self.flat_memory)} facts.")

    def _flatten(self, data, parent_key=""):
        flat = {}
        def recurse(obj, prefix=""):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    recurse(v, f"{prefix}.{k}" if prefix else k)
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    recurse(v, f"{prefix}[{i}]")
            else:
                flat[prefix] = str(obj)
        recurse(data, parent_key)
        return flat

    def _refresh_if_updated(self):
        """Reload memory if LTM.json has been modified"""
        if os.path.getmtime(LTM_PATH) > self.last_modified:
            print("[LTM] Detected update. Reloading memory.")
            self._load_and_index()

    def search(self, query: str, top_k=5):
        self._refresh_if_updated()

        query_vec = self.model.encode([query])
        D, I = self.index.search(np.array(query_vec).astype("float32"), top_k)

        results = []
        for dist, idx in zip(D[0], I[0]):
            if idx < len(self.flat_memory):
                key = list(self.flat_memory.keys())[idx]
                value = self.flat_memory[key]
                confidence = 1 / (1 + dist)  # Simple inverse distance heuristic
                if confidence > RELEVANCE_THRESHOLD:
                    results.append({
                        "key": key,
                        "value": value,
                        "confidence": round(confidence, 2)
                    })

        return results

    def respond(self, query: str, top_k=3) -> str:
        """Generates a natural INDICA-style response from memory"""
        if query.strip().lower() in {"my", "me", "info", "information", "about me"}:
            return ("Darling, that's charmingly vague. Care to be more specific? "
                    "You can ask about your projects, preferences, or even your Spotify schemes.")

        results = self.search(query, top_k)
        if not results:
            return "I looked deep into my memory banks, but alas, I couldn't find anything matching that."

        reply = "Here's what I remember:\n"
        for r in results:
            reply += f"• {r['value']}\n"
        return reply.strip()

    def print_results(self, query: str, top_k=5):
        print(f"\n🔍 LTM Results for: '{query}'")
        results = self.search(query, top_k)
        for r in results:
            print(f"• {r['key']} → {r['value']} (conf: {r['confidence']})")
