from app.nlp    import extract_symptoms_from_text
from app.model  import get_top3_predictions
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


def _contains(msg: str, keywords: list) -> bool:
    return any(w in msg for w in keywords)


def _missed_dose_response(lang: str = 'en') -> str:
    return (
        "If you forgot a dose, do not double the next dose unless a doctor or pharmacist has told you to.\n\n"
        "General guidance:\n"
        "• If it has only been a short time, take it when you remember.\n"
        "• If it is almost time for your next dose, skip the missed one and continue your normal schedule.\n"
        "• For antibiotics, diabetes, blood pressure, heart, seizure, blood thinner, or steroid medicines, contact a doctor or pharmacist for specific advice.\n"
        "• If your fever is high, lasts more than 3 days, or comes with breathing trouble, chest pain, confusion, stiff neck, rash, or dehydration, seek medical care urgently.\n\n"
        "Tell me the medicine name and dose timing if you want more general guidance."
    )


def _should_predict_from_symptoms(msg: str, symptoms: list) -> bool:
    if len(symptoms) >= 2:
        return True
    if not symptoms:
        return False
    return _contains(msg, _SYMPTOM_INTENT_KW)


def build_chat_response(message: str, last_disease: str = None, lang: str = 'en', context: list | None = None) -> dict:
    msg = message.lower().strip()

    emergency = detect_emergency(message)
    if emergency:
        return {
            'type': 'emergency',
            'text': emergency_message(lang),
            'disease': last_disease,
            'emergency': True,
        }

    if _contains(msg, _MISSED_DOSE_KW):
        gemini_text = get_gemini_response(message, lang, last_disease, context)
        return {
            'type': 'medicine_advice',
            'text': gemini_text or _missed_dose_response(lang),
            'disease': last_disease,
        }

    # ── Greeting ──────────────────────────────────────────────────────────────
    if any(msg == g or msg.startswith(g + ' ') for g in _GREETING_KW):
        return {'type': 'greeting', 'text': t('greeting', lang), 'disease': None}

    # ── Help ──────────────────────────────────────────────────────────────────
    if 'help' in msg or ('how' in msg and 'use' in msg):
        return {'type': 'help', 'text': t('help', lang), 'disease': None}

    # ── Follow-up on known disease ────────────────────────────────────────────
    if last_disease:
        desc, pre, med, die, wrk = helper(last_disease)

        if _contains(msg, _MEDICINE_KW):
            med_list = '\n'.join([f"• {m}" for m in med if m]) or t('consult_doctor', lang)
            return {
                'type': 'followup',
                'text': t('medicines_header', lang, disease=last_disease, list=med_list),
                'disease': last_disease
            }

        if _contains(msg, _DIET_KW):
            diet_list = '\n'.join([f"• {d}" for d in die if d]) or t('no_data', lang)
            return {
                'type': 'followup',
                'text': t('diet_header', lang, disease=last_disease, list=diet_list),
                'disease': last_disease
            }

        if _contains(msg, _PRECAUTION_KW):
            pre_clean = [p for p in pre if p and str(p) != 'nan']
            pre_text  = '\n'.join([f"• {p}" for p in pre_clean]) or t('consult_doctor', lang)
            return {
                'type': 'followup',
                'text': t('precaution_header', lang, disease=last_disease, list=pre_text),
                'disease': last_disease
            }

        if _contains(msg, _WORKOUT_KW):
            wrk_list = '\n'.join([f"• {w}" for w in wrk if w]) or t('consult_doctor', lang)
            return {
                'type': 'followup',
                'text': t('workout_header', lang, disease=last_disease, list=wrk_list),
                'disease': last_disease
            }

        if _contains(msg, _ABOUT_KW):
            return {
                'type': 'followup',
                'text': t('about_header', lang, disease=last_disease, desc=desc),
                'disease': last_disease
            }

        gemini_text = get_gemini_response(message, lang, last_disease, context)
        if gemini_text:
            return {'type': 'ai', 'text': gemini_text, 'disease': last_disease}

    # ── Symptom extraction + prediction ──────────────────────────────────────
    symptoms = extract_symptoms_from_text(message)

    if not symptoms:
        gemini_text = get_gemini_response(message, lang, last_disease, context)
        if gemini_text:
            return {'type': 'ai', 'text': gemini_text, 'disease': last_disease}

        fallback = t('no_symptoms', lang)
        if not is_gemini_configured():
            fallback += "\n\nAI fallback is not configured yet. Add GEMINI_API_KEY to your .env file to let MediBot answer general questions."
        if last_disease:
            fallback += f"\n\n{t('about_header', lang, disease=last_disease, desc='')[:60]}..."
        return {'type': 'unknown', 'text': fallback, 'disease': last_disease}

    if not _should_predict_from_symptoms(msg, symptoms):
        gemini_text = get_gemini_response(message, lang, last_disease, context)
        if gemini_text:
            return {'type': 'ai', 'text': gemini_text, 'disease': last_disease}

        return {
            'type': 'clarify',
            'text': (
                "I noticed a possible symptom, but your message sounds more like a general question than a symptom check. "
                "If you want a prediction, please list at least two symptoms clearly, for example: "
                "\"I have fever, headache, and nausea.\""
            ),
            'disease': last_disease,
        }

    top3, unrecognized = get_top3_predictions(symptoms)

    if not top3:
        return {'type': 'error', 'text': t('error_predict', lang), 'disease': None}

    # ── Primary disease (rank 1) ──────────────────────────────────────────────
    primary   = top3[0]
    disease   = primary['disease']
    confidence= primary['confidence']
    severity  = primary['severity']
    note      = confidence_note(confidence)

    desc, pre, med, die, _ = helper(disease)
    med_short  = ', '.join([m for m in med[:3] if m]) or t('consult_doctor', lang)
    pre_clean  = [p for p in pre if p and str(p) != 'nan']
    pre_short  = pre_clean[0] if pre_clean else t('consult_doctor', lang)
    sym_display = ', '.join([s.replace('_', ' ') for s in symptoms])

    # ── Alternatives (rank 2 & 3) ─────────────────────────────────────────────
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
    response_text += "\n\n**Safety:** This is not a medical diagnosis. Please consult a qualified doctor before taking medicines or making treatment decisions."

    return {
        'type':         'diagnosis',
        'text':         response_text,
        'disease':      disease,
        'confidence':   confidence,
        'top3':         top3,
        'symptoms':     symptoms,
        'unrecognized': unrecognized,
        'confidence_note': note,
        'lang':         lang,
    }
