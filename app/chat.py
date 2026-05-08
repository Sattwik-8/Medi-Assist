from app.nlp    import extract_symptoms_from_text
from app.model  import get_top3_predictions, diseases_list
from app.data   import helper
from app.i18n   import t
from app.gemini import get_gemini_response, is_gemini_configured
from app.safety import confidence_note, detect_emergency, emergency_message


# ── Keyword groups ────────────────────────────────────────────────────────────
_MEDICINE_KW   = ['medicine', 'medication', 'drug', 'tablet', 'pill', 'treat', 'cure',
                   'dawai', 'dawa', 'aushadh', 'ওষুধ', 'দাওয়াই']
_DIET_KW       = ['eat', 'food', 'diet', 'nutrition', 'meal', 'drink',
                   'khana', 'khaana', 'खाना', 'খাবার', 'খাই']
_PRECAUTION_KW = ['precaution', 'avoid', 'careful', 'prevention', 'prevent', 'care',
                   'savdhani', 'সতর্কতা', 'সাবধান']
_WORKOUT_KW    = ['exercise', 'workout', 'gym', 'physical', 'walk', 'fitness',
                   'vyayam', 'byayam', 'ব্যায়াম', 'व्यायाम']
_ABOUT_KW      = ['describe', 'what is', 'explain', 'tell me about', 'information',
                   'more about', 'batao', 'বলুন', 'জানতে চাই']
_GREETING_KW   = ['hi', 'hello', 'hey', 'helo', 'namaste', 'namaskar',
                   'good morning', 'good evening', 'sup', 'hii',
                   'নমস্কার', 'হ্যালো', 'हेलो', 'नमस्ते']
_MISSED_DOSE_KW = [
    'forget to take', 'forgot to take', 'missed my medicine', 'missed medicine',
    'missed my dose', 'missed dose', 'forgot my medicine', 'forgot dose',
    'did not take my medicine', "didn't take my medicine", 'skip medicine',
    'skipped medicine', 'late medicine', 'missed tablet', 'forgot tablet'
]
_SYMPTOM_INTENT_KW = [
    'i have', 'i am having', "i'm having", 'i feel', 'feeling', 'symptom',
    'symptoms', 'suffering from', 'pain', 'ache', 'rash', 'vomiting', 'cough',
    'nausea', 'diarrhea', 'diarrhoea', 'breathless', 'dizziness'
]

# ── Denial — user rejects last prediction ─────────────────────────────────────
_DENIAL_KW = [
    "not heart", "not a heart", "isn't heart",
    "not correct", "not right", "wrong diagnosis", "disagree",
    "not feel like", "not feeling like",
    "don't think", "dont think", "i think not",
    "something else", "different disease", "another disease",
    "not accurate", "incorrect",
    "that is not", "this is not", "it is not", "it's not",
    "not malaria", "not dengue", "not typhoid", "not diabetes",
    "not the right", "doesn't seem right", "does not seem right",
    "not sure about", "i doubt",
]

# ── Known disease aliases for name-matching ───────────────────────────────────
_DISEASE_ALIASES: dict[str, str] = {
    'heart attack': 'Heart attack',
    'heart': 'Heart attack',
    'malaria': 'Malaria',
    'dengue': 'Dengue',
    'typhoid': 'Typhoid',
    'diabetes': 'Diabetes',
    'tb': 'Tuberculosis',
    'tuberculosis': 'Tuberculosis',
    'flu': 'Common Cold',
    'common cold': 'Common Cold',
    'pneumonia': 'Pneumonia',
    'asthma': 'Bronchial Asthma',
    'bronchial asthma': 'Bronchial Asthma',
    'migraine': 'Migraine',
    'jaundice': 'Jaundice',
    'hypertension': 'Hypertension',
    'high blood pressure': 'Hypertension',
    'hepatitis a': 'hepatitis A',
    'hepatitis b': 'Hepatitis B',
    'hepatitis c': 'Hepatitis C',
    'hepatitis d': 'Hepatitis D',
    'hepatitis e': 'Hepatitis E',
    'hepatitis': 'hepatitis A',
    'uti': 'Urinary tract infection',
    'urinary tract infection': 'Urinary tract infection',
    'acne': 'Acne',
    'psoriasis': 'Psoriasis',
    'vertigo': 'Paroxysmal Positional Vertigo',
    'arthritis': 'Arthritis',
    'fungal infection': 'Fungal infection',
    'allergy': 'Allergy',
    'gerd': 'GERD',
    'aids': 'AIDS',
    'hiv': 'AIDS',
    'chicken pox': 'Chicken pox',
    'chickenpox': 'Chicken pox',
    'piles': 'Dimorphic hemmorhoids(piles)',
    'hemorrhoids': 'Dimorphic hemmorhoids(piles)',
    'hypothyroidism': 'Hypothyroidism',
    'hyperthyroidism': 'Hyperthyroidism',
    'thyroid': 'Hypothyroidism',
    'varicose veins': 'Varicose veins',
    'impetigo': 'Impetigo',
    'hypoglycemia': 'Hypoglycemia',
    'low blood sugar': 'Hypoglycemia',
    'osteoarthritis': 'Osteoarthristis',
    'drug reaction': 'Drug Reaction',
    'gastroenteritis': 'Gastroenteritis',
    'gastro': 'Gastroenteritis',
    'peptic ulcer': 'Peptic ulcer disease',
    'ulcer': 'Peptic ulcer disease',
    'paralysis': 'Paralysis (brain hemorrhage)',
    'stroke': 'Paralysis (brain hemorrhage)',
    'jaundice': 'Jaundice',
    'alcoholic hepatitis': 'Alcoholic hepatitis',
    'cholestasis': 'Chronic cholestasis',
    'cervical spondylosis': 'Cervical spondylosis',
}

