"""Standard Tamil Vedic Planetary Dignity & Navagraha Pariharams.

Provides planetary dignity (ஆட்சி / உச்சம் / நீசம் / நட்பு / சமம்) and
traditional Tamil Navagraha Pariharams (deity, day, lamp, daanam, temple)
for all 9 planets when Maha Dasa or Bhukti lord is placed in 6, 8, or 12.
"""

from typing import Any, Dict

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


_CAREER_H_ADVICE: Dict[int, Dict[str, str]] = {
    1: {
        "ta": "சுய முயற்சியாலும் தனித்திறமையாலும் முன்னேறும் அமைப்பு. பிறரை நம்பி இருக்காமல் நீங்களே முன்னின்று செயல்பட்டால் தொழில் சிறக்கும்.",
        "en": "Your career grows through self-effort and personal initiative. Taking ownership rather than waiting on others brings steady recognition.",
        "tanglish": "Suya muyarchiyaala munnerram kedaikkum. Mathavangala nambi irukkaama neengale lead eduthaa career super-aa pogum.",
    },
    2: {
        "ta": "பேச்சுத் திறமை, ஆலோசனை அல்லது நிதி சார்ந்த துறைகளில் நல்ல வருமானம் வரும். கடுமையான சொற்களைத் தவிர்த்து இனிமையாகப் பேசுவது பலம் தரும்.",
        "en": "Communication, consulting, or finance-linked work suits you well. Calm, thoughtful speech protects your professional reputation.",
        "tanglish": "Pechu thiramai, finance or consulting field nalla set aagum. Calm-aa & polite-aa pesinaale periya growth kedaikkum.",
    },
    3: {
        "ta": "தொழிலில் துணிச்சலும் சிறு பயணங்களும் முன்னேற்றம் தரும். ஒரே இடத்தில் தேங்கி நிற்காமல் புதிய திறன்களைக் கற்றுக்கொள்வது நல்லது.",
        "en": "Bold initiative, networking, and short trips drive progress. Keep upgrading your skills instead of staying in a comfort zone.",
        "tanglish": "Bold steps & new skills kathukkuradhu career-ku periya boost tharum. Oru idathula stay pannaama puthu attempts pannunga.",
    },
    4: {
        "ta": "நிலம், வாகனம், கல்வி அல்லது நிர்வாகத் துறையில் நிலையான வளர்ச்சி உண்டு. மன அமைதியைக் கெடுக்கும் வேலை அழுத்தத்தைத் தவிர்க்கவும்.",
        "en": "Real estate, education, operations, or steady management roles favor you. Protect your mental peace from unnecessary work stress.",
        "tanglish": "Management, property, education or stable role-la nalla growth irukku. Unnecessary work stress-a mind-la yethikkaadheenga.",
    },
    5: {
        "ta": "அறிவுத்திறன், படைப்பாற்றல் மற்றும் வழிகாட்டும் பதவிகள் உங்களுக்கு ஏற்றவை. திட்டமிடாத ரிஸ்க் எடுப்பதைத் தவிர்த்து அனுபவத்தை நம்புங்கள்.",
        "en": "Creative strategy, mentoring, and advisory roles fit your chart. Rely on proven experience rather than impulsive risks.",
        "tanglish": "Creative thinking, mentoring & advisory roles ungalukku super-aa set aagum. Avathara risk edukkaama experience-a nambunga.",
    },
    6: {
        "ta": "சேவை, டெக், நிர்வாகம் அல்லது போட்டி மிகுந்த துறையில் உங்கள் கடின உழைப்பே கைகொடுக்கும். அலுவலக வாக்குவாதங்களைத் தவிர்த்துப் பொறுமையாகச் செயல்பட்டால் வெற்றி நிச்சயம்.",
        "en": "Service, tech, operations, or competitive fields reward your persistence. Avoid workplace friction and let consistent work speak for itself.",
        "tanglish": "Service, tech or competitive field-la unga hard work dhaan ungalukku periya balam. Office arguments avoid panni porumaiyaa ponga, vetri nichayam.",
    },
    7: {
        "ta": "கூட்டுத் தொழில், வாடிக்கையாளர் தொடர்பு மற்றும் வெளியூர் வாய்ப்புகள் நன்மை தரும். ஒப்பந்தங்களில் தெளிவான நிபந்தனைகளுடன் செயல்படுவது அவசியம்.",
        "en": "Partnerships, client-facing roles, and external collaborations bring growth. Keep agreements clear and documented.",
        "tanglish": "Partnership, client relations & outside opportunities nalla workout aagum. Agreements & commitments mattum clear-aa vachikonga.",
    },
    8: {
        "ta": "ஆராய்ச்சி, ஆழமான தொழில்நுட்பம் அல்லது சவாலான பணிகளில் தனி முத்திரை பதிப்பீர்கள். திடீர் மாற்றங்களின்போது பதற்றப்படாமல் நிதானமாகத் திட்டமிடுங்கள்.",
        "en": "Research, deep technical work, or problem-solving roles suit you. Stay calm during sudden shifts and avoid shortcuts.",
        "tanglish": "Research, deep tech or problem-solving work-la shine aaguveenga. Sudden changes varumbodhu padhattam illaama calm-aa plan pannunga.",
    },
    9: {
        "ta": "நல்ல வழிகாட்டிகள், உயர் கல்வி மற்றும் தூரத்து வாய்ப்புகள் மூலம் தொழில் உயரும். தர்மத்தையும் நேர்மையையும் கடைப்பிடித்தால் அதிர்ஷ்டம் துணை நிற்கும்.",
        "en": "Mentors, higher learning, and long-distance opportunities uplift your career. Staying ethical keeps luck on your side.",
        "tanglish": "Nalla mentors, higher knowledge & long-distance chances moolama career uyarum. Straightforward-aa irundhaa luck support pannum.",
    },
    10: {
        "ta": "தொழில் ஸ்தானம் வலுவாக உள்ளது — பொறுப்பும் சமூக மதிப்பும் தானாகத் தேடி வரும். உயரத்தில் இருக்கும்போது பணிவுடன் நடப்பது நிலையான வெற்றியைத் தரும்.",
        "en": "Your career house is well-supported, bringing authority and respect. Staying humble as responsibility grows secures lasting success.",
        "tanglish": "Career sthanam romba strong-aa irukku — responsibility & respect thaanaa varum. Humble-aa irundhaa indha growth permanent-aa nikkum.",
    },
    11: {
        "ta": "நண்பர்கள் மற்றும் நல்ல தொடர்புகள் வழியாகப் பல புதிய வாய்ப்புகள் வரும். ஒரே நேரத்தில் பல வேலைகளை இழுத்துப்போடாமல் முக்கியமானதில் கவனம் செலுத்துங்கள்.",
        "en": "Strong networks and allies open multiple doors for income. Focus on your top priorities rather than scattering effort.",
        "tanglish": "Friends & strong network moolama pudhu opportunities varum. Ellathayum ore nerathula pannaama mukkiyamaanadhula focus pannunga.",
    },
    12: {
        "ta": "வெளிநாடு, தொலைதூர நிறுவனங்கள் அல்லது பின்னணியில் இருந்து இயங்கும் பணிகள் நன்மை தரும். தேவையற்ற கடன் மற்றும் ஆடம்பர முதலீடுகளைத் தவிர்ப்பது நல்லது.",
        "en": "Global, remote, or behind-the-scenes work aligns well with your chart. Avoid unverified investments or heavy borrowing.",
        "tanglish": "Foreign/remote/backend work ungalukku nalla suit aagum. Thevaiyillaadha kadan & risky investment avoid panradhu romba nalladhu.",
    },
}

