from config import classify, unclassified

def detection(x):
    extension = x.suffix.lower()
    category = classify.get(extension, unclassified)
    return category, x