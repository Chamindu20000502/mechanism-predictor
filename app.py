from train_model import train_mechanism_model
from predictor import predict_reaction

DATA_FILE = 'data/reaction_data.csv'
MODEL_PATH = 'models/chemistry_model_v1.pkl'

#  model training
try:
    result = train_mechanism_model(DATA_FILE, MODEL_PATH, n_estimators=200)
    print(result)
except Exception as e:
    print(f"Skipping training (Error: {e})")


#  Call the Prediction Script
print("\n--- Step 2: Predicting New Reactions ---")
try:
    result = predict_reaction(
        model_path="models/chemistry_model_v1.pkl",
        input_data={
            "Substrate_Deg": 2,
            "Base_pKa": 15.7,
            "Solvent_Epsilon": 20,
            "Temp_C": 80,
            "Is_Bulky": 1
        }
    )
    print(result)

except Exception as e:
    print(f"Prediction failed: {e}")