"""Standard Tamil Vedic Planetary Dignity & Navagraha Pariharams.

Provides planetary dignity (ஆட்சி / உச்சம் / நீசம் / நட்பு / சமம்) and
traditional Tamil Navagraha Pariharams (deity, day, lamp, daanam, temple)
for all 9 planets when Maha Dasa or Bhukti lord is placed in 6, 8, or 12.
"""

from typing import Dict

# Standard Vedic Planetary Dignities (Rasi indices 0=Mesham .. 11=Meenam)
PLANETARY_DIGNITY: Dict[str, Dict[str, list[int]]] = {
    "Sun": {"own": [4], "exalted": [0], "debilitated": [6], "friend": [7, 8, 11]},
    "Moon": {"own": [3], "exalted": [1], "debilitated": [7], "friend": [2, 4, 5]},
    "Mars": {"own": [0, 7], "exalted": [9], "debilitated": [3], "friend": [4, 8, 11]},
    "Mercury": {"own": [2, 5], "exalted": [5], "debilitated": [11], "friend": [1, 4, 6]},
    "Jupiter": {"own": [8, 11], "exalted": [3], "debilitated": [9], "friend": [0, 4, 7]},
    "Venus": {"own": [1, 6], "exalted": [11], "debilitated": [5], "friend": [2, 9, 10]},
    "Saturn": {"own": [9, 10], "exalted": [6], "debilitated": [0], "friend": [1, 2, 5]},
    "Rahu": {"own": [10], "exalted": [1, 2], "debilitated": [7, 8], "friend": [5, 6, 9]},
    "Ketu": {"own": [7], "exalted": [7, 8], "debilitated": [1, 2], "friend": [0, 8, 11]},
}

DIGNITY_LABELS: Dict[str, Dict[str, str]] = {
    "exalted": {"ta": "உச்சம் (மிக வலுவான நிலை)", "en": "Exalted (Peak Strength)", "tanglish": "Ucham (Peak Strength)"},
    "own": {"ta": "ஆட்சி (சொந்த வீடு)", "en": "Own House (Strong)", "tanglish": "Aatchi (Own House)"},
    "friend": {"ta": "நட்பு வீடு", "en": "Friendly Sign", "tanglish": "Natpu Veedu (Friendly)"},
    "debilitated": {"ta": "நீசம் (கவனம் தேவை)", "en": "Debilitated (Needs Care)", "tanglish": "Neesam (Needs Care)"},
    "neutral": {"ta": "சம நிலை", "en": "Neutral Sign", "tanglish": "Sama Nilai (Neutral)"},
}


def get_pulipani_dignity(planet_key: str, rasi_idx: int, lang: str = "ta") -> Dict[str, str]:
    """Return planetary dignity dict with status and localized label."""
    rules = PLANETARY_DIGNITY.get(planet_key, {})
    if rasi_idx in rules.get("exalted", []):
        status = "exalted"
    elif rasi_idx in rules.get("own", []):
        status = "own"
    elif rasi_idx in rules.get("debilitated", []):
        status = "debilitated"
    elif rasi_idx in rules.get("friend", []):
        status = "friend"
    else:
        status = "neutral"
    return {
        "status": status,
        "label": DIGNITY_LABELS[status].get(lang, DIGNITY_LABELS[status]["en"]),
    }


