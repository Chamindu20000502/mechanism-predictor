import joblib
import pandas as pd
import os
import tkinter.messagebox as tkmb

def predict_reaction(model_path, input_data):
    """
    Predicts the reaction mechanism for a single reaction.

    Args:
        model_path (str): Path to trained .pkl model.
        input_data (dict): {
            'Substrate_Deg': int (1, 2, 3),
            'Base_pKa': float,
            'Solvent_Epsilon': float,
            'Temp_C': float,
            'Is_Bulky': int (0 or 1)
        }

    Returns:
        dict: {
            'prediction': str,
            'probabilities': dict
        }
    """

    if not os.path.exists(model_path):
        tkmb.showerror(
            "Model Not Found",
            "The required machine learning model could not be found.\n"
            "Please make sure the model file is available and try again."
        )
        raise FileNotFoundError(
            f"Model not found at {model_path}. Train the model first."
        )

    model = joblib.load(model_path)

    expected_cols = [
        'Substrate_Deg',
        'Base_pKa',
        'Solvent_Epsilon',
        'Temp_C',
        'Is_Bulky'
    ]

    # Validate input
    missing = [c for c in expected_cols if c not in input_data]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")

    # Convert to DataFrame (1-row)
    df_predict = pd.DataFrame([input_data])[expected_cols]

    # Predict
    pred_class = model.predict(df_predict)[0]

    # Predict probabilities (confidence)
    prob_values = model.predict_proba(df_predict)[0]
    prob_dict = dict(zip(model.classes_, prob_values))

    return {
        "prediction": pred_class,
        "probabilities": prob_dict
    }