# Suggestion trigger words — indicates user is naming a disease, not listing symptoms
_SUGGESTION_PREFIXES = [
    "think its", "think it's", "think it is",
    "maybe its", "maybe it's", "maybe it is",
    "could be", "might be", "it could be",
    "it might be", "probably", "i think its",
    "seems like", "looks like", "feel like its",
    "it seems like", "its probably", "it's probably",
    "is it", "could it be", "might it be",
]


def _contains(msg: str, keywords: list) -> bool:
    return any(w in msg for w in keywords)


def _is_greeting(msg: str) -> bool:
    return any(
        msg == g or msg.startswith(g + ' ') or msg.startswith(g + ',')
        for g in _GREETING_KW
    )


def _is_denial(msg: str) -> bool:
    return _contains(msg, _DENIAL_KW)


def _extract_suggested_disease(msg: str) -> str | None:
    """
    Returns a canonical disease name if the user is suggesting/naming one.
    e.g. "think its dengue" -> "Dengue"
         "could be typhoid" -> "Typhoid"
         "is it malaria?"   -> "Malaria"
    """
    # Only activate when a suggestion prefix is present OR it's a short message
    # naming a disease directly (e.g. "dengue" or "its dengue")
    has_prefix = _contains(msg, _SUGGESTION_PREFIXES)
    is_short   = len(msg.split()) <= 5  # short messages like "think its dengue"

    if not has_prefix and not is_short:
        return None

    # Check aliases longest-first to avoid "heart" matching before "heart attack"
    for alias in sorted(_DISEASE_ALIASES.keys(), key=len, reverse=True):
        if alias in msg:
            return _DISEASE_ALIASES[alias]

    return None


def _should_predict_from_symptoms(msg: str, symptoms: list) -> bool:
    if len(symptoms) >= 2:
        return True
    if not symptoms:
        return False
    return _contains(msg, _SYMPTOM_INTENT_KW)


def _missed_dose_response() -> str:
    return (
        "If you forgot a dose, do not double the next dose unless a doctor or pharmacist has told you to.\n\n"
        "General guidance:\n"
        "• If it has only been a short time, take it when you remember.\n"
        "• If it is almost time for your next dose, skip the missed one and continue your normal schedule.\n"
        "• For antibiotics, diabetes, blood pressure, heart, seizure, blood thinner, or steroid medicines, "
        "contact a doctor or pharmacist for specific advice.\n"
        "• If your fever is high, lasts more than 3 days, or comes with breathing trouble, chest pain, "
        "confusion, stiff neck, rash, or dehydration, seek medical care urgently.\n\n"
        "Tell me the medicine name and dose timing if you want more general guidance."
    )


def _gemini_or_fallback(message, lang, last_disease, context, fallback_text) -> dict:
    """Try Gemini; on failure return fallback. Always returns disease=None to avoid looping."""
    gemini_text = get_gemini_response(message, lang, last_disease, context)
    if gemini_text:
        return {'type': 'ai', 'text': gemini_text, 'disease': last_disease}
    return {'type': 'unknown', 'text': fallback_text, 'disease': None}


