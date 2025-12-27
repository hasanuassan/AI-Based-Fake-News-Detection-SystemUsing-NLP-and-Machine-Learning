"""
Training Script for Fake News Detection ML Model
Run this script to train a model on your dataset
"""

import pandas as pd
import numpy as np
from ml_model import FakeNewsMLModel
import os

def create_sample_data():
    """
    Create sample training data if no dataset is available
    This is for demonstration - replace with your actual dataset
    """
    # Sample fake news texts
    fake_texts = [
        "BREAKING: Doctors HATE this one simple trick that cures all diseases instantly! Click now!",
        "SHOCKING: This miracle cure will completely eliminate diabetes in just 15 days! Guaranteed 100%!",
        "You won't believe what this secret formula does! Scientists are FURIOUS!",
        "URGENT: Act now before it's too late! This exclusive offer cures cancer overnight!",
        "Amazing discovery! This revolutionary treatment makes all doctors obsolete!",
        "Breaking: Unverified sources claim this instant cure works for everything!",
        "Incredible! This guaranteed method will make you rich in 3 days! No risk!",
        "Shocking revelation! Government confirms this secret that changes everything!",
        "Exclusive: This never-before-seen cure eliminates all health problems!",
        "Act now! Limited time offer! This miracle solution cures all diseases!",
        "Breaking news: Anonymous sources reveal this amazing cure that doctors don't want you to know!",
        "You must see this! This incredible discovery will change your life forever!",
        "Urgent warning! This secret formula is being hidden from the public!",
        "Revolutionary breakthrough! This instant cure works for everyone!",
        "Exposed: The truth about this miracle cure that cures everything!",
    ]
    
    # Sample real news texts
    real_texts = [
        "According to a peer-reviewed study published in the Journal of Medicine, researchers found that regular exercise can help manage diabetes.",
        "The World Health Organization confirmed that vaccination programs have significantly reduced disease transmission rates.",
        "A research team from Harvard University published findings showing the benefits of a balanced diet on cardiovascular health.",
        "The Centers for Disease Control and Prevention released official data showing improvements in public health metrics.",
        "Scientists at MIT conducted a study that was published in a reputable journal, showing evidence-based results.",
        "According to verified sources, the government announced new healthcare policies based on scientific evidence.",
        "A peer-reviewed research paper in Nature journal presented findings from a controlled clinical trial.",
        "The Food and Drug Administration confirmed the safety and efficacy of the new treatment after rigorous testing.",
        "Medical experts from multiple institutions collaborated on a study published in a respected medical journal.",
        "According to official reports from health authorities, the new guidelines are based on extensive research.",
        "A comprehensive study involving thousands of participants was published in a leading medical journal.",
        "Researchers from multiple universities collaborated on a peer-reviewed study with verified results.",
        "The study, published in a reputable journal, included proper methodology and statistical analysis.",
        "According to verified medical sources, the treatment showed positive results in controlled trials.",
        "Official health organizations confirmed the findings after reviewing the published research data.",
    ]
    
    texts = fake_texts + real_texts
    labels = [1] * len(fake_texts) + [0] * len(real_texts)  # 1 = Fake, 0 = Real
    
    return texts, labels


def load_dataset(file_path):
    """
    Load dataset from CSV file
    Expected format: CSV with 'text' and 'label' columns
    label: 0 = Real, 1 = Fake
    """
    try:
        df = pd.read_csv(file_path)
        
        # Handle different column names
        if 'text' in df.columns and 'label' in df.columns:
            texts = df['text'].tolist()
            labels = df['label'].tolist()
        elif 'title' in df.columns and 'label' in df.columns:
            texts = df['title'].tolist()
            labels = df['label'].tolist()
        elif len(df.columns) >= 2:
            texts = df.iloc[:, 0].tolist()
            labels = df.iloc[:, 1].tolist()
        else:
            raise ValueError("Dataset format not recognized")
        
        return texts, labels
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return None, None


def main():
    """Main training function"""
    print("=" * 60)
    print("Fake News Detection ML Model Training")
    print("=" * 60)
    
    # Try to load dataset from file
    dataset_paths = [
        'dataset/fake_news_dataset.csv',
        'data/train.csv',
        'dataset.csv'
    ]
    
    texts, labels = None, None
    
    for path in dataset_paths:
        if os.path.exists(path):
            print(f"\nLoading dataset from {path}...")
            texts, labels = load_dataset(path)
            if texts and labels:
                print(f"Loaded {len(texts)} samples")
                break
    
    # If no dataset found, use sample data
    if not texts or not labels:
        print("\nNo dataset file found. Using sample data for demonstration.")
        print("To train on your own data, place a CSV file with 'text' and 'label' columns.")
        texts, labels = create_sample_data()
    
    # Initialize and train model
    model = FakeNewsMLModel()
    
    print(f"\nTraining on {len(texts)} samples...")
    accuracy = model.train(texts, labels)
    
    # Save model
    print("\nSaving model...")
    model.save_model()
    
    print("\n" + "=" * 60)
    print("Training Complete!")
    print("=" * 60)
    print("\nThe model is now ready to use in app.py")
    print("Model files saved in 'models/' directory")


if __name__ == '__main__':
    main()

