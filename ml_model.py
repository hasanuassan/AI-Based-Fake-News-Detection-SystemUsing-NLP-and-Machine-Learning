"""
Machine Learning Model for Fake News Detection
Uses TF-IDF Vectorization + Logistic Regression
"""

import re
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

# Download NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

class FakeNewsMLModel:
    """Machine Learning Model for Fake News Detection"""
    
    def __init__(self):
        self.vectorizer = None
        self.model = None
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        self.is_trained = False
    
    def preprocess_text(self, text):
        """Preprocess text for ML model"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and stem
        tokens = [self.stemmer.stem(word) for word in tokens if word not in self.stop_words]
        
        # Join back
        return ' '.join(tokens)
    
    def train(self, texts, labels, test_size=0.2, random_state=42):
        """
        Train the ML model
        
        Args:
            texts: List of news article texts
            labels: List of labels (0 = Real, 1 = Fake)
            test_size: Proportion of test set
            random_state: Random seed
        """
        print("Preprocessing texts...")
        processed_texts = [self.preprocess_text(text) for text in texts]
        
        print("Creating TF-IDF vectors...")
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),  # Unigrams and bigrams
            min_df=2,
            max_df=0.95
        )
        
        X = self.vectorizer.fit_transform(processed_texts)
        y = np.array(labels)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        print("Training Logistic Regression model...")
        self.model = LogisticRegression(
            max_iter=1000,
            random_state=random_state,
            class_weight='balanced'  # Handle imbalanced data
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\nModel Training Complete!")
        print(f"Test Accuracy: {accuracy:.4f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=['Real', 'Fake']))
        
        self.is_trained = True
        return accuracy
    
    def predict(self, text):
        """
        Predict if text is fake news
        
        Args:
            text: News article text
            
        Returns:
            tuple: (prediction, confidence, probabilities)
                prediction: 0 (Real) or 1 (Fake)
                confidence: float 0-100
                probabilities: dict with 'real' and 'fake' probabilities
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Please train the model first or load a saved model.")
        
        # Preprocess
        processed_text = self.preprocess_text(text)
        
        # Vectorize
        text_vector = self.vectorizer.transform([processed_text])
        
        # Predict
        prediction = self.model.predict(text_vector)[0]
        probabilities = self.model.predict_proba(text_vector)[0]
        
        # Get confidence (probability of predicted class)
        confidence = probabilities[prediction] * 100
        
        return {
            'prediction': int(prediction),
            'prediction_label': 'Fake' if prediction == 1 else 'Real',
            'confidence': round(confidence, 2),
            'probabilities': {
                'real': round(probabilities[0] * 100, 2),
                'fake': round(probabilities[1] * 100, 2)
            }
        }
    
    def save_model(self, vectorizer_path='models/tfidf_vectorizer.pkl', 
                   model_path='models/ml_model.pkl'):
        """Save the trained model"""
        import os
        os.makedirs('models', exist_ok=True)
        
        with open(vectorizer_path, 'wb') as f:
            pickle.dump(self.vectorizer, f)
        
        with open(model_path, 'wb') as f:
            pickle.dump(self.model, f)
        
        print(f"Model saved to {model_path}")
        print(f"Vectorizer saved to {vectorizer_path}")
    
    def load_model(self, vectorizer_path='models/tfidf_vectorizer.pkl',
                   model_path='models/ml_model.pkl'):
        """Load a pre-trained model"""
        try:
            with open(vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            
            self.is_trained = True
            print("Model loaded successfully!")
            return True
        except FileNotFoundError:
            print("Model files not found. Using default heuristics.")
            return False


# Create a global model instance
ml_model = FakeNewsMLModel()

# Try to load pre-trained model, or use heuristics
def initialize_model():
    """Initialize the ML model"""
    success = ml_model.load_model()
    if not success:
        print("No pre-trained model found. Using rule-based heuristics.")
        print("Run train_model.py to train a model with your dataset.")
    return success

