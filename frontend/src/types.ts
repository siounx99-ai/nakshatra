export type Lang = 'ta' | 'en' | 'tanglish';
export type TabId = 'today' | 'jathagam' | 'porutham' | 'ask';

export interface CityPreset {
  label: string;
  lat: number;
  lon: number;
  tz: number;
}

export const CITIES: CityPreset[] = [
  { label: 'Chennai', lat: 13.0827, lon: 80.2707, tz: 5.5 },
  { label: 'Madurai', lat: 9.9252, lon: 78.1198, tz: 5.5 },
  { label: 'Coimbatore', lat: 11.0168, lon: 76.9558, tz: 5.5 },
  { label: 'Trichy', lat: 10.7905, lon: 78.7047, tz: 5.5 },
  { label: 'Salem', lat: 11.6643, lon: 78.146, tz: 5.5 },
  { label: 'Tirunelveli', lat: 8.7139, lon: 77.7567, tz: 5.5 },
  { label: 'Erode', lat: 11.341, lon: 77.7172, tz: 5.5 },
  { label: 'Vellore', lat: 12.9165, lon: 79.1325, tz: 5.5 },
  { label: 'Thanjavur', lat: 10.787, lon: 79.1378, tz: 5.5 },
  { label: 'Kumbakonam', lat: 10.9602, lon: 79.3845, tz: 5.5 },
  { label: 'Dindigul', lat: 10.3624, lon: 77.9695, tz: 5.5 },
  { label: 'Thoothukudi', lat: 8.7642, lon: 78.1348, tz: 5.5 },
  { label: 'Nagercoil', lat: 8.1833, lon: 77.4119, tz: 5.5 },
  { label: 'Karur', lat: 10.9601, lon: 78.0766, tz: 5.5 },
  { label: 'Puducherry', lat: 11.9416, lon: 79.8083, tz: 5.5 },
  { label: 'Cuddalore', lat: 11.748, lon: 79.7714, tz: 5.5 },
  { label: 'Tiruvannamalai', lat: 12.2253, lon: 79.0747, tz: 5.5 },
  { label: 'Hosur', lat: 12.7409, lon: 77.8253, tz: 5.5 },
  { label: 'Kanchipuram', lat: 12.8342, lon: 79.7036, tz: 5.5 },
  { label: 'Bengaluru', lat: 12.9716, lon: 77.5946, tz: 5.5 },
  { label: 'Jaffna (SL)', lat: 9.6615, lon: 80.0255, tz: 5.5 },
  { label: 'Singapore', lat: 1.3521, lon: 103.8198, tz: 8.0 },
  { label: 'Kuala Lumpur', lat: 3.139, lon: 101.6869, tz: 8.0 },
  { label: 'London', lat: 51.5072, lon: -0.1276, tz: 0.0 },
  { label: 'New York', lat: 40.7128, lon: -74.006, tz: -5.0 },
];

export interface SavedProfile {
  name: string;
  dob: string;
  tob: string;
  city: string;
  lat: number;
  lon: number;
  tz: number;
  ayanamsa: 'lahiri' | 'raman' | 'kp';
  privacyMode: boolean;
  code?: string;
  overrideRasiIdx?: number | null;
  overrideNakIdx?: number | null;
  overrideLagnamIdx?: number | null;
}

export interface GrahaItem {
  key: string;
  short: string;
  name: string;
  degree: number;
  rasi_idx: number;
  rasi_name: string;
  navamsam_idx: number;
  navamsam_name: string;
  nakshatram_idx: number;
  nakshatram_name: string;
  pada: number;
  retrograde: boolean;
}

export interface JathagamResponse {
  name: string;
  dob: string;
  age?: number;
  tob: string;
  ayanamsa: string;
  birth_is_valarpirai?: boolean;
  code: string;
  privacy_mode: boolean;
  lagnam: { idx: number; name: string };
  rasi: { idx: number; name: string };
  nakshatram: { idx: number; name: string; pada: number };
  grahas: GrahaItem[];
  dasa: {
    maha: string;
    maha_key: string;
    bhukti: string;
    bhukti_key?: string;
    anthar?: string;
    anthar_key?: string;
    years_remaining: number;
    maha_end?: string;
    bhukti_end?: string;
    anthar_end?: string;
  };
  pulipani_insight: string;
  pulipani_palangal?: {
    career: string;
    wealth: string;
    family: string;
    dasa_effect: string;
    pariharam: string;
  };
  sevvai_dosham: boolean;
  borderline_alert: boolean;
  manual_override_applied: boolean;
}

export interface PatchiJamam {
  jamam: number;
  period?: 'day' | 'night';
  start: string;
  end: string;
  state: string;
  label: string;
  advice: string;
  power: number;
  tone: string;
  is_current: boolean;
}

export interface PanchangamResponse {
  date: string;
  sunrise: string;
  sunset: string;
  nalla_neram: string;
  nalla_neram_evening: string;
  rahu_kalam: string;
  yemagandam: string;
  kuligai: string;
  nakshatram: { idx: number; name: string; pada: number };
  moon_rasi: { idx: number; name: string };
  thithi_number: number;
  is_valarpirai: boolean;
  chandrashtamam_rasi: { idx: number; name: string };
  is_user_chandrashtamam: boolean;
  pancha_patchi: {
    bird: { idx: number; emoji: string; name: string };
    paksham: string;
    is_valarpirai: boolean;
    current: PatchiJamam;
    next_jamam: PatchiJamam;
    next_arasu: PatchiJamam;
    next_best: PatchiJamam;
    timeline: PatchiJamam[];
    day_jamams: PatchiJamam[];
    night_jamams: PatchiJamam[];
  };
  personal_palan?: {
    primary_anchor: 'rasi' | 'lagnam';
    age: number;
    age_rule_note: string;
    dasa_summary?: string | null;
    transit_notes?: string[];
    tara_balam: { index: number; name: string; score: number; good: boolean; valid_from?: string; valid_till?: string };
    rasi_house: number;
    lagnam_house: number;
    primary_house: number;
    headline: string;
    action_advice: string;
    daily_details?: string[];
  } | null;
  rasi_palan: { idx: number; name: string; tone: string; is_chandrashtamam: boolean; summary: string }[];
}

export interface PoruthamResponse {
  score: number;
  total: number;
  status: string;
  rajju_ok: boolean;
  vedhai_ok: boolean;
  verdict: string;
  bride_label?: string | null;
  groom_label?: string | null;
  items: { key: string; label: string; passed: boolean; critical: boolean }[];
}
