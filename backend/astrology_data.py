"""3-language (ta, en, tanglish) Tamil Vedic Astrology, Pancha Patchi, and Pulipani Siddhar constants."""

RASIS = [
    {"idx": 0, "en": "Aries", "tanglish": "Mesham", "ta": "மேஷம்", "lord": "Mars"},
    {"idx": 1, "en": "Taurus", "tanglish": "Rishabam", "ta": "ரிஷபம்", "lord": "Venus"},
    {"idx": 2, "en": "Gemini", "tanglish": "Midhunam", "ta": "மிதுனம்", "lord": "Mercury"},
    {"idx": 3, "en": "Cancer", "tanglish": "Kadagam", "ta": "கடகம்", "lord": "Moon"},
    {"idx": 4, "en": "Leo", "tanglish": "Simmam", "ta": "சிம்மம்", "lord": "Sun"},
    {"idx": 5, "en": "Virgo", "tanglish": "Kanni", "ta": "கன்னி", "lord": "Mercury"},
    {"idx": 6, "en": "Libra", "tanglish": "Thulam", "ta": "துலாம்", "lord": "Venus"},
    {"idx": 7, "en": "Scorpio", "tanglish": "Viruchigam", "ta": "விருச்சிகம்", "lord": "Mars"},
    {"idx": 8, "en": "Sagittarius", "tanglish": "Dhanusu", "ta": "தனுசு", "lord": "Jupiter"},
    {"idx": 9, "en": "Capricorn", "tanglish": "Magaram", "ta": "மகரம்", "lord": "Saturn"},
    {"idx": 10, "en": "Aquarius", "tanglish": "Kumbam", "ta": "கும்பம்", "lord": "Saturn"},
    {"idx": 11, "en": "Pisces", "tanglish": "Meenam", "ta": "மீனம்", "lord": "Jupiter"},
]

DASA_LORDS = [
    {"key": "Ketu", "years": 7, "ta": "கேது", "en": "Ketu", "tanglish": "Ketu"},
    {"key": "Venus", "years": 20, "ta": "சுக்கிரன்", "en": "Venus", "tanglish": "Sukkiran (Venus)"},
    {"key": "Sun", "years": 6, "ta": "சூரியன்", "en": "Sun", "tanglish": "Sooriyan (Sun)"},
    {"key": "Moon", "years": 10, "ta": "சந்திரன்", "en": "Moon", "tanglish": "Chandran (Moon)"},
    {"key": "Mars", "years": 7, "ta": "செவ்வாய்", "en": "Mars", "tanglish": "Sevvai (Mars)"},
    {"key": "Rahu", "years": 18, "ta": "ராகு", "en": "Rahu", "tanglish": "Rahu"},
    {"key": "Jupiter", "years": 16, "ta": "குரு", "en": "Jupiter", "tanglish": "Guru (Jupiter)"},
    {"key": "Saturn", "years": 19, "ta": "சனி", "en": "Saturn", "tanglish": "Sani (Saturn)"},
    {"key": "Mercury", "years": 17, "ta": "புதன்", "en": "Mercury", "tanglish": "Budhan (Mercury)"},
]

GRAHA_LABELS = {
    "Ascendant": {"ta": "லக்", "en": "Asc", "tanglish": "Lag", "full_ta": "லக்னம்", "full_en": "Ascendant", "full_tanglish": "Lagnam"},
    "Sun": {"ta": "சூ", "en": "Su", "tanglish": "Soo", "full_ta": "சூரியன்", "full_en": "Sun", "full_tanglish": "Sooriyan"},
    "Moon": {"ta": "சந்", "en": "Mo", "tanglish": "Cha", "full_ta": "சந்திரன்", "full_en": "Moon", "full_tanglish": "Chandran"},
    "Mars": {"ta": "செ", "en": "Ma", "tanglish": "Sev", "full_ta": "செவ்வாய்", "full_en": "Mars", "full_tanglish": "Sevvai"},
    "Mercury": {"ta": "பு", "en": "Me", "tanglish": "Bud", "full_ta": "புதன்", "full_en": "Mercury", "full_tanglish": "Budhan"},
    "Jupiter": {"ta": "கு", "en": "Ju", "tanglish": "Gur", "full_ta": "குரு", "full_en": "Jupiter", "full_tanglish": "Guru"},
    "Venus": {"ta": "சுக்", "en": "Ve", "tanglish": "Suk", "full_ta": "சுக்கிரன்", "full_en": "Venus", "full_tanglish": "Sukkiran"},
    "Saturn": {"ta": "சனி", "en": "Sa", "tanglish": "San", "full_ta": "சனி", "full_en": "Saturn", "full_tanglish": "Sani"},
    "Rahu": {"ta": "ரா", "en": "Ra", "tanglish": "Rah", "full_ta": "ராகு", "full_en": "Rahu", "full_tanglish": "Rahu"},
    "Ketu": {"ta": "கே", "en": "Ke", "tanglish": "Ket", "full_ta": "கேது", "full_en": "Ketu", "full_tanglish": "Ketu"},
}