def _denial_response(last_disease: str) -> str:
    """Context-aware denial reply. Works without Gemini."""
    return (
        f"That's okay — the AI prediction isn't always right, especially with only 1–2 symptoms.\n\n"
        f"The model suggested **{last_disease}** based on your symptoms, but it could be something else.\n\n"
        f"To get a more accurate result, try listing **3 or more specific symptoms**. For example:\n"
        f'*"I have fever, loose motions, stomach cramps, and fatigue"*\n\n'
        f"You can also ask about a specific disease — for example:\n"
        f'*"Tell me about dengue"* or *"What are symptoms of typhoid?"*'
    )


def _disease_info_card(disease: str, lang: str) -> dict:
    """Info card for a user-suggested disease. Works without Gemini."""
    desc, pre, med, die, _ = helper(disease)
    med_short = ', '.join([m for m in med[:3] if m]) or t('consult_doctor', lang)
    pre_clean = [p for p in pre if p and str(p) != 'nan']
    pre_short = pre_clean[0] if pre_clean else t('consult_doctor', lang)

    text = (
        f"Here's what I know about **{disease}**:\n\n"
        f"📄 **About:** {desc[:260]}...\n\n"
        f"💊 **Common Medicines:** {med_short}\n"
        f"⚠️ **Key Precaution:** {pre_short}\n\n"
        f"💬 Ask me *\"What medicines?\"* • *\"What to eat?\"* • *\"Precautions?\"* for full details.\n\n"
        f"**Safety:** This is general information only. Consult a qualified doctor for a proper diagnosis."
    )
    return {'type': 'followup', 'text': text, 'disease': disease}


