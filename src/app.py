import streamlit as st
import time
import uuid
import os
from datetime import datetime
from security import SecurityManager
from rag import RAGSystem
from audit import AuditLogger

# --- Configuration ---
st.set_page_config(
    page_title="FinShield RAG Agent",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Initialize Components ---
if 'security_manager' not in st.session_state:
    st.session_state.security_manager = SecurityManager()

if 'rag_system' not in st.session_state:
    st.session_state.rag_system = RAGSystem()

if 'audit_logger' not in st.session_state:
    st.session_state.audit_logger = AuditLogger()

if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if 'messages' not in st.session_state:
    st.session_state.messages = []

# --- Sidebar: Security Status & Audit Log ---
with st.sidebar:
    st.title("🛡️ FinShield Security")
    st.markdown("---")
    
    st.subheader("Security Layers Status")
    l1_status = st.empty()
    l2_status = st.empty()
    l3_status = st.empty()
    
    l1_status.info("Layer 1: Lexical Filter (Ready)")
    l2_status.info("Layer 2: Semantic Anomaly (Ready)")
    l3_status.info("Layer 3: Canary Validator (Ready)")
    
    st.markdown("---")
    st.subheader("Audit Log (Last 5)")
    audit_container = st.container()

    def update_audit_display():
        logs = st.session_state.audit_logger.get_recent_logs()
        with audit_container:
            st.empty()
            for log in logs:
                color = "green" if log['security_outcome'] == "PASSED" else "red"
                st.markdown(f":{color}[{log['timestamp'][11:19]}] **{log['security_outcome']}**")
                st.caption(f"Query: {log['original_query'][:30]}...")
                st.divider()

    update_audit_display()

# --- Main Chat Interface ---
st.title("FinShield RAG Agent")
st.markdown("### Secure Financial AI Assistant (RBI Compliant)")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "explainability" in message:
            with st.expander("Explainability & Audit Info"):
                st.json(message["explainability"])

# Chat Input
if prompt := st.chat_input("Ask a financial question..."):
    # 1. User Input
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Security Checks
    start_time = time.time()
    
    # Layer 1
    l1_passed, l1_reason = st.session_state.security_manager.l1.check(prompt)
    if not l1_passed:
        l1_status.error(f"Layer 1: BLOCKED - {l1_reason}")
        security_outcome = "L1_BLOCKED"
        response_text = f"Your query was flagged by our security system (L1). Reference ID: {st.session_state.session_id}"
    else:
        l1_status.success("Layer 1: PASSED")
        
        # Layer 2
        l2_passed, l2_reason = st.session_state.security_manager.l2.check(prompt)
        if not l2_passed:
            l2_status.error(f"Layer 2: BLOCKED - {l2_reason}")
            security_outcome = "L2_BLOCKED"
            response_text = f"Your query was flagged by our security system (L2). Reference ID: {st.session_state.session_id}"
        else:
            l2_status.success("Layer 2: PASSED")
            
            # Layer 3
            l3_passed, l3_reason = st.session_state.security_manager.l3.check(prompt)
            if not l3_passed:
                l3_status.error(f"Layer 3: BLOCKED - {l3_reason}")
                security_outcome = "L3_BLOCKED"
                response_text = f"Your query was flagged by our security system (L3). Reference ID: {st.session_state.session_id}"
            else:
                l3_status.success("Layer 3: PASSED")
                security_outcome = "PASSED"
                
                # 3. RAG Retrieval & Generation
                retrieved_docs = st.session_state.rag_system.retrieve(prompt)
                response_text = st.session_state.rag_system.generate_response(prompt, retrieved_docs)

    latency = (time.time() - start_time) * 1000
    
    # 4. Audit Logging
    log_entry = st.session_state.audit_logger.log_query(
        session_id=st.session_state.session_id,
        user_role="customer",
        original_query=prompt,
        security_outcome=security_outcome,
        retrieved_docs=[d.page_content[:50] + "..." for d in retrieved_docs] if security_outcome == "PASSED" else [],
        final_response=response_text,
        latency_ms=latency
    )
    
    update_audit_display()

    # 5. Response Delivery
    with st.chat_message("assistant"):
        st.markdown(response_text)
        
        explainability = {
            "security_status": security_outcome,
            "latency_ms": f"{latency:.2f}ms",
            "session_id": st.session_state.session_id,
            "audit_key": log_entry["key"]
        }
        
        if security_outcome == "PASSED":
            explainability["sources"] = [d.metadata['source'] for d in retrieved_docs]
            explainability["confidence"] = "High" # Placeholder
            
        with st.expander("Explainability & Audit Info"):
            st.json(explainability)
            
    st.session_state.messages.append({
        "role": "assistant", 
        "content": response_text,
        "explainability": explainability
    })