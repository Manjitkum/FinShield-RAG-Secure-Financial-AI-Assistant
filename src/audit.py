import time
import hashlib
import json
import os
from datetime import datetime

# Resolve log path relative to this file so it works regardless of launch dir
_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SRC_DIR)
AUDIT_LOG_FILE = os.path.join(_PROJECT_ROOT, "logs", "audit_trail.jsonl")

class AuditLogger:
    def __init__(self):
        os.makedirs(os.path.dirname(AUDIT_LOG_FILE), exist_ok=True)

    def log_query(self, session_id, user_role, original_query, security_outcome, retrieved_docs, final_response, latency_ms):
        timestamp = datetime.utcnow().isoformat()
        
        # Mask PII in query (Simple simulation)
        sanitized_query = self._mask_pii(original_query)
        
        # Hash the response for immutability check
        response_hash = hashlib.sha256(final_response.encode('utf-8')).hexdigest() if final_response else None

        log_entry = {
            "key": f"audit:{session_id}:{timestamp}",
            "timestamp": timestamp,
            "session_id": session_id,
            "user_role": user_role,
            "original_query": sanitized_query,
            "security_outcome": security_outcome,
            "retrieved_documents": retrieved_docs,
            "final_response_hash": response_hash,
            "latency_ms": latency_ms
        }

        with open(AUDIT_LOG_FILE, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
            
        return log_entry

    def _mask_pii(self, text):
        # Simple PII masking simulation
        # In a real system, this would use NER models or regex for PAN, Aadhaar, etc.
        # Here we just mask 10-digit numbers (potential phone/PAN) and 12-digit numbers (Aadhaar)
        import re
        text = re.sub(r'\b\d{10}\b', '[MASKED_ID]', text)
        text = re.sub(r'\b\d{12}\b', '[MASKED_AADHAAR]', text)
        return text

    def get_recent_logs(self, limit=5):
        logs = []
        if os.path.exists(AUDIT_LOG_FILE):
            with open(AUDIT_LOG_FILE, "r") as f:
                for line in f:
                    logs.append(json.loads(line))
        return logs[-limit:][::-1]