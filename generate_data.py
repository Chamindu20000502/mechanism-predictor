# import pandas as pd
# import numpy as np
# import random
#
#
# def get_mechanism(row):
#     """
#     Assigns a reaction mechanism based on simplified Organic Chem rules.
#     """
#     deg = row['Substrate_Deg']  # 1=Primary, 2=Secondary, 3=Tertiary
#     pka = row['Base_pKa']  # <10 Weak, >15 Strong
#     temp = row['Temp_C']  # High temp favors elimination
#     bulky = row['Is_Bulky']  # Bulky base favors E2
#     solvent = row['Solvent_Epsilon']  # High (>50) = Polar Protic (favors ions)
#
#     # --- TERTIARY (3°) ---
#     if deg == 3:
#         if pka > 12:  # Strong Base
#             return 'E2'  # 3° substrates + strong base -> E2 (Steric hindrance stops SN2)
#         else:  # Weak Base
#             if temp > 60:
#                 return 'E1'  # Heat favors Elimination
#             else:
#                 return 'SN1'  # Cool/Room temp favors Substitution
#
#     # --- PRIMARY (1°) ---
#     elif deg == 1:
#         if bulky == 1:
#             return 'E2'  # Bulky base on 1° forces E2 (e.g., t-BuOK)
#         elif pka > 12:
#             return 'SN2'  # Strong nuc/base, unhindered -> SN2
#         else:
#             return 'No_Reaction'  # 1° typically unreactive with weak nuc/base (unless very specific conditions)
#
#     # --- SECONDARY (2°) - The Battleground ---
#     elif deg == 2:
#         if pka > 12:  # Strong Base
#             if temp > 70 or bulky == 1:
#                 return 'E2'  # Heat or Bulk favors E2
#             else:
#                 return 'SN2'  # Strong nuc, low heat, not bulky -> SN2
#         else:  # Weak Base
#             if solvent > 40:  # Polar solvent stabilizes carbocation
#                 if temp > 60:
#                     return 'E1'
#                 else:
#                     return 'SN1'
#             else:
#                 return 'No_Reaction'
#
#     return 'Other'
#
#
# # 1. Generate Random Feature Data
# n_samples = 2000
# data = {
#     'Substrate_Deg': np.random.choice([1, 2, 3], n_samples),
#     # pKa: Mix of weak (e.g., H2O=15.7, Acetate=4.7) and strong (e.g., Amide=35, Alkoxide=16)
#     'Base_pKa': np.round(np.random.uniform(0, 35, n_samples), 1),
#     'Solvent_Epsilon': np.random.choice([2, 20, 33, 80], n_samples),  # Hexane, Acetone, Methanol, Water
#     'Temp_C': np.random.randint(0, 150, n_samples),
#     'Is_Bulky': np.random.choice([0, 1], n_samples, p=[0.7, 0.3])
# }
#
# df = pd.DataFrame(data)
#
# # 2. Apply Chemistry Logic to create labels
# df['Mechanism'] = df.apply(get_mechanism, axis=1)
#
# # 3. Filter out 'Other' or 'No_Reaction' for cleaner training
# df = df[~df['Mechanism'].isin(['Other', 'No_Reaction'])]
#
# # 4. Save
# df.to_csv('data/reaction_data.csv', index=False)
# print(f"Dataset generated with {len(df)} rows. Saved to reaction_data.csv")
# print(df['Mechanism'].value_counts())

import pandas as pd
import numpy as np
import random

# --- 1. Define The Chemical Domain ---
substrates = ['Methyl', 'Primary', 'Secondary', 'Tertiary']
solvents = ['Polar Protic', 'Polar Aprotic']

# Specific Leaving Groups mapped to their "Ability" (internal logic)
# F- (Poor), Cl- (Fair), Br- (Good), I- (Excellent), TsO- (Excellent)
leaving_groups = {
    'F-': 'Poor',
    'Cl-': 'Fair',
    'Br-': 'Good',
    'I-': 'Excellent',
    'TsO-': 'Excellent'
}

# Specific Nucleophiles mapped to Strength & Hindrance
# This replaces the explicit "Base Strength" column logic
nucleophiles = [
    # (Name, Strength, Intrinsic Hindrance)
    ('H2O', 'Weak', 'Low'),
    ('CH3OH', 'Weak', 'Low'),
    ('NH3', 'Moderate', 'Low'),
    ('OH-', 'Strong', 'Low'),
    ('CH3O-', 'Strong', 'Low'),
    ('CN-', 'Strong', 'Low'),  # Great Nu, Weak Base
    ('tBuO-', 'Strong', 'High'),  # Bulky Base
    ('LDA', 'Strong', 'High')  # Very Bulky
]


