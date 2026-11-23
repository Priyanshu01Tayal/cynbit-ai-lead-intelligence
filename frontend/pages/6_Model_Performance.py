"""
Cynbit AI - ML Model Performance & Evaluation Page
Visualizes genuine test-set metrics, confusion matrix, top features, and retraining controls.
"""

import streamlit as st
import pandas as pd
from app.routes.ml import get_metrics, retrain_model
from frontend.components.styles import apply_cynbit_theme
from frontend.components.sidebar import render_sidebar
from frontend.components.cards import render_kpi_card
from frontend.components.charts import create_confusion_matrix_heatmap, LAYOUT_DEFAULTS
import plotly.graph_objects as go

st.set_page_config(page_title="Model Performance | Cynbit AI", page_icon="🤖", layout="wide")
apply_cynbit_theme()
render_sidebar()

st.title("🤖 ML Model Evaluation & Transparency")
st.markdown("Detailed breakdown of Scikit-Learn TF-IDF + Logistic Regression classification performance on held-out test data.")

# Fetch real saved metrics
try:
    metrics = get_metrics()
except Exception as e:
    st.error(f"Error loading model metrics: {e}")
    st.stop()

# 1. Top Metrics KPI Row
overall = metrics.get("overall", {})
col1, col2, col3, col4 = st.columns(4)

with col1:
    acc = overall.get("accuracy", 0.0)
    render_kpi_card("Test Accuracy", f"{acc*100:.1f}%", f"{metrics.get('test_samples', 0)} test samples", "#06D6A0")

with col2:
    macro_f1 = overall.get("macro_f1", 0.0)
    render_kpi_card("Macro F1-Score", f"{macro_f1:.3f}", "Unweighted mean across classes", "#3A86FF")

with col3:
    macro_p = overall.get("macro_precision", 0.0)
    render_kpi_card("Macro Precision", f"{macro_p:.3f}", "Reliability of positive predictions", "#00B4D8")

with col4:
    macro_r = overall.get("macro_recall", 0.0)
    render_kpi_card("Macro Recall", f"{macro_r:.3f}", "Sensitivity across classes", "#FFB703")

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# 2. Confusion Matrix & Per-Class Table
col_cm, col_report = st.columns([1.2, 1.2])

with col_cm:
    st.subheader("Confusion Matrix (Held-out Test Set)")
    labels = metrics.get("labels", [])
    matrix = metrics.get("confusion_matrix", [])
    if matrix:
        fig_cm = create_confusion_matrix_heatmap(labels, matrix)
        st.plotly_chart(fig_cm, use_container_width=True)

with col_report:
    st.subheader("Per-Class Classification Report")
    per_class = metrics.get("per_class", {})
    if per_class:
        report_rows = []
        for label, scores in per_class.items():
            report_rows.append({
                "Service Category": label,
                "Precision": f"{scores['precision']:.3f}",
                "Recall": f"{scores['recall']:.3f}",
                "F1-Score": f"{scores['f1_score']:.3f}",
                "Support (N)": scores["support"]
            })
        df_report = pd.DataFrame(report_rows)
        st.dataframe(df_report, use_container_width=True, hide_index=True)
        
    st.markdown("""
    <div style="background-color: #141C36; border-radius: 8px; padding: 14px 18px; margin-top: 15px; font-size: 0.85rem; color: #CCD6F6;">
        <strong>Pipeline Details:</strong><br>
        • Algorithm: <code>TF-IDF Vectorizer + Multinomial Logistic Regression</code><br>
        • Feature Space: <code>Unigrams + Bigrams (Sublinear TF)</code><br>
        • Total Dataset: <code>240 Inquiries (80% Train, 20% Test Stratified)</code><br>
        • Regularization: <code>L2 Penalty (C=2.0, balanced class weights)</code>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# 3. Top Predictive TF-IDF N-Grams per Category
st.subheader("Top Predictive Features (Model Interpretability)")
st.caption("Highest positive coefficients indicating key vocabulary for each service class.")

top_features = metrics.get("top_features", {})
if top_features:
    categories = list(top_features.keys())
    selected_class = st.selectbox("Select Service Category to Inspect Features:", categories)
    
    feats = top_features[selected_class]
    df_feat = pd.DataFrame(feats)
    df_feat = df_feat.sort_values(by="weight", ascending=True)
    
    fig_feat = go.Figure(go.Bar(
        x=df_feat["weight"],
        y=df_feat["feature"],
        orientation="h",
        marker_color="#48CAE4",
        text=[f"+{w:.3f}" for w in df_feat["weight"]],
        textposition="outside",
        textfont=dict(color="#FFFFFF")
    ))
    fig_feat.update_layout(
        **LAYOUT_DEFAULTS,
        xaxis_title="Logistic Regression Weight (Log-Odds Impact)",
        yaxis_title="TF-IDF N-Gram Feature",
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)")
    )
    st.plotly_chart(fig_feat, use_container_width=True)

st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

# 4. Retrain Model Action
st.subheader("🔄 Retrain Classification Model")
st.markdown("Trigger an end-to-end retraining run on the dataset to update pipeline weights and persist new artifacts.")

col_r1, col_r2 = st.columns([1, 3])
with col_r1:
    if st.button("🚀 Retrain Model Now", use_container_width=True):
        with st.spinner("Retraining model on training dataset..."):
            retrain_res = retrain_model()
            st.success(retrain_res["message"])
            st.rerun()
