import ast
import pandas as pd

# ── Load all datasets ────────────────────────────────────────────────────────
sym_des     = pd.read_csv("datasets/symtoms_df.csv")
precautions = pd.read_csv("datasets/precautions_df.csv")
workout     = pd.read_csv("datasets/workout_df.csv")
description = pd.read_csv("datasets/description.csv")
medications = pd.read_csv("datasets/medications.csv")
diets       = pd.read_csv("datasets/diets.csv")
severity_df = pd.read_csv("datasets/Symptomseverity.csv")

# ── Normalize disease name casing ────────────────────────────────────────────
for df in [description, precautions, medications, diets]:
    df['Disease'] = df['Disease'].str.strip().str.lower()
workout['disease'] = workout['disease'].str.strip().str.lower()

# ── Severity weight map  {symptom_name: weight} ──────────────────────────────
severity_map = dict(
    zip(
        severity_df['Symptom'].str.strip().str.lower().str.replace(' ', '_'),
        severity_df['weight']
    )
)

# ── Disease list (index → name) ───────────────────────────────────────────────
diseases_list = {
    15: 'Fungal infection', 4: 'Allergy', 16: 'GERD',
    9: 'Chronic cholestasis', 14: 'Drug Reaction', 33: 'Peptic ulcer disease',
    1: 'AIDS', 12: 'Diabetes', 17: 'Gastroenteritis', 6: 'Bronchial Asthma',
    23: 'Hypertension', 30: 'Migraine', 7: 'Cervical spondylosis',
    32: 'Paralysis (brain hemorrhage)', 28: 'Jaundice', 29: 'Malaria',
    8: 'Chicken pox', 11: 'Dengue', 37: 'Typhoid', 40: 'hepatitis A',
    19: 'Hepatitis B', 20: 'Hepatitis C', 21: 'Hepatitis D', 22: 'Hepatitis E',
    3: 'Alcoholic hepatitis', 36: 'Tuberculosis', 10: 'Common Cold',
    34: 'Pneumonia', 13: 'Dimorphic hemmorhoids(piles)', 18: 'Heart attack',
    39: 'Varicose veins', 26: 'Hypothyroidism', 24: 'Hyperthyroidism',
    25: 'Hypoglycemia', 31: 'Osteoarthristis', 5: 'Arthritis',
    0: 'Paroxysmal Positional Vertigo', 2: 'Acne',
    38: 'Urinary tract infection', 35: 'Psoriasis', 27: 'Impetigo'
}


def _clean_items(values) -> list:
    cleaned = []

    for value in values:
        if pd.isna(value):
            continue

        if isinstance(value, str):
            text = value.strip()
            if text.startswith('[') and text.endswith(']'):
                try:
                    parsed = ast.literal_eval(text)
                    cleaned.extend(str(item).strip() for item in parsed if str(item).strip())
                    continue
                except (ValueError, SyntaxError):
                    pass
            if text:
                cleaned.append(text)
        else:
            cleaned.append(str(value).strip())

    return cleaned


def helper(dis: str) -> tuple:
    """Return (desc, precautions, medications, diets, workouts) for a disease."""
    dis = dis.strip().lower()

    desc = description[description['Disease'] == dis]["Description"]
    desc = " ".join(desc.values) if len(desc) > 0 else "No description available."

    pre = precautions[precautions['Disease'] == dis][
        ['Precaution_1', 'Precaution_2', 'Precaution_3', 'Precaution_4']
    ].values.tolist()
    pre = pre[0] if len(pre) > 0 else ["No precautions available."]

    med = medications[medications['Disease'] == dis]['Medication'].values
    med = _clean_items(med) if len(med) > 0 else ["No medication data."]

    die = diets[diets['Disease'] == dis]['Diet'].values
    die = _clean_items(die) if len(die) > 0 else ["No diet data."]

    wrk = workout[workout['disease'] == dis]['workout'].values
    wrk = _clean_items(wrk) if len(wrk) > 0 else ["No workout data."]

    return desc, pre, med, die, wrk
