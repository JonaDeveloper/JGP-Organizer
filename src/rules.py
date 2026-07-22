from pathlib import Path
from config import classify, unclassified

p = Path('.')

def detection(x):
    extension = x.suffix.lower()
    category = classify.get(extension, unclassified)
    return category, x