# --- 2. The Reaction Logic (The "Teacher") ---
def determine_mechanism(row):
    # Unpack features
    sub = row['Substrate_Degree']
    lg_type = row['Leaving_Group']
    lg_quality = leaving_groups[lg_type]
    solv = row['Solvent_Type']
    temp = row['Temperature']

    # We derive strength/hindrance from the specific Nucleophile chosen
    nu_name = row['Nucleophile']
    # Find the properties of this nucleophile from our list above
    nu_props = next(x for x in nucleophiles if x[0] == nu_name)
    strength = nu_props[1]

    # User provided explicit Steric Hindrance column.
    # To keep data consistent, we use the user's column, but we align our choice
    # of nucleophile to match that hindrance during generation (see loop below).
    hindrance = row['Steric_Hindrance']

    # --- RULES ---

    # 1. Bad Leaving Group Rule
    # If LG is F- (Poor), reaction is very rare unless conditions are extreme (not modeled here)
    if lg_quality == 'Poor':
        return 'No Reaction'

    # 2. Temperature Thresholds (Soft boundaries for randomness)
    # High temp favors Elimination (Entropy). Low temp favors Substitution.
    # We set a crossover point around 50°C
    is_high_temp = temp > 50

    # 3. Methyl
    if sub == 'Methyl':
        if strength == 'Strong' and hindrance == 'Low': return 'SN2'
        return 'No Reaction'  # No E1/E2/SN1

    # 4. Primary
    if sub == 'Primary':
        if hindrance == 'High': return 'E2'  # Bulky base (tBuO-) forces E2 even on primary
        if strength == 'Strong': return 'SN2'
        return 'No Reaction'  # Primary carbocations are too unstable for SN1/E1

    # 5. Tertiary
    if sub == 'Tertiary':
        if strength == 'Strong': return 'E2'  # Strong bases force E2
        # Weak base context (Solvolysis)
        if solv == 'Polar Protic':
            return 'E1' if is_high_temp else 'SN1'
        return 'No Reaction'

    # 6. Secondary (The Complex Case)
    if sub == 'Secondary':
        # Strong Base/Nu
        if strength == 'Strong':
            if hindrance == 'High': return 'E2'
            if is_high_temp: return 'E2'  # Heat favors elimination
            if solv == 'Polar Aprotic': return 'SN2'  # Naked Nu
            return 'E2'  # Protic solvent cages Nu, favors E2 slightly or mix

        # Weak Base/Nu
        if solv == 'Polar Protic':
            return 'E1' if is_high_temp else 'SN1'

    return 'No Reaction'


# --- 3. Generate the Dataset ---
data = []
for _ in range(5000):
    # Randomly pick features
    sub = random.choice(substrates)
    lg = random.choice(list(leaving_groups.keys()))
    solv = random.choice(solvents)

    # Temperature: Random float between 0 and 100
    temp = round(random.uniform(0.0, 100.0), 1)

    # Pick a nucleophile
    nu_selection = random.choice(nucleophiles)
    nu_name = nu_selection[0]
    nu_hindrance = nu_selection[2]  # Intrinsic hindrance of the chemical

    # We set the 'Steric_Hindrance' column based on the chemical chosen
    # so the data is physically consistent.
    hind = nu_hindrance

    row = {
        'Substrate_Degree': sub,
        'Leaving_Group': lg,
        'Nucleophile': nu_name,  # Added this so the model knows what is reacting!
        'Solvent_Type': solv,
        'Steric_Hindrance': hind,
        'Temperature': temp
    }

    row['Target_Mechanism'] = determine_mechanism(row)
    data.append(row)

df = pd.DataFrame(data)

# Shuffle columns for cleaner look
df = df[['Substrate_Degree', 'Leaving_Group', 'Nucleophile', 'Solvent_Type', 'Steric_Hindrance', 'Temperature',
         'Target_Mechanism']]

csv_filename = 'data/organic_reaction_dataset.csv'
df.to_csv(csv_filename, index=False)
print(f"✅ Data exported successfully to {csv_filename}")

print(df.head(10))
print("\nStats:")
print(df['Target_Mechanism'].value_counts())