_PLANET_TONE: Dict[str, Dict[str, str]] = {
    "Sun": {"ta": "தன்னம்பிக்கையும் தலைமைப் பண்பும்", "en": "confidence and leadership", "tanglish": "confidence & leadership"},
    "Moon": {"ta": "மன அமைதியும் தெளிவான சிந்தனையும்", "en": "emotional clarity and calm focus", "tanglish": "manasu amaithi & clear thinking"},
    "Mars": {"ta": "துணிச்சலும் வேகமான செயல்பாடும்", "en": "courage and decisive action", "tanglish": "dhairiyam & fast action"},
    "Mercury": {"ta": "புத்திசாலித்தனமும் பேச்சுத் திறமையும்", "en": "sharp strategy and communication", "tanglish": "smart planning & communication"},
    "Jupiter": {"ta": "நல்ல வழிகாட்டுதலும் சுப பலமும்", "en": "wisdom, mentorship, and grace", "tanglish": "nalla vazhikaattudhal & suba balam"},
    "Venus": {"ta": "சுகமும் உறவு இனிமையும்", "en": "harmony, comfort, and goodwill", "tanglish": "harmony & comfort"},
    "Saturn": {"ta": "பொறுமையும் நிலையான உழைப்பும்", "en": "discipline and steady endurance", "tanglish": "porumai & steady hard work"},
    "Rahu": {"ta": "புதிய சிந்தனையும் எதிர்பாராத திருப்பங்களும்", "en": "unconventional breakthroughs", "tanglish": "puthu ideas & unexpected turns"},
    "Ketu": {"ta": "ஆழ்ந்த சிந்தனையும் ஆன்மீகத் தெளிவும்", "en": "inner clarity and detachment", "tanglish": "inner clarity & detachment"},
}


