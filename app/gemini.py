import json
import os
import urllib.error
import urllib.request


GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
DEFAULT_MODEL = "gemini-2.5-flash-lite"


LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "bn": "Bengali",
}


def is_gemini_configured() -> bool:
    return bool(os.environ.get("GEMINI_API_KEY"))


def build_system_prompt(
    lang: str,
    last_disease: str | None = None,
    conversation_context: list | None = None,
) -> str:
    language = LANGUAGE_NAMES.get(lang, "English")
    context = f"The user's last predicted condition is {last_disease}." if last_disease else ""
    history = ""
    if conversation_context:
        recent = conversation_context[-6:]
        history = "\nRecent chat context:\n" + "\n".join(
            f"{item.get('role', 'user')}: {str(item.get('text', ''))[:220]}" for item in recent
        )

    return f"""
You are MediBot, the friendly AI chat assistant inside Medi-Assist.
Reply in {language}.

Important safety rules:
- Give general health education only.
- Do not claim to diagnose, prescribe, or replace a doctor.
- If the user reports emergency symptoms such as severe chest pain, trouble breathing, fainting, stroke symptoms, heavy bleeding, or suicidal thoughts, tell them to seek emergency medical help immediately.
- Keep answers short, clear, and practical.
- If the user asks about symptoms, suggest they use Medi-Assist symptom prediction or list their symptoms clearly.
- For medicines, advise consulting a qualified doctor or pharmacist before taking anything.

{context}
{history}
""".strip()


def get_gemini_response(
    message: str,
    lang: str = "en",
    last_disease: str | None = None,
    conversation_context: list | None = None,
) -> str | None:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None

    model = os.environ.get("GEMINI_MODEL", DEFAULT_MODEL)
    url = GEMINI_API_URL.format(model=model) + f"?key={api_key}"

    payload = {
        "systemInstruction": {
            "parts": [{"text": build_system_prompt(lang, last_disease, conversation_context)}]
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": message}],
            }
        ],
        "generationConfig": {
            "temperature": 0.4,
            "topP": 0.9,
            "maxOutputTokens": 420,
        },
    }

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"GEMINI ERROR: {exc}")
        return None

    candidates = data.get("candidates", [])
    if not candidates:
        return None

    parts = candidates[0].get("content", {}).get("parts", [])
    text = "\n".join(part.get("text", "") for part in parts).strip()
    return text or None