# Traditional Tamil Navagraha Pariharams for all 9 planets
NAVAGRAHA_PARIHARAMS: Dict[str, Dict[str, str]] = {
    "Sun": {
        "ta": "சூரிய பரிகாரம்: ஞாயிற்றுக்கிழமை சிவபெருமான் / சூரிய பகவானுக்கு நெய் தீபம் ஏற்றி, கோதுமை அல்லது வெல்லம் தானம் செய்யவும். வாய்ப்புள்ளபோது சூரியனார் கோவில் தரிசனம் சிறப்பு.",
        "en": "Surya Pariharam: On Sundays, light a ghee lamp for Lord Shiva / Surya Bhagavan and donate wheat or jaggery. Visiting Suriyanar Kovil is auspicious.",
        "tanglish": "Surya Pariharam: Sunday annaiku Shiva / Surya Bhagavan ku nei deepam yethi, godhumai alladhu vellam daanam pannunga. Suriyanar Kovil darisanam sirappu.",
    },
    "Moon": {
        "ta": "சந்திர பரிகாரம்: திங்கட்கிழமை அம்பாள் / சந்திரமௌலீஸ்வரருக்கு வெண்திரியில் தீபம் ஏற்றி, பச்சரிசி அல்லது பால் தானம் செய்யவும். திங்களூர் தரிசனம் நன்மை தரும்.",
        "en": "Chandra Pariharam: On Mondays, light a lamp with a white wick for Goddess Parvati / Chandramouliswarar and donate raw rice or milk. Visiting Thingaloor is auspicious.",
        "tanglish": "Chandra Pariharam: Monday annaiku Amman / Chandramouliswarar ku vellai thiri deepam yethi, pacharisi alladhu paal daanam pannunga. Thingaloor darisanam nalladhu.",
    },
    "Mars": {
        "ta": "செவ்வாய் பரிகாரம்: செவ்வாய்க்கிழமை முருகப்பெருமான் சந்நிதியில் தீபம் ஏற்றி, துவரம் பருப்பு அல்லது சிவப்பு வஸ்திரம் தானம் செய்யவும். வைத்தீஸ்வரன் கோவில் தரிசனம் சிறப்பு.",
        "en": "Sevvai Pariharam: On Tuesdays, light a lamp for Lord Murugan and donate toor dal or red cloth. Visiting Vaitheeswaran Kovil is auspicious.",
        "tanglish": "Sevvai Pariharam: Tuesday annaiku Murugan sannidhi la deepam yethi, thuvaram paruppu alladhu red vasthram daanam pannunga. Vaitheeswaran Kovil darisanam sirappu.",
    },
    "Mercury": {
        "ta": "புதன் பரிகாரம்: புதன்கிழமை மகாவிஷ்ணுவுக்கு நெய் தீபம் ஏற்றி, பச்சைப் பயிறு அல்லது ஏழை மாணவர்களுக்குப் புத்தகம் தானம் செய்யவும். திருவெண்காடு தரிசனம் சிறப்பு.",
        "en": "Budha Pariharam: On Wednesdays, light a ghee lamp for Lord Mahavishnu and donate green gram or books to students in need. Visiting Thiruvenkadu is auspicious.",
        "tanglish": "Budha Pariharam: Wednesday annaiku Mahavishnu ku nei deepam yethi, pachai payiru alladhu students ku books daanam pannunga. Thiruvenkadu darisanam sirappu.",
    },
    "Jupiter": {
        "ta": "குரு பரிகாரம்: வியாழக்கிழமை தட்சிணாமூர்த்திக்கு மஞ்சள் திரியில் நெய் தீபம் ஏற்றி, கொண்டைக்கடலை அல்லது மஞ்சள் பழங்கள் தானம் செய்யவும். ஆலங்குடி தரிசனம் சிறப்பு.",
        "en": "Guru Pariharam: On Thursdays, light a ghee lamp with a yellow wick for Lord Dakshinamurthy and donate chana dal or yellow fruits. Visiting Alangudi is auspicious.",
        "tanglish": "Guru Pariharam: Thursday annaiku Dakshinamurthy ku manjal thiri la nei deepam yethi, kondakadalai alladhu manjal pazham daanam pannunga. Alangudi darisanam sirappu.",
    },
    "Venus": {
        "ta": "சுக்கிரன் பரிகாரம்: வெள்ளிக்கிழமை மகாலட்சுமி / துர்க்கை அம்மனுக்கு நெய் தீபம் ஏற்றி, மொச்சைப் பயிறு அல்லது வெண் பச்சரிசி தானம் செய்யவும். கஞ்சனூர் தரிசனம் சிறப்பு.",
        "en": "Shukra Pariharam: On Fridays, light a ghee lamp for Goddess Mahalakshmi / Durga and donate white beans or raw rice. Visiting Kanjanur is auspicious.",
        "tanglish": "Shukra Pariharam: Friday annaiku Mahalakshmi / Durga Amman ku nei deepam yethi, mochai payiru alladhu pacharisi daanam pannunga. Kanjanur darisanam sirappu.",
    },
    "Saturn": {
        "ta": "சனி பரிகாரம்: சனிக்கிழமை சனி பகவானுக்கு எள் முடிச்சு நல்லெண்ணெய் தீபம் ஏற்றி, காகம் மற்றும் எளியவர்களுக்கு அன்னதானம் செய்யவும். திருநள்ளாறு தரிசனம் சிறப்பு.",
        "en": "Shani Pariharam: On Saturdays, light a sesame-oil (gingelly) lamp with an ellu kizhi for Shani Bhagavan and offer food (Annadanam) or feed crows. Visiting Thirunallar is auspicious.",
        "tanglish": "Shani Pariharam: Saturday annaiku Shani Bhagavan ku nallennai ellu kizhi deepam yethi, kaagam alladhu poor people ku annadanam pannunga. Thirunallar darisanam sirappu.",
    },
    "Rahu": {
        "ta": "ராகு பரிகாரம்: ராகு காலத்தில் துர்க்கை அம்மனுக்கு எலுமிச்சம்பழ விளக்கு ஏற்றி வழிபடவும்; உளுத்தம் பருப்பு தானம் மற்றும் திருநாகேஸ்வரம் தரிசனம் சிறப்பு.",
        "en": "Rahu Pariharam: During Rahukaalam, light a lemon lamp for Goddess Durga and donate black urad dal. Visiting Thirunageswaram is auspicious.",
        "tanglish": "Rahu Pariharam: Rahu kaalathula Durga Amman ku elumichai vilakku yethi vazhipadunga; ulutham paruppu daanam & Thirunageswaram darisanam sirappu.",
    },
    "Ketu": {
        "ta": "கேது பரிகாரம்: செவ்வாய் அல்லது வியாழக்கிழமை விநாயகப் பெருமானுக்கு இலுப்பை எண்ணெய் / நெய் தீபம் ஏற்றி, கொள்ளு தானம் செய்யவும். கீழப்பெரும்பள்ளம் தரிசனம் சிறப்பு.",
        "en": "Ketu Pariharam: On Tuesdays or Thursdays, light a ghee or mahua-oil lamp for Lord Ganesha and donate horse gram (kollu). Visiting Kizhperumpallam is auspicious.",
        "tanglish": "Ketu Pariharam: Tuesday or Thursday annaiku Vinayagar ku nei / iluppai ennai deepam yethi, kollu daanam pannunga. Kizhperumpallam darisanam sirappu.",
    },
}


