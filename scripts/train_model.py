"""
Train a tiny example classifier and save vectorizer + classifier into app/models.
Run: python scripts/train_model.py
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import pickle
import os

EXAMPLES = [
    ("There is a large water leak near the main road and traffic is affected", "Water"),
    ("Garbage bins are overflowing in our street", "Waste"),
    ("Street light is broken and not working at night", "Electricity"),
    ("Huge pothole on the main road causing accidents", "Road"),
    ("Drain is blocked and water is not draining", "Drainage"),
    ("Area feels unsafe at night with no lighting", "Safety"),
    ("Minor pothole near my house", "Road"),
]

texts = [t for t, l in EXAMPLES]
labels = [l for t, l in EXAMPLES]

vec = TfidfVectorizer(ngram_range=(1,2), max_features=1000)
X = vec.fit_transform(texts)

clf = LogisticRegression(max_iter=500)
clf.fit(X, labels)

base = os.path.join(os.path.dirname(__file__), '..', 'app', 'models')
base = os.path.normpath(base)
os.makedirs(base, exist_ok=True)

with open(os.path.join(base, 'vectorizer.pkl'), 'wb') as f:
    pickle.dump(vec, f)

with open(os.path.join(base, 'classifier.pkl'), 'wb') as f:
    pickle.dump(clf, f)

print('Saved vectorizer and classifier to', base)
