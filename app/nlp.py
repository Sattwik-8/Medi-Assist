from app.model import symptoms_dict

# ── Natural language aliases → canonical symptom names ────────────────────────
symptom_aliases = {
    'fever': 'high_fever', 'temperature': 'high_fever', 'mild fever': 'mild_fever',
    'low fever': 'mild_fever', 'headache': 'headache', 'head pain': 'headache',
    'head ache': 'headache', 'vomit': 'vomiting', 'vomiting': 'vomiting',
    'nausea': 'nausea', 'nauseous': 'nausea', 'cough': 'cough', 'coughing': 'cough',
    'cold': 'runny_nose', 'runny nose': 'runny_nose', 'sneezing': 'continuous_sneezing',
    'sneeze': 'continuous_sneezing', 'fatigue': 'fatigue', 'tired': 'fatigue',
    'tiredness': 'fatigue', 'weakness': 'fatigue', 'weak': 'fatigue',
    'itching': 'itching', 'itch': 'itching', 'rash': 'skin_rash',
    'skin rash': 'skin_rash', 'diarrhea': 'diarrhoea', 'diarrhoea': 'diarrhoea',
    'loose motion': 'diarrhoea', 'loose motions': 'diarrhoea',
    'stomach pain': 'stomach_pain', 'stomach ache': 'stomach_pain',
    'abdominal pain': 'abdominal_pain', 'belly pain': 'belly_pain',
    'chest pain': 'chest_pain', 'back pain': 'back_pain', 'neck pain': 'neck_pain',
    'joint pain': 'joint_pain', 'knee pain': 'knee_pain', 'muscle pain': 'muscle_pain',
    'breathless': 'breathlessness', 'breathing problem': 'breathlessness',
    'shortness of breath': 'breathlessness', 'sweating': 'sweating', 'sweat': 'sweating',
    'chills': 'chills', 'shivering': 'shivering', 'shiver': 'shivering',
    'dizziness': 'dizziness', 'dizzy': 'dizziness', 'constipation': 'constipation',
    'acidity': 'acidity', 'anxiety': 'anxiety', 'depression': 'depression',
    'weight loss': 'weight_loss', 'weight gain': 'weight_gain',
    'loss of appetite': 'loss_of_appetite', 'no appetite': 'loss_of_appetite',
    'dark urine': 'dark_urine', 'yellow skin': 'yellowish_skin',
    'yellowish skin': 'yellowish_skin', 'yellow eyes': 'yellowing_of_eyes',
    'blurred vision': 'blurred_and_distorted_vision', 'palpitation': 'palpitations',
    'fast heartbeat': 'fast_heart_rate', 'high sugar': 'irregular_sugar_level',
    'blood in stool': 'bloody_stool', 'phlegm': 'phlegm', 'mucus': 'phlegm',
    'swollen legs': 'swollen_legs', 'polyuria': 'polyuria',
    'frequent urination': 'polyuria', 'burning urination': 'burning_micturition',
    'painful urination': 'burning_micturition', 'blackheads': 'blackheads',
    'pimples': 'pus_filled_pimples', 'red eyes': 'redness_of_eyes',
    'watery eyes': 'watering_from_eyes', 'loss of smell': 'loss_of_smell',
    'sore throat': 'throat_irritation', 'throat pain': 'throat_irritation',
    'congestion': 'congestion', 'stiff neck': 'stiff_neck',
    'dehydration': 'dehydration', 'indigestion': 'indigestion',
    'body ache': 'muscle_pain', 'body pain': 'muscle_pain',
    'sugar': 'irregular_sugar_level', 'diabetes symptom': 'polyuria',
    'skin peeling': 'skin_peeling', 'blisters': 'blister', 'blister': 'blister',
    'swelling': 'swelling_joints', 'swollen': 'swelling_joints',
    'gas': 'passage_of_gases', 'bloating': 'passage_of_gases',
    'loss of balance': 'loss_of_balance', 'unsteady': 'unsteadiness',
    'slurred speech': 'slurred_speech', 'speech problem': 'slurred_speech',
    # ── Hindi aliases ──────────────────────────────────────────────────────────
    'bukhar': 'high_fever', 'bukhaar': 'high_fever', 'tez bukhar': 'high_fever',
    'sir dard': 'headache', 'sardard': 'headache', 'sar dard': 'headache',
    'ulti': 'vomiting', 'vomit': 'vomiting', 'ji machalna': 'nausea',
    'khansi': 'cough', 'khansi aana': 'cough', 'nazla': 'runny_nose',
    'thakan': 'fatigue', 'kamzori': 'fatigue', 'khujli': 'itching',
    'daane': 'skin_rash', 'dast': 'diarrhoea', 'pet dard': 'stomach_pain',
    'seene mein dard': 'chest_pain', 'sans lena mushkil': 'breathlessness',
    'pasina': 'sweating', 'kaanpna': 'shivering', 'chakkar': 'dizziness',
    'kabz': 'constipation', 'acidity': 'acidity', 'bhooj na lagna': 'loss_of_appetite',
    'vajan kam hona': 'weight_loss', 'peeli skin': 'yellowish_skin',
    'aankhon mein pelapan': 'yellowing_of_eyes', 'dark peshab': 'dark_urine',
    'baar baar peshab': 'polyuria', 'peshab mein jalan': 'burning_micturition',
    'gala dard': 'throat_irritation', 'gardan akad': 'stiff_neck',
    'paani ki kami': 'dehydration', 'badan dard': 'muscle_pain',
    # ── Bengali aliases ────────────────────────────────────────────────────────
    'jor': 'high_fever', 'jwar': 'high_fever', 'mathay byatha': 'headache',
    'bomi': 'vomiting', 'bomi bomi bhab': 'nausea', 'kashi': 'cough',
    'naak diya jol': 'runny_nose', 'thakthakia': 'fatigue', 'durbolota': 'fatigue',
    'chulkani': 'itching', 'chama phola': 'skin_rash', 'paitshya': 'diarrhoea',
    'pater byatha': 'stomach_pain', 'buker byatha': 'chest_pain',
    'shwas koshto': 'breathlessness', 'ghama': 'sweating', 'kaapa': 'shivering',
    'mathaghoranো': 'dizziness', 'kashtho': 'constipation',
    'khide nei': 'loss_of_appetite', 'ojon koma': 'weight_loss',
    'holud chama': 'yellowish_skin', 'gantu peshab': 'dark_urine',
    'baar baar peshab': 'polyuria', 'peshabe jwala': 'burning_micturition',
    'gola byatha': 'throat_irritation', 'gharer akorno': 'stiff_neck',
    'pani shonya': 'dehydration', 'sharir byatha': 'muscle_pain',
}


def extract_symptoms_from_text(text: str) -> list:
    """
    Extract canonical symptom names from free-form text.
    Checks aliases first (longest match wins), then raw symptom keys.
    Returns a deduplicated list of symptom strings.
    """
    text_lower = text.lower()
    found = set()

    # Longest alias first to avoid partial matches
    for alias in sorted(symptom_aliases.keys(), key=len, reverse=True):
        if alias in text_lower:
            found.add(symptom_aliases[alias])

    # Also check raw symptom names (with and without underscores)
    for sym in symptoms_dict.keys():
        sym_readable = sym.replace('_', ' ')
        if sym_readable in text_lower or sym in text_lower:
            found.add(sym)

    return list(found)