# 27 Nakshatrams with Tamil, English, Tanglish, Gana (0=Deva, 1=Manushya, 2=Rakshasa),
# Rajju (0=Paadha, 1=Ooru, 2=Udhara, 3=Kandu, 4=Siru), Yoni (animal idx), Bird idx (0..4)
# Birds: 0=Vallooru (Vulture), 1=Aandhai (Owl), 2=Kaagam (Crow), 3=Kozhi (Cock), 4=Mayil (Peacock)
NAKSHATRAMS = [
    {"idx": 0, "ta": "அஸ்வினி", "en": "Ashwini", "tanglish": "Ashwini", "gana": 0, "rajju": 0, "yoni": 0, "bird_valar": 0, "bird_thei": 4},
    {"idx": 1, "ta": "பரணி", "en": "Bharani", "tanglish": "Bharani", "gana": 1, "rajju": 1, "yoni": 1, "bird_valar": 0, "bird_thei": 4},
    {"idx": 2, "ta": "கார்த்திகை", "en": "Krittika", "tanglish": "Karthigai", "gana": 2, "rajju": 2, "yoni": 2, "bird_valar": 0, "bird_thei": 4},
    {"idx": 3, "ta": "ரோகிணி", "en": "Rohini", "tanglish": "Rohini", "gana": 1, "rajju": 3, "yoni": 3, "bird_valar": 0, "bird_thei": 4},
    {"idx": 4, "ta": "மிருகசீரிஷம்", "en": "Mrigashira", "tanglish": "Mrigasheerisham", "gana": 0, "rajju": 4, "yoni": 3, "bird_valar": 0, "bird_thei": 4},
    {"idx": 5, "ta": "திருவாதிரை", "en": "Ardra", "tanglish": "Thiruvadhirai", "gana": 1, "rajju": 3, "yoni": 4, "bird_valar": 1, "bird_thei": 3},
    {"idx": 6, "ta": "புனர்பூசம்", "en": "Punarvasu", "tanglish": "Punarpoosam", "gana": 0, "rajju": 2, "yoni": 5, "bird_valar": 1, "bird_thei": 3},
    {"idx": 7, "ta": "பூசம்", "en": "Pushya", "tanglish": "Poosam", "gana": 0, "rajju": 1, "yoni": 2, "bird_valar": 1, "bird_thei": 3},
    {"idx": 8, "ta": "ஆயில்யம்", "en": "Ashlesha", "tanglish": "Ayilyam", "gana": 2, "rajju": 0, "yoni": 5, "bird_valar": 1, "bird_thei": 3},
    {"idx": 9, "ta": "மகம்", "en": "Magha", "tanglish": "Magam", "gana": 2, "rajju": 0, "yoni": 6, "bird_valar": 1, "bird_thei": 3},
    {"idx": 10, "ta": "பூரம்", "en": "Purva Phalguni", "tanglish": "Pooram", "gana": 1, "rajju": 1, "yoni": 6, "bird_valar": 1, "bird_thei": 3},
    {"idx": 11, "ta": "உத்திரம்", "en": "Uttara Phalguni", "tanglish": "Uthiram", "gana": 1, "rajju": 2, "yoni": 7, "bird_valar": 2, "bird_thei": 2},
    {"idx": 12, "ta": "ஹஸ்தம்", "en": "Hasta", "tanglish": "Hastham", "gana": 0, "rajju": 3, "yoni": 8, "bird_valar": 2, "bird_thei": 2},
    {"idx": 13, "ta": "சித்திரை", "en": "Chitra", "tanglish": "Chithirai", "gana": 2, "rajju": 4, "yoni": 9, "bird_valar": 2, "bird_thei": 2},
    {"idx": 14, "ta": "சுவாதி", "en": "Swati", "tanglish": "Swathi", "gana": 0, "rajju": 3, "yoni": 8, "bird_valar": 2, "bird_thei": 2},
    {"idx": 15, "ta": "விசாகம்", "en": "Vishakha", "tanglish": "Visagam", "gana": 2, "rajju": 2, "yoni": 9, "bird_valar": 2, "bird_thei": 2},
    {"idx": 16, "ta": "அனுஷம்", "en": "Anuradha", "tanglish": "Anusham", "gana": 0, "rajju": 1, "yoni": 10, "bird_valar": 3, "bird_thei": 1},
    {"idx": 17, "ta": "கேட்டை", "en": "Jyeshtha", "tanglish": "Kettai", "gana": 2, "rajju": 0, "yoni": 10, "bird_valar": 3, "bird_thei": 1},
    {"idx": 18, "ta": "மூலம்", "en": "Mula", "tanglish": "Moolam", "gana": 2, "rajju": 0, "yoni": 4, "bird_valar": 3, "bird_thei": 1},
    {"idx": 19, "ta": "பூராடம்", "en": "Purva Ashadha", "tanglish": "Pooradam", "gana": 1, "rajju": 1, "yoni": 11, "bird_valar": 3, "bird_thei": 1},
    {"idx": 20, "ta": "உத்திராடம்", "en": "Uttara Ashadha", "tanglish": "Uthiradam", "gana": 1, "rajju": 2, "yoni": 12, "bird_valar": 3, "bird_thei": 1},
    {"idx": 21, "ta": "திருவோணம்", "en": "Shravana", "tanglish": "Thiruvonam", "gana": 0, "rajju": 3, "yoni": 11, "bird_valar": 4, "bird_thei": 0},
    {"idx": 22, "ta": "அவிட்டம்", "en": "Dhanishta", "tanglish": "Avittam", "gana": 2, "rajju": 4, "yoni": 13, "bird_valar": 4, "bird_thei": 0},
    {"idx": 23, "ta": "சதயம்", "en": "Shatabhisha", "tanglish": "Sadhayam", "gana": 2, "rajju": 3, "yoni": 0, "bird_valar": 4, "bird_thei": 0},
    {"idx": 24, "ta": "பூரட்டாதி", "en": "Purva Bhadrapada", "tanglish": "Poorattadhi", "gana": 1, "rajju": 2, "yoni": 13, "bird_valar": 4, "bird_thei": 0},
    {"idx": 25, "ta": "உத்திரட்டாதி", "en": "Uttara Bhadrapada", "tanglish": "Uthirattadhi", "gana": 1, "rajju": 1, "yoni": 7, "bird_valar": 4, "bird_thei": 0},
    {"idx": 26, "ta": "ரேவதி", "en": "Revati", "tanglish": "Revathi", "gana": 0, "rajju": 0, "yoni": 1, "bird_valar": 4, "bird_thei": 0},
]

