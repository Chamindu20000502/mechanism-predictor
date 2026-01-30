import customtkinter as ctk
import tkinter.messagebox as tkmb
from predictor import predict_reaction

# --- Configuration ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")


def predict(data):
    try:
        result = predict_reaction(
            input_data={
                "Substrate_Degree": data["substrate_degree"],
                "Leaving_Group": data["leaving_group"],
                "Nucleophile": data["nucleophile"],
                "Solvent_Type": data["solvent_type"],
                "Steric_Hindrance": data["steric_hindrance"],
                "Temperature": data["temperature"]
            }
        )
        return result
    except Exception as e:
        return {"error": str(e)}


class ReactionPredictorApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("ChemPredict: Organic Reaction Mechanism Predictor")
        self.geometry("950x700")
        self.resizable(False, False)

        # Layout Configuration (2 Columns)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- LEFT SIDEBAR (Inputs) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=350, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(13, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="ChemPredict ML",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # 1. Substrate Degree
        self.lbl_substrate = ctk.CTkLabel(
            self.sidebar_frame,
            text="Substrate Degree:",
            anchor="w"
        )
        self.lbl_substrate.grid(row=1, column=0, padx=20, pady=(10, 5), sticky="ew")

        self.substrate_var = ctk.StringVar(value="Secondary")
        self.seg_substrate = ctk.CTkSegmentedButton(
            self.sidebar_frame,
            values=["Methyl", "Primary", "Secondary", "Tertiary"],
            variable=self.substrate_var
        )
        self.seg_substrate.grid(row=2, column=0, padx=20, pady=(0, 15), sticky="ew")

        # 2. Leaving Group
        self.lbl_leaving = ctk.CTkLabel(
            self.sidebar_frame,
            text="Leaving Group:",
            anchor="w"
        )
        self.lbl_leaving.grid(row=3, column=0, padx=20, pady=(5, 5), sticky="ew")

        self.leaving_var = ctk.StringVar(value="Br-")
        self.menu_leaving = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["F-", "Cl-", "Br-", "I-", "TsO-"],
            variable=self.leaving_var
        )
        self.menu_leaving.grid(row=4, column=0, padx=20, pady=(0, 15), sticky="ew")

        # 3. Nucleophile
        self.lbl_nucleophile = ctk.CTkLabel(
            self.sidebar_frame,
            text="Nucleophile:",
            anchor="w"
        )
        self.lbl_nucleophile.grid(row=5, column=0, padx=20, pady=(5, 5), sticky="ew")

        self.nucleophile_var = ctk.StringVar(value="OH-")
        self.menu_nucleophile = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["H2O", "CH3OH", "NH3", "OH-", "CH3O-", "CN-", "tBuO-", "LDA"],
            variable=self.nucleophile_var
        )
        self.menu_nucleophile.grid(row=6, column=0, padx=20, pady=(0, 15), sticky="ew")

        # 4. Solvent Type
        self.lbl_solvent = ctk.CTkLabel(
            self.sidebar_frame,
            text="Solvent Type:",
            anchor="w"
        )
        self.lbl_solvent.grid(row=7, column=0, padx=20, pady=(5, 5), sticky="ew")

        self.solvent_var = ctk.StringVar(value="Polar Protic")
        self.seg_solvent = ctk.CTkSegmentedButton(
            self.sidebar_frame,
            values=["Polar Protic", "Polar Aprotic"],
            variable=self.solvent_var
        )
        self.seg_solvent.grid(row=8, column=0, padx=20, pady=(0, 15), sticky="ew")

        # 5. Steric Hindrance
        self.lbl_steric = ctk.CTkLabel(
            self.sidebar_frame,
            text="Steric Hindrance:",
            anchor="w"
        )
        self.lbl_steric.grid(row=9, column=0, padx=20, pady=(5, 5), sticky="ew")

        self.steric_var = ctk.StringVar(value="Low")
        self.seg_steric = ctk.CTkSegmentedButton(
            self.sidebar_frame,
            values=["Low", "High"],
            variable=self.steric_var
        )
        self.seg_steric.grid(row=10, column=0, padx=20, pady=(0, 15), sticky="ew")

        # 6. Temperature
        self.lbl_temp = ctk.CTkLabel(
            self.sidebar_frame,
            text="Temperature (°C):",
            anchor="w"
        )
        self.lbl_temp.grid(row=11, column=0, padx=20, pady=(5, 5), sticky="ew")

        self.entry_temp = ctk.CTkEntry(
            self.sidebar_frame,
            placeholder_text="e.g. 25 (0-100°C)"
        )
        self.entry_temp.grid(row=12, column=0, padx=20, pady=(0, 15), sticky="ew")

        # Predict Button
        self.btn_predict = ctk.CTkButton(
            self.sidebar_frame,
            text="PREDICT MECHANISM",
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.run_prediction
        )
        self.btn_predict.grid(row=13, column=0, padx=20, pady=(0, 30), sticky="ew")

        # --- RIGHT MAIN AREA (Results) ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Header
        self.header = ctk.CTkLabel(
            self.main_frame,
            text="Prediction Results",
            font=ctk.CTkFont(size=26, weight="bold")
        )
        self.header.pack(pady=20)

        # Result Display Box
        self.result_frame = ctk.CTkFrame(self.main_frame, fg_color=("#EBEBEB", "#2B2B2B"))
        self.result_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.lbl_result_title = ctk.CTkLabel(
            self.result_frame,
            text="PREDICTED MECHANISM",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="gray"
        )
        self.lbl_result_title.pack(pady=(40, 10))

        self.lbl_prediction = ctk.CTkLabel(
            self.result_frame,
            text="WAITING FOR INPUT...",
            font=ctk.CTkFont(size=42, weight="bold")
        )
        self.lbl_prediction.pack(pady=10)

        # Stereochemistry Result
        self.lbl_stereo_title = ctk.CTkLabel(
            self.result_frame,
            text="STEREOCHEMISTRY",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="gray"
        )
        self.lbl_stereo_title.pack(pady=(30, 5))

        self.lbl_stereo = ctk.CTkLabel(
            self.result_frame,
            text="—",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.lbl_stereo.pack(pady=(0, 20))

        # Probability Bars
        self.stats_frame = ctk.CTkFrame(self.result_frame, fg_color="transparent")
        self.stats_frame.pack(fill="x", padx=40, pady=40)

        self.bars = {}
        self.percentage_labels = {}

        self.create_stat_bar("SN1", "SN1 Probability", "#1f6aa5")
        self.create_stat_bar("SN2", "SN2 Probability", "#1f8aa5")
        self.create_stat_bar("E1", "E1 Probability", "#a51f1f")
        self.create_stat_bar("E2", "E2 Probability", "#a5501f")
        self.create_stat_bar("No Reaction", "No Reaction", "#666666")

        # Model accuracy (bottom-right, small & subtle)
        self.lbl_accuracy = ctk.CTkLabel(
            self,
            text="Model accuracy: 97.1%",
            font=ctk.CTkFont(size=11),
            text_color="#888888"
        )
        self.lbl_accuracy.place(relx=0.99, rely=0.99, anchor="se")

    def get_stereochemistry(self, mechanism):
        if mechanism == "SN1":
            return "Racemization (Stereochemistry Lost)"
        elif mechanism == "SN2":
            return "Inversion of Configuration"
        elif mechanism == "E1":
            return "Stereochemistry Lost"
        elif mechanism == "E2":
            return "Anti-Periplanar Requirement"
        else:
            return "No Change"

    def create_stat_bar(self, key, label_text, color, value=0):
        """Helper to create progress bars with percentage labels"""
        container = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
        container.pack(fill="x", pady=8)

        label = ctk.CTkLabel(container, text=label_text, width=140, anchor="w")
        label.pack(side="left")

        progress = ctk.CTkProgressBar(container, progress_color=color)
        progress.set(float(value))
        progress.pack(side="left", fill="x", expand=True, padx=10)

        percentage_label = ctk.CTkLabel(container, text=f"{int(value * 100)}%", width=50, anchor="e")
        percentage_label.pack(side="left")

        self.bars[key] = progress
        self.percentage_labels[key] = percentage_label

    def get_inputs(self):
        """Validation and retrieval of inputs"""
        try:
            # Validate temperature
            temp = float(self.entry_temp.get())
            if temp < 0 or temp > 100:
                tkmb.showwarning("Temperature Warning", "Temperature should be between 0-100°C")
                return None
            data = {
                "substrate_degree": self.substrate_var.get(),
                "leaving_group": self.leaving_var.get(),
                "nucleophile": self.nucleophile_var.get(),
                "solvent_type": self.solvent_var.get(),
                "steric_hindrance": self.steric_var.get(),
                "temperature": temp
            }
            return data
        except ValueError:
            tkmb.showerror("Input Error", "Please ensure Temperature is a valid number.")
            return None

    def run_prediction(self):
        """Run ML prediction"""
        inputs = self.get_inputs()
        if not inputs:
            return

        result = predict(inputs)

        # Check for errors
        if "error" in result:
            tkmb.showerror("Prediction Error", f"Error: {result['error']}")
            return

        # Update probability bars
        for key, value in result["probabilities"].items():
            if key in self.bars:
                self.bars[key].set(float(value))
                self.percentage_labels[key].configure(text=f"{value * 100:.1f}%")

        # Update prediction label
        prediction = result["prediction"]
        self.lbl_prediction.configure(text=prediction)
        self.lbl_prediction.configure(text=prediction)

        stereo_text = self.get_stereochemistry(prediction)
        self.lbl_stereo.configure(text=stereo_text)

        # Optional color coding
        if prediction == "SN2":
            self.lbl_stereo.configure(text_color="#1f8aa5")
        elif prediction in ["SN1", "E1"]:
            self.lbl_stereo.configure(text_color="#a51f1f")
        elif prediction == "E2":
            self.lbl_stereo.configure(text_color="#a5501f")
        else:
            self.lbl_stereo.configure(text_color="#888888")

        # Change color based on result
        if prediction == "SN1":
            self.lbl_prediction.configure(text_color="#1f6aa5")
        elif prediction == "SN2":
            self.lbl_prediction.configure(text_color="#1f8aa5")
        elif prediction == "E1":
            self.lbl_prediction.configure(text_color="#a51f1f")
        elif prediction == "E2":
            self.lbl_prediction.configure(text_color="#a5501f")
        else:  # No Reaction
            self.lbl_prediction.configure(text_color="#888888")


if __name__ == "__main__":
    app = ReactionPredictorApp()
    app.mainloop()