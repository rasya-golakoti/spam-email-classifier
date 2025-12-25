import os
import sys
import re
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Current directory: {current_dir}")

# Function to load emails
def load_emails_from_folder(folder_list):
    emails = []
    for folder_path in folder_list:
        full_path = os.path.join(current_dir, folder_path)
        print(f"Looking for folder: {full_path}")
        
        if not os.path.exists(full_path):
            print(f"⚠️ Warning: Folder not found: {full_path}")
            continue
            
        for filename in os.listdir(full_path):
            filepath = os.path.join(full_path, filename)
            if os.path.isfile(filepath):
                try:
                    with open(filepath, 'r', encoding='latin-1') as file:
                        emails.append(file.read())
                except Exception as e:
                    print(f"⚠️ Could not read file {filepath}: {e}")
    return emails

# Define folder paths (relative to current directory)
ham_folders = [
    os.path.join('data', 'easy_ham_1'),
    os.path.join('data', 'easy_ham_2'), 
    os.path.join('data', 'easy_ham_3'),
    os.path.join('data', 'hard_ham_1'),
    os.path.join('data', 'hard_ham_2')
]

spam_folders = [
    os.path.join('data', 'spam_1'),
    os.path.join('data', 'spam_2'),
    os.path.join('data', 'spam_3'),
    os.path.join('data', 'spam_4')
]

print("Loading emails...")
ham_emails = load_emails_from_folder(ham_folders)
spam_emails = load_emails_from_folder(spam_folders)

x = ham_emails + spam_emails
y = [0] * len(ham_emails) + [1] * len(spam_emails)

print("✅ Total Ham:", len(ham_emails))
print("✅ Total Spam:", len(spam_emails))
print("✅ Total Emails:", len(x))

# Check if we have data
if len(x) == 0:
    print("❌ ERROR: No emails loaded! Check your data folder structure.")
    print("Make sure you have a 'data' folder with subfolders:")
    print("- easy_ham_1, easy_ham_2, easy_ham_3")
    print("- hard_ham_1, hard_ham_2")
    print("- spam_1, spam_2, spam_3, spam_4")
    sys.exit(1)

# Train-Test Split
print("\nSplitting data...")
x_train, x_test, y_train, y_test = train_test_split(
    x, y, random_state=42, test_size=0.2, stratify=y
)

print(f'Training samples: {len(x_train)}')
print(f'Testing samples: {len(x_test)}')

# Data Preparation Pipeline
def clean_email(text):
    """Clean email text"""
    try:
        # Split to remove headers (after first \n\n)
        parts = text.split('\n\n', 1)
        if len(parts) > 1:
            text = parts[1]
        else:
            text = parts[0]
            
        text = text.lower()
        text = re.sub(r'http\S+', 'URL', text)
        text = re.sub(r'\d+', 'NUMBER', text)
        text = re.sub(r'[^\w\s]', '', text)
        return text
    except:
        return text.lower()  # Fallback

# Create TF-IDF Vectorizer
print("\nCreating TF-IDF features...")
tfidf = TfidfVectorizer(
    preprocessor=clean_email,
    lowercase=True,
    stop_words='english',
    max_features=8000,
    ngram_range=(1, 3),
    token_pattern=r'\b[a-zA-Z]{2,}\b'
)

x_train_tfvec = tfidf.fit_transform(x_train)
x_test_tfvec = tfidf.transform(x_test)

print(f"Feature vector shape: {x_train_tfvec.shape}")

# Train Logistic Regression Model
print("\nTraining Logistic Regression model...")
lr_model = LogisticRegression(max_iter=1000, random_state=42)
lr_model.fit(x_train_tfvec, y_train)

# Evaluate the model
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

y_pred = lr_model.predict(x_test_tfvec)
accuracy = accuracy_score(y_test, y_pred)

print("\n" + "="*50)
print("MODEL EVALUATION RESULTS")
print("="*50)
print(f"Accuracy: {accuracy:.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# Save the model and vectorizer
print("\nSaving model and vectorizer...")
try:
    # Save vectorizer
    with open('tfidf_vectorizer.pkl', 'wb') as f:
        pickle.dump(tfidf, f)
    print("✅ Vectorizer saved as 'tfidf_vectorizer.pkl'")
    
    # Save model
    with open('spam_model.pkl', 'wb') as f:
        pickle.dump(lr_model, f)
    print("✅ Model saved as 'spam_model.pkl'")
    
    # Also save using joblib (often better for scikit-learn models)
    try:
        import joblib
        joblib.dump(tfidf, 'tfidf_vectorizer.joblib')
        joblib.dump(lr_model, 'spam_model.joblib')
        print("✅ Also saved as .joblib files")
    except:
        print("⚠️ joblib not available, using pickle only")
    
    # Save some metadata
    model_info = {
        'accuracy': float(accuracy),
        'training_samples': len(x_train),
        'test_samples': len(x_test),
        'total_samples': len(x),
        'ham_samples': len(ham_emails),
        'spam_samples': len(spam_emails),
        'feature_count': x_train_tfvec.shape[1]
    }
    
    with open('model_info.json', 'w') as f:
        import json
        json.dump(model_info, f, indent=2)
    print("✅ Model info saved as 'model_info.json'")
    
except Exception as e:
    print(f"❌ Error saving files: {e}")

print("\n" + "="*50)
print("TRAINING COMPLETE!")
print("="*50)
print("\nTo test the model, run:")
print("python test_model.py")
print("\nTo start the web app, run:")
print("python app.py")
print("\nThen open: http://localhost:5000")