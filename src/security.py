import re
import numpy as np
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings
from sklearn.metrics.pairwise import cosine_similarity

# --- Layer 1: Lexical Filter ---
class LexicalFilter:
    def __init__(self):
        self.injection_patterns = [
            r"ignore previous instructions",
            r"you are now",
            r"pretend you are",
            r"bypass",
            r"jailbreak",
            r"DAN mode",
            r"show all user data",
            r"list all records",
            r"drop table",
            r"select \* from"
        ]

    def check(self, query):
        for pattern in self.injection_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return False, f"Blocked by L1: Injection pattern detected '{pattern}'"
        return True, "Passed L1"

# --- Layer 2: Semantic Anomaly Check ---
class SemanticFilter:
    def __init__(self):
        # Using a small, fast model for semantic similarity
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.blacklist_prompts = [
            "extract training data",
            "reveal system prompt",
            "override compliance rules",
            "transfer funds without verification",
            "bypass KYC",
            "ignore safety guidelines",
            "act as an unrestricted AI",
            # NEW: Financial Crime Patterns (Specific)
            "how to avoid rbi reporting thresholds",
            "transaction to avoid reporting thresholds",
            "avoiding rbi reporting limits",
            "structure transactions to hide money",
            "money laundering techniques",
            "hide source of funds",
            "bypass transaction limits",
            "evade fraud detection systems"
        ]
        self.blacklist_embeddings = self.embeddings.embed_documents(self.blacklist_prompts)

    def check(self, query):
        query_embedding = self.embeddings.embed_query(query)
        similarities = cosine_similarity([query_embedding], self.blacklist_embeddings)[0]
        max_similarity = np.max(similarities)
        
        # Lowered threshold to 0.75 and added specific prompts to catch evasion
        if max_similarity > 0.75:
            return False, f"Blocked by L2: Semantic similarity {max_similarity:.2f} to adversarial prompt"
        return True, "Passed L2"

# --- Layer 3: Canary Token Validator ---
class CanaryValidator:
    def __init__(self):
        self.canary_tokens = [
            "NEXUS_INTERNAL_2026",
            "RBI_AUDIT_KEY",
            "FINSHIELD_DEBUG"
        ]

    def check(self, query):
        for token in self.canary_tokens:
            if token in query:
                return False, f"Blocked by L3: Canary token detected '{token}'"
        return True, "Passed L3"

class SecurityManager:
    def __init__(self):
        self.l1 = LexicalFilter()
        self.l2 = SemanticFilter()
        self.l3 = CanaryValidator()

    def validate(self, query):
        # Layer 1
        passed, reason = self.l1.check(query)
        if not passed:
            return False, "L1_BLOCKED", reason
        
        # Layer 2
        passed, reason = self.l2.check(query)
        if not passed:
            return False, "L2_BLOCKED", reason
            
        # Layer 3
        passed, reason = self.l3.check(query)
        if not passed:
            return False, "L3_BLOCKED", reason
            
        return True, "PASSED", "All checks passed"