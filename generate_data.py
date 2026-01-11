import pandas as pd
import numpy as np
import random


def get_mechanism(row):
    """
    Assigns a reaction mechanism based on simplified Organic Chem rules.
    """
    deg = row['Substrate_Deg']  # 1=Primary, 2=Secondary, 3=Tertiary
    pka = row['Base_pKa']  # <10 Weak, >15 Strong
    temp = row['Temp_C']  # High temp favors elimination
    bulky = row['Is_Bulky']  # Bulky base favors E2
    solvent = row['Solvent_Epsilon']  # High (>50) = Polar Protic (favors ions)

    # --- TERTIARY (3°) ---
    if deg == 3:
        if pka > 12:  # Strong Base
            return 'E2'  # 3° substrates + strong base -> E2 (Steric hindrance stops SN2)
        else:  # Weak Base
            if temp > 60:
                return 'E1'  # Heat favors Elimination
            else:
                return 'SN1'  # Cool/Room temp favors Substitution

    # --- PRIMARY (1°) ---
    elif deg == 1:
        if bulky == 1:
            return 'E2'  # Bulky base on 1° forces E2 (e.g., t-BuOK)
        elif pka > 12:
            return 'SN2'  # Strong nuc/base, unhindered -> SN2
        else:
            return 'No_Reaction'  # 1° typically unreactive with weak nuc/base (unless very specific conditions)

    # --- SECONDARY (2°) - The Battleground ---
    elif deg == 2:
        if pka > 12:  # Strong Base
            if temp > 70 or bulky == 1:
                return 'E2'  # Heat or Bulk favors E2
            else:
                return 'SN2'  # Strong nuc, low heat, not bulky -> SN2
        else:  # Weak Base
            if solvent > 40:  # Polar solvent stabilizes carbocation
                if temp > 60:
                    return 'E1'
                else:
                    return 'SN1'
            else:
                return 'No_Reaction'

    return 'Other'


# 1. Generate Random Feature Data
n_samples = 2000
data = {
    'Substrate_Deg': np.random.choice([1, 2, 3], n_samples),
    # pKa: Mix of weak (e.g., H2O=15.7, Acetate=4.7) and strong (e.g., Amide=35, Alkoxide=16)
    'Base_pKa': np.round(np.random.uniform(0, 35, n_samples), 1),
    'Solvent_Epsilon': np.random.choice([2, 20, 33, 80], n_samples),  # Hexane, Acetone, Methanol, Water
    'Temp_C': np.random.randint(0, 150, n_samples),
    'Is_Bulky': np.random.choice([0, 1], n_samples, p=[0.7, 0.3])
}

df = pd.DataFrame(data)

# 2. Apply Chemistry Logic to create labels
df['Mechanism'] = df.apply(get_mechanism, axis=1)

# 3. Filter out 'Other' or 'No_Reaction' for cleaner training
df = df[~df['Mechanism'].isin(['Other', 'No_Reaction'])]

# 4. Save
df.to_csv('data/reaction_data.csv', index=False)
print(f"Dataset generated with {len(df)} rows. Saved to reaction_data.csv")
print(df['Mechanism'].value_counts())