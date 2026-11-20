"""Core Tamil Vedic Astrology, Pancha Patchi, Pulipani Siddhar & Porutham engine using pyswisseph."""

from __future__ import annotations

import datetime as dt
import math
import os
import random
from typing import Any, Dict, List, Optional

import httpx
import swisseph as swe

from astrology_data import (
    BIRDS,
    DASA_LORDS,
    GRAHA_LABELS,
    NAKSHATRAMS,
    PATCHI_STATES,
    PULIPANI_DASA_INSIGHTS,
    RASIS,
    STATE_CYCLE,
    TRANSIT_MOOD,
    WEEKDAY_BIRD_OFFSET_THEI_DAY,
    WEEKDAY_BIRD_OFFSET_THEI_NIGHT,
    WEEKDAY_BIRD_OFFSET_VALAR_DAY,
    WEEKDAY_BIRD_OFFSET_VALAR_NIGHT,
)

AYANAMSA_MAP = {
    "lahiri": swe.SIDM_LAHIRI,
    "raman": swe.SIDM_RAMAN,
    "kp": swe.SIDM_KRISHNAMURTI,
}

PLANETS = [
    ("Sun", swe.SUN),
    ("Moon", swe.MOON),
    ("Mars", swe.MARS),
    ("Mercury", swe.MERCURY),
    ("Jupiter", swe.JUPITER),
    ("Venus", swe.VENUS),
    ("Saturn", swe.SATURN),
    ("Rahu", swe.MEAN_NODE),
]

# Rahu Kalam, Yemagandam, Kuligai octant index (0..7 of daytime) by Python weekday (0=Mon..6=Sun)
RAHU_OCTANT = {0: 1, 1: 6, 2: 4, 3: 5, 4: 3, 5: 2, 6: 7}
YEMA_OCTANT = {0: 3, 1: 2, 2: 1, 3: 0, 4: 6, 5: 5, 6: 4}
KULI_OCTANT = {0: 5, 1: 4, 2: 3, 3: 2, 4: 1, 5: 0, 6: 6}


def _set_ayanamsa(ayanamsa: str) -> None:
    mode = AYANAMSA_MAP.get(ayanamsa.lower(), swe.SIDM_LAHIRI)
    swe.set_sid_mode(mode)


def _to_jd_ut(date_str: str, time_str: str, tz_offset: float) -> float:
    year, month, day = map(int, date_str.split("-"))
    parts = time_str.split(":")
    hour = int(parts[0])
    minute = int(parts[1]) if len(parts) > 1 else 0
    second = int(parts[2]) if len(parts) > 2 else 0
    ut_hours = hour + minute / 60.0 + second / 3600.0 - tz_offset
    return swe.julday(year, month, day, ut_hours)


def _jd_to_local_str(jd_ut: float, tz_offset: float) -> str:
    y, m, d, ut_h = swe.revjul(jd_ut + tz_offset / 24.0)
    total_mins = int(round(ut_h * 60)) % 1440
    hh = total_mins // 60
    mm = total_mins % 60
    suffix = "AM" if hh < 12 else "PM"
    disp_h = hh % 12 or 12
    return f"{disp_h:02d}:{mm:02d} {suffix}"


def _jd_to_local_dt_str(jd_ut: float, tz_offset: float, ref_date_str: str) -> str:
    y, m, d, ut_h = swe.revjul(jd_ut + tz_offset / 24.0)
    total_mins = int(round(ut_h * 60))
    extra_days, total_mins = divmod(total_mins, 1440)
    local_dt = dt.datetime(int(y), int(m), int(d)) + dt.timedelta(days=extra_days)
    hh = total_mins // 60
    mm = total_mins % 60
    suffix = "AM" if hh < 12 else "PM"
    disp_h = hh % 12 or 12
    time_part = f"{disp_h:02d}:{mm:02d} {suffix}"
    return f"{local_dt.strftime('%d %b')}, {time_part}"


def _format_minutes_to_str(minutes_from_midnight: float) -> str:
    total_mins = int(round(minutes_from_midnight)) % 1440
    hh = total_mins // 60
    mm = total_mins % 60
    suffix = "AM" if hh < 12 else "PM"
    disp_h = hh % 12 or 12
    return f"{disp_h:02d}:{mm:02d} {suffix}"


def _get_sunrise_sunset_jd(date_str: str, lat: float, lon: float, tz_offset: float) -> tuple[float, float]:
    year, month, day = map(int, date_str.split("-"))
    jd_midnight_ut = swe.julday(year, month, day, -tz_offset)
    geopos = (lon, lat, 0.0)
    res_rise = swe.rise_trans(jd_midnight_ut, swe.SUN, swe.CALC_RISE | swe.BIT_DISC_CENTER, geopos)
    sunrise_jd = res_rise[1][0]
    res_set = swe.rise_trans(sunrise_jd, swe.SUN, swe.CALC_SET | swe.BIT_DISC_CENTER, geopos)
    sunset_jd = res_set[1][0]
    return sunrise_jd, sunset_jd


