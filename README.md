# FinShield RAG

> A **secure, RBI-compliant financial AI assistant** powered by Retrieval-Augmented Generation (RAG) with multi-layer prompt injection protection.

## Features

- **3-Layer Security System**
  - **Layer 1 (Lexical Filter):** Regex-based injection pattern blocking
  - **Layer 2 (Semantic Filter):** AI-powered cosine similarity detection for adversarial prompts
  - **Layer 3 (Canary Validator):** Internal token leak detection
- **RAG Pipeline:** FAISS vector search over RBI & fintech policy documents
- **Explainability Panel:** Every response includes sources, latency, and audit key
- **Immutable Audit Logging:** SHA-256 response hashing + PII masking (Aadhaar, PAN)
- **Streamlit UI:** Clean chat interface with live security status sidebar

## Project Structure

```
finshield/
├── data/                         # Knowledge base (policy docs)
│   ├── rbi_master_circular.txt
│   ├── loan_terms.txt
│   └── credit_card_policy.txt
├── logs/                         # Append-only audit trail
├── src/
│   ├── app.py                    # Streamlit main entry point
│   ├── rag.py                    # FAISS retrieval + context-grounded generator
│   ├── security.py               # 3-layer security module
│   └── audit.py                  # PII masking & audit logger
└── requirements.txt
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
cd src
streamlit run app.py
```

## Tech Stack

| Tool | Purpose |
|---|---|
| Streamlit | Web UI |
| LangChain | Document loading & RAG abstraction |
| FAISS | Vector similarity search |
| HuggingFace `all-MiniLM-L6-v2` | Embeddings |
| scikit-learn | Cosine similarity (L2 security) |

## Compliance

Built with **RBI Master Circular 2025–26** guidelines in mind:
- Cooling-off periods, data privacy, grievance redressal norms
- Personal loan T&Cs and credit card policy enforcement

---

*Developed by Manjit Kumar*
