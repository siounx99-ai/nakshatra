"""FastAPI backend for Enathu Jothidar — Personal Tamil Horoscope, Pancha Patchi & Vedic Jothidam app."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

import httpx

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from astrology import (
    ask_personal_jothidar,
    calculate_jathagam,
    calculate_panchangam,
    calculate_porutham,
    check_goal_alignment,
    generate_8_digit_code,
)
from astrology_data import NAKSHATRAMS, RASIS

load_dotenv()

DATA_DIR = Path("/tmp/nakshatra_data") if os.getenv("VERCEL") else (Path(__file__).parent / "data")
DATA_DIR.mkdir(exist_ok=True)
CHARTS_FILE = DATA_DIR / "charts.json"
LEADS_FILE = DATA_DIR / "leads.json"
FIREBASE_KEY_FILE = Path(__file__).parent / "firebase-key.json"
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID", "nakshatra-65c02")

_firestore_db = None
try:
    import firebase_admin
    from firebase_admin import credentials, firestore

    if not firebase_admin._apps:
        creds_json_str = os.getenv("FIREBASE_CREDENTIALS_JSON", "").strip()
        if creds_json_str:
            cred = credentials.Certificate(json.loads(creds_json_str))
            firebase_admin.initialize_app(cred, {"projectId": FIREBASE_PROJECT_ID})
            _firestore_db = firestore.client()
        elif FIREBASE_KEY_FILE.exists():
            cred = credentials.Certificate(str(FIREBASE_KEY_FILE))
            firebase_admin.initialize_app(cred, {"projectId": FIREBASE_PROJECT_ID})
            _firestore_db = firestore.client()
        elif os.getenv("K_SERVICE"):  # Running on Google Cloud Run
            firebase_admin.initialize_app(options={"projectId": FIREBASE_PROJECT_ID})
            _firestore_db = firestore.client()
except Exception:
    _firestore_db = None

app = FastAPI(title="Enathu Jothidar API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _save_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _get_chart(code: str) -> Optional[Dict[str, Any]]:
    if _firestore_db is not None:
        doc = _firestore_db.collection("charts").document(code).get()
        if doc.exists:
            return doc.to_dict()
    charts_db: Dict[str, Any] = _load_json(CHARTS_FILE, {})
    return charts_db.get(code)


def _save_chart(code: str, payload: Dict[str, Any]) -> None:
    if _firestore_db is not None:
        _firestore_db.collection("charts").document(code).set(payload)
        return
    charts_db: Dict[str, Any] = _load_json(CHARTS_FILE, {})
    charts_db[code] = payload
    _save_json(CHARTS_FILE, charts_db)


def _save_lead(payload: Dict[str, Any]) -> None:
    if _firestore_db is not None:
        _firestore_db.collection("leads").add(payload)
        return
    leads = _load_json(LEADS_FILE, [])
    leads.append(payload)
    _save_json(LEADS_FILE, leads)


class PanchangamRequest(BaseModel):
    date: Optional[str] = None
    lat: float = 13.0827
    lon: float = 80.2707
    tz_offset: float = 5.5
    lang: str = "tanglish"
    user_rasi_idx: Optional[int] = None
    user_nak_idx: Optional[int] = None
    user_lagnam_idx: Optional[int] = None
    user_age: Optional[int] = None
    user_dasa: Optional[Dict[str, Any]] = None
    natal_grahas: Optional[Dict[str, int]] = None
    birth_is_valarpirai: Optional[bool] = None
    ayanamsa: str = "lahiri"


class JathagamRequest(BaseModel):
    name: str = "Nanba"
    gender: str = "unspecified"
    dob: str = "1998-05-14"
    tob: str = "06:30"
    lat: float = 13.0827
    lon: float = 80.2707
    tz_offset: float = 5.5
    ayanamsa: str = "lahiri"
    lang: str = "tanglish"
    privacy_mode: bool = True
    existing_code: Optional[str] = None
    override_rasi_idx: Optional[int] = None
    override_nak_idx: Optional[int] = None
    override_lagnam_idx: Optional[int] = None


class PoruthamRequest(BaseModel):
    bride_nak_idx: Optional[int] = None
    bride_rasi_idx: Optional[int] = None
    groom_nak_idx: Optional[int] = None
    groom_rasi_idx: Optional[int] = None
    bride_code: Optional[str] = None
    groom_code: Optional[str] = None
    lang: str = "tanglish"


class AskJothidarRequest(BaseModel):
    question: str = Field(..., min_length=2)
    chart: Optional[Dict[str, Any]] = None
    panchangam: Optional[Dict[str, Any]] = None
    lang: str = "tanglish"


class LeadRequest(BaseModel):
    name: str
    phone: str
    email: Optional[str] = ""
    request_type: str = "full_jathagam_pdf"
    notes: Optional[str] = ""
    chart_code: Optional[str] = ""


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "engine": "pyswisseph + Tamil Vedic Jothidam + Pancha Patchi",
        "storage": "firestore" if _firestore_db is not None else "local_json",
    }


@app.get("/api/meta")
def get_meta(lang: str = "tanglish"):
    return {
        "rasis": [{"idx": r["idx"], "name": r.get(lang, r["en"])} for r in RASIS],
        "nakshatrams": [{"idx": n["idx"], "name": n.get(lang, n["en"])} for n in NAKSHATRAMS],
    }


@app.post("/api/panchangam")
def api_panchangam(req: PanchangamRequest):
    return calculate_panchangam(
        date_str=req.date,
        lat=req.lat,
        lon=req.lon,
        tz_offset=req.tz_offset,
        lang=req.lang,
        user_rasi_idx=req.user_rasi_idx,
        user_nak_idx=req.user_nak_idx,
        user_lagnam_idx=req.user_lagnam_idx,
        user_age=req.user_age,
        user_dasa=req.user_dasa,
        natal_grahas=req.natal_grahas,
        birth_is_valarpirai=req.birth_is_valarpirai,
        ayanamsa=req.ayanamsa,
    )


@app.post("/api/jathagam")
def api_jathagam(req: JathagamRequest):
    chart = calculate_jathagam(
        name=req.name,
        dob=req.dob,
        tob=req.tob,
        lat=req.lat,
        lon=req.lon,
        tz_offset=req.tz_offset,
        ayanamsa=req.ayanamsa,
        lang=req.lang,
        gender=req.gender,
        override_rasi_idx=req.override_rasi_idx,
        override_nak_idx=req.override_nak_idx,
        override_lagnam_idx=req.override_lagnam_idx,
    )

    clean_existing = req.existing_code.replace("-", "").strip() if req.existing_code else None
    code = clean_existing if (clean_existing and _get_chart(clean_existing) is not None) else generate_8_digit_code(set())
    _save_chart(
        code,
        {
            "code": code,
            "display_name": (req.name[:1] + "***" if req.privacy_mode and len(req.name) > 1 else req.name),
            "full_name": req.name,
            "privacy_mode": req.privacy_mode,
            "rasi_idx": chart["rasi"]["idx"],
            "nak_idx": chart["nakshatram"]["idx"],
            "pada": chart["nakshatram"]["pada"],
            "lagnam_idx": chart["lagnam"]["idx"],
            "sevvai_dosham": chart["sevvai_dosham"],
            "dasa_maha": chart["dasa"]["maha_key"],
        },
    )

    chart["code"] = code
    chart["privacy_mode"] = req.privacy_mode
    return chart


@app.get("/api/chart/{code}")
def api_get_chart_by_code(code: str, lang: str = "tanglish"):
    clean_code = code.replace("-", "").strip()
    entry = _get_chart(clean_code)
    if not entry:
        raise HTTPException(status_code=404, detail="8-digit Jathagam code not found")

    r_idx = entry["rasi_idx"]
    n_idx = entry["nak_idx"]
    return {
        "code": clean_code,
        "display_name": entry["display_name"] if entry.get("privacy_mode", True) else entry["full_name"],
        "privacy_mode": entry.get("privacy_mode", True),
        "rasi_idx": r_idx,
        "rasi_name": RASIS[r_idx].get(lang, RASIS[r_idx]["en"]),
        "nak_idx": n_idx,
        "nak_name": NAKSHATRAMS[n_idx].get(lang, NAKSHATRAMS[n_idx]["en"]),
        "pada": entry["pada"],
        "sevvai_dosham": entry["sevvai_dosham"],
    }


@app.post("/api/porutham")
def api_porutham(req: PoruthamRequest):
    b_nak, b_rasi = req.bride_nak_idx, req.bride_rasi_idx
    g_nak, g_rasi = req.groom_nak_idx, req.groom_rasi_idx
    bride_label = None
    groom_label = None

    if req.bride_code:
        c = req.bride_code.replace("-", "").strip()
        b_entry = _get_chart(c)
        if not b_entry:
            raise HTTPException(status_code=404, detail=f"Bride code {req.bride_code} not found")
        b_nak = b_entry["nak_idx"]
        b_rasi = b_entry["rasi_idx"]
        bride_label = b_entry["display_name"]

    if req.groom_code:
        c = req.groom_code.replace("-", "").strip()
        g_entry = _get_chart(c)
        if not g_entry:
            raise HTTPException(status_code=404, detail=f"Groom code {req.groom_code} not found")
        g_nak = g_entry["nak_idx"]
        g_rasi = g_entry["rasi_idx"]
        groom_label = g_entry["display_name"]

    if b_nak is None or b_rasi is None or g_nak is None or g_rasi is None:
        raise HTTPException(status_code=400, detail="Provide both Bride and Groom Rasi/Nakshatram or valid 8-digit codes")

    result = calculate_porutham(b_nak, b_rasi, g_nak, g_rasi, lang=req.lang)
    result["bride_label"] = bride_label
    result["groom_label"] = groom_label
    return result


class GoalCheckRequest(BaseModel):
    goal_key: str = "career"
    step_desc: str = ""
    chart: Optional[Dict[str, Any]] = None
    panchangam: Optional[Dict[str, Any]] = None
    lang: str = "tanglish"


@app.post("/api/goal-check")
def api_goal_check(req: GoalCheckRequest):
    return check_goal_alignment(req.goal_key, req.step_desc, req.chart, req.panchangam, lang=req.lang)


@app.post("/api/ask-jothidar")
async def api_ask_jothidar(req: AskJothidarRequest):
    return await ask_personal_jothidar(req.question, req.chart, req.panchangam, lang=req.lang)


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    name: str
    phone: str
    request_type: str = "detailed_report_pdf"
    notes: str = ""
    chart_code: str = ""


@app.post("/api/leads")
def api_save_lead(req: LeadRequest):
    _save_lead(req.model_dump())
    return {"status": "saved", "message": "Request received! Our Tamil Jothidar team will reach out on WhatsApp."}


@app.post("/api/payment/create-order")
async def api_create_razorpay_order(req: LeadRequest):
    key_id = os.getenv("RAZORPAY_KEY_ID", "").strip()
    key_secret = os.getenv("RAZORPAY_KEY_SECRET", "").strip()
    if not key_id or not key_secret:
        return {"configured": False}

    amount_paise = 9900  # ₹99 fixed server-side
    receipt = f"nak_{int(time.time())}"
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                "https://api.razorpay.com/v1/orders",
                auth=(key_id, key_secret),
                json={
                    "amount": amount_paise,
                    "currency": "INR",
                    "receipt": receipt,
                    "notes": {
                        "name": req.name[:80],
                        "phone": req.phone[:30],
                        "request_type": req.request_type[:40],
                        "chart_code": req.chart_code[:20],
                    },
                },
            )
        if resp.status_code not in (200, 201):
            raise HTTPException(status_code=502, detail=f"Razorpay order error: {resp.text}")
        order = resp.json()
        return {
            "configured": True,
            "order_id": order["id"],
            "amount": order["amount"],
            "currency": order.get("currency", "INR"),
            "key_id": key_id,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Razorpay connection error: {type(exc).__name__}")


@app.post("/api/payment/verify")
def api_verify_razorpay_payment(req: VerifyPaymentRequest):
    key_secret = os.getenv("RAZORPAY_KEY_SECRET", "").strip()
    if not key_secret:
        raise HTTPException(status_code=500, detail="Razorpay secret not configured")

    payload = f"{req.razorpay_order_id}|{req.razorpay_payment_id}".encode("utf-8")
    expected = hmac.new(key_secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, req.razorpay_signature):
        raise HTTPException(status_code=400, detail="Invalid payment signature")

    _save_lead({
        "name": req.name,
        "phone": req.phone,
        "request_type": req.request_type,
        "notes": req.notes,
        "chart_code": req.chart_code,
        "payment_status": "paid",
        "amount_inr": 99,
        "razorpay_order_id": req.razorpay_order_id,
        "razorpay_payment_id": req.razorpay_payment_id,
        "paid_at_epoch": int(time.time()),
    })
    return {"verified": True, "payment_id": req.razorpay_payment_id}
