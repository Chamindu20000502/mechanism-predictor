import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import os


def train_mechanism_model(
        data_path,
        model_save_path,
        test_size=0.2,
        n_estimators=100
):
    """
    Trains a Random Forest classifier to predict chemical reaction mechanisms.

    Args:
        data_path (str): Path to the CSV file containing training data.
        model_save_path (str): Path where the .pkl model file will be saved.
        test_size (float): Proportion of dataset to include in the test split.
        n_estimators (int): Number of trees in the forest.

    Returns:
        dict: A dictionary containing accuracy and the classification report.
    """

    # 1. Load Data
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"The file {data_path} was not found.")

    df = pd.read_csv(data_path)

    # Basic validation
    required_cols = {'Substrate_Deg', 'Base_pKa', 'Solvent_Epsilon', 'Temp_C', 'Is_Bulky', 'Mechanism'}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"CSV is missing required columns: {required_cols - set(df.columns)}")

    # 2. Preprocessing
    X = df.drop('Mechanism', axis=1)
    y = df['Mechanism']

    # 3. Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y
    )

    # 4. Train
    print(f"Training RandomForest with {n_estimators} trees...")
    rf = RandomForestClassifier(n_estimators=n_estimators, max_depth=8, random_state=42)
    rf.fit(X_train, y_train)

    # 5. Evaluate
    predictions = rf.predict(X_test)
    acc = accuracy_score(y_test, predictions)
    report = classification_report(y_test, predictions, output_dict=True)

    print(f"Training Complete. Accuracy: {acc:.2f}")

    # 6. Save Model
    # Ensure directory exists
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    joblib.dump(rf, model_save_path)
    print(f"Model saved to: {model_save_path}")

    return {
        "accuracy": acc,
        "report": report,
        "model_path": model_save_path
    }