"""
Cynbit AI - About Project & Technical Architecture Page
"""

import streamlit as st
from frontend.components.styles import apply_cynbit_theme
from frontend.components.sidebar import render_sidebar

st.set_page_config(page_title="About Project | Cynbit AI", page_icon="ℹ️", layout="wide")
apply_cynbit_theme()
render_sidebar()

st.title("ℹ️ About the Platform & Architecture")
st.markdown("Cynbit AI – Intelligent Lead Qualification & Automation Agent technical overview.")

# Executive Summary
st.markdown("""
<div class="cynbit-card">
    <h3 style="color: #48CAE4; margin-top: 0;">🎯 Technical Assessment Context</h3>
    <p style="color: #CCD6F6; font-size: 0.95rem; line-height: 1.6;">
        This platform was engineered as the technical assessment submission for the <strong>AI/ML Engineer Intern</strong>
        role at <strong>Cynbit Technologies</strong>. It addresses a real business bottleneck: rapid, high-accuracy screening
        of inbound commercial inquiries, automated entity extraction, algorithmic lead prioritization, and instant executive response generation.
    </p>
</div>
""", unsafe_allow_html=True)

# Architecture Breakdown
st.subheader("🏗️ System Architecture & Workflow")

st.markdown("""
```mermaid
flowchart LR
    A[Inbound Customer Inquiry] --> B[Streamlit Multi-Page UI]
    B -->|HTTP REST API / JSON| C[FastAPI Production Backend]
    C --> D[NLP Preprocessor & Tokenizer]
    D --> E[TF-IDF N-Gram Vectorizer]
    E --> F[Logistic Regression Classifier]
    F --> G[Service Category & Confidence]
    
    D --> H[Heuristic & Regex Entity Extractor]
    H --> I[Budget, Timeline, Urgency & Tech Stack]
    
    G --> J[Multidimensional Scoring Engine]
    I --> J
    J --> K[Score 0-100 & Priority: Hot / Warm / Cold]
    
    K --> L[Personalized Proposal Generator]
    L --> M[Persistent Database Storage]
    M --> N[Real-Time Analytics Dashboard]
```
""")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="cynbit-card">
        <h4 style="color: #48CAE4; margin-top: 0;">🛠️ Backend & ML Technology Stack</h4>
        <ul style="color: #CCD6F6; font-size: 0.9rem; line-height: 1.7;">
            <li><strong>Python 3.11:</strong> High-performance core runtime</li>
            <li><strong>FastAPI & Uvicorn:</strong> Production asynchronous REST API with Pydantic v2 schemas</li>
            <li><strong>Render Cloud:</strong> Live deployed backend at <code>cynbit-ai-lead-intelligence.onrender.com</code></li>
            <li><strong>Scikit-Learn:</strong> TF-IDF N-gram feature extraction & multi-class Logistic Regression (85.42% accuracy)</li>
            <li><strong>SQLAlchemy 2.0 & SQLite:</strong> Transactional persistence, multi-field filtering, and CSV streaming</li>
            <li><strong>Pytest:</strong> Comprehensive test suite covering ML, extraction, scoring, and endpoints</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="cynbit-card">
        <h4 style="color: #48CAE4; margin-top: 0;">🎨 Frontend & Visualization Stack</h4>
        <ul style="color: #CCD6F6; font-size: 0.9rem; line-height: 1.7;">
            <li><strong>Streamlit:</strong> Multi-page reactive web application</li>
            <li><strong>Decoupled HTTP Architecture:</strong> Centralized API client reading <code>API_BASE_URL</code></li>
            <li><strong>Plotly:</strong> Interactive GPU-accelerated business and ML charts</li>
            <li><strong>Custom Dark Theme:</strong> Modern enterprise SaaS palette (#0B132B / #48CAE4)</li>
            <li><strong>Transparent Metrics:</strong> Live confusion matrix, per-class F1, and top TF-IDF n-grams</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# Deliverables Checklist
st.subheader("✅ Assessment Deliverables")
st.markdown("""
- [x] **Intelligent Lead Analysis:** Regex & semantic entity extraction for budget, timeline, urgency, intent, and tech stack.
- [x] **AI-Based Lead Classification:** Real TF-IDF + Logistic Regression pipeline evaluated on 48 held-out test inquiries.
- [x] **Multidimensional Lead Scoring:** 0-100 composite scoring across 5 weighted dimensions with explainable reasons.
- [x] **AI Response Generator:** Context-aware proposal emails tailored by service, priority, and timeline (with LLM support).
- [x] **Executive Analytics Dashboard:** Conversion funnel, KPI metrics, category breakdown, score distributions.
- [x] **Decoupled REST API & Cloud Backend:** FastAPI deployed on Render with HTTP communication via `API_BASE_URL`.
- [x] **Persistent SQLite Storage:** CRUD operations, multi-filter search, status updates, and CSV export.
- [x] **AI Opportunity Report:** Comprehensive business analysis of 5 strategic AI/ML opportunities for Cynbit.
- [x] **Technical Approach Report:** Exhaustive technical documentation covering data, ML, API, security, and scaling.
""")
