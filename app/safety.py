EMERGENCY_PATTERNS = [
    "severe chest pain",
    "chest pain and sweating",
    "chest pain with sweating",
    "chest pain and breathlessness",
    "can't breathe",
    "cannot breathe",
    "difficulty breathing",
    "trouble breathing",
    "shortness of breath",
    "fainting",
    "fainted",
    "unconscious",
    "stroke",
    "face drooping",
    "slurred speech",
    "weakness on one side",
    "heavy bleeding",
    "severe bleeding",
    "blood loss",
    "suicide",
    "suicidal",
    "kill myself",
    "self harm",
]


def detect_emergency(text: str) -> str | None:
    normalized = " ".join(str(text).lower().replace("_", " ").split())

    for pattern in EMERGENCY_PATTERNS:
        if pattern in normalized:
            return pattern

    return None


def emergency_message(lang: str = "en") -> str:
    if lang == "hi":
        return (
            "Emergency warning: Your message may describe a serious medical emergency. "
            "Please call 108 immediately or go to the nearest emergency department. "
            "Do not wait for an AI response."
        )

    if lang == "bn":
        return (
            "Emergency warning: Your message may describe a serious medical emergency. "
            "Please call 108 immediately or go to the nearest emergency department. "
            "Do not wait for an AI response."
        )

    return (
        "Emergency warning: Your message may describe a serious medical emergency. "
        "Please call 108 immediately or go to the nearest emergency department. "
        "Do not wait for an AI response."
    )


def confidence_note(confidence: float) -> str:
    if confidence >= 80:
        return "High confidence match based on the symptoms provided. Still confirm with a qualified healthcare professional."
    if confidence >= 55:
        return "Moderate confidence. Add more symptoms or consult a clinician if symptoms continue."
    return "Low confidence. The result is uncertain, so add more symptoms and seek medical advice if you are worried."