def build_chat_response(
    message: str,
    last_disease: str = None,
    lang: str = 'en',
    context: list | None = None
) -> dict:
    msg = message.lower().strip()

    # ── 1. Emergency — always first ───────────────────────────────────────────
    emergency = detect_emergency(message)
    if emergency:
        return {
            'type': 'emergency', 'text': emergency_message(lang),
            'disease': last_disease, 'emergency': True,
        }

    # ── 2. Missed dose ────────────────────────────────────────────────────────
    if _contains(msg, _MISSED_DOSE_KW):
        gemini_text = get_gemini_response(message, lang, last_disease, context)
        return {
            'type': 'medicine_advice',
            'text': gemini_text or _missed_dose_response(),
            'disease': last_disease,
        }

    # ── 3. Greeting — before last_disease so it always fires ─────────────────
    if _is_greeting(msg):
        return {'type': 'greeting', 'text': t('greeting', lang), 'disease': None}

    # ── 4. Help ───────────────────────────────────────────────────────────────
    if 'help' in msg or ('how' in msg and 'use' in msg):
        return {'type': 'help', 'text': t('help', lang), 'disease': None}

    # ── 5. User names a specific disease ─────────────────────────────────────
    # e.g. "think its dengue", "could be typhoid", "is it malaria?"
    # Must be checked BEFORE denial so "think its dengue" routes here, not denial
    suggested = _extract_suggested_disease(msg)
    if suggested:
        gemini_text = get_gemini_response(message, lang, suggested, context)
        if gemini_text:
            return {'type': 'ai', 'text': gemini_text, 'disease': suggested}
        return _disease_info_card(suggested, lang)

    # ── 6. Denial of last prediction ─────────────────────────────────────────
    if last_disease and _is_denial(msg):
        gemini_text = get_gemini_response(message, lang, last_disease, context)
        if gemini_text:
            return {'type': 'ai', 'text': gemini_text, 'disease': None}
        return {
            'type': 'clarify',
            'text': _denial_response(last_disease),
            'disease': None,   # clear so user isn't stuck
        }

    # ── 7. Follow-up on active disease ───────────────────────────────────────
    if last_disease:
        desc, pre, med, die, wrk = helper(last_disease)

        if _contains(msg, _MEDICINE_KW):
            med_list = '\n'.join([f"• {m}" for m in med if m]) or t('consult_doctor', lang)
            return {
                'type': 'followup',
                'text': t('medicines_header', lang, disease=last_disease, list=med_list),
                'disease': last_disease,
            }

        if _contains(msg, _DIET_KW):
            diet_list = '\n'.join([f"• {d}" for d in die if d]) or t('no_data', lang)
            return {
                'type': 'followup',
                'text': t('diet_header', lang, disease=last_disease, list=diet_list),
                'disease': last_disease,
            }

        if _contains(msg, _PRECAUTION_KW):
            pre_clean = [p for p in pre if p and str(p) != 'nan']
            pre_text  = '\n'.join([f"• {p}" for p in pre_clean]) or t('consult_doctor', lang)
            return {
                'type': 'followup',
                'text': t('precaution_header', lang, disease=last_disease, list=pre_text),
                'disease': last_disease,
            }

        if _contains(msg, _WORKOUT_KW):
            wrk_list = '\n'.join([f"• {w}" for w in wrk if w]) or t('consult_doctor', lang)
            return {
                'type': 'followup',
                'text': t('workout_header', lang, disease=last_disease, list=wrk_list),
                'disease': last_disease,
            }

        if _contains(msg, _ABOUT_KW):
            return {
                'type': 'followup',
                'text': t('about_header', lang, disease=last_disease, desc=desc),
                'disease': last_disease,
            }

        # Free-form — try Gemini
        gemini_text = get_gemini_response(message, lang, last_disease, context)
        if gemini_text:
            return {'type': 'ai', 'text': gemini_text, 'disease': last_disease}

        # Gemini down — helpful menu, keep disease context
        return {
            'type': 'clarify',
            'text': (
                f"I can answer specific questions about **{last_disease}**. Try:\n\n"
                f"• 💊 *\"What medicines should I take?\"*\n"
                f"• 🥗 *\"What should I eat?\"*\n"
                f"• ⚠️ *\"What precautions should I take?\"*\n"
                f"• 🏃 *\"What exercise is safe?\"*\n"
                f"• 📄 *\"Tell me more about this disease\"*\n\n"
                f"Or list new symptoms for a fresh prediction."
            ),
            'disease': last_disease,
        }

    # ── 8. Symptom extraction + prediction ───────────────────────────────────
    symptoms = extract_symptoms_from_text(message)

    if not symptoms:
        return _gemini_or_fallback(message, lang, last_disease, context, t('no_symptoms', lang))

    if not _should_predict_from_symptoms(msg, symptoms):
        gemini_text = get_gemini_response(message, lang, last_disease, context)
        if gemini_text:
            return {'type': 'ai', 'text': gemini_text, 'disease': last_disease}
        return {
            'type': 'clarify',
            'text': (
                "I noticed a possible symptom in your message, but it reads more like a general question. "
                "For a prediction, list at least two symptoms clearly — for example: "
                "*\"I have fever, headache, and nausea.\"*"
            ),
            'disease': last_disease,
        }

    top3, unrecognized = get_top3_predictions(symptoms)

    if not top3:
        return {'type': 'error', 'text': t('error_predict', lang), 'disease': None}

    # ── Build prediction response ─────────────────────────────────────────────
    primary    = top3[0]
    disease    = primary['disease']
    confidence = primary['confidence']
    severity   = primary['severity']
    note       = confidence_note(confidence)

    desc, pre, med, die, _ = helper(disease)
    med_short   = ', '.join([m for m in med[:3] if m]) or t('consult_doctor', lang)
    pre_clean   = [p for p in pre if p and str(p) != 'nan']
    pre_short   = pre_clean[0] if pre_clean else t('consult_doctor', lang)
    sym_display = ', '.join([s.replace('_', ' ') for s in symptoms])

    alt_lines = []
    ranks = ['🥈', '🥉']
    for i, alt in enumerate(top3[1:], start=0):
        alt_lines.append(
            t('alt_row', lang,
              rank=ranks[i] if i < len(ranks) else f"{i+2}.",
              disease=alt['disease'],
              confidence=alt['confidence'])
        )
    alternatives = '\n'.join(alt_lines) if alt_lines else '—'

    response_text = t(
        'top_disease', lang,
        symptoms=sym_display,
        disease=disease,
        confidence=confidence,
        severity=severity,
        desc=desc[:220] + '...',
        med=med_short,
        pre=pre_short,
        alternatives=alternatives
    )
    response_text += f"\n\n**Confidence note:** {note}"
    response_text += (
        "\n\n**Safety:** This is not a medical diagnosis. "
        "Please consult a qualified doctor before taking medicines or making treatment decisions."
    )

    return {
        'type':            'diagnosis',
        'text':            response_text,
        'disease':         disease,
        'confidence':      confidence,
        'top3':            top3,
        'symptoms':        symptoms,
        'unrecognized':    unrecognized,
        'confidence_note': note,
        'lang':            lang,
    }