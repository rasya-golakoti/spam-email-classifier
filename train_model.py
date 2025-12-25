# train_model.py
import pickle
import re
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

# Load Emails Function (same as original)
def load_emails_from_folder(folder_list):
    emails = []
    for folder_path in folder_list:
        for filename in os.listdir(folder_path):
            filepath = os.path.join(folder_path, filename)
            if os.path.isfile(filepath):
                with open(filepath, 'r', encoding='latin-1') as file:
                    emails.append(file.read())
    return emails

# Clean email function
def clean_email(text):
    text = text.split('\n\n', 1)[-1]
    text = text.lower()
    text = re.sub(r'http\S+', 'URL', text)
    text = re.sub(r'\d+', 'NUMBER', text)
    text = re.sub(r'[^\w\s]', '', text)
    return text

# Main training function
def train_and_save_model():
    print("🚀 Loading datasets...")
    
    # Define folders (adjust paths based on your directory structure)
    ham_folders = [
        'data/easy_ham_1',
        'data/easy_ham_2', 
        'data/easy_ham_3',
        'data/hard_ham_1',
        'data/hard_ham_2'
    ]
    
    spam_folders = [
        'data/spam_1',
        'data/spam_2',
        'data/spam_3',
        'data/spam_4'
    ]
    
    # Check if data folders exist
    all_folders = ham_folders + spam_folders
    missing_folders = [f for f in all_folders if not os.path.exists(f)]
    
    if missing_folders:
        print(f"❌ Missing data folders: {missing_folders}")
        print("Please make sure the 'data' folder exists with the required subfolders.")
        return
    
    # Load emails
    ham_emails = load_emails_from_folder(ham_folders)
    spam_emails = load_emails_from_folder(spam_folders)
    
    x = ham_emails + spam_emails
    y = [0] * len(ham_emails) + [1] * len(spam_emails)
    
    print(f"✅ Total Ham: {len(ham_emails)}")
    print(f"✅ Total Spam: {len(spam_emails)}")
    print(f"✅ Total Emails: {len(x)}")
    
    # Train-test split
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, random_state=42, test_size=0.2, stratify=y
    )
    
    print(f"📊 Training samples: {len(x_train)}")
    print(f"📊 Testing samples: {len(x_test)}")
    
    # Create and fit CountVectorizer
    print("🔧 Creating CountVectorizer...")
    vectorizer = CountVectorizer(
        preprocessor=clean_email,
        stop_words='english',
        max_features=5000
    )
    
    # Transform training data
    x_train_vec = vectorizer.fit_transform(x_train)
    x_test_vec = vectorizer.transform(x_test)
    
    print(f"📐 Feature vector shape: {x_train_vec.shape}")
    
    # Train Logistic Regression model
    print("🤖 Training Logistic Regression model...")
    model = LogisticRegression(
        max_iter=1000,
        random_state=42,
        C=1.0  # Regularization parameter
    )
    
    model.fit(x_train_vec, y_train)
    
    # Evaluate the model
    from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
    
    y_pred = model.predict(x_test_vec)
    accuracy = accuracy_score(y_test, y_pred)
    
    print("\n" + "="*50)
    print("📈 MODEL EVALUATION RESULTS")
    print("="*50)
    print(f"✅ Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    print("\n📋 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['HAM', 'SPAM']))
    
    print("📊 Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    print("="*50)
    
    # Save the model and vectorizer
    print("\n💾 Saving model and vectorizer...")
    
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    # Save vectorizer
    with open('models/count_vectorizer.pkl', 'wb') as f:
        pickle.dump(vectorizer, f)
    
    # Save model
    with open('models/best_spam_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    print("✅ Model and vectorizer saved successfully!")
    print("📁 Files saved in 'models/' directory:")
    print("   - count_vectorizer.pkl")
    print("   - best_spam_model.pkl")
    
    # Create a simple test
    test_emails = [
        "Congratulations! You've won a $1000 Amazon gift card. Click here: http://winprize.com",
        "Hi John, meeting scheduled for tomorrow at 2 PM. Please bring the project documents."
    ]
    
    print("\n🧪 Quick Test Predictions:")
    for i, email in enumerate(test_emails, 1):
        cleaned = clean_email(email)
        vectorized = vectorizer.transform([cleaned])
        prediction = model.predict(vectorized)[0]
        probability = model.predict_proba(vectorized)[0]
        
        result = "SPAM" if prediction == 1 else "HAM"
        spam_prob = probability[1] * 100
        
        print(f"Email {i}: {result} (Spam probability: {spam_prob:.2f}%)")

if __name__ == "__main__":
    train_and_save_model()