BIRDS = [
    {"idx": 0, "ta": "வல்லூறு", "en": "Vulture (Vallooru)", "tanglish": "Vallooru (Vulture)", "emoji": "🦅"},
    {"idx": 1, "ta": "ஆந்தை", "en": "Owl (Aandhai)", "tanglish": "Aandhai (Owl)", "emoji": "🦉"},
    {"idx": 2, "ta": "காகம்", "en": "Crow (Kaagam)", "tanglish": "Kaagam (Crow)", "emoji": "🐦‍⬛"},
    {"idx": 3, "ta": "கோழி", "en": "Cock (Kozhi)", "tanglish": "Kozhi (Cock)", "emoji": "🐓"},
    {"idx": 4, "ta": "மயில்", "en": "Peacock (Mayil)", "tanglish": "Mayil (Peacock)", "emoji": "🦚"},
]

# Pancha Patchi 5 states: Arasu (Ruling), Oon (Eating), Nadai (Walking), Thuyil (Sleeping), Saavu (Dying)
PATCHI_STATES = {
    "Arasu": {
        "power": 100,
        "tone": "emerald",
        "ta": "அரசு (உச்ச பலம்)",
        "en": "Arasu — Peak Power",
        "tanglish": "Arasu (Peak Power)",
        "advice_ta": "மிகச் சிறப்பான நேரம்! நேர்காணல், ஒப்பந்தம், முக்கிய பேச்சுவார்த்தைகளை இப்போது செய்யலாம்.",
        "advice_en": "Peak cosmic window! Ideal for interviews, closing deals, proposals, and bold decisions.",
        "advice_tanglish": "Semma peak time! Interview, deal closing, important calls ippo pannunga — success chance romba high.",
    },
    "Oon": {
        "power": 80,
        "tone": "gold",
        "ta": "ஊண் (நல்ல பலம்)",
        "en": "Oon — Productive & Nourishing",
        "tanglish": "Oon (Good & Productive)",
        "advice_ta": "ஆக்கப்பூர்வமான நேரம். புதிய முயற்சிகள், நிதி மற்றும் குடும்ப விஷயங்களுக்கு நன்று.",
        "advice_en": "Strong, supportive energy. Great for steady work, financial tasks, and planning.",
        "advice_tanglish": "Nalla productive time! Puthu work start panna, finance & family talks-ku super.",
    },
    "Nadai": {
        "power": 55,
        "tone": "slate",
        "ta": "நடை (சாதாரண பலம்)",
        "en": "Nadai — Moderate / Routine",
        "tanglish": "Nadai (Average / Routine)",
        "advice_ta": "சமநிலையான நேரம். அன்றாட பணிகள் மற்றும் பயணங்களுக்கு ஏற்றது.",
        "advice_en": "Balanced, neutral window. Stick to routine tasks, travel, and regular follow-ups.",
        "advice_tanglish": "Normal balanced time. Daily routine work & travel-ku ok, periya risk vendam.",
    },
    "Thuyil": {
        "power": 30,
        "tone": "amber",
        "ta": "துயில் (குறைந்த பலம்)",
        "en": "Thuyil — Low Energy / Rest",
        "tanglish": "Thuyil (Low Energy)",
        "advice_ta": "சோர்வு தரக்கூடிய நேரம். பெரிய வாக்குறுதிகள் அல்லது முதலீடுகளை தவிர்க்கவும்.",
        "advice_en": "Restful, low-momentum window. Avoid big commitments, arguments, or rushing.",
        "advice_tanglish": "Energy konjam low-aa irukkum. Periya commitments or arguments avoid pannunga.",
    },
    "Saavu": {
        "power": 10,
        "tone": "crimson",
        "ta": "சாவு (எச்சரிக்கை நேரம்)",
        "en": "Saavu — Caution Window",
        "tanglish": "Saavu (Caution Time)",
        "advice_ta": "கவனமாக இருக்க வேண்டிய நேரம். முக்கிய முடிவுகளை அடுத்த அரசு/ஊண் நேரத்திற்கு தள்ளி வைக்கவும்.",
        "advice_en": "Weakest window. Pause major decisions, signing, or confrontations until your next Oon/Arasu.",
        "advice_tanglish": "Strict caution time! Important decisions, signing ellam next Arasu/Oon time-ku thalli vainga.",
    },
}

