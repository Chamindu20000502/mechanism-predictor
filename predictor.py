import joblib
import pandas as pd
import os
import tkinter.messagebox as tkmb

MODEL_PATH = 'models/chemistry_model_v2.pkl'
ENCODERS_PATH = 'models/label_encoders.pkl'


def predict_reaction(input_data, model_path=MODEL_PATH, encoders_path=ENCODERS_PATH):
    """
    Predicts the reaction mechanism for a single reaction.

    Args:
        input_data (dict): {
            'Substrate_Degree': str ('Methyl', 'Primary', 'Secondary', 'Tertiary'),
            'Leaving_Group': str ('F-', 'Cl-', 'Br-', 'I-', 'TsO-'),
            'Nucleophile': str (e.g., 'OH-', 'Br-', 'CN-'),
            'Solvent_Type': str ('Polar Protic', 'Polar Aprotic'),
            'Steric_Hindrance': str ('Low', 'High'),
            'Temperature': float (0.0 to 100.0)
        }
        model_path (str): Path to trained .pkl model.
        encoders_path (str): Path to saved label encoders.

    Returns:
        dict: {
            'prediction': str (e.g., 'SN2', 'E1'),
            'probabilities': dict
        }
    """

    # Check if model exists
    if not os.path.exists(model_path):
        tkmb.showerror(
            "Model Not Found",
            "The required machine learning model could not be found.\n"
            "Please train the model first using the training script."
        )
        raise FileNotFoundError(f"Model not found at {model_path}. Train the model first.")

    # Check if encoders exist
    if not os.path.exists(encoders_path):
        tkmb.showerror(
            "Encoders Not Found",
            "The required label encoders could not be found.\n"
            "Please train the model first using the training script."
        )
        raise FileNotFoundError(f"Encoders not found at {encoders_path}. Train the model first.")

    # Load model and encoders
    model = joblib.load(model_path)
    encoders = joblib.load(encoders_path)

    expected_cols = [
        'Substrate_Degree',
        'Leaving_Group',
        'Nucleophile',
        'Solvent_Type',
        'Steric_Hindrance',
        'Temperature'
    ]

    # Validate input
    missing = [c for c in expected_cols if c not in input_data]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")

    # Create DataFrame with input data
    df_predict = pd.DataFrame([input_data])[expected_cols]

    # Encode categorical features
    categorical_cols = ['Substrate_Degree', 'Leaving_Group', 'Nucleophile',
                        'Solvent_Type', 'Steric_Hindrance']

    for col in categorical_cols:
        if col in encoders:
            try:
                df_predict[col] = encoders[col].transform(df_predict[col])
            except ValueError as e:
                raise ValueError(f"Invalid value for {col}: {input_data[col]}. "
                                 f"Expected one of: {list(encoders[col].classes_)}")

    # Ensure Temperature is float
    df_predict['Temperature'] = df_predict['Temperature'].astype(float)

    # Predict
    pred_class_encoded = model.predict(df_predict)[0]

    # Decode prediction
    target_encoder = encoders['Target_Mechanism']
    pred_class = target_encoder.inverse_transform([pred_class_encoded])[0]

    # Predict probabilities
    prob_values = model.predict_proba(df_predict)[0]

    # Decode class names for probabilities
    prob_dict = {}
    for i, class_name in enumerate(target_encoder.classes_):
        prob_dict[class_name] = prob_values[i]

    return {
        "prediction": pred_class,
        "probabilities": prob_dict
    }


# # Example usage
# example_input = {
#         'Substrate_Degree': 'Tertiary',
#         'Leaving_Group': 'Br-',
#         'Nucleophile': 'CH3O-',
#         'Solvent_Type': 'Polar Protic',
#         'Steric_Hindrance': 'Low',
#         'Temperature': 25.0
#     }
#
# try:
#     result = predict_reaction(example_input)
#     print("Prediction:", result['prediction'])
#     print("\nProbabilities:")
#     for mechanism, prob in sorted(result['probabilities'].items(),
#                                       key=lambda x: x[1], reverse=True):
#         print(f"  {mechanism}: {prob:.4f} ({prob * 100:.2f}%)")
# except Exception as e:
#     print(f"Prediction failed: {e}")