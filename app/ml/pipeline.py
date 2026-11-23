"""
Cynbit AI - ML Pipeline
Contains the NLP preprocessing, TF-IDF feature extraction, and Classification Model.
"""

import os
import re
import joblib
import numpy as np
from typing import Dict, Any, List, Tuple

# Predefined stop words for lightweight, deterministic cleaning without extra external downloads
COMMON_STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", 
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", 
    "by", "can", "could", "did", "do", "does", "doing", "down", "during", "each", "few", "for", 
    "from", "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself", 
    "him", "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "just", 
    "me", "more", "most", "my", "myself", "no", "nor", "not", "now", "of", "off", "on", "once", 
    "only", "or", "other", "our", "ours", "ourselves", "out", "over", "own", "s", "same", "she", 
    "should", "so", "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves", 
    "then", "there", "these", "they", "this", "those", "through", "to", "too", "under", "until", 
    "up", "very", "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom", 
    "why", "will", "with", "would", "you", "your", "yours", "yourself", "yourselves"
}

CONTRACTIONS = {
    "we're": "we are",
    "i'm": "i am",
    "we've": "we have",
    "it's": "it is",
    "can't": "cannot",
    "won't": "will not",
    "don't": "do not",
    "doesn't": "does not",
    "didn't": "did not",
    "we'll": "we will",
    "you'll": "you will",
    "they're": "they are",
    "that's": "that is"
}

def clean_text(text: str) -> str:
    """Preprocesses and normalizes raw customer inquiry text."""
    if not isinstance(text, str):
        return ""
    
    text = text.lower()
    
    # Expand common contractions
    for cont, expanded in CONTRACTIONS.items():
        text = text.replace(cont, expanded)
        
    # Replace non-alphanumeric chars (keep spaces and dashes inside words)
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    
    # Tokenize and remove stopwords
    tokens = [t.strip() for t in text.split() if t.strip()]
    meaningful_tokens = [t for t in tokens if t not in COMMON_STOPWORDS and len(t) > 1]
    
    return " ".join(meaningful_tokens)

class LeadClassificationPipeline:
    """Production ML Inference Wrapper for Lead Classification."""
    
    def __init__(self, model_path: str = "models/lead_classifier.joblib", 
                 vectorizer_path: str = "models/tfidf_vectorizer.joblib"):
        self.model_path = model_path
        self.vectorizer_path = vectorizer_path
        self.model = None
        self.vectorizer = None
        self.classes_ = []
        self._load_model()
        
    def _load_model(self):
        """Loads serialized model and vectorizer from disk if present."""
        if os.path.exists(self.model_path) and os.path.exists(self.vectorizer_path):
            try:
                self.model = joblib.load(self.model_path)
                self.vectorizer = joblib.load(self.vectorizer_path)
                self.classes_ = list(self.model.classes_)
            except Exception as e:
                print(f"Warning: Failed to load ML model from {self.model_path}: {e}")
                self.model = None
                self.vectorizer = None
        else:
            self.model = None
            self.vectorizer = None
            
    @property
    def is_loaded(self) -> bool:
        return self.model is not None and self.vectorizer is not None
        
    def predict(self, raw_text: str) -> Dict[str, Any]:
        """
        Classifies lead inquiry text into service category with calibrated confidence.
        Fallback to intelligent keyword heuristics if model artifact is not yet trained.
        """
        cleaned = clean_text(raw_text)
        
        if self.is_loaded and cleaned:
            # Vectorize
            vec = self.vectorizer.transform([cleaned])
            probabilities = self.model.predict_proba(vec)[0]
            pred_idx = int(np.argmax(probabilities))
            pred_class = str(self.classes_[pred_idx])
            confidence = float(probabilities[pred_idx])
            
            prob_dict = {
                str(cls_name): round(float(prob), 4)
                for cls_name, prob in zip(self.classes_, probabilities)
            }
            
            # Extract top contributing features (n-grams) from input text
            feature_names = self.vectorizer.get_feature_names_out()
            feature_indices = vec.nonzero()[1]
            words_present = [feature_names[idx] for idx in feature_indices]
            
            return {
                "category": pred_class,
                "confidence": round(confidence, 4),
                "probabilities": prob_dict,
                "key_terms": words_present[:8],
                "cleaned_text": cleaned,
                "model_used": "TF-IDF + LogisticRegression"
            }
            
        # Intelligent Heuristic Fallback
        return self._heuristic_fallback(raw_text)
        
    def _heuristic_fallback(self, text: str) -> Dict[str, Any]:
        """Rule-based heuristic classifier used as initial bootstrap or fallback."""
        text_lower = text.lower()
        
        scores = {
            "AI/ML Development": 0,
            "Web Development": 0,
            "Mobile App Development": 0,
            "Cloud & DevOps": 0,
            "Business Automation": 0,
            "Other": 1 # baseline
        }
        
        keywords = {
            "AI/ML Development": ["ai", "machine learning", "ml", "nlp", "computer vision", "llm", "deep learning", "model", "rag", "predictive", "recommendation", "neural", "vision", "gpt"],
            "Web Development": ["web", "website", "react", "next.js", "frontend", "full-stack", "django", "portal", "cms", "ecommerce", "storefront", "javascript", "tailwind", "responsive"],
            "Mobile App Development": ["mobile", "app", "flutter", "ios", "android", "swift", "kotlin", "react native", "iphone", "wearable", "tablet", "cross-platform"],
            "Cloud & DevOps": ["aws", "azure", "gcp", "devops", "kubernetes", "docker", "ci/cd", "cloud", "terraform", "infrastructure", "sre", "migration", "monitoring", "grafana"],
            "Business Automation": ["automation", "automate", "workflow", "rpa", "zapier", "make", "n8n", "invoice", "sync", "bot", "triage", "reconciliation", "onboarding", "scraped"]
        }
        
        for category, terms in keywords.items():
            for term in terms:
                if re.search(r"\b" + re.escape(term) + r"\b", text_lower):
                    scores[category] += 2
                    
        best_category = max(scores, key=scores.get)
        if scores[best_category] <= 1:
            best_category = "Other"
            confidence = 0.55
        else:
            confidence = min(0.92, 0.50 + scores[best_category] * 0.08)
            
        total = sum(scores.values()) or 1
        probs = {k: round(v / total, 4) for k, v in scores.items()}
        
        return {
            "category": best_category,
            "confidence": round(confidence, 4),
            "probabilities": probs,
            "key_terms": [k for k in keywords.get(best_category, []) if k in text_lower][:5],
            "cleaned_text": clean_text(text),
            "model_used": "Heuristic Rule Fallback"
        }
