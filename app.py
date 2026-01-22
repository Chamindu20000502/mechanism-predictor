# from train_model import train_mechanism_model
#
# DATA_FILE = 'data/reaction_data.csv'
# MODEL_PATH = 'models/chemistry_model_v1.pkl'
#
# #  model training
# try:
#     result = train_mechanism_model(DATA_FILE, MODEL_PATH, n_estimators=200)
#     print(result)
# except Exception as e:
#     print(f"Skipping training (Error: {e})")



import customtkinter as ctk
import tkinter.messagebox as tkmb
from predictor import predict_reaction

# --- Configuration ---
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"


def predict(data):
    try:
        result = predict_reaction(
            model_path="models/chemistry_model_v1.pkl",
            input_data={
                "Substrate_Deg": data["degree"],
                "Base_pKa": data["pka"],
                "Solvent_Epsilon": data["epsilon"],
                "Temp_C": data["temp"],
                "Is_Bulky": data["bulky"]
            }
        )
        return result

    except Exception as e:
        return e


class ReactionPredictorApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("ChemPredict: Reaction Classifier")
        self.geometry("900x600")
        self.resizable(False, False)

        # Layout Configuration (2 Columns)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- LEFT SIDEBAR (Inputs) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1)  # Push button to bottom

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="ChemPredict ML",
                                       font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # 1. Substrate Degree (Segmented Button for categorical data)
        self.lbl_substrate = ctk.CTkLabel(self.sidebar_frame, text="Substrate Degree:", anchor="w")
        self.lbl_substrate.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")

        self.substrate_var = ctk.StringVar(value="Secondary")
        self.seg_substrate = ctk.CTkSegmentedButton(self.sidebar_frame, values=["Primary", "Secondary", "Tertiary"],
                                                    variable=self.substrate_var)
        self.seg_substrate.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")

        # 2. Base pKa (Slider + Entry for precision)
        self.lbl_pka = ctk.CTkLabel(self.sidebar_frame, text="Base pKa:", anchor="w")
        self.lbl_pka.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="w")

        self.entry_pka = ctk.CTkEntry(self.sidebar_frame, placeholder_text="e.g. 15.7")
        self.entry_pka.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="ew")

        # 3. Solvent Epsilon (Dielectric Constant)
        self.lbl_solv = ctk.CTkLabel(self.sidebar_frame, text="Solvent Dielectric (ε):", anchor="w")
        self.lbl_solv.grid(row=5, column=0, padx=20, pady=(10, 0), sticky="w")

        self.entry_epsilon = ctk.CTkEntry(self.sidebar_frame, placeholder_text="e.g. 78.4 (Water)")
        self.entry_epsilon.grid(row=6, column=0, padx=20, pady=(0, 10), sticky="ew")

        # 4. Temperature
        self.lbl_temp = ctk.CTkLabel(self.sidebar_frame, text="Temperature (°C):", anchor="w")
        self.lbl_temp.grid(row=7, column=0, padx=20, pady=(10, 0), sticky="w")

        self.entry_temp = ctk.CTkEntry(self.sidebar_frame, placeholder_text="e.g. 25")
        self.entry_temp.grid(row=8, column=0, padx=20, pady=(0, 10), sticky="ew")

        # 5. Bulkiness (Switch)
        self.switch_bulk = ctk.CTkSwitch(self.sidebar_frame, text="Sterically Hindered Base?")
        self.switch_bulk.grid(row=9, column=0, padx=20, pady=20, sticky="w")

        # Predict Button
        self.btn_predict = ctk.CTkButton(self.sidebar_frame, text="PREDICT REACTION", height=40,
                                         command=self.run_prediction)
        self.btn_predict.grid(row=10, column=0, padx=20, pady=30, sticky="ew")

        # --- RIGHT MAIN AREA (Results) ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Header
        self.header = ctk.CTkLabel(self.main_frame, text="Prediction Analysis",
                                   font=ctk.CTkFont(size=24, weight="bold"))
        self.header.pack(pady=20)

        # Result Display Box
        self.result_frame = ctk.CTkFrame(self.main_frame, fg_color=("#EBEBEB", "#2B2B2B"))  # Light/Dark mode colors
        self.result_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.lbl_result_title = ctk.CTkLabel(self.result_frame, text="PREDICTED MECHANISM",
                                             font=ctk.CTkFont(size=14, weight="bold"), text_color="gray")
        self.lbl_result_title.pack(pady=(40, 10))

        self.lbl_prediction = ctk.CTkLabel(self.result_frame, text="WAITING FOR INPUT...",
                                           font=ctk.CTkFont(size=40, weight="bold"))
        self.lbl_prediction.pack(pady=10)

        # Probability Bars (Mockup)
        self.stats_frame = ctk.CTkFrame(self.result_frame, fg_color="transparent")
        self.stats_frame.pack(fill="x", padx=40, pady=40)

        self.bars={}

        # The first argument is the dictionary key, the second is the UI label
        self.create_stat_bar("SN1", "SN1 Probability")
        self.create_stat_bar("SN2", "SN2 Probability")
        self.create_stat_bar("E1", "E1 Probability")
        self.create_stat_bar("E2", "E2 Probability")

    def create_stat_bar(self, key, label_text, value=0):
        """Helper to create progress bars and store them in self.bars"""
        container = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
        container.pack(fill="x", pady=5)

        label = ctk.CTkLabel(container, text=label_text, width=100, anchor="w")
        label.pack(side="left")

        # Color logic
        color = "#1f6aa5"
        if "E" in key: color = "#a51f1f"

        progress = ctk.CTkProgressBar(container, progress_color=color)
        progress.set(float(value))  # Ensure it's a float
        progress.pack(side="left", fill="x", expand=True, padx=10)

        # STORE THE REFERENCE: This is the critical "dictionary-ready" step
        self.bars[key] = progress

    def get_inputs(self):
        """Validation and retrieval of inputs"""
        try:
            # Map Categorical to Numerical if your model needs it
            degree_map = {"Primary": 1, "Secondary": 2, "Tertiary": 3}

            data = {
                "degree": degree_map[self.substrate_var.get()],
                "pka": float(self.entry_pka.get()),
                "epsilon": float(self.entry_epsilon.get()),
                "temp": float(self.entry_temp.get()),
                "bulky": 1 if self.switch_bulk.get() == 1 else 0
            }
            return data
        except ValueError:
            tkmb.showerror("Input Error", "Please ensure pKa, Epsilon, and Temp are valid numbers.")
            return None

    def run_prediction(self):
        """Connect your ML Model Here"""
        inputs = self.get_inputs()
        if not inputs:
            return

        result = predict(inputs)

        for key, value in result["probabilities"].items():
            if key in self.bars:
                # Convert numpy float to standard float and update
                self.bars[key].set(float(value))

        # Update UI
        self.lbl_prediction.configure(text=result["prediction"])

        # Change color based on result
        if "SN" in result["prediction"]:
            self.lbl_prediction.configure(text_color="#4CC9F0")  # Cyan
        else:
            self.lbl_prediction.configure(text_color="#F72585")  # Pink


if __name__ == "__main__":
    app = ReactionPredictorApp()
    app.mainloop()