def build_human_jothidar_palangal(
    tenth_lord_h: int,
    lagna_lord_h: int,
    guru_h: int,
    sani_h: int,
    seventh_lord_h: int,
    maha_key: str,
    bhukti_key: str,
    maha_h: int,
    bhukti_h: int,
    dignity: Dict[str, str],
    dasa_info: Dict[str, Any],
    lang: str = "ta",
) -> Dict[str, str]:
    """Generate warm, human Tamil Jothidar readings & practical advice (arivurai)."""
    career_body = _CAREER_H_ADVICE.get(tenth_lord_h, _CAREER_H_ADVICE[10]).get(lang, _CAREER_H_ADVICE[10]["en"])
    career = {
        "ta": f"தொழில் வழிகாட்டல்: {career_body}",
        "en": f"Career Guidance: {career_body}",
        "tanglish": f"Career Vazhikaattal: {career_body}",
    }[lang]

    # Wealth advice tailored to Guru & Lagna lord placement
    if guru_h == 7 or lagna_lord_h == 7:
        wealth = {
            "ta": "பொருளாதார அறிவுரை: வாழ்க்கைத் துணை அல்லது நம்பிக்கையான கூட்டாளியின் ஆலோசனையோடு எடுக்கும் நிதி முடிவுகள் கைகொடுக்கும். அவசர முதலீட்டைத் தவிர்த்து நிலையான சேமிப்பில் கவனம் செலுத்துங்கள்.",
            "en": "Financial Advice: Financial decisions taken with your spouse or a trusted partner will pay off. Favor steady savings over rushed bets.",
            "tanglish": "Money Arivurai: Spouse or trusted partner kitta discuss panni edukkuradhu nalla multi-gain tharum. Avathara investment avoid panni steady savings pannunga.",
        }[lang]
    elif guru_h in (2, 5, 9, 11) or lagna_lord_h in (1, 2, 5, 9, 11):
        wealth = {
            "ta": "பொருளாதார அறிவுரை: வருமானம் படிப்படியாக உயரும் அமைப்பு உள்ளது. பணம் வரும்போது ஒரு பகுதியை நிலையான சொத்து அல்லது பாதுகாப்பான சேமிப்பாக மாற்றி வைப்பது எதிர்காலத்திற்குப் பலம் தரும்.",
            "en": "Financial Advice: Steady income flow is supported in your chart. Converting surplus into safe long-term assets protects future stability.",
            "tanglish": "Money Arivurai: Income steady-aa grow aagum. Kaila varra panathula oru part-a safe long-term savings/asset-aa maathi vainga.",
        }[lang]
    else:
        wealth = {
            "ta": "பொருளாதார அறிவுரை: வரவுக்கு ஏற்ற செலவுத் திட்டமும் கடன் கட்டுப்பாடும் இந்தக் காலகட்டத்தில் மிக அவசியம். பிறருக்காக ஜாமீன் கையெழுத்து போடுவதைத் தவிர்க்கவும்.",
            "en": "Financial Advice: Strict budgeting and debt control are essential. Avoid standing surety or lending casually without clear terms.",
            "tanglish": "Money Arivurai: Expense control & budget romba mukkiyam. Mathavangalukku guarantee sign or casual loan kodukkuradha avoid pannunga.",
        }[lang]

    # Family advice tailored to 7th lord house
    if seventh_lord_h in (1, 2, 4, 5, 7, 9, 11):
        family = {
            "ta": "குடும்ப அறிவுரை: குடும்பத்தினரின் அன்பும் துணைவரின் ஆதரவும் உங்கள் மன அழுத்தத்தைக் குறைக்கும். தினமும் சிறிது நேரமாவது குடும்பத்துடன் மனம் விட்டுப் பேசுவது வீட்டில் அமைதியைக் கூட்டும்.",
            "en": "Family Advice: Warmth from your partner and family eases external stress. Carve out calm, unhurried time together each day.",
            "tanglish": "Family Arivurai: Partner & family support unga stress-a kuraikkum. Daily konjam neram free-aa manasu vittu pesina veetla amaithi irukkum.",
        }[lang]
    else:
        family = {
            "ta": "குடும்ப அறிவுரை: குடும்பப் பொறுப்புகள் அதிகமாகத் தோன்றும் நேரங்களில் கோபத்தைத் தவிர்த்துக் காது கொடுத்துக் கேளுங்கள். சிறிய விட்டுக்கொடுத்தல் பெரிய மனக்கசப்பைத் தடுக்கும்.",
            "en": "Family Advice: When responsibilities feel heavy, listen patiently before reacting. Small adjustments preserve deep peace at home.",
            "tanglish": "Family Arivurai: Responsibilities adhigama theriyumbodhu kovam illaama calm-aa listen pannunga. Chinna adjustment periya peace tharum.",
        }[lang]

    # Dasa + Bhukti + House + Dignity reading
    maha_tone = _PLANET_TONE.get(maha_key, _PLANET_TONE["Saturn"]).get(lang, "steady effort")
    bhukti_tone = _PLANET_TONE.get(bhukti_key, _PLANET_TONE["Jupiter"]).get(lang, "guidance")
    maha_name = dasa_info["maha_dasa"].get(lang, maha_key)
    bhukti_name = dasa_info["bhukti"].get(lang, bhukti_key)
    dasa_end = dasa_info["maha_end"]
    anthar_name = dasa_info["anthar"].get(lang, "")
    anthar_end = dasa_info["anthar_end"]

    if maha_key == bhukti_key:
        if maha_h in (6, 8, 12):
            dasa_effect = {
                "ta": (
                    f"நடப்பு தசை வழிகாட்டல் ({maha_name} சுயபுத்தி): தசா நாதன் {maha_h}-ம் இடத்தில் ({dignity['label']}) இருப்பதால் "
                    f"உழைப்பு அதிகமாக இருந்தாலும் {maha_tone} கைகொடுக்கும். {dasa_end} வரை அவசரப்படாமல் நிதானமாகச் செயல்படுங்கள்; "
                    f"{anthar_name} அந்தரம் ({anthar_end} வரை) பொறுமையோடு திட்டமிட ஏற்ற நேரம்."
                ),
                "en": (
                    f"Dasa Guidance ({maha_name} Swa-Bhukti): With your Dasa lord in H{maha_h} ({dignity['label']}), effort feels demanding yet builds {maha_tone}. "
                    f"Stay patient and steady till {dasa_end} (Anthar: {anthar_name} till {anthar_end})."
                ),
                "tanglish": (
                    f"Dasa Vazhikaattal ({maha_name} Swa-Bhukti): Dasa lord H{maha_h}-la ({dignity['label']}) irukkuradhala uzhaippu adhigama irundhaalum {maha_tone} kaikkodukkum. "
                    f"{dasa_end} varaikum avasara padama nidhaanamaa ponga (Anthar: {anthar_name} till {anthar_end})."
                ),
            }[lang]
        else:
            dasa_effect = {
                "ta": (
                    f"நடப்பு தசை வழிகாட்டல் ({maha_name} சுயபுத்தி): தசா நாதன் {maha_h}-ம் இடத்தில் ({dignity['label']}) நல்ல பலத்துடன் உள்ளார். "
                    f"{maha_tone} மூலம் {dasa_end} வரை நல்ல முன்னேற்றம் தரும்; "
                    f"{anthar_name} அந்தரம் ({anthar_end} வரை) புதிய முயற்சிகளுக்குத் துணை நிற்கும்."
                ),
                "en": (
                    f"Dasa Guidance ({maha_name} Swa-Bhukti): Your Dasa lord sits well in H{maha_h} ({dignity['label']}), "
                    f"bringing {maha_tone} for steady progress till {dasa_end} (Anthar: {anthar_name} till {anthar_end})."
                ),
                "tanglish": (
                    f"Dasa Vazhikaattal ({maha_name} Swa-Bhukti): Dasa lord H{maha_h}-la ({dignity['label']}) nalla balathoda irukku. "
                    f"{maha_tone} moolama {dasa_end} varaikum nalla progress tharum (Anthar: {anthar_name} till {anthar_end})."
                ),
            }[lang]
    elif maha_h in (6, 8, 12):
        dasa_effect = {
            "ta": (
                f"நடப்பு தசை வழிகாட்டல் ({maha_name} → {bhukti_name}): தசா நாதன் {maha_h}-ம் இடத்தில் ({dignity['label']}) இருப்பதால் "
                f"உழைப்பு அதிகமாக இருந்தாலும் {maha_tone} கைகொடுக்கும். {bhukti_name} புத்தி ({dasa_end} வரை) {bhukti_tone} தந்து "
                f"தடைகளிலிருந்து மீட்கும்; {anthar_name} அந்தரம் {anthar_end} வரை நிதானமாகச் செயல்படுங்கள்."
            ),
            "en": (
                f"Dasa Guidance ({maha_name} → {bhukti_name}): With your Dasa lord in H{maha_h} ({dignity['label']}), effort feels demanding yet builds {maha_tone}. "
                f"{bhukti_name} Bhukti (till {dasa_end}) brings {bhukti_tone} to clear hurdles; stay steady through {anthar_name} Anthar till {anthar_end}."
            ),
            "tanglish": (
                f"Dasa Vazhikaattal ({maha_name} → {bhukti_name}): Dasa lord H{maha_h}-la ({dignity['label']}) irukkuradhala uzhaippu adhigama irundhaalum {maha_tone} kaikkodukkum. "
                f"{bhukti_name} Bhukti ({dasa_end} varaikum) {bhukti_tone} thandhu thadaigala clear pannum; {anthar_name} Anthar ({anthar_end}) varaikum nidhaanamaa irunga."
            ),
        }[lang]
    else:
        dasa_effect = {
            "ta": (
                f"நடப்பு தசை வழிகாட்டல் ({maha_name} → {bhukti_name}): தசா நாதன் {maha_h}-ம் இடத்தில் ({dignity['label']}) நல்ல பலத்துடன் உள்ளார். "
                f"{maha_tone} மற்றும் {bhukti_name} புத்தியின் {bhukti_tone} இணைந்து {dasa_end} வரை நல்ல முன்னேற்றத்தைத் தரும்; "
                f"{anthar_name} அந்தரம் ({anthar_end} வரை) புதிய முயற்சிகளுக்குத் துணை நிற்கும்."
            ),
            "en": (
                f"Dasa Guidance ({maha_name} → {bhukti_name}): Your Dasa lord sits well in H{maha_h} ({dignity['label']}). "
                f"{maha_tone} paired with {bhukti_name} Bhukti's {bhukti_tone} supports steady progress till {dasa_end} (Anthar: {anthar_name} till {anthar_end})."
            ),
            "tanglish": (
                f"Dasa Vazhikaattal ({maha_name} → {bhukti_name}): Dasa lord H{maha_h}-la ({dignity['label']}) nalla balathoda irukku. "
                f"{maha_tone} + {bhukti_name} Bhukti-oda {bhukti_tone} serndhu {dasa_end} varaikum nalla progress tharum (Anthar: {anthar_name} till {anthar_end})."
            ),
        }[lang]

    pariharam = select_pulipani_remedy(maha_key, maha_h, bhukti_key, bhukti_h, lang)
    return {
        "career": career,
        "wealth": wealth,
        "family": family,
        "dasa_effect": dasa_effect,
        "pariharam": pariharam,
    }