# Ruling bird per weekday (0=Mon..6=Sun) -> maps weekday to which state cycle applies
# Standard Tamil Pancha Patchi Valarpirai Day sequence for each bird
# States order: Oon, Nadai, Arasu, Thuyil, Saavu
STATE_CYCLE = ["Oon", "Nadai", "Arasu", "Thuyil", "Saavu"]

# Weekday (0=Mon .. 6=Sun) starting offset per bird in Valarpirai Day / Night and Theipirai Day / Night
# Ensures every Jamam has all 5 states distributed across the 5 birds cleanly
WEEKDAY_BIRD_OFFSET_VALAR_DAY = [1, 2, 3, 4, 0, 1, 2]
WEEKDAY_BIRD_OFFSET_VALAR_NIGHT = [3, 4, 0, 1, 2, 3, 4]
WEEKDAY_BIRD_OFFSET_THEI_DAY = [2, 3, 4, 0, 1, 2, 3]
WEEKDAY_BIRD_OFFSET_THEI_NIGHT = [4, 0, 1, 2, 3, 4, 0]

# Pulipani Siddhar classical insights keyed by Maha Dasa lord
PULIPANI_DASA_INSIGHTS = {
    "Jupiter": {
        "ta": "புலிப்பாணி சித்தர் விதிப்படி, குரு தசை கல்வி, செல்வம், சுப காரியங்கள் மற்றும் ஆன்மீக உயர்வை தரும். வியாழக்கிழமை தட்சிணாமூர்த்தியை வழிபட தடைகள் நீங்கும்.",
        "en": "Per Pulipani Siddhar's rule, Guru (Jupiter) Dasa brings wisdom, steady wealth, auspicious family events, and mentorship. Thursday prayers to Dakshinamurthy amplify results.",
        "tanglish": "Pulipani Siddhar rule padi, ippo ungalukku Guru Dasa! Growth, nalla mentors, suba kaariyam ellam favor-aa irukkum. Thursday Dakshinamurthy/temple visit romba nalladhu.",
    },
    "Saturn": {
        "ta": "புலிப்பாணி சித்தர் வாக்குப்படி, சனி தசை பொறுமையையும் கடின உழைப்பையும் சோதித்தாலும் நிலையான வெற்றியைத் தரும். சனிக்கிழமை எள் தீபம் ஏற்றுவது சிறந்த பரிகாரம்.",
        "en": "Per Pulipani Siddhar, Sani (Saturn) Dasa rewards patience, discipline, and long-term foundations. Lighting a sesame oil lamp on Saturdays brings calm progress.",
        "tanglish": "Pulipani Siddhar rule padi, Sani Dasa-la shortcuts work aagadhu—aana steady hard work panna solid success kedaikkum. Saturday sesame lamp (ellu deepam) simple pariharam.",
    },
    "Venus": {
        "ta": "புலிப்பாணி சித்தர் ஜோதிடப்படி, சுக்கிர தசை கலை, காதல், திருமணம் மற்றும் சுகபோகங்களை வளர்க்கும். வெள்ளிக்கிழமை மகாலட்சுமி வழிபாடு நலம் தரும்.",
        "en": "Per Pulipani Siddhar, Sukkiran (Venus) Dasa elevates relationships, creativity, luxury, and marriage prospects. Friday Mahalakshmi prayers enhance harmony.",
        "tanglish": "Pulipani Siddhar rule padi, Sukkira Dasa-la relationships, luxury, career charm ellam boost aagum! Friday Mahalakshmi prayer or white sweets daanam nalladhu.",
    },
    "Mercury": {
        "ta": "புலிப்பாணி சித்தர் விதிப்படி, புதன் தசை வியாபாரம், பேச்சுத்திறமை, தொழில்நுட்பம் மற்றும் புத்திசாலித்தனத்தால் வெற்றியைத் தரும். புதன்கிழமை பெருமாள் வழிபாடு சிறந்தது.",
        "en": "Per Pulipani Siddhar, Budhan (Mercury) Dasa sharpens business acumen, communication, tech skills, and finances. Wednesday Vishnu prayers bring clarity.",
        "tanglish": "Pulipani Siddhar rule padi, Budhan Dasa business, tech career, communication-ku super period! Wednesday Perumal koil or green moong daanam nalladhu.",
    },
    "Sun": {
        "ta": "புலிப்பாணி சித்தர் வாக்குப்படி, சூரிய தசை அதிகாரம், அரசு உதவி மற்றும் தலைமைப் பண்பை உயர்த்தும். அதிகாலை சூரிய நமஸ்காரம் பலம் தரும்.",
        "en": "Per Pulipani Siddhar, Sooriyan (Sun) Dasa strengthens leadership, recognition, and authority. Morning Surya Namaskar aligns your vitality.",
        "tanglish": "Pulipani Siddhar rule padi, Sooriya Dasa-la leadership, recognition & govt/management support kedaikkum. Morning sunlight / Surya Namaskar energy tharum.",
    },
    "Moon": {
        "ta": "புலிப்பாணி சித்தர் விதிப்படி, சந்திர தசை மன அமைதி, தாயார் ஆசி மற்றும் பயணங்களைத் தரும். பௌர்ணமி நாளில் அம்மன் வழிபாடு மன குழப்பத்தை நீக்கும்.",
        "en": "Per Pulipani Siddhar, Chandran (Moon) Dasa activates intuition, emotional growth, travel, and family bonds. Full-moon prayers bring mental peace.",
        "tanglish": "Pulipani Siddhar rule padi, Chandra Dasa-la intuition, travel & family bonding strong-aa irukkum. Pournami annaikku koil pona manasu calm aagum.",
    },
    "Mars": {
        "ta": "புலிப்பாணி சித்தர் ஜோதிடப்படி, செவ்வாய் தசை தைரியம், பூமி லாபம் மற்றும் வெற்றியைத் தரும்; கோபத்தைக் கட்டுப்படுத்த செவ்வாய்க்கிழமை முருகன் வழிபாடு நன்று.",
        "en": "Per Pulipani Siddhar, Sevvai (Mars) Dasa gives courage, property gains, and bold action. Channel impatience through Tuesday Murugan prayers.",
        "tanglish": "Pulipani Siddhar rule padi, Sevvai Dasa-la boldness, property/career jump varum—aana kovatha control pannanum. Tuesday Murugan prayer best pariharam.",
    },
    "Rahu": {
        "ta": "புலிப்பாணி சித்தர் விதிப்படி, ராகு தசை திடீர் மாற்றங்கள், வெளிநாட்டு வாய்ப்புகள் மற்றும் புதிய தொழில் வளர்ச்சியைத் தரும். துர்க்கை வழிபாடு தெளிவு தரும்.",
        "en": "Per Pulipani Siddhar, Rahu Dasa triggers sudden breakthroughs, foreign opportunities, and unconventional growth. Durga prayers keep you grounded.",
        "tanglish": "Pulipani Siddhar rule padi, Rahu Dasa-la sudden breakthroughs, abroad/tech chances varum—overthinking avoid panna Durga/Rahu kaalam lamp nalladhu.",
    },
    "Ketu": {
        "ta": "புலிப்பாணி சித்தர் வாக்குப்படி, கேது தசை ஆழ்ந்த ஞானம், ஆராய்ச்சி மற்றும் ஆன்மீகத் தெளிவைத் தரும். விநாயகர் வழிபாடு அனைத்துத் தடைகளையும் நீக்கும்.",
        "en": "Per Pulipani Siddhar, Ketu Dasa deepens wisdom, research, and spiritual clarity while detaching you from toxic paths. Ganesha prayers remove obstacles.",
        "tanglish": "Pulipani Siddhar rule padi, Ketu Dasa-la inner clarity, research/skill depth & detachment varum. Daily Vinayagar prayer ella hurdles-ayum clear pannum.",
    },
}

