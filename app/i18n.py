# ── Supported languages ───────────────────────────────────────────────────────
SUPPORTED_LANGS = {
    'en': 'English',
    'hi': 'हिन्दी',
    'bn': 'বাংলা',
}

# ── Translation strings ───────────────────────────────────────────────────────
translations = {
    'en': {
        'greeting':         "Hello! 👋 I'm **MediBot**, your AI health assistant.\n\nDescribe your symptoms in plain language and I'll analyze them for you.\n\nExample: *\"I have fever, headache and nausea since yesterday\"*",
        'help':             "Here's how to use me:\n\n🗣️ **Describe symptoms naturally**\nExample: *\"I have chest pain and sweating\"*\n\nAfter diagnosis, ask:\n• 💊 *\"What medicines should I take?\"*\n• 🥗 *\"What should I eat?\"*\n• ⚠️ *\"What precautions should I take?\"*\n• 🏃 *\"What exercise is safe for me?\"*\n• 📄 *\"Tell me more about this disease\"*",
        'no_symptoms':      "I couldn't detect any symptoms in your message. 🤔\n\nTry: *\"I have fever, headache and body ache\"*",
        'top_disease':      "🔍 **Symptoms detected:** {symptoms}\n\n🥇 **Most likely:** {disease} ({confidence}%)\n🚦 **Severity:** {severity}\n\n📄 **About:** {desc}\n\n💊 **Common Medicines:** {med}\n⚠️ **Key Precaution:** {pre}\n\n📊 **Other possibilities:**\n{alternatives}\n\n💬 *Ask me:* *\"What medicines?\"* • *\"What to eat?\"* • *\"Precautions?\"*",
        'alt_row':          "  {rank}. {disease} — {confidence}%",
        'medicines_header': "💊 **Medications for {disease}:**\n\n{list}\n\n⚠️ *Always consult a doctor before taking any medicine.*",
        'diet_header':      "🥗 **Recommended Diet for {disease}:**\n\n{list}",
        'precaution_header':"⚠️ **Precautions for {disease}:**\n\n{list}",
        'workout_header':   "🏃 **Safe Exercises for {disease}:**\n\n{list}",
        'about_header':     "📄 **About {disease}:**\n\n{desc}",
        'error_predict':    "I recognized some symptoms but couldn't make a confident prediction. Please add more symptoms.",
        'consult_doctor':   "Consult a doctor",
        'no_data':          "No data available",
    },
    'hi': {
        'greeting':         "नमस्ते! 👋 मैं **MediBot** हूँ, आपका AI स्वास्थ्य सहायक।\n\nअपने लक्षण सरल भाषा में बताएं और मैं उनका विश्लेषण करूँगा।\n\nउदाहरण: *\"मुझे बुखार, सिरदर्द और जी मिचलाना है\"*",
        'help':             "मुझे इस तरह उपयोग करें:\n\n🗣️ **लक्षण बताएं**\nउदाहरण: *\"मुझे सीने में दर्द और पसीना है\"*\n\nनिदान के बाद पूछें:\n• 💊 *\"कौन सी दवाई लूं?\"*\n• 🥗 *\"क्या खाऊं?\"*\n• ⚠️ *\"क्या सावधानियां बरतूं?\"*\n• 🏃 *\"कौन सी एक्सरसाइज करूं?\"*",
        'no_symptoms':      "मुझे आपके संदेश में कोई लक्षण नहीं मिले। 🤔\n\nकोशिश करें: *\"मुझे बुखार, सिरदर्द और बदन दर्द है\"*",
        'top_disease':      "🔍 **पहचाने गए लक्षण:** {symptoms}\n\n🥇 **सबसे संभावित:** {disease} ({confidence}%)\n🚦 **गंभीरता:** {severity}\n\n📄 **बारे में:** {desc}\n\n💊 **सामान्य दवाइयां:** {med}\n⚠️ **मुख्य सावधानी:** {pre}\n\n📊 **अन्य संभावनाएं:**\n{alternatives}\n\n💬 *पूछें:* *\"दवाइयां?\"* • *\"क्या खाएं?\"* • *\"सावधानियां?\"*",
        'alt_row':          "  {rank}. {disease} — {confidence}%",
        'medicines_header': "💊 **{disease} के लिए दवाइयां:**\n\n{list}\n\n⚠️ *कोई भी दवा लेने से पहले डॉक्टर से सलाह लें।*",
        'diet_header':      "🥗 **{disease} के लिए अनुशंसित आहार:**\n\n{list}",
        'precaution_header':"⚠️ **{disease} के लिए सावधानियां:**\n\n{list}",
        'workout_header':   "🏃 **{disease} के लिए सुरक्षित व्यायाम:**\n\n{list}",
        'about_header':     "📄 **{disease} के बारे में:**\n\n{desc}",
        'error_predict':    "कुछ लक्षण पहचाने गए लेकिन पूर्ण निदान नहीं हो सका। कृपया और लक्षण बताएं।",
        'consult_doctor':   "डॉक्टर से मिलें",
        'no_data':          "कोई डेटा उपलब्ध नहीं",
    },
    'bn': {
        'greeting':         "নমস্কার! 👋 আমি **MediBot**, আপনার AI স্বাস্থ্য সহায়ক।\n\nআপনার লক্ষণগুলি সহজ ভাষায় বলুন এবং আমি সেগুলি বিশ্লেষণ করব।\n\nউদাহরণ: *\"আমার জ্বর, মাথাব্যথা এবং বমি বমি ভাব আছে\"*",
        'help':             "আমাকে এভাবে ব্যবহার করুন:\n\n🗣️ **লক্ষণ বলুন**\nউদাহরণ: *\"আমার বুকে ব্যথা এবং ঘাম হচ্ছে\"*\n\nরোগ নির্ণয়ের পর জিজ্ঞেস করুন:\n• 💊 *\"কোন ওষুধ খাব?\"*\n• 🥗 *\"কী খাব?\"*\n• ⚠️ *\"কী সতর্কতা নেব?\"*\n• 🏃 *\"কোন ব্যায়াম করব?\"*",
        'no_symptoms':      "আমি আপনার বার্তায় কোনো লক্ষণ খুঁজে পাইনি। 🤔\n\nচেষ্টা করুন: *\"আমার জ্বর, মাথাব্যথা এবং শরীর ব্যথা আছে\"*",
        'top_disease':      "🔍 **চিহ্নিত লক্ষণ:** {symptoms}\n\n🥇 **সবচেয়ে সম্ভবত:** {disease} ({confidence}%)\n🚦 **তীব্রতা:** {severity}\n\n📄 **সম্পর্কে:** {desc}\n\n💊 **সাধারণ ওষুধ:** {med}\n⚠️ **প্রধান সতর্কতা:** {pre}\n\n📊 **অন্য সম্ভাবনা:**\n{alternatives}\n\n💬 *জিজ্ঞেস করুন:* *\"ওষুধ?\"* • *\"কী খাব?\"* • *\"সতর্কতা?\"*",
        'alt_row':          "  {rank}. {disease} — {confidence}%",
        'medicines_header': "💊 **{disease} এর জন্য ওষুধ:**\n\n{list}\n\n⚠️ *যেকোনো ওষুধ খাওয়ার আগে ডাক্তারের সাথে পরামর্শ করুন।*",
        'diet_header':      "🥗 **{disease} এর জন্য প্রস্তাবিত খাদ্য:**\n\n{list}",
        'precaution_header':"⚠️ **{disease} এর জন্য সতর্কতা:**\n\n{list}",
        'workout_header':   "🏃 **{disease} এর জন্য নিরাপদ ব্যায়াম:**\n\n{list}",
        'about_header':     "📄 **{disease} সম্পর্কে:**\n\n{desc}",
        'error_predict':    "কিছু লক্ষণ চিহ্নিত হয়েছে কিন্তু সম্পূর্ণ রোগ নির্ণয় করা যায়নি। আরও লক্ষণ বলুন।",
        'consult_doctor':   "ডাক্তারের সাথে দেখা করুন",
        'no_data':          "কোনো তথ্য পাওয়া যায়নি",
    }
}


def t(key: str, lang: str = 'en', **kwargs) -> str:
    """Translate a key with optional format kwargs."""
    lang = lang if lang in translations else 'en'
    text = translations[lang].get(key, translations['en'].get(key, key))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    return text