def select_pulipani_remedy(maha_key: str, maha_h: int, bhukti_key: str, bhukti_h: int, lang: str = "ta") -> str:
    """Return traditional Tamil Navagraha Pariharam when Dasa/Bhukti lord is in 6, 8, or 12."""
    if maha_h in (6, 8, 12):
        remedy = NAVAGRAHA_PARIHARAMS.get(maha_key, NAVAGRAHA_PARIHARAMS["Saturn"])
        return remedy.get(lang, remedy["en"])

    if bhukti_h in (6, 8, 12):
        remedy = NAVAGRAHA_PARIHARAMS.get(bhukti_key, NAVAGRAHA_PARIHARAMS["Rahu"])
        return remedy.get(lang, remedy["en"])

    if lang == "ta":
        return "நடப்பு தசை-புத்தி நாதர்கள் நல்ல இடத்தில் உள்ளதால் தனிப்பட்ட கடுமையான பரிகாரம் தேவையில்லை; தினமும் குலதெய்வ வழிபாடு மற்றும் எளியோருக்கு அன்னதானம் போதுமானது."
    if lang == "tanglish":
        return "Nadappu Dasa-Bhukti lords nalla house la irukradhala heavy Pariharam thevaiyillai; daily Kuladeivam vazhipaadu & annadanam podhum."
    return "Your active Dasa and Bhukti lords are well-placed, so no heavy Pariharam is needed; regular Kuladeivam prayer and Annadanam are sufficient."
