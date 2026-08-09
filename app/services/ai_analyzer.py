import os
import json
import pickle
from typing import Dict


class AIAnalyzer:
    def __init__(self):
        base = os.path.dirname(os.path.dirname(__file__))
        models_dir = os.path.join(base, "models")
        self.vec_path = os.path.join(models_dir, "vectorizer.pkl")
        self.clf_path = os.path.join(models_dir, "classifier.pkl")
        self.vectorizer = None
        self.classifier = None
        if os.path.exists(self.vec_path) and os.path.exists(self.clf_path):
            try:
                with open(self.vec_path, "rb") as f:
                    self.vectorizer = pickle.load(f)
                with open(self.clf_path, "rb") as f:
                    self.classifier = pickle.load(f)
            except Exception:
                self.vectorizer = None
                self.classifier = None

    def analyze(self, text: str) -> Dict:
        cat = self.classify(text)
        pr = self.predict_priority(text)
        summ = self.summarize(text)
        dept = self.recommend_department(cat)
        return {"category": cat, "priority": pr, "summary": summ, "recommended_department": dept}

    def classify(self, text: str) -> str:
        if self.vectorizer and self.classifier:
            X = self.vectorizer.transform([text])
            pred = self.classifier.predict(X)
            return str(pred[0])
        # fallback simple keyword rules
        t = text.lower()
        if any(k in t for k in ["water", "leak", "flood", "pipe"]):
            return "Water"
        if any(k in t for k in ["garbage", "trash", "bin", "waste"]):
            return "Waste"
        if any(k in t for k in ["light", "electric", "power", "electricity"]):
            return "Electricity"
        if any(k in t for k in ["road", "pothole", "gaddha", "traffic"]):
            return "Road"
        if any(k in t for k in ["drain", "sewer", "drainage"]):
            return "Drainage"
        if any(k in t for k in ["unsafe", "crime", "danger", "attack"]):
            return "Safety"
        return "Other"

    def predict_priority(self, text: str) -> str:
        t = text.lower()
        if any(k in t for k in ["urgent", "immediately", "traffic", "critical", "major", "collapse", "flood"]):
            return "Critical"
        if any(k in t for k in ["accident", "danger", "unsafe", "blocked"]):
            return "High"
        if any(k in t for k in ["leak", "pothole", "overflow", "delay"]):
            return "Medium"
        return "Low"

    def recommend_department(self, category: str) -> str:
        mapping = {
            'Water': 'Water & Sanitation',
            'Waste': 'Sanitation',
            'Electricity': 'Electrical',
            'Road': 'Road & Transport',
            'Drainage': 'Drainage',
            'Safety': 'Public Safety',
            'Other': 'General Services',
        }
        return mapping.get(category, 'General Services')

    def summarize(self, text: str) -> str:
        # very simple summarization: first sentence or truncated text
        if not text:
            return ""
        parts = text.split('.')
        first = parts[0].strip()
        if len(first) > 120:
            return first[:117] + '...'
        return first
