import pandas as pd
import pickle
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

# -------------------------------
# 1. Text Cleaning Function
# -------------------------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r'\W', ' ', text)   # remove special characters
    text = re.sub(r'\s+', ' ', text)  # remove extra spaces
    return text

# -------------------------------
# 2. Load Dataset
# -------------------------------
def load_data():
    # Replace with your dataset path
    df = pd.read_csv("resume_dataset.csv")

    # Make sure dataset has these columns:
    # 'Resume' → text
    # 'Category' → label (job role)
    df['Resume'] = df['Resume'].apply(clean_text)

    return df

# -------------------------------
# 3. Train Model
# -------------------------------
def train_model():
    df = load_data()

    X = df['Resume']
    y = df['Category']

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Create pipeline (TF-IDF + Naive Bayes)
    model = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english', max_features=5000)),
        ('clf', MultinomialNB())
    ])

    # Train model
    model.fit(X_train, y_train)

    # Accuracy
    accuracy = model.score(X_test, y_test)
    print(f"Model Accuracy: {accuracy:.2f}")

    # Save model
    with open("resume_model.pkl", "wb") as f:
        pickle.dump(model, f)

    print("Model saved as resume_model.pkl")

# -------------------------------
# 4. Load Model
# -------------------------------
def load_model():
    with open("resume_model.pkl", "rb") as f:
        model = pickle.load(f)
    return model

# -------------------------------
# 5. Predict Function
# -------------------------------
def predict_category(resume_text):
    model = load_model()
    resume_text = clean_text(resume_text)
    prediction = model.predict([resume_text])
    return prediction[0]


# -------------------------------
# 6. Run Training (Only once)
# -------------------------------
if __name__ == "__main__":
    train_model()