import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder

# File paths
DATA_FILE = 'data/organic_reaction_dataset.csv'
MODEL_PATH = 'models/chemistry_model_v2.pkl'
ENCODERS_PATH = 'models/label_encoders.pkl'

# Load data
df = pd.read_csv(DATA_FILE)
print(f"Loaded {len(df)} samples")

# Encode categorical features
encoders = {}
for col in ['Substrate_Degree', 'Leaving_Group', 'Nucleophile', 'Solvent_Type', 'Steric_Hindrance']:
    encoders[col] = LabelEncoder()
    df[col] = encoders[col].fit_transform(df[col])

# Encode target
encoders['Target_Mechanism'] = LabelEncoder()
y = encoders['Target_Mechanism'].fit_transform(df['Target_Mechanism'])

# Prepare features
X = df[['Substrate_Degree', 'Leaving_Group', 'Nucleophile', 'Solvent_Type', 'Steric_Hindrance', 'Temperature']]

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
print("Training model...")
model = RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42)
model.fit(X_train, y_train)

# Evaluate
accuracy = accuracy_score(y_test, model.predict(X_test))
print(f"Accuracy: {accuracy:.4f}")

# Save model and encoders
joblib.dump(model, MODEL_PATH)
joblib.dump(encoders, ENCODERS_PATH)
print(f"Model saved to {MODEL_PATH}")
print(f"Encoders saved to {ENCODERS_PATH}")