"""ChromaDB baseline adapter for DeepMemEval.

A simple vector-search-only baseline using ChromaDB.
This represents the minimum viable memory system.
"""

from src.adapter import MemorySystemAdapter


class ChromaDBAdapter(MemorySystemAdapter):
    """Baseline: store everything, retrieve by similarity, no intelligence."""

    def __init__(self):
        try:
            import chromadb
        except ImportError:
            raise ImportError("pip install chromadb")

        self._client = chromadb.Client()
        self._collection = None
        self._last_context_tokens = 0

    def reset(self) -> None:
        self._client.reset()
        self._collection = self._client.create_collection("deepmemeval")
        self._last_context_tokens = 0

    def ingest_session(self, session: dict, timestamp: str) -> None:
        for i, turn in enumerate(session["turns"]):
            doc_id = f"{session['session_id']}-{i}"
            self._collection.add(
                documents=[turn["content"]],
                metadatas=[{"role": turn["role"], "date": timestamp, "session": session["session_id"]}],
                ids=[doc_id],
            )

    def query(self, question: str, timestamp: str = "now") -> str:
        results = self._collection.query(query_texts=[question], n_results=10)
        docs = results["documents"][0] if results["documents"] else []
        context = "\n".join(docs)
        self._last_context_tokens = len(context.split()) * 1.3
        return context

    def get_context_tokens(self) -> int:
        return int(self._last_context_tokens)