def _navamsam_rasi(sidereal_deg: float) -> int:
    rasi_idx = int(sidereal_deg // 30.0) % 12
    deg_in_rasi = sidereal_deg % 30.0
    pada_in_rasi = int(deg_in_rasi // (30.0 / 9.0))
    # Movable (0,3,6,9): start same; Fixed (1,4,7,10): start 9th; Dual (2,5,8,11): start 5th
    mod3 = rasi_idx % 3
    if mod3 == 0:
        start = rasi_idx
    elif mod3 == 1:
        start = (rasi_idx + 8) % 12
    else:
        start = (rasi_idx + 4) % 12
    return (start + pada_in_rasi) % 12


def _compute_vimshottari_dasa(moon_deg: float, dob_str: str, now_dt: Optional[dt.datetime] = None) -> Dict[str, Any]:
    if now_dt is None:
        now_dt = dt.datetime.now()
    nak_span = 360.0 / 27.0
    nak_idx = int(moon_deg // nak_span) % 27
    frac_elapsed = (moon_deg % nak_span) / nak_span
    start_lord_idx = nak_idx % 9
    first_lord = DASA_LORDS[start_lord_idx]
    remaining_first = first_lord["years"] * (1.0 - frac_elapsed)

    dob = dt.datetime.strptime(dob_str, "%Y-%m-%d")
    age_years = max(0.0, (now_dt - dob).days / 365.2425)

    elapsed = 0.0
    idx = start_lord_idx
    current_maha = first_lord
    maha_elapsed = 0.0
    maha_total = first_lord["years"]

    # Walk Dasa sequence until we find current Maha Dasa
    for step in range(27):
        lord = DASA_LORDS[idx]
        dur = remaining_first if step == 0 else float(lord["years"])
        if age_years < elapsed + dur:
            current_maha = lord
            maha_total = float(lord["years"])
            maha_elapsed = (age_years - elapsed) + (lord["years"] - remaining_first if step == 0 else 0.0)
            break
        elapsed += dur
        idx = (idx + 1) % 9

    # Find Bhukti inside current Maha Dasa
    maha_idx = next(i for i, l in enumerate(DASA_LORDS) if l["key"] == current_maha["key"])
    bhukti_elapsed = 0.0
    bhukti_dur = maha_total / 9.0
    current_bhukti = current_maha
    for b_step in range(9):
        b_lord = DASA_LORDS[(maha_idx + b_step) % 9]
        b_dur = (maha_total * b_lord["years"]) / 120.0
        if maha_elapsed < bhukti_elapsed + b_dur:
            current_bhukti = b_lord
            bhukti_dur = b_dur
            break
        bhukti_elapsed += b_dur

    # Find Anthar Dasa (Pratyantardasa) inside current Bhukti
    bhukti_idx = next(i for i, l in enumerate(DASA_LORDS) if l["key"] == current_bhukti["key"])
    in_bhukti_elapsed = max(0.0, maha_elapsed - bhukti_elapsed)
    anthar_elapsed = 0.0
    anthar_dur = bhukti_dur / 9.0
    current_anthar = current_bhukti
    for a_step in range(9):
        a_lord = DASA_LORDS[(bhukti_idx + a_step) % 9]
        a_dur = (bhukti_dur * a_lord["years"]) / 120.0
        if in_bhukti_elapsed < anthar_elapsed + a_dur:
            current_anthar = a_lord
            anthar_dur = a_dur
            break
        anthar_elapsed += a_dur

    years_left = max(0.1, round(maha_total - maha_elapsed, 1))
    maha_end_dt = dob + dt.timedelta(days=(age_years + (maha_total - maha_elapsed)) * 365.2425)
    bhukti_end_dt = dob + dt.timedelta(days=(age_years + ((bhukti_elapsed + bhukti_dur) - maha_elapsed)) * 365.2425)
    anthar_end_dt = dob + dt.timedelta(days=(age_years + ((anthar_elapsed + anthar_dur) - in_bhukti_elapsed)) * 365.2425)

    return {
        "maha_dasa": current_maha,
        "bhukti": current_bhukti,
        "anthar": current_anthar,
        "years_remaining": years_left,
        "maha_end": maha_end_dt.strftime("%d %b %Y"),
        "bhukti_end": bhukti_end_dt.strftime("%d %b %Y"),
        "anthar_end": anthar_end_dt.strftime("%d %b %Y"),
    }


def _compute_pancha_patchi(
    nak_idx: int,
    is_valarpirai: bool,
    weekday: int,
    sunrise_jd: float,
    sunset_jd: float,
    now_jd: float,
    tz_offset: float,
    lang: str,
    birth_is_valarpirai: Optional[bool] = None,
) -> Dict[str, Any]:
    nak = NAKSHATRAMS[nak_idx % 27]
    use_valar_for_bird = is_valarpirai if birth_is_valarpirai is None else birth_is_valarpirai
    bird_idx = nak["bird_valar"] if use_valar_for_bird else nak["bird_thei"]
    bird = BIRDS[bird_idx]

    day_len = sunset_jd - sunrise_jd
    next_sunrise_jd = sunrise_jd + 1.0
    night_len = next_sunrise_jd - sunset_jd

    day_offset = (WEEKDAY_BIRD_OFFSET_VALAR_DAY if is_valarpirai else WEEKDAY_BIRD_OFFSET_THEI_DAY)[weekday]
    night_offset = (WEEKDAY_BIRD_OFFSET_VALAR_NIGHT if is_valarpirai else WEEKDAY_BIRD_OFFSET_THEI_NIGHT)[weekday]

    day_jamams = []
    for j in range(5):
        s_jd = sunrise_jd + (j / 5.0) * day_len
        e_jd = sunrise_jd + ((j + 1) / 5.0) * day_len
        state_name = STATE_CYCLE[(bird_idx + day_offset + j) % 5]
        st = PATCHI_STATES[state_name]
        day_jamams.append({
            "jamam": j + 1,
            "period": "day",
            "start": _jd_to_local_str(s_jd, tz_offset),
            "end": _jd_to_local_str(e_jd, tz_offset),
            "state": state_name,
            "label": st.get(lang, st["en"]),
            "advice": st.get(f"advice_{lang}", st["advice_en"]),
            "power": st["power"],
            "tone": st["tone"],
            "is_current": s_jd <= now_jd < e_jd,
        })

    night_jamams = []
    for j in range(5):
        s_jd = sunset_jd + (j / 5.0) * night_len
        e_jd = sunset_jd + ((j + 1) / 5.0) * night_len
        state_name = STATE_CYCLE[(bird_idx + night_offset + j) % 5]
        st = PATCHI_STATES[state_name]
        night_jamams.append({
            "jamam": j + 1,
            "period": "night",
            "start": _jd_to_local_str(s_jd, tz_offset),
            "end": _jd_to_local_str(e_jd, tz_offset),
            "state": state_name,
            "label": st.get(lang, st["en"]),
            "advice": st.get(f"advice_{lang}", st["advice_en"]),
            "power": st["power"],
            "tone": st["tone"],
            "is_current": s_jd <= now_jd < e_jd,
        })

    all_jamams = day_jamams + night_jamams
    cur_idx = next((i for i, jm in enumerate(all_jamams) if jm["is_current"]), 0)
    current_jamam = all_jamams[cur_idx]
    ordered_upcoming = [all_jamams[(cur_idx + k) % len(all_jamams)] for k in range(1, len(all_jamams))]
    next_jamam = ordered_upcoming[0]
    next_arasu = next((jm for jm in ordered_upcoming if jm["state"] == "Arasu"), ordered_upcoming[0])
    next_best = next((jm for jm in ordered_upcoming if jm["state"] in ("Arasu", "Oon")), next_arasu)
    timeline = [current_jamam] + ordered_upcoming[:4]

    return {
        "bird": {
            "idx": bird["idx"],
            "emoji": bird["emoji"],
            "name": bird.get(lang, bird["en"]),
        },
        "paksham": (
            ("வளர்பிறை" if lang == "ta" else "Valarpirai (Waxing)" if lang == "tanglish" else "Waxing Moon (Shukla)")
            if is_valarpirai
            else ("தேய்பிறை" if lang == "ta" else "Theipirai (Waning)" if lang == "tanglish" else "Waning Moon (Krishna)")
        ),
        "is_valarpirai": is_valarpirai,
        "current": current_jamam,
        "next_jamam": next_jamam,
        "next_arasu": next_arasu,
        "next_best": next_best,
        "timeline": timeline,
        "day_jamams": day_jamams,
        "night_jamams": night_jamams,
    }


TARA_BALAM = {
    1: {"good": True, "score": 65, "ta": "ஜன்ம தாரை (மனம் & ஆரோக்கியம்)", "en": "Janma Tara (Self & Focus)", "tanglish": "Janma Tara (Self Focus)"},
    2: {"good": True, "score": 95, "ta": "சம்பத் தாரை (செல்வம் & லாபம்)", "en": "Sampath Tara (Wealth & Gains)", "tanglish": "Sampath Tara (Money & Gains)"},
    3: {"good": False, "score": 30, "ta": "விபத் தாரை (தடைகள் — நிதானம் தேவை)", "en": "Vipat Tara (Obstacles — Go Slow)", "tanglish": "Vipat Tara (Slow & Careful)"},
    4: {"good": True, "score": 90, "ta": "க்ஷேம தாரை (பாதுகாப்பு & நலம்)", "en": "Kshema Tara (Well-being & Comfort)", "tanglish": "Kshema Tara (Peace & Safety)"},
    5: {"good": False, "score": 40, "ta": "பிரத்யரி தாரை (எதிர்ப்பு — வாக்குவாதம் தவிர்க்கவும்)", "en": "Pratyari Tara (Friction — Avoid Debates)", "tanglish": "Pratyari Tara (Avoid Arguments)"},
    6: {"good": True, "score": 95, "ta": "சாதக தாரை (காரிய சித்தி & வெற்றி)", "en": "Sadhaka Tara (Success & Execution)", "tanglish": "Sadhaka Tara (Sure Success)"},
    7: {"good": False, "score": 25, "ta": "வதை தாரை (எச்சரிக்கை — முக்கிய முடிவு வேண்டாம்)", "en": "Vadha Tara (Caution — Pause Big Risks)", "tanglish": "Vadha Tara (Pause Big Risks)"},
    8: {"good": True, "score": 85, "ta": "மித்ர தாரை (நண்பர்கள் & கூட்டாளிகள் உதவி)", "en": "Mitra Tara (Allies & Support)", "tanglish": "Mitra Tara (Friends & Support)"},
    9: {"good": True, "score": 95, "ta": "பரம மித்ர தாரை (மிகச் சிறந்த அதிர்ஷ்டம்)", "en": "Parama Mitra Tara (Peak Alignment)", "tanglish": "Parama Mitra Tara (Top Luck)"},
}


def calculate_panchangam(
    date_str: Optional[str] = None,
    lat: float = 13.0827,
    lon: float = 80.2707,
    tz_offset: float = 5.5,
    lang: str = "tanglish",
    user_rasi_idx: Optional[int] = None,
    user_nak_idx: Optional[int] = None,
    user_lagnam_idx: Optional[int] = None,
    user_age: Optional[int] = None,
    user_dasa: Optional[Dict[str, Any]] = None,
    natal_grahas: Optional[Dict[str, int]] = None,
    birth_is_valarpirai: Optional[bool] = None,
    ayanamsa: str = "lahiri",
) -> Dict[str, Any]:
    _set_ayanamsa(ayanamsa)
    now_local = dt.datetime.utcnow() + dt.timedelta(hours=tz_offset)
    if not date_str:
        date_str = now_local.strftime("%Y-%m-%d")

    target_date = dt.datetime.strptime(date_str, "%Y-%m-%d")
    weekday = target_date.weekday()
    now_time_str = now_local.strftime("%H:%M:%S")
    now_jd = _to_jd_ut(date_str, now_time_str, tz_offset)

    sunrise_jd, sunset_jd = _get_sunrise_sunset_jd(date_str, lat, lon, tz_offset)
    day_dur_hours = (sunset_jd - sunrise_jd) * 24.0
    octant_hours = day_dur_hours / 8.0

    def octant_window(oct_idx: int) -> str:
        s_jd = sunrise_jd + (oct_idx * octant_hours) / 24.0
        e_jd = sunrise_jd + ((oct_idx + 1) * octant_hours) / 24.0
        return f"{_jd_to_local_str(s_jd, tz_offset)} - {_jd_to_local_str(e_jd, tz_offset)}"

    # Sun & Moon sidereal longitudes at current time
    sun_lon = swe.calc_ut(now_jd, swe.SUN, swe.FLG_SIDEREAL)[0][0] % 360.0
    moon_res = swe.calc_ut(now_jd, swe.MOON, swe.FLG_SIDEREAL | swe.FLG_SPEED)[0]
    moon_lon = moon_res[0] % 360.0
    moon_speed = max(10.0, float(moon_res[3]))

    moon_rasi_idx = int(moon_lon // 30.0) % 12
    nak_span = 360.0 / 27.0
    moon_nak_idx = int(moon_lon // nak_span) % 27
    moon_pada = int((moon_lon % nak_span) // (nak_span / 4.0)) + 1
    deg_since_nak_start = moon_lon - (moon_nak_idx * nak_span)
    nak_start_jd = now_jd - (deg_since_nak_start / moon_speed)
    tara_valid_from = _jd_to_local_dt_str(nak_start_jd, tz_offset, date_str)
    deg_to_next_nak = ((moon_nak_idx + 1) * nak_span) - moon_lon
    nak_end_jd = now_jd + (deg_to_next_nak / moon_speed)
    tara_valid_till = _jd_to_local_dt_str(nak_end_jd, tz_offset, date_str)

    diff = (moon_lon - sun_lon) % 360.0
    is_valarpirai = diff < 180.0
    thithi_num = int(diff // 12.0) + 1  # 1..30

    # Chandrashtamam Rasi: Moon in 8th from natal Rasi means natal Rasi = (moon_rasi - 7) % 12
    chandrashtamam_rasi_idx = (moon_rasi_idx - 7) % 12

    # Nalla Neram (morning & evening auspicious windows avoiding Rahu/Yema)
    nalla_morning = octant_window(2 if RAHU_OCTANT[weekday] != 2 and YEMA_OCTANT[weekday] != 2 else 0)
    nalla_evening = octant_window(7 if RAHU_OCTANT[weekday] != 7 and YEMA_OCTANT[weekday] != 7 else 6)

    effective_nak = user_nak_idx if user_nak_idx is not None else moon_nak_idx
    pancha_patchi = _compute_pancha_patchi(
        nak_idx=effective_nak,
        is_valarpirai=is_valarpirai,
        weekday=weekday,
        sunrise_jd=sunrise_jd,
        sunset_jd=sunset_jd,
        now_jd=now_jd,
        tz_offset=tz_offset,
        lang=lang,
        birth_is_valarpirai=birth_is_valarpirai,
    )

    # 12 Rasi Palan based on Moon transit relative to each Rasi
    rasi_palan = []
    for r in RASIS:
        house_from_moon = ((moon_rasi_idx - r["idx"]) % 12) + 1
        tone, ta_msg, en_msg, tg_msg = TRANSIT_MOOD[house_from_moon]
        msg = ta_msg if lang == "ta" else en_msg if lang == "en" else tg_msg
        rasi_palan.append({
            "idx": r["idx"],
            "name": r.get(lang, r["en"]),
            "tone": tone,
            "is_chandrashtamam": house_from_moon == 8,
            "summary": msg,
        })

    is_user_chandrashtamam = user_rasi_idx is not None and user_rasi_idx == chandrashtamam_rasi_idx

    # Precision Customized Personal Palan (Age Rule: <30 Rasi primary, 30+ Lagnam primary + Tara Balam)
    personal_palan = None
    if user_rasi_idx is not None and user_nak_idx is not None:
        eff_lagnam = user_lagnam_idx if user_lagnam_idx is not None else user_rasi_idx
        eff_age = user_age if user_age is not None else 28
        use_lagnam = eff_age >= 30
        primary_anchor = "lagnam" if use_lagnam else "rasi"

        rasi_house = ((moon_rasi_idx - user_rasi_idx) % 12) + 1
        lagnam_house = ((moon_rasi_idx - eff_lagnam) % 12) + 1
        primary_house = lagnam_house if use_lagnam else rasi_house

        tara_idx = ((moon_nak_idx - user_nak_idx) % 9) + 1
        tara = TARA_BALAM[tara_idx]

        _, ta_h, en_h, tg_h = TRANSIT_MOOD[primary_house]
        house_summary = ta_h if lang == "ta" else en_h if lang == "en" else tg_h

        age_note = {
            "ta": (
                f"வயது {eff_age} (30+): உங்கள் லக்னமே ({RASIS[eff_lagnam]['ta']}) முதன்மை பலன் தரும்."
                if use_lagnam
                else f"வயது {eff_age} (<30): உங்கள் ராசியே ({RASIS[user_rasi_idx]['ta']}) முதன்மை பலன் தரும்."
            ),
            "en": (
                f"Age {eff_age} (30+): Your Lagnam ({RASIS[eff_lagnam]['en']}) is the primary anchor."
                if use_lagnam
                else f"Age {eff_age} (<30): Your Moon Rasi ({RASIS[user_rasi_idx]['en']}) is the primary anchor."
            ),
            "tanglish": (
                f"Age {eff_age} (30+): Unga Lagnam ({RASIS[eff_lagnam]['tanglish']}) dhaan primary palan tharum."
                if use_lagnam
                else f"Age {eff_age} (<30): Unga Rasi ({RASIS[user_rasi_idx]['tanglish']}) dhaan primary palan tharum."
            ),
        }[lang]

        if is_user_chandrashtamam:
            action_advice = {
                "ta": "இன்று சந்திராஷ்டமம் என்பதால் முக்கிய ஒப்பந்தங்கள், பயணத் தொடக்கங்களைத் தவிர்த்து நிதானமாகச் செயல்படுங்கள்.",
                "en": "Chandrashtamam is active on your Rasi today — keep communication gentle and postpone major commitments.",
                "tanglish": "Innaikku Chandrashtamam! Important deals, arguments & sudden decisions avoid pannittu calm-aa irunga.",
            }[lang]
        elif tara["good"] and primary_house in (1, 2, 3, 5, 6, 7, 9, 10, 11):
            action_advice = {
                "ta": f"சந்திரன் {primary_house}-ம் இடத்திலும் {tara['ta']} இருப்பதாலும், உங்கள் பஞ்ச பட்சி அரசு/ஊண் நேரத்தில் முக்கிய பணிகளைச் செய்யுங்கள்.",
                "en": f"Strong alignment: Moon in house {primary_house} + {tara['en']}. Execute high-priority tasks during your Arasu/Oon Patchi window.",
                "tanglish": f"Strong day! {primary_house}-th house transit + {tara['tanglish']}. Unga Arasu/Oon Patchi time-la important work mudichidunga.",
            }[lang]
        else:
            action_advice = {
                "ta": f"{tara['ta']} மற்றும் {primary_house}-ம் இட சஞ்சாரம் உள்ளதால், வழக்கமான பணிகளில் கவனம் செலுத்தி பெரிய ரிஸ்க் தவிர்க்கவும்.",
                "en": f"Mixed day ({tara['en']}, house {primary_house}). Focus on routine execution and double-check details before committing.",
                "tanglish": f"Mixed energy ({tara['tanglish']}, {primary_house}-th house). Routine work mattum pannunga; big risks or hasty promises vendam.",
            }[lang]

        # Live Planetary Transits (Gocharam) vs Natal Jathagam
        anchor_idx = eff_lagnam if use_lagnam else user_rasi_idx
        transit_rasi: Dict[str, int] = {"Sun": int(sun_lon // 30.0) % 12, "Moon": moon_rasi_idx}
        for p_name, p_id in [("Mars", swe.MARS), ("Mercury", swe.MERCURY), ("Jupiter", swe.JUPITER), ("Venus", swe.VENUS), ("Saturn", swe.SATURN), ("Rahu", swe.MEAN_NODE)]:
            p_lon = swe.calc_ut(now_jd, p_id, swe.FLG_SIDEREAL)[0][0] % 360.0
            transit_rasi[p_name] = int(p_lon // 30.0) % 12
        transit_rasi["Ketu"] = (transit_rasi["Rahu"] + 6) % 12

        guru_house = ((transit_rasi["Jupiter"] - anchor_idx) % 12) + 1
        sani_house = ((transit_rasi["Saturn"] - anchor_idx) % 12) + 1
        sani_from_moon = ((transit_rasi["Saturn"] - user_rasi_idx) % 12) + 1

        guru_good = guru_house in (2, 5, 7, 9, 11)
        sani_phase = (
            ("ஏழரைச் சனி" if lang == "ta" else "Ezharai Sani (Sade Sati)" if lang == "tanglish" else "Sade Sati (7.5-yr Saturn)")
            if sani_from_moon in (12, 1, 2)
            else ("அஷ்டம சனி" if lang == "ta" else "Ashtama Sani" if lang == "tanglish" else "Ashtama Sani (8th Saturn)")
            if sani_from_moon == 8
            else None
        )

        transit_notes = []
        transit_notes.append({
            "ta": f"குரு சஞ்சாரம்: {guru_house}-ம் இடம் ({'பலம்' if guru_good else 'சமம்'}) · சனி சஞ்சாரம்: {sani_house}-ம் இடம்" + (f" ({sani_phase})" if sani_phase else ""),
            "en": f"Guru (Jupiter) in H{guru_house} ({'Favorable' if guru_good else 'Neutral'}) · Sani (Saturn) in H{sani_house}" + (f" ({sani_phase})" if sani_phase else ""),
            "tanglish": f"Live Guru: H{guru_house} ({'Strong' if guru_good else 'Normal'}) · Live Sani: H{sani_house}" + (f" ({sani_phase})" if sani_phase else ""),
        }[lang])

        if user_dasa and user_dasa.get("maha_key"):
            m_key = user_dasa["maha_key"]
            d_tr_rasi = transit_rasi.get(m_key, moon_rasi_idx)
            d_tr_house = ((d_tr_rasi - anchor_idx) % 12) + 1
            natal_rasi_for_lord = natal_grahas.get(m_key) if natal_grahas else None
            same_as_natal = natal_rasi_for_lord is not None and natal_rasi_for_lord == d_tr_rasi
            natal_house_str = f" (Natal H{((natal_rasi_for_lord - anchor_idx) % 12) + 1})" if natal_rasi_for_lord is not None else ""
            transit_notes.append({
                "ta": f"தசா நாதன் ({user_dasa.get('maha')}) இன்று {d_tr_house}-ம் இடத்தில்{natal_house_str}" + (" — ஜாதக அமைப்புடன் ஒத்துப்போகிறது!" if same_as_natal else ""),
                "en": f"Dasa Lord ({user_dasa.get('maha')}) transits H{d_tr_house}{natal_house_str}" + (" — Exact natal alignment!" if same_as_natal else ""),
                "tanglish": f"Dasa Lord ({user_dasa.get('maha')}) innaikku H{d_tr_house}-la irukku{natal_house_str}" + (" — Natal chart-oda exact sync!" if same_as_natal else ""),
            }[lang])

        next_best_win = f"{pancha_patchi['next_best']['start']} – {pancha_patchi['next_best']['end']}"
        if is_user_chandrashtamam:
            daily_details = [
                {
                    "ta": "💼 தொழில் & பணம்: இன்று புதிய முதலீடு, கடன் அல்லது முக்கிய ஒப்பந்தங்களில் கையெழுத்திடுவதைத் தவிர்க்கவும்; நிலுவை வேலைகளை மட்டும் முடிக்கவும்.",
                    "en": "💼 Work & Money: Postpone new investments, loans, or signing key contracts today; focus on wrapping up pending tasks.",
                    "tanglish": "💼 Work & Money: Puthu investment, loan or agreement sign panradha innaikku avoid pannunga; pending work mattum mudinga.",
                }[lang],
                {
                    "ta": "🤝 பேச்சு & உறவு: சந்திராஷ்டமம் என்பதால் மன அழுத்தம் வரலாம் — குடும்பம் மற்றும் சக ஊழியர்களிடம் வாக்குவாதத்தைத் தவிர்க்கவும்.",
                    "en": "🤝 People & Mind: Chandrashtamam can trigger impatience — keep conversations calm with family and colleagues.",
                    "tanglish": "🤝 People & Mind: Chandrashtamam irukkuradhala mood swing varalam — family & office-la arguments avoid pannunga.",
                }[lang],
                {
                    "ta": f"🕒 நேரம்: {tara_valid_till} வரை நிதானம் காத்து, அவசியமான பணிகளை மட்டும் {next_best_win} நேரத்தில் செய்யுங்கள்.",
                    "en": f"🕒 Timing: Stay patient until {tara_valid_till}; handle only essential tasks during {next_best_win}.",
                    "tanglish": f"🕒 Timing: {tara_valid_till} varaikum calm-aa irunga; must-do work mattum {next_best_win}-la pannunga.",
                }[lang],
            ]
        elif tara["good"] and primary_house in (1, 2, 3, 5, 6, 7, 9, 10, 11):
            daily_details = [
                {
                    "ta": f"💼 தொழில் & பணம்: {primary_house}-ம் இட சந்திரனும் {tara['ta']} இணைவதால் புதிய முயற்சிகள், பணப் பேச்சுவார்த்தை மற்றும் வாடிக்கையாளர் சந்திப்புகள் கைகூடும்.",
                    "en": f"💼 Work & Money: Moon in H{primary_house} + {tara['en']} strongly favor pitches, financial talks, and new initiatives.",
                    "tanglish": f"💼 Work & Money: H{primary_house} transit + {tara['tanglish']} super-aa irukku — client calls, money talks & new steps edukkalam.",
                }[lang],
                {
                    "ta": "🤝 பேச்சு & உறவு: உங்கள் கருத்திற்கு நல்ல வரவேற்பு கிடைக்கும்; நண்பர்கள் அல்லது பெரியோர்களின் ஆலோசனை உதவும்.",
                    "en": "🤝 People & Mind: Clear communication wins support today; mentors and allies back your ideas.",
                    "tanglish": "🤝 People & Mind: Unga words-ku nalla value irukkum; friends & elders support kedaikkum.",
                }[lang],
                {
                    "ta": f"✅ சிறந்த நேரம்: {tara_valid_till} வரை இந்த நற்பலன் தொடரும். முக்கிய செயல்களை {next_best_win} (அரசு/ஊண்) நேரத்தில் தொடங்குங்கள்.",
                    "en": f"✅ Best Action: This supportive Tara holds until {tara_valid_till}. Start key moves in {next_best_win}.",
                    "tanglish": f"✅ Best Action: {tara_valid_till} varaikum indha good Tara irukku — main work-a {next_best_win}-la start pannunga.",
                }[lang],
            ]
        else:
            daily_details = [
                {
                    "ta": f"💼 தொழில் & பணம்: {primary_house}-ம் இட சஞ்சாரமும் {tara['ta']} இருப்பதால் ஆவணங்களை இருமுறை சரிபார்த்து, செலவுகளைக் கட்டுப்படுத்தவும்.",
                    "en": f"💼 Work & Money: With Moon in H{primary_house} and {tara['en']}, double-check documents and avoid impulse spending.",
                    "tanglish": f"💼 Work & Money: H{primary_house} & {tara['tanglish']} irukkuradhala documents double-check pannunga; extra expenses control pannunga.",
                }[lang],
                {
                    "ta": "🤝 பேச்சு & உறவு: அவசரப் பதில்களைத் தவிர்த்து, அமைதியாகக் கேட்டு முடிவெடுப்பது தேவையற்ற மனக்கசப்பைத் தடுக்கும்.",
                    "en": "🤝 People & Mind: Listen calmly before reacting today to prevent avoidable misunderstandings.",
                    "tanglish": "🤝 People & Mind: Avasarama react pannama calm-aa ketta, unnecessary misunderstanding avoid aagum.",
                }[lang],
                {
                    "ta": f"🕒 மாற்றம் எப்போது?: {tara_valid_till}-க்குப் பிறகு நட்சத்திரம் மாறும். இன்று முக்கிய வேலைகளுக்கு {next_best_win} நேரத்தைப் பயன்படுத்துங்கள்.",
                    "en": f"🕒 When it shifts: Current Tara ends at {tara_valid_till}. Use {next_best_win} for priority tasks today.",
                    "tanglish": f"🕒 Eppo Maarum?: {tara_valid_till} apram Tara maarum. Innaikku important work-ku {next_best_win} use pannunga.",
                }[lang],
            ]

        personal_palan = {
            "primary_anchor": primary_anchor,
            "age": eff_age,
            "age_rule_note": age_note,
            "dasa_summary": (
                f"{user_dasa.get('maha')} → {user_dasa.get('bhukti')} → {user_dasa.get('anthar')} (till {user_dasa.get('maha_end')})"
                if user_dasa
                else None
            ),
            "transit_notes": transit_notes,
            "tara_balam": {
                "index": tara_idx,
                "name": tara.get(lang, tara["en"]),
                "score": tara["score"],
                "good": tara["good"],
                "valid_from": tara_valid_from,
                "valid_till": tara_valid_till,
            },
            "rasi_house": rasi_house,
            "lagnam_house": lagnam_house,
            "primary_house": primary_house,
            "headline": house_summary,
            "action_advice": action_advice,
            "daily_details": daily_details,
        }

    return {
        "date": date_str,
        "sunrise": _jd_to_local_str(sunrise_jd, tz_offset),
        "sunset": _jd_to_local_str(sunset_jd, tz_offset),
        "nalla_neram": f"{nalla_morning}",
        "nalla_neram_evening": nalla_evening,
        "rahu_kalam": octant_window(RAHU_OCTANT[weekday]),
        "yemagandam": octant_window(YEMA_OCTANT[weekday]),
        "kuligai": octant_window(KULI_OCTANT[weekday]),
        "nakshatram": {
            "idx": moon_nak_idx,
            "name": NAKSHATRAMS[moon_nak_idx].get(lang, NAKSHATRAMS[moon_nak_idx]["en"]),
            "pada": moon_pada,
        },
        "moon_rasi": {
            "idx": moon_rasi_idx,
            "name": RASIS[moon_rasi_idx].get(lang, RASIS[moon_rasi_idx]["en"]),
        },
        "thithi_number": thithi_num,
        "is_valarpirai": is_valarpirai,
        "chandrashtamam_rasi": {
            "idx": chandrashtamam_rasi_idx,
            "name": RASIS[chandrashtamam_rasi_idx].get(lang, RASIS[chandrashtamam_rasi_idx]["en"]),
        },
        "is_user_chandrashtamam": is_user_chandrashtamam,
        "pancha_patchi": pancha_patchi,
        "personal_palan": personal_palan,
        "rasi_palan": rasi_palan,
    }


def _compute_pulipani_palangal(
    lagnam_idx: int,
    grahas: List[Dict[str, Any]],
    dasa_info: Dict[str, Any],
    age_years: int,
    lang: str,
) -> Dict[str, str]:
    """Compute chart-specific, age-aware Pulipani Jothidam 300 style predictions (Palangal) + Pariharam."""
    pos = {g["key"]: ((g["rasi_idx"] - lagnam_idx) % 12) + 1 for g in grahas}

    lagna_lord = RASIS[lagnam_idx]["lord"]
    tenth_lord = RASIS[(lagnam_idx + 9) % 12]["lord"]
    seventh_lord = RASIS[(lagnam_idx + 6) % 12]["lord"]

    lagna_lord_h = pos.get(lagna_lord, 1)
    tenth_lord_h = pos.get(tenth_lord, 10)
    seventh_lord_h = pos.get(seventh_lord, 7)
    guru_h = pos.get("Jupiter", 1)
    sani_h = pos.get("Saturn", 1)
    maha_key = dasa_info["maha_dasa"]["key"]
    bhukti_key = dasa_info["bhukti"]["key"]
    maha_h = pos.get(maha_key, 1)

    if age_years < 25:
        stage_ta, stage_en, stage_tg = (
            f"உங்கள் {age_years} வயதில் கல்வி மற்றும் அடித்தளத் திறனை வலுப்படுத்தும் காலம்",
            f"At age {age_years}, focus on building core skills and early career momentum",
            f"Unga {age_years} age-la strong skill foundation & early career growth phase",
        )
    elif age_years < 35:
        stage_ta, stage_en, stage_tg = (
            f"உங்கள் {age_years} வயதில் தொழில் வளர்ச்சி மற்றும் சுய நிலைப்பாடு பெறும் காலம்",
            f"At age {age_years}, this is your prime expansion and career-building phase",
            f"Unga {age_years} age-la career jump, growth & settling down phase",
        )
    elif age_years < 50:
        stage_ta, stage_en, stage_tg = (
            f"உங்கள் {age_years} வயதில் அனுபவத்தை அதிகாரமாகவும் நிலையான சொத்தாகவும் மாற்றும் பருவம்",
            f"At age {age_years}, your chart favors leadership, consolidation, and scaling authority",
            f"Unga {age_years} age-la experience-a authority, business scale & solid assets-aa maathura phase",
        )
    else:
        stage_ta, stage_en, stage_tg = (
            f"உங்கள் {age_years} வயதில் வழிகாட்டுதல், மன அமைதி மற்றும் நிலைத்த சொத்துப் பாதுகாப்பு காலம்",
            f"At age {age_years}, focus on mentorship, wealth preservation, and peaceful balance",
            f"Unga {age_years} age-la mentorship, asset protection & peaceful stability phase",
        )

    # 1. Career & Authority Palan (Age-Aware)
    if tenth_lord_h in (1, 4, 5, 7, 9, 10, 11):
        career = {
            "ta": f"தொழில் பலன்: 10-ம் அதிபதி ({tenth_lord}) {tenth_lord_h}-ம் இடத்தில் வலுவாக உள்ளார் — {stage_ta}; பதவி உயர்வு மற்றும் சமூக மதிப்பு கிடைக்கும்.",
            "en": f"Career Palan: 10th lord ({tenth_lord}) in H{tenth_lord_h} is strong — {stage_en} with leadership respect.",
            "tanglish": f"Career Palan: 10th lord ({tenth_lord}) H{tenth_lord_h}-la strong — {stage_tg}; promotion & recognition kedaikkum.",
        }[lang]
    else:
        career = {
            "ta": f"தொழில் பலன்: 10-ம் அதிபதி {tenth_lord_h}-ம் இடத்தில் உள்ளதால் {stage_ta}; போட்டி மற்றும் உழைப்புக்குப் பிறகே உறுதியான வெற்றி கைகூடும்.",
            "en": f"Career Palan: 10th lord in H{tenth_lord_h} — {stage_en}; steady persistence and smart delegation turn competition into lasting wins.",
            "tanglish": f"Career Palan: 10th lord H{tenth_lord_h}-la irukku — {stage_tg}; competition-a smart work & persistence moolama win pannuveenga.",
        }[lang]

    # 2. Wealth & Dhanayoga Palan (Age-Aware)
    if guru_h in (1, 2, 5, 7, 9, 11) or lagna_lord_h in (1, 2, 5, 9, 11):
        wealth = {
            "ta": f"செல்வ யோகம் ({age_years} வயது): லக்னாதிபதி {lagna_lord_h}-ம் இடத்திலும் குரு {guru_h}-ம் இடத்திலும் இருப்பதால் சொத்து, சேமிப்பு மற்றும் பலவழி வருமானம் சிறக்கும்.",
            "en": f"Wealth Palan (Age {age_years}): Lagna lord in H{lagna_lord_h} and Guru in H{guru_h} support assets, savings, and multi-source income.",
            "tanglish": f"Wealth Palan (Age {age_years}): Lagnathipathi H{lagna_lord_h} & Guru H{guru_h} support nalla irukku — assets & steady savings grow aagum.",
        }[lang]
    else:
        wealth = {
            "ta": f"செல்வ பலன் ({age_years} வயது): குரு {guru_h}-ம் இடத்திலும் சனி {sani_h}-ம் இடத்திலும் உள்ளதால் திட்டமிட்ட முதலீடும் கடன் கட்டுப்பாடும் செல்வத்தை நிலைநிறுத்தும்.",
            "en": f"Wealth Palan (Age {age_years}): With Guru in H{guru_h} and Sani in H{sani_h}, structured investments and debt control protect wealth.",
            "tanglish": f"Wealth Palan (Age {age_years}): Guru H{guru_h} & Sani H{sani_h} padi structured investment & expense control pannaa wealth strong-aa irukkum.",
        }[lang]

    # 3. Family & Relationship Palan (Age-Aware)
    if seventh_lord_h in (1, 2, 4, 5, 7, 9, 11):
        family = {
            "ta": f"குடும்ப பலன் ({age_years} வயது): 7-ம் அதிபதி {seventh_lord_h}-ம் இடத்தில் இருப்பதால் குடும்ப ஒற்றுமை, துணைவர் ஆதரவு மற்றும் சுப காரியங்கள் சிறப்பாக அமையும்.",
            "en": f"Family Palan (Age {age_years}): 7th lord in H{seventh_lord_h} brings partner support, family harmony, and auspicious milestones.",
            "tanglish": f"Family Palan (Age {age_years}): 7th lord H{seventh_lord_h}-la irukkuradhala partner support & family harmony nalla irukkum.",
        }[lang]
    else:
        family = {
            "ta": f"குடும்ப பலன் ({age_years} வயது): 7-ம் அதிபதி {seventh_lord_h}-ம் இடத்தில் உள்ளதால் குடும்பப் பொறுப்புகளில் நிதானமும் வெளிப்படையான பேச்சும் மகிழ்ச்சி தரும்.",
            "en": f"Family Palan (Age {age_years}): 7th lord in H{seventh_lord_h} rewards calm listening and balanced work-family time.",
            "tanglish": f"Family Palan (Age {age_years}): 7th lord H{seventh_lord_h}-la irukku — family responsibilities-la calm-aa & open-aa pesina smooth-aa irukkum.",
        }[lang]

    # 4. Active Dasa-Bhukti Palan
    dasa_effect = {
        "ta": f"நடப்பு தசை பலன் ({dasa_info['maha_dasa']['ta']} → {dasa_info['bhukti']['ta']}): தசா நாதன் உங்கள் ஜாதகத்தில் {maha_h}-ம் இடத்தில் உள்ளதால் {dasa_info['maha_end']} வரை முக்கிய மாற்றங்களும் பொறுப்புகளும் வரும்.",
        "en": f"Active Dasa Palan ({dasa_info['maha_dasa']['en']} → {dasa_info['bhukti']['en']}): Your Dasa lord sits in natal H{maha_h}, driving key shifts in {bhukti_key} themes until {dasa_info['maha_end']}.",
        "tanglish": f"Active Dasa Palan ({dasa_info['maha_dasa']['tanglish']} → {dasa_info['bhukti']['tanglish']}): Dasa lord natal H{maha_h}-la irukkuradhala {dasa_info['maha_end']} varaikum puthu responsibilities & turning points varum.",
    }[lang]

    # Realistic, non-cluttered Pariharam: only prescribe a focused remedy for an actual 6/8/12 challenge;
    # otherwise honestly state that no heavy pariharam is needed.
    SIMPLE_PRACTICE = {
        "Sun": ("ஞாயிறு காலை 5 நிமிடம் சூரிய நமஸ்காரம்", "5 mins of morning sunlight / Surya Namaskar on Sundays", "Sunday morning 5 mins sunlight"),
        "Moon": ("திங்கள் அல்லது பௌர்ணமி நாளில் தாயார் / பெரியோர் ஆசி", "respecting elders & staying hydrated on Mondays", "Monday/Pournami elders-kitta aasi"),
        "Mars": ("செவ்வாய் அன்று கோபத்தைக் கட்டுப்படுத்தி நிதானம் காத்தல்", "practicing calm patience on Tuesdays", "Tuesday kovam control & patience"),
        "Mercury": ("புதன் அன்று மாணவர்கள் அல்லது இளையோருக்கு வழிகாட்டுதல்", "mentoring or gifting a book on Wednesdays", "Wednesday students/youngsters-ku help"),
        "Jupiter": ("வியாழன் அன்று குரு / ஆசிரியரை நினைவுகூர்தல்", "expressing gratitude to a mentor/teacher on Thursdays", "Thursday guru/mentor-ku gratitude"),
        "Venus": ("வெள்ளி அன்று வீடு/பணி இடத்தை சுத்தமாக வைத்தல்", "keeping your space neat & harmonious on Fridays", "Friday workspace/home clean-aa vaikkuradhu"),
        "Saturn": ("சனி அன்று உழைப்பாளிகளுக்கு மரியாதையும் சிறு உதவியும்", "helping an elderly person or worker on Saturdays", "Saturday workers/elders-ku small help"),
        "Rahu": ("கவனம் சிதறாமல் தியானம் அல்லது மூச்சுப் பயிற்சி", "10 mins of quiet breathing to avoid overthinking", "Daily 10 mins breathing/focus (no overthinking)"),
        "Ketu": ("தினமும் 5 நிமிடம் மௌன தியானம்", "5 mins of silent reflection daily", "Daily 5 mins silent reflection"),
    }

    bhukti_h = pos.get(bhukti_key, 1)
    if maha_h in (6, 8, 12):
        act = SIMPLE_PRACTICE.get(maha_key, SIMPLE_PRACTICE["Saturn"])
        pariharam = {
            "ta": f"நடைமுறை பரிகாரம்: தசா நாதன் ({dasa_info['maha_dasa']['ta']}) {maha_h}-ம் இடத்தில் உள்ளதால், {act[0]} போதும்.",
            "en": f"Realistic Remedy: Since your Dasa lord ({dasa_info['maha_dasa']['en']}) is in H{maha_h}, simply practice {act[1]}.",
            "tanglish": f"Practical Pariharam: Dasa lord ({dasa_info['maha_dasa']['tanglish']}) H{maha_h}-la irukkuradhala, {act[2]} pannaa podhum.",
        }[lang]
    elif bhukti_h in (6, 8, 12):
        act = SIMPLE_PRACTICE.get(bhukti_key, SIMPLE_PRACTICE["Moon"])
        pariharam = {
            "ta": f"நடைமுறை பரிகாரம்: {dasa_info['bhukti_end']} வரை உள்ள {dasa_info['bhukti']['ta']} புத்தி ({bhukti_h}-ம் இடம்) அமைதியாகச் செல்ல, {act[0]} உதவும்.",
            "en": f"Realistic Remedy: For your {dasa_info['bhukti']['en']} Bhukti (H{bhukti_h}, till {dasa_info['bhukti_end']}), simply practice {act[1]}.",
            "tanglish": f"Practical Pariharam: {dasa_info['bhukti_end']} varaikum irukkara {dasa_info['bhukti']['tanglish']} Bhukti (H{bhukti_h}) smooth-aa poga {act[2]} podhum.",
        }[lang]
    else:
        act = SIMPLE_PRACTICE.get(maha_key, SIMPLE_PRACTICE["Jupiter"])
        pariharam = {
            "ta": f"சிறப்பு பரிகாரம் தேவையில்லை: தசா ({maha_h}-ம் இடம்) & புத்தி ({bhukti_h}-ம் இடம்) நல்ல நிலையில் உள்ளன. {act[0]} தொடர்ந்தால் போதும்.",
            "en": f"No Heavy Remedy Needed: Both Dasa (H{maha_h}) and Bhukti (H{bhukti_h}) are well-placed. Continue {act[1]}.",
            "tanglish": f"Periya Pariharam Thevaiyilla: Dasa (H{maha_h}) & Bhukti (H{bhukti_h}) nalla irukku. Just {act[2]} continue pannunga podhum.",
        }[lang]

    return {
        "career": career,
        "wealth": wealth,
        "family": family,
        "dasa_effect": dasa_effect,
        "pariharam": pariharam,
    }


def calculate_jathagam(
    name: str,
    dob: str,
    tob: str,
    lat: float = 13.0827,
    lon: float = 80.2707,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
    lang: str = "tanglish",
    gender: str = "unspecified",
    override_rasi_idx: Optional[int] = None,
    override_nak_idx: Optional[int] = None,
    override_lagnam_idx: Optional[int] = None,
) -> Dict[str, Any]:
    _set_ayanamsa(ayanamsa)
    jd_ut = _to_jd_ut(dob, tob, tz_offset)

    # Sidereal Ascendant (Lagnam)
    cusps, ascmc = swe.houses_ex(jd_ut, lat, lon, b"P", swe.FLG_SIDEREAL)
    asc_deg = ascmc[0] % 360.0
    asc_rasi_idx = override_lagnam_idx if override_lagnam_idx is not None else int(asc_deg // 30.0) % 12

    grahas: List[Dict[str, Any]] = []
    nak_span = 360.0 / 27.0

    def build_entry(key: str, deg: float, retro: bool = False, force_rasi: Optional[int] = None, force_nak: Optional[int] = None) -> Dict[str, Any]:
        r_idx = force_rasi if force_rasi is not None else int(deg // 30.0) % 12
        deg_in_rasi = deg % 30.0
        n_idx = force_nak if force_nak is not None else int(deg // nak_span) % 27
        pada = int((deg % nak_span) // (nak_span / 4.0)) + 1
        d9_idx = _navamsam_rasi(deg)
        gl = GRAHA_LABELS[key]
        return {
            "key": key,
            "short": gl.get(lang, gl["en"]),
            "name": gl.get(f"full_{lang}", gl["full_en"]),
            "degree": round(deg_in_rasi, 2),
            "rasi_idx": r_idx,
            "rasi_name": RASIS[r_idx].get(lang, RASIS[r_idx]["en"]),
            "navamsam_idx": d9_idx,
            "navamsam_name": RASIS[d9_idx].get(lang, RASIS[d9_idx]["en"]),
            "nakshatram_idx": n_idx,
            "nakshatram_name": NAKSHATRAMS[n_idx].get(lang, NAKSHATRAMS[n_idx]["en"]),
            "pada": pada,
            "retrograde": retro,
        }

    grahas.append(build_entry("Ascendant", asc_deg, False, force_rasi=asc_rasi_idx))

    sun_deg = 0.0
    moon_deg = 0.0
    rahu_deg = 0.0
    mars_rasi_idx = 0
    for pname, pid in PLANETS:
        res = swe.calc_ut(jd_ut, pid, swe.FLG_SIDEREAL | swe.FLG_SPEED)[0]
        lon_deg = res[0] % 360.0
        speed = res[3]
        retro = speed < 0 and pname != "Rahu"
        if pname == "Sun":
            sun_deg = lon_deg
        if pname == "Moon":
            moon_deg = lon_deg
            grahas.append(build_entry(pname, lon_deg, retro, force_rasi=override_rasi_idx, force_nak=override_nak_idx))
        else:
            if pname == "Rahu":
                rahu_deg = lon_deg
            if pname == "Mars":
                mars_rasi_idx = int(lon_deg // 30.0) % 12
            grahas.append(build_entry(pname, lon_deg, retro))

    ketu_deg = (rahu_deg + 180.0) % 360.0
    grahas.append(build_entry("Ketu", ketu_deg, True))

    moon_entry = next(g for g in grahas if g["key"] == "Moon")
    asc_entry = next(g for g in grahas if g["key"] == "Ascendant")

    # Borderline check (±1 deg of Rasi or Nakshatram boundary)
    moon_deg_in_rasi = moon_deg % 30.0
    asc_deg_in_rasi = asc_deg % 30.0
    borderline_alert = (
        moon_deg_in_rasi < 1.0 or moon_deg_in_rasi > 29.0 or asc_deg_in_rasi < 1.0 or asc_deg_in_rasi > 29.0
    )

    age_years = max(0, int((dt.datetime.now() - dt.datetime.strptime(dob, "%Y-%m-%d")).days // 365.2425))
    dasa_info = _compute_vimshottari_dasa(moon_deg, dob)
    maha_key = dasa_info["maha_dasa"]["key"]
    pulipani_palangal = _compute_pulipani_palangal(asc_entry["rasi_idx"], grahas, dasa_info, age_years, lang)
    pulipani_msg = pulipani_palangal["dasa_effect"]

    # Simple Sevvai Dosham indicator (Mars in 2, 4, 7, 8, 12 from Lagnam)
    mars_house = ((mars_rasi_idx - asc_entry["rasi_idx"]) % 12) + 1
    sevvai_dosham = mars_house in (2, 4, 7, 8, 12)

    return {
        "name": name,
        "gender": gender,
        "dob": dob,
        "age": age_years,
        "tob": tob,
        "ayanamsa": ayanamsa,
        "birth_is_valarpirai": ((moon_deg - sun_deg) % 360.0) < 180.0,
        "lagnam": {"idx": asc_entry["rasi_idx"], "name": asc_entry["rasi_name"]},
        "rasi": {"idx": moon_entry["rasi_idx"], "name": moon_entry["rasi_name"]},
        "nakshatram": {
            "idx": moon_entry["nakshatram_idx"],
            "name": moon_entry["nakshatram_name"],
            "pada": moon_entry["pada"],
        },
        "grahas": grahas,
        "dasa": {
            "maha": dasa_info["maha_dasa"].get(lang, dasa_info["maha_dasa"]["en"]),
            "maha_key": maha_key,
            "bhukti": dasa_info["bhukti"].get(lang, dasa_info["bhukti"]["en"]),
            "bhukti_key": dasa_info["bhukti"]["key"],
            "anthar": dasa_info["anthar"].get(lang, dasa_info["anthar"]["en"]),
            "anthar_key": dasa_info["anthar"]["key"],
            "years_remaining": dasa_info["years_remaining"],
            "maha_end": dasa_info["maha_end"],
            "bhukti_end": dasa_info["bhukti_end"],
            "anthar_end": dasa_info["anthar_end"],
        },
        "pulipani_insight": pulipani_msg,
        "pulipani_palangal": pulipani_palangal,
        "sevvai_dosham": sevvai_dosham,
        "borderline_alert": borderline_alert,
        "manual_override_applied": any(v is not None for v in (override_rasi_idx, override_nak_idx, override_lagnam_idx)),
    }


def generate_8_digit_code(existing_codes: set[str]) -> str:
    while True:
        num = random.randint(10000000, 99999999)
        code = str(num)
        if code not in existing_codes:
            return code


def calculate_porutham(
    bride_nak_idx: int,
    bride_rasi_idx: int,
    groom_nak_idx: int,
    groom_rasi_idx: int,
    lang: str = "tanglish",
) -> Dict[str, Any]:
    b_nak = NAKSHATRAMS[bride_nak_idx % 27]
    g_nak = NAKSHATRAMS[groom_nak_idx % 27]

    # Count from Bride's Nakshatram to Groom's Nakshatram (1..27)
    count_nak = ((groom_nak_idx - bride_nak_idx) % 27) + 1
    # Count from Bride's Rasi to Groom's Rasi (1..12)
    count_rasi = ((groom_rasi_idx - bride_rasi_idx) % 12) + 1

    # 1. Dina Porutham
    dina_ok = (count_nak % 9) in (2, 4, 6, 8, 0) or count_nak == 27
    # 2. Gana Porutham (0=Deva, 1=Manushya, 2=Rakshasa)
    gana_ok = (b_nak["gana"] == g_nak["gana"]) or (b_nak["gana"] == 0 and g_nak["gana"] == 1) or (g_nak["gana"] == 0 and b_nak["gana"] == 1)
    # 3. Mahendra Porutham
    mahendra_ok = count_nak in (4, 7, 10, 13, 16, 19, 22, 25)
    # 4. Stree Deergha Porutham
    stree_ok = count_nak > 13
    # 5. Yoni Porutham (different or friendly animal groups)
    yoni_ok = b_nak["yoni"] == g_nak["yoni"] or abs(b_nak["yoni"] - g_nak["yoni"]) not in (3, 7)
    # 6. Rasi Porutham
    rasi_ok = count_rasi not in (2, 5, 6, 8, 12)
    # 7. Rasiyathipathi Porutham (Rasi lords same or non-hostile)
    b_lord = RASIS[bride_rasi_idx % 12]["lord"]
    g_lord = RASIS[groom_rasi_idx % 12]["lord"]
    rasi_lord_ok = (b_lord == g_lord) or not ({b_lord, g_lord} in ({"Sun", "Saturn"}, {"Sun", "Venus"}, {"Moon", "Mercury"}))
    # 8. Vasya Porutham
    vasya_ok = count_rasi in (1, 2, 4, 5, 7, 9, 10, 11)
    # 9. Rajju Porutham (CRITICAL: Must NOT share the same Rajju!)
    rajju_ok = b_nak["rajju"] != g_nak["rajju"]
    # 10. Vedhai Porutham (Mutually incompatible pairs)
    vedhai_pairs = {(0, 17), (1, 16), (2, 15), (3, 14), (5, 21), (6, 20), (7, 19), (8, 18), (9, 26), (10, 25), (11, 24), (12, 23)}
    pair = tuple(sorted((bride_nak_idx % 27, groom_nak_idx % 27)))
    vedhai_ok = pair not in vedhai_pairs

    items = [
        ("Dina", "தினப் பொருத்தம்", "Dina (Health & Longevity)", "Dina (Health & Daily Harmony)", dina_ok),
        ("Gana", "கணப் பொருத்தம்", "Gana (Temperament)", "Gana (Vibe & Temperament)", gana_ok),
        ("Mahendra", "மகேந்திரப் பொருத்தம்", "Mahendra (Progeny & Growth)", "Mahendra (Family Growth)", mahendra_ok),
        ("Stree Deergha", "ஸ்திரீ தீர்க்கம்", "Stree Deergha (Prosperity)", "Stree Deergha (Prosperity)", stree_ok),
        ("Yoni", "யோனிப் பொருத்தம்", "Yoni (Intimacy & Bonding)", "Yoni (Physical & Emotional Bond)", yoni_ok),
        ("Rasi", "ராசிப் பொருத்தம்", "Rasi (Compatibility)", "Rasi (Life Alignment)", rasi_ok),
        ("Rasiyathipathi", "ராசியதிபதி", "Rasiyathipathi (Planetary Harmony)", "Rasiyathipathi (Mental Peace)", rasi_lord_ok),
        ("Vasya", "வசியப் பொருத்தம்", "Vasya (Mutual Attraction)", "Vasya (Mutual Attraction)", vasya_ok),
        ("Rajju", "ரஜ்ஜுப் பொருத்தம் (முக்கியம்)", "Rajju (Critical Longevity)", "Rajju (Most Important)", rajju_ok),
        ("Vedhai", "வேதைப் பொருத்தம் (முக்கியம்)", "Vedhai (Obstacle Check)", "Vedhai (Obstacle Check)", vedhai_ok),
    ]

    score = sum(1 for item in items if item[4])
    formatted_items = [
        {
            "key": k,
            "label": ta if lang == "ta" else en if lang == "en" else tg,
            "passed": ok,
            "critical": k in ("Rajju", "Vedhai"),
        }
        for k, ta, en, tg, ok in items
    ]

    if not rajju_ok or not vedhai_ok:
        verdict = {
            "ta": f"{score}/10 பொருத்தம் — ரஜ்ஜு/வேதை கவனம் தேவை. மூத்த ஜோதிடரிடம் சரிபார்க்கவும்.",
            "en": f"{score}/10 Match — Critical Rajju/Vedhai alert. Consult a Senior Jothidar before finalizing.",
            "tanglish": f"{score}/10 Porutham — Rajju/Vedhai warning irukku! Finalize pannum munnadi Senior Jothidar-kitta check pannunga.",
        }[lang]
        status = "caution"
    elif score >= 7:
        verdict = {
            "ta": f"{score}/10 சிறந்த பொருத்தம்! திருமணத்திற்கு மிகவும் உகந்தது.",
            "en": f"{score}/10 Excellent Match! Strong compatibility across key factors.",
            "tanglish": f"{score}/10 Semma Match! Kalyana porutham romba strong-aa irukku.",
        }[lang]
        status = "excellent"
    elif score >= 5:
        verdict = {
            "ta": f"{score}/10 நடுத்தர பொருத்தம். தசா சந்தி மற்றும் தோஷம் சரிபார்ப்பது நலம்.",
            "en": f"{score}/10 Moderate Match. Verify Dasa Sandhi and Sevvai Dosham before proceeding.",
            "tanglish": f"{score}/10 Decent Match. Dasa Sandhi & Dosham check pannittu proceed pannalam.",
        }[lang]
        status = "moderate"
    else:
        verdict = {
            "ta": f"{score}/10 குறைவான பொருத்தம். மாற்று வரன் அல்லது ஜோதிட ஆலோசனை நலம்.",
            "en": f"{score}/10 Low Match. Deeper chart verification is recommended.",
            "tanglish": f"{score}/10 Kammiyaana Porutham. Senior Jothidar-kitta deep check pannuradhu nalladhu.",
        }[lang]
        status = "low"

    return {
        "score": score,
        "total": 10,
        "status": status,
        "rajju_ok": rajju_ok,
        "vedhai_ok": vedhai_ok,
        "verdict": verdict,
        "items": formatted_items,
    }


async def ask_personal_jothidar(
    question: str,
    chart: Optional[Dict[str, Any]],
    panchangam: Optional[Dict[str, Any]],
    lang: str = "tanglish",
) -> Dict[str, Any]:
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    deepseek_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    provider = os.getenv("LLM_PROVIDER", "").strip().lower()

    chart_summary = ""
    if chart:
        chart_summary = (
            f"User: {chart.get('name', 'Friend')}, Age: {chart.get('age', '')}, "
            f"Lagnam: {chart.get('lagnam', {}).get('name')}, "
            f"Rasi: {chart.get('rasi', {}).get('name')}, Nakshatram: {chart.get('nakshatram', {}).get('name')}, "
            f"Maha Dasa: {chart.get('dasa', {}).get('maha')} (till {chart.get('dasa', {}).get('maha_end')}), "
            f"Bhukti: {chart.get('dasa', {}).get('bhukti')} (till {chart.get('dasa', {}).get('bhukti_end')}), "
            f"Sevvai Dosham: {chart.get('sevvai_dosham')}."
        )
    patchi_summary = ""
    if panchangam and panchangam.get("pancha_patchi"):
        pp = panchangam["pancha_patchi"]
        patchi_summary = f"Pancha Patchi Bird: {pp['bird']['name']}, Current State: {pp['current']['label']}."

    lang_instruction = (
        "Respond in simple, everyday, grammatically accurate Tamil script (எளிய இயல்பான தமிழ்) with zero spelling mistakes. "
        "Use exact Tamil spellings: ஞாயிறு, திங்கள், செவ்வாய், புதன், வியாழன், வெள்ளி, சனி, சந்நிதி, கோவில், பரிகாரம், "
        "தசை, புத்தி, அந்தரம், தசா சந்தி, நவாம்சம், லக்னம், ராசி, நட்சத்திரம், பஞ்ச பட்சி, சந்திராஷ்டமம், புலிப்பாணி சித்தர். "
        "Avoid rare or archaic words; keep sentences short and natural."
        if lang == "ta"
        else "Respond in warm, clear English with Tamil astrology terms explained."
        if lang == "en"
        else "Respond in natural, friendly Tanglish (Tamil written in English letters) like a caring personal Tamil astrologer."
    )
    system_prompt = (
        f"You are 'Enathu Jothidar' (Personal Tamil Astrologer) trained in Pulipani Siddhar Jothidam and Pancha Patchi Saasthiram. "
        f"{lang_instruction} Do NOT use markdown bold/italics (no ** or * or #). "
        f"Keep your answer concise (4-5 sentences), practical, age-appropriate, and grounded ONLY in this chart & Pancha Patchi:\n"
        f"{chart_summary}\n{patchi_summary}"
    )

    if deepseek_key and (provider == "deepseek" or not gemini_key):
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    "https://api.deepseek.com/chat/completions",
                    headers={"Authorization": f"Bearer {deepseek_key}", "Content-Type": "application/json"},
                    json={
                        "model": "deepseek-chat",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": question},
                        ],
                        "temperature": 0.3,
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    text = data["choices"][0]["message"]["content"]
                    text = text.replace("**", "").replace("__", "").replace("### ", "").replace("## ", "")
                    return {"answer": text, "source": "deepseek"}
        except Exception:
            pass

    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    url,
                    json={"contents": [{"parts": [{"text": f"{system_prompt}\nUser Question: {question}"}]}]},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    text = text.replace("**", "").replace("__", "").replace("### ", "").replace("## ", "")
                    return {"answer": text, "source": "gemini"}
        except Exception:
            pass

    # Built-in Pulipani Siddhar + Pancha Patchi chart-aware fallback (works 100% offline/free)
    q_low = question.lower()
    name = chart.get("name", "Nanba") if chart else "Nanba"
    rasi = chart.get("rasi", {}).get("name", "Mesham") if chart else "your Rasi"
    nak = chart.get("nakshatram", {}).get("name", "Rohini") if chart else "your Nakshatram"
    dasa = chart.get("dasa", {}).get("maha", "Guru") if chart else "current Dasa"
    pulipani = chart.get("pulipani_insight", "") if chart else ""
    patchi_cur = panchangam["pancha_patchi"]["current"] if panchangam else None
    bird_name = panchangam["pancha_patchi"]["bird"]["name"] if panchangam else "Mayil"

    if any(w in q_low for w in ["job", "career", "work", "business", "money", "velai", "பணி", "வேலை", "தொழில்"]):
        ans = {
            "ta": f"{name}, உங்கள் {rasi} ராசி மற்றும் {nak} நட்சத்திரப்படி இப்போது {dasa} தசை நடக்கிறது. {pulipani} இன்று உங்கள் {bird_name} பட்சி '{patchi_cur['label'] if patchi_cur else 'நல்ல'}' நிலையில் உள்ளதால், முக்கிய வேலைகளை அரசு/ஊண் நேரத்தில் தொடங்குங்கள்.",
            "en": f"{name}, for your {rasi} Rasi and {nak} star, you are currently in {dasa} Dasa. {pulipani} With your {bird_name} bird in '{patchi_cur['label'] if patchi_cur else 'active'}' state right now, schedule key career calls during your Arasu window.",
            "tanglish": f"{name}, unga {rasi} Rasi & {nak} star padi ippo {dasa} Dasa nadakkudhu. {pulipani} Ippo unga {bird_name} patchi '{patchi_cur['label'] if patchi_cur else 'active'}' state-la irukku — important job/business calls-a Arasu/Oon window-la pannunga!",
        }[lang]
    elif any(w in q_low for w in ["love", "marriage", "kalyanam", "partner", "porutham", "திருமணம்", "காதல்"]):
        dosham_note = (
            ("செவ்வாய் தோஷ அமைப்பு உள்ளதால் சரியான பொருத்தம் பார்ப்பது நல்லது." if lang == "ta" else "Since Sevvai Dosham is indicated, verify 10-Porutham carefully." if lang == "en" else "Sevvai Dosham indicator irukkuradhala 10-Porutham & Rajju check pannittu move pannunga.")
            if (chart and chart.get("sevvai_dosham"))
            else ("பொருத்தம் பார்க்கும்போது ரஜ்ஜு மற்றும் தசா சந்தி முக்கியம்." if lang == "ta" else "Focus on Rajju and Dasa Sandhi when matching." if lang == "en" else "Porutham paakkumbodhu Rajju & Dasa Sandhi strong-aa irundha podhum!")
        )
        ans = {
            "ta": f"{name}, உங்கள் {dasa} தசையில் உறவு மற்றும் திருமண விஷயங்களில் தெளிவு கிடைக்கும். {dosham_note} Porutham பகுதியில் உங்கள் 8-இலக்க குறியீட்டைப் பகிர்ந்து உடனே சரிபார்க்கலாம்.",
            "en": f"{name}, your {dasa} Dasa shapes relationship clarity. {dosham_note} Use your 8-digit Jathagam Code in the Porutham tab to check compatibility instantly.",
            "tanglish": f"{name}, ippo {dasa} Dasa nadakkuradhala relationship & marriage clarity nalla irukkum. {dosham_note} Unga 8-digit Jathagam Code-a Porutham tab-la use panni instant-aa match check pannikkalam.",
        }[lang]
    else:
        ans = {
            "ta": f"வணக்கம் {name}! உங்கள் {rasi} ராசி ({nak}) மற்றும் {dasa} தசைப்படி: {pulipani} இப்போது உங்கள் பஞ்ச பட்சி ({bird_name}) '{patchi_cur['label'] if patchi_cur else ''}' நிலையில் உள்ளது — {patchi_cur['advice'] if patchi_cur else ''}",
            "en": f"Vanakkam {name}! Based on your {rasi} Rasi ({nak}) and {dasa} Dasa: {pulipani} Right now your {bird_name} bird is in '{patchi_cur['label'] if patchi_cur else ''}' — {patchi_cur['advice'] if patchi_cur else ''}",
            "tanglish": f"Vanakkam {name}! Unga {rasi} Rasi ({nak}) & {dasa} Dasa padi: {pulipani} Ippo unga {bird_name} patchi '{patchi_cur['label'] if patchi_cur else ''}'-la irukku — {patchi_cur['advice'] if patchi_cur else ''}",
        }[lang]

    return {"answer": ans, "source": "pulipani_engine"}


GOAL_META = {
    "career": {
        "house": 10,
        "karakas": ("Sun", "Saturn"),
        "friendly_dasas": ("Sun", "Saturn", "Jupiter", "Mercury", "Mars"),
        "ta": "தொழில் / வேலை உயர்வு",
        "en": "Career / Job Growth",
        "tanglish": "Career / Job Switch",
    },
    "business": {
        "house": 11,
        "karakas": ("Mercury", "Jupiter"),
        "friendly_dasas": ("Mercury", "Jupiter", "Venus", "Rahu", "Sun"),
        "ta": "வியாபாரம் / வருமானம்",
        "en": "Business / Startup & Income",
        "tanglish": "Business / Money Goal",
    },
    "marriage": {
        "house": 7,
        "karakas": ("Venus", "Jupiter"),
        "friendly_dasas": ("Venus", "Jupiter", "Moon", "Mercury"),
        "ta": "திருமணம் / உறவு",
        "en": "Marriage / Relationship",
        "tanglish": "Marriage / Relationship",
    },
    "property": {
        "house": 4,
        "karakas": ("Mars", "Venus"),
        "friendly_dasas": ("Mars", "Venus", "Jupiter", "Saturn"),
        "ta": "வீடு / நிலம் / வாகனம்",
        "en": "Home / Property / Vehicle",
        "tanglish": "House / Property / Vehicle",
    },
    "abroad": {
        "house": 9,
        "karakas": ("Rahu", "Jupiter"),
        "friendly_dasas": ("Rahu", "Jupiter", "Venus", "Moon", "Mercury"),
        "ta": "வெளிநாடு / உயர்கல்வி",
        "en": "Abroad / Higher Studies / Visa",
        "tanglish": "Abroad / Visa / Studies",
    },
}


def check_goal_alignment(
    goal_key: str,
    step_desc: str,
    chart: Optional[Dict[str, Any]],
    panchangam: Optional[Dict[str, Any]],
    lang: str = "tanglish",
) -> Dict[str, Any]:
    meta = GOAL_META.get(goal_key, GOAL_META["career"])
    score = 55

    lagnam_idx = chart.get("lagnam", {}).get("idx", 0) if chart else 0
    grahas = chart.get("grahas", []) if chart else []
    pos = {g["key"]: ((g["rasi_idx"] - lagnam_idx) % 12) + 1 for g in grahas}

    maha_key = chart.get("dasa", {}).get("maha_key", "Jupiter") if chart else "Jupiter"
    maha_name = chart.get("dasa", {}).get("maha", maha_key) if chart else maha_key
    maha_end = chart.get("dasa", {}).get("maha_end", "") if chart else ""

    # 1. Long-term Dasa + Natal Karaka check
    dasa_aligned = maha_key in meta["friendly_dasas"]
    if dasa_aligned:
        score += 18

    karaka_good = any(pos.get(k, 6) in (1, 2, 4, 5, 7, 9, 10, 11) for k in meta["karakas"])
    if karaka_good:
        score += 12

    # 2. Today's Timing (Pancha Patchi + Tara Balam + Chandrashtamam)
    pp = panchangam.get("pancha_patchi", {}) if panchangam else {}
    cur_state = pp.get("current", {}).get("state", "Nadai")
    next_best = pp.get("next_best", {})
    tara_good = panchangam.get("personal_palan", {}).get("tara_balam", {}).get("good", True) if panchangam else True
    is_chandra = panchangam.get("is_user_chandrashtamam", False) if panchangam else False

    if cur_state in ("Arasu", "Oon"):
        score += 12
    elif cur_state == "Saavu":
        score -= 15

    if tara_good:
        score += 5
    if is_chandra:
        score -= 18

    score = max(20, min(96, score))

    if score >= 75:
        verdict_code = "go"
        verdict_label = {"ta": "இப்போது தொடங்கலாம் (GO AHEAD)", "en": "GO AHEAD — Strong Alignment", "tanglish": "GO AHEAD — Strong Match!"}[lang]
    elif score >= 52:
        verdict_code = "time_it"
        verdict_label = {"ta": "நல்ல நேரத்தில் செய்யவும் (TIME IT)", "en": "PREPARE & TIME IT", "tanglish": "PREPARE & TIME IT"}[lang]
    else:
        verdict_code = "wait"
        verdict_label = {"ta": "சற்று பொறுமை தேவை (WAIT)", "en": "WAIT & REFINE PLAN", "tanglish": "KONJAM WAIT PANNUNGA"}[lang]

    goal_name = meta.get(lang, meta["en"])
    step_text = f"'{step_desc}' " if step_desc.strip() else ""

    long_term = {
        "ta": (
            f"உங்கள் '{goal_name}' இலக்கிற்கு நடப்பு {maha_name} தசை ({maha_end} வரை) மற்றும் {meta['house']}-ம் இட பலம் "
            + ("நல்ல ஆதரவு தருகிறது." if dasa_aligned else "பொறுமையான திட்டமிடலைக் கோருகிறது.")
        ),
        "en": (
            f"For your '{goal_name}' goal, your active {maha_name} Dasa (till {maha_end}) and House {meta['house']} placement "
            + ("strongly support steady progress." if dasa_aligned else "reward patience and structured preparation.")
        ),
        "tanglish": (
            f"Unga '{goal_name}' goal-ku ippo nadakkura {maha_name} Dasa (till {maha_end}) & House {meta['house']} "
            + ("nalla support kudukkudhu." if dasa_aligned else "konjam patience & careful planning ketkudhu.")
        ),
    }[lang]

    best_win = f"{next_best.get('start', '')} – {next_best.get('end', '')}" if next_best else ""
    today_timing = {
        "ta": (
            f"இன்று {step_text}முயற்சியை எடுக்க: இப்போது பஞ்ச பட்சி '{cur_state}' நிலையில் உள்ளது. "
            + (f"சிறந்த அடுத்த நேரம்: {best_win}." if best_win else "")
        ),
        "en": (
            f"For taking {step_text}today: your Pancha Patchi is currently '{cur_state}'. "
            + (f"Best window to execute: {best_win}." if best_win else "")
        ),
        "tanglish": (
            f"Innaikku {step_text}step edukkanum-na: ippo Pancha Patchi '{cur_state}'-la irukku. "
            + (f"Best time to act: {best_win}." if best_win else "")
        ),
    }[lang]

    return {
        "goal": goal_name,
        "score": score,
        "verdict_code": verdict_code,
        "verdict_label": verdict_label,
        "long_term_reason": long_term,
        "today_step_timing": today_timing,
    }