# Daily Rasi Palan templates (combined with Moon transit relative to user's Rasi)
TRANSIT_MOOD = {
    1: ("emerald", "புதிய உற்சாகம் & சுயநம்பிக்கை", "Fresh energy & confidence", "Puthu energy & confidence high-aa irukkum"),
    2: ("gold", "பண வரவு & குடும்ப இனிமை", "Financial flow & warm family talks", "Money flow & family talks nalla irukkum"),
    3: ("emerald", "தைரியம் & வெற்றி செய்தி", "Courage & positive news", "Bold-aa step edunga, nalla news varum"),
    4: ("amber", "மன அமைதி & வீட்டுப் பணி", "Home focus & quiet pace", "Veetu vishayam & rest-ku priority kudunga"),
    5: ("gold", "புத்திசாலித்தனம் & காதல்", "Creativity, romance & smart ideas", "Creative ideas & love/bonding super-aa irukkum"),
    6: ("emerald", "போட்டிகளில் வெற்றி & ஆரோக்கியம்", "Victory over hurdles & good health", "Work hurdles clear aagum, health strong"),
    7: ("gold", "கூட்டாளிகள் & பயண நலம்", "Partnerships & pleasant meetings", "Partner / client meetings positive-aa mudiyum"),
    8: ("crimson", "சந்திராஷ்டமம் — கவனம் தேவை!", "Chandrashtamam — Stay calm & avoid risks", "Chandrashtamam! Calm-aa irunga, no big risks"),
    9: ("emerald", "அதிர்ஷ்டம் & பெரியோர் ஆசி", "Luck, mentors & blessings", "Luck & elders blessings unga pakkam irukku"),
    10: ("emerald", "தொழில் உயர்வு & பாராட்டு", "Career progress & recognition", "Career-la appreciation & progress kedaikkum"),
    11: ("emerald", "லாபம் & நண்பர்கள் உதவி", "Gains, income & supportive friends", "Income/gains & friends support super"),
    12: ("amber", "செலவு கட்டுப்பாடு & ஓய்வு", "Watch expenses & prioritize rest", "Extra expenses control pannunga, nalla rest edunga"),
}
