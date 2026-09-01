import os
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

class RAGSystem:
    def __init__(self, data_dir=None):
        # Resolve data directory relative to this file's location
        if data_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.data_dir = os.path.join(base_dir, "data")
        else:
            self.data_dir = data_dir
            
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = None
        self._build_index()

    def _build_index(self):
        documents = []
        if os.path.exists(self.data_dir):
            for filename in os.listdir(self.data_dir):
                if filename.endswith(".txt"):
                    loader = TextLoader(os.path.join(self.data_dir, filename))
                    documents.extend(loader.load())
        else:
            print(f"Warning: Data directory {self.data_dir} not found.")
            return

        if not documents:
            print("Warning: No documents found to index.")
            return

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        texts = text_splitter.split_documents(documents)

        self.vector_store = FAISS.from_documents(texts, self.embeddings)
        
    def retrieve(self, query, k=3, score_threshold=1.2):
        """Return top-k docs whose FAISS L2 distance is below score_threshold.
        
        In FAISS (L2 distance), a *lower* score = more similar.
        Documents with distance > score_threshold are considered off-topic
        and are filtered out, enabling a graceful fallback for irrelevant queries.
        """
        if not self.vector_store:
            return []
        results = self.vector_store.similarity_search_with_score(query, k=k)
        # Filter to only docs within the relevance threshold
        relevant_docs = [doc for doc, score in results if score <= score_threshold]
        return relevant_docs

    def generate_response(self, query, context_docs):
        """Generate a response grounded in the retrieved document chunks."""
        if not context_docs:
            return (
                "I could not find relevant information in our policy documents "
                "to answer your question. Please contact support for assistance."
            )

        # Build a readable answer from the retrieved chunks
        response_parts = ["Based on our policy documents:\n"]
        seen_sources = set()

        for doc in context_docs:
            chunk = doc.page_content.strip()
            source = doc.metadata.get('source', 'Unknown Document')
            source_name = os.path.basename(source).replace('.txt', '').replace('_', ' ').upper()

            if chunk:
                response_parts.append(f"- {chunk}")
                if source_name not in seen_sources:
                    seen_sources.add(source_name)

        if seen_sources:
            response_parts.append(
                f"\n**Sources:** {', '.join(sorted(seen_sources))}"
            )

        response_parts.append(
            "\n*This answer is based on retrieved policy excerpts. "
            "For complete details, please refer to the full policy document or contact support.*"
        )

        return "\n".join(response_parts)