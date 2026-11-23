"""
Cynbit AI - ML Training Script
Trains a TF-IDF + Logistic Regression classification model on customer inquiry data.
Evaluates model on held-out test set and saves artifacts.
"""

import os
import json
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report
)

from app.ml.pipeline import clean_text

def train_lead_classifier(
    data_path: str = "data/training_leads.csv",
    model_save_path: str = "models/lead_classifier.joblib",
    vectorizer_save_path: str = "models/tfidf_vectorizer.joblib",
    metrics_save_path: str = "models/model_metrics.json",
    test_size: float = 0.20,
    random_state: int = 42
):
    print("=" * 60)
    print("Starting Cynbit Lead Intelligence ML Model Training")
    print("=" * 60)
    
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Training dataset not found at: {data_path}")
        
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} samples from {data_path}")
    
    # 1. Preprocessing
    print("Preprocessing text inputs...")
    df["cleaned_text"] = df["inquiry_text"].apply(clean_text)
    
    X = df["cleaned_text"].tolist()
    y = df["category"].tolist()
    
    # 2. Stratified Train / Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        stratify=y,
        random_state=random_state
    )
    print(f"Split data: {len(X_train)} training samples, {len(X_test)} held-out testing samples")
    
    # 3. TF-IDF Vectorization
    print("Fitting TF-IDF Vectorizer (unigrams + bigrams)...")
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.95,
        sublinear_tf=True
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    print(f"Vocabulary size: {len(vectorizer.get_feature_names_out())} features")
    
    # 4. Model Training
    print("Training Logistic Regression classifier (multi_class='ovr', balanced weights)...")
    clf = LogisticRegression(
        C=2.0,
        max_iter=1000,
        class_weight="balanced",
        random_state=random_state,
        solver="lbfgs"
    )
    clf.fit(X_train_vec, y_train)
    
    # 5. Held-out Evaluation
    print("\nEvaluating model on held-out test set...")
    y_pred = clf.predict(X_test_vec)
    y_pred_proba = clf.predict_proba(X_test_vec)
    
    acc = accuracy_score(y_test, y_pred)
    macro_p, macro_r, macro_f1, _ = precision_recall_fscore_support(y_test, y_pred, average="macro", zero_division=0)
    weighted_p, weighted_r, weighted_f1, _ = precision_recall_fscore_support(y_test, y_pred, average="weighted", zero_division=0)
    
    labels = sorted(list(set(y)))
    cm = confusion_matrix(y_test, y_pred, labels=labels)
    
    # Per-class metrics
    class_p, class_r, class_f1, class_supp = precision_recall_fscore_support(y_test, y_pred, labels=labels, zero_division=0)
    per_class_metrics = {}
    for i, label in enumerate(labels):
        per_class_metrics[label] = {
            "precision": round(float(class_p[i]), 4),
            "recall": round(float(class_r[i]), 4),
            "f1_score": round(float(class_f1[i]), 4),
            "support": int(class_supp[i])
        }
        
    # Top predictive features per category
    feature_names = np.array(vectorizer.get_feature_names_out())
    top_features_per_class = {}
    for i, label in enumerate(clf.classes_):
        top_indices = np.argsort(clf.coef_[i])[-10:][::-1]
        top_features_per_class[label] = [
            {"feature": feature_names[idx], "weight": round(float(clf.coef_[i][idx]), 4)}
            for idx in top_indices
        ]
        
    print("\n" + "=" * 50)
    print("MODEL EVALUATION RESULTS (Test Set)")
    print("=" * 50)
    print(f"Accuracy:          {acc:.4f} ({acc*100:.2f}%)")
    print(f"Macro Precision:   {macro_p:.4f}")
    print(f"Macro Recall:      {macro_r:.4f}")
    print(f"Macro F1-Score:    {macro_f1:.4f}")
    print(f"Weighted F1-Score: {weighted_f1:.4f}")
    print("\nDetailed Classification Report:")
    print(classification_report(y_test, y_pred, labels=labels, zero_division=0))
    
    # Save artifacts
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    joblib.dump(clf, model_save_path)
    joblib.dump(vectorizer, vectorizer_save_path)
    
    metrics_payload = {
        "timestamp": datetime.now().isoformat(),
        "algorithm": "TF-IDF + LogisticRegression",
        "dataset_size": len(df),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "vocabulary_size": len(feature_names),
        "overall": {
            "accuracy": round(float(acc), 4),
            "macro_precision": round(float(macro_p), 4),
            "macro_recall": round(float(macro_r), 4),
            "macro_f1": round(float(macro_f1), 4),
            "weighted_f1": round(float(weighted_f1), 4)
        },
        "labels": labels,
        "confusion_matrix": cm.tolist(),
        "per_class": per_class_metrics,
        "top_features": top_features_per_class
    }
    
    with open(metrics_save_path, "w") as f:
        json.dump(metrics_payload, f, indent=2)
        
    print(f"\nArtifacts saved successfully:")
    print(f" -> Model:      {model_save_path}")
    print(f" -> Vectorizer: {vectorizer_save_path}")
    print(f" -> Metrics:    {metrics_save_path}")
    print("=" * 60)
    return metrics_payload

if __name__ == "__main__":
    train_lead_classifier()
