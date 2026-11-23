import { useEffect, useState } from 'react';
import {
  AlertTriangle,
  Calendar,
  CheckCircle2,
  Compass,
  Copy,
  HeartHandshake,
  Lock,
  Moon,
  Send,
  Share2,
  Sparkles,
  Sun,
  UserCheck,
  X,
  XCircle,
} from 'lucide-react';
import { JothidamEmblem } from './components/JothidamEmblem';
import { SouthIndianChart } from './components/SouthIndianChart';
import { UI_COPY } from './i18n';
import {
  CITIES,
  type JathagamResponse,
  type Lang,
  type PanchangamResponse,
  type PoruthamResponse,
  type SavedProfile,
  type TabId,
} from './types';

const API_BASE = (import.meta.env.VITE_API_URL || '').replace(/\/+$/, '');

const DEFAULT_PROFILE: SavedProfile = {
  name: '',
  dob: '1998-05-14',
  tob: '06:30',
  city: 'Chennai',
  lat: 13.0827,
  lon: 80.2707,
  tz: 5.5,
  ayanamsa: 'lahiri',
  privacyMode: true,
};

interface MetaOption {
  idx: number;
  name: string;
}

interface ChatMsg {
  role: 'user' | 'jothidar';
  text: string;
}

export function App() {
  const [lang, setLang] = useState<Lang>(() => (localStorage.getItem('nk_lang') as Lang) || 'tanglish');
  const [ivoryTheme, setIvoryTheme] = useState<boolean>(() => localStorage.getItem('nk_theme') === 'ivory');
  const [isOnboarded, setIsOnboarded] = useState<boolean>(() => localStorage.getItem('nk_profile_onboarded') === '1');
  const [showSplash, setShowSplash] = useState<boolean>(true);
  const [splashFading, setSplashFading] = useState<boolean>(false);
  const [tab, setTab] = useState<TabId>('today');

  const [profile, setProfile] = useState<SavedProfile>(() => {
    try {
      const saved = localStorage.getItem('nk_profile');
      return saved ? JSON.parse(saved) : DEFAULT_PROFILE;
    } catch {
      return DEFAULT_PROFILE;
    }
  });

  const [rasis, setRasis] = useState<MetaOption[]>([]);
  const [nakshatrams, setNakshatrams] = useState<MetaOption[]>([]);
  const [panchangam, setPanchangam] = useState<PanchangamResponse | null>(null);
  const [jathagam, setJathagam] = useState<JathagamResponse | null>(null);
  const [selectedRasiIdx, setSelectedRasiIdx] = useState<number>(0);
  const [chartMode, setChartMode] = useState<'rasi' | 'navamsam'>('rasi');
  const [showAllJamams, setShowAllJamams] = useState(false);
  const [showOverride, setShowOverride] = useState(false);
  const [copiedCode, setCopiedCode] = useState(false);
  const [nowTime, setNowTime] = useState<Date>(() => new Date());

  // Porutham state
  const [brideNak, setBrideNak] = useState(3);
  const [brideRasi, setBrideRasi] = useState(1);
  const [groomNak, setGroomNak] = useState(10);
  const [groomRasi, setGroomRasi] = useState(4);
  const [brideCode, setBrideCode] = useState('');
  const [groomCode, setGroomCode] = useState('');
  const [porutham, setPorutham] = useState<PoruthamResponse | null>(null);
  const [poruthamErr, setPoruthamErr] = useState('');

  // Ask Jothidar Chat state
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [messages, setMessages] = useState<ChatMsg[]>([]);
  const [goalKey, setGoalKey] = useState('career');
  const [stepDesc, setStepDesc] = useState('');
  const [goalResult, setGoalResult] = useState<{
    goal: string;
    score: number;
    verdict_code: string;
    verdict_label: string;
    long_term_reason: string;
    today_step_timing: string;
  } | null>(null);

  // Lead Capture Modal
  const [leadModal, setLeadModal] = useState<{ open: boolean; type: string }>({ open: false, type: 'full_jathagam_pdf' });
  const [leadName, setLeadName] = useState('');
  const [leadPhone, setLeadPhone] = useState('');
  const [leadNotes, setLeadNotes] = useState('');
  const [leadDone, setLeadDone] = useState(false);
  const [leadLoading, setLeadLoading] = useState(false);
  const [leadError, setLeadError] = useState('');

  // Daily Ask Jothidar limit (3 questions per 24h IST day, no carry-forward)
  const DAILY_ASK_LIMIT = 3;
  const getTodayIst = () => {
    const ist = new Date(Date.now() + 5.5 * 3600 * 1000);
    return ist.toISOString().slice(0, 10);
  };
  const readAskRemaining = () => {
    try {
      const raw = localStorage.getItem('nk_ask_quota');
      if (!raw) return DAILY_ASK_LIMIT;
      const parsed = JSON.parse(raw) as { date?: string; used?: number };
      if (parsed.date !== getTodayIst()) return DAILY_ASK_LIMIT;
      return Math.max(0, DAILY_ASK_LIMIT - (parsed.used ?? 0));
    } catch {
      return DAILY_ASK_LIMIT;
    }
  };
  const [askRemaining, setAskRemaining] = useState<number>(() => readAskRemaining());
  const persistAskRemaining = (rem: number) => {
    const clamped = Math.max(0, Math.min(DAILY_ASK_LIMIT, rem));
    setAskRemaining(clamped);
    localStorage.setItem('nk_ask_quota', JSON.stringify({ date: getTodayIst(), used: DAILY_ASK_LIMIT - clamped }));
  };

  const [installPrompt, setInstallPrompt] = useState<{ prompt: () => Promise<void>; userChoice: Promise<{ outcome: string }> } | null>(null);

  useEffect(() => {
    const handler = (e: Event) => {
      e.preventDefault();
      setInstallPrompt(e as unknown as { prompt: () => Promise<void>; userChoice: Promise<{ outcome: string }> });
    };
    window.addEventListener('beforeinstallprompt', handler);
    return () => window.removeEventListener('beforeinstallprompt', handler);
  }, []);

  const t = UI_COPY[lang];

  useEffect(() => {
    localStorage.setItem('nk_lang', lang);
  }, [lang]);

  useEffect(() => {
    localStorage.setItem('nk_theme', ivoryTheme ? 'ivory' : 'midnight');
    document.documentElement.classList.toggle('theme-ivory', ivoryTheme);
  }, [ivoryTheme]);

  useEffect(() => {
    localStorage.setItem('nk_profile', JSON.stringify(profile));
  }, [profile]);

  // Load metadata + Jathagam + Panchangam whenever language or profile changes
  const fetchCoreData = async (activeProfile: SavedProfile, activeLang: Lang) => {
    try {
      const metaRes = await fetch(`${API_BASE}/api/meta?lang=${activeLang}`);
      const meta = await metaRes.json();
      setRasis(meta.rasis || []);
      setNakshatrams(meta.nakshatrams || []);

      const jRes = await fetch(`${API_BASE}/api/jathagam`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: activeProfile.name,
          dob: activeProfile.dob,
          tob: activeProfile.tob,
          lat: activeProfile.lat,
          lon: activeProfile.lon,
          tz_offset: activeProfile.tz,
          ayanamsa: activeProfile.ayanamsa,
          lang: activeLang,
          privacy_mode: activeProfile.privacyMode,
          existing_code: activeProfile.code,
          override_rasi_idx: activeProfile.overrideRasiIdx ?? null,
          override_nak_idx: activeProfile.overrideNakIdx ?? null,
          override_lagnam_idx: activeProfile.overrideLagnamIdx ?? null,
        }),
      });
      const jData: JathagamResponse = await jRes.json();
      setJathagam(jData);
      setSelectedRasiIdx(jData.rasi.idx);
      if (!activeProfile.code && jData.code) {
        setProfile((prev) => ({ ...prev, code: jData.code }));
      }

      const natalMap: Record<string, number> = {};
      for (const g of jData.grahas) {
        natalMap[g.key] = g.rasi_idx;
      }

      const pRes = await fetch(`${API_BASE}/api/panchangam`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          lat: activeProfile.lat,
          lon: activeProfile.lon,
          tz_offset: activeProfile.tz,
          lang: activeLang,
          user_rasi_idx: jData.rasi.idx,
          user_nak_idx: jData.nakshatram.idx,
          user_lagnam_idx: jData.lagnam.idx,
          user_age: jData.age,
          user_dasa: jData.dasa,
          natal_grahas: natalMap,
          birth_is_valarpirai: jData.birth_is_valarpirai,
          ayanamsa: activeProfile.ayanamsa,
        }),
      });
      const pData: PanchangamResponse = await pRes.json();
      setPanchangam(pData);
    } catch (err) {
      console.error('Failed to load astrology data', err);
    }
  };

  useEffect(() => {
    if (isOnboarded) {
      fetchCoreData(profile, lang);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lang, isOnboarded]);

  // 4-second Cosmic Splash Screen on initial load
  useEffect(() => {
    const fadeTimer = setTimeout(() => setSplashFading(true), 3600);
    const hideTimer = setTimeout(() => setShowSplash(false), 4000);
    return () => {
      clearTimeout(fadeTimer);
      clearTimeout(hideTimer);
    };
  }, []);

  // Realtime 1-second clock + automatic Pancha Patchi refresh on Jamam change
  useEffect(() => {
    const timer = setInterval(() => {
      setNowTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const parseClockTime = (tStr: string, ref: Date): Date | null => {
    const match = tStr.match(/^(\d{1,2}):(\d{2})\s*(AM|PM)$/i);
    if (!match) return null;
    let hh = parseInt(match[1], 10);
    const mm = parseInt(match[2], 10);
    const ampm = match[3].toUpperCase();
    if (ampm === 'PM' && hh !== 12) hh += 12;
    if (ampm === 'AM' && hh === 12) hh = 0;
    const d = new Date(ref);
    d.setHours(hh, mm, 0, 0);
    return d;
  };

  const getJamamProgress = (startStr?: string, endStr?: string) => {
    if (!startStr || !endStr) return { remainingText: '--:--', progressPct: 0, isEnded: false };
    const startDt = parseClockTime(startStr, nowTime);
    const endDt = parseClockTime(endStr, nowTime);
    if (!startDt || !endDt) return { remainingText: '--:--', progressPct: 0, isEnded: false };

    if (endDt.getTime() <= startDt.getTime()) {
      if (nowTime.getTime() < endDt.getTime()) startDt.setDate(startDt.getDate() - 1);
      else endDt.setDate(endDt.getDate() + 1);
    }

    const totalSec = Math.max(1, Math.floor((endDt.getTime() - startDt.getTime()) / 1000));
    const remSec = Math.max(0, Math.floor((endDt.getTime() - nowTime.getTime()) / 1000));
    const elapsedSec = Math.min(totalSec, Math.max(0, totalSec - remSec));
    const progressPct = Math.min(100, Math.max(0, Math.round((elapsedSec / totalSec) * 100)));

    const hrs = Math.floor(remSec / 3600);
    const mins = Math.floor((remSec % 3600) / 60);
    const secs = remSec % 60;
    const remainingText =
      hrs > 0
        ? `${String(hrs).padStart(2, '0')}:${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
        : `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;

    return { remainingText, progressPct, isEnded: remSec === 0 };
  };

  useEffect(() => {
    if (!isOnboarded || !panchangam?.pancha_patchi?.current?.end) return;
    const prog = getJamamProgress(panchangam.pancha_patchi.current.start, panchangam.pancha_patchi.current.end);
    if (prog.isEnded) {
      fetchCoreData(profile, lang);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [nowTime]);

  const handleCompleteOnboarding = (e: React.FormEvent) => {
    e.preventDefault();
    if (!profile.name.trim() || !profile.dob || !profile.tob) return;
    localStorage.setItem('nk_profile_onboarded', '1');
    setIsOnboarded(true);
    fetchCoreData(profile, lang);
  };

  const handleCalculateJathagam = () => {
    fetchCoreData(profile, lang);
  };

  const handleCheckGoal = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/goal-check`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          goal_key: goalKey,
          step_desc: stepDesc,
          chart: jathagam,
          panchangam,
          lang,
        }),
      });
      const data = await res.json();
      setGoalResult(data);
    } catch (err) {
      console.error('Goal check failed', err);
    }
  };

  const handleCheckPorutham = async () => {
    setPoruthamErr('');
    try {
      const res = await fetch(`${API_BASE}/api/porutham`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          bride_nak_idx: brideNak,
          bride_rasi_idx: brideRasi,
          groom_nak_idx: groomNak,
          groom_rasi_idx: groomRasi,
          bride_code: brideCode.trim() || null,
          groom_code: groomCode.trim() || null,
          lang,
        }),
      });
      if (!res.ok) {
        const errData = await res.json();
        setPoruthamErr(errData.detail || 'Invalid code or input');
        return;
      }
      const data: PoruthamResponse = await res.json();
      setPorutham(data);
    } catch {
      setPoruthamErr('Connection error');
    }
  };

  const handleAskJothidar = async (customQ?: string) => {
    const q = (customQ ?? chatInput).trim();
    if (!q || chatLoading) return;
    const currentRem = readAskRemaining();
    if (currentRem <= 0) {
      setAskRemaining(0);
      const limitMsg =
        lang === 'ta'
          ? `இன்றைய ${DAILY_ASK_LIMIT} இலவச கேள்விகள் முடிந்துவிட்டன. நாளை மீண்டும் புதிய ${DAILY_ASK_LIMIT} கேள்விகள் கேட்கலாம்.`
          : lang === 'en'
          ? `You have used all ${DAILY_ASK_LIMIT} questions for today. Your limit resets tomorrow (no carry-forward).`
          : `Innaikku ${DAILY_ASK_LIMIT} free kelvigal mudinjiduchu. Naalaikku pudhu ${DAILY_ASK_LIMIT} kelvigal kekkalam.`;
      setMessages((prev) => [...prev, { role: 'jothidar', text: limitMsg }]);
      return;
    }
    setMessages((prev) => [...prev, { role: 'user', text: q }]);
    if (!customQ) setChatInput('');
    setChatLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/ask-jothidar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: q,
          chart: jathagam,
          panchangam,
          lang,
        }),
      });
      const data = await res.json();
      if (res.status === 429) {
        persistAskRemaining(0);
        setMessages((prev) => [...prev, { role: 'jothidar', text: data.detail || 'Daily limit reached.' }]);
        return;
      }
      if (typeof data.remaining_today === 'number') {
        persistAskRemaining(data.remaining_today);
      } else {
        persistAskRemaining(currentRem - 1);
      }
      setMessages((prev) => [...prev, { role: 'jothidar', text: data.answer }]);
    } catch {
      setMessages((prev) => [...prev, { role: 'jothidar', text: 'Network error. Try again.' }]);
    } finally {
      setChatLoading(false);
    }
  };

  const handleLeadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!leadName.trim() || !leadPhone.trim() || leadLoading) return;
    setLeadError('');
    setLeadLoading(true);
    const leadPayload = {
      name: leadName,
      phone: leadPhone,
      request_type: leadModal.type,
      notes: leadNotes,
      chart_code: jathagam?.code || '',
    };
    try {
      const orderRes = await fetch(`${API_BASE}/api/payment/create-order`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(leadPayload),
      });
      const orderData = await orderRes.json();
      const RazorpayCtor = (window as unknown as { Razorpay?: new (opts: Record<string, unknown>) => { open: () => void; on: (ev: string, cb: () => void) => void } }).Razorpay;

      if (orderRes.ok && orderData.configured && orderData.order_id && RazorpayCtor) {
        const rzp = new RazorpayCtor({
          key: orderData.key_id,
          amount: orderData.amount,
          currency: orderData.currency || 'INR',
          name: 'Nakshatra · எனது ஜோதிடர்',
          description: '20-Page Detailed Jathagam & Pariharam Report',
          order_id: orderData.order_id,
          prefill: { name: leadName, contact: leadPhone },
          theme: { color: '#D4AF37' },
          handler: async (response: { razorpay_order_id: string; razorpay_payment_id: string; razorpay_signature: string }) => {
            try {
              const verifyRes = await fetch(`${API_BASE}/api/payment/verify`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ...leadPayload, ...response }),
              });
              if (verifyRes.ok) {
                setLeadDone(true);
              } else {
                setLeadError('Payment verification failed. Please contact support.');
              }
            } catch {
              setLeadError('Verification error. Please check your connection.');
            } finally {
              setLeadLoading(false);
            }
          },
          modal: {
            ondismiss: () => setLeadLoading(false),
          },
        });
        rzp.on('payment.failed', () => {
          setLeadError('Payment failed or cancelled. Please try again.');
          setLeadLoading(false);
        });
        rzp.open();
        return;
      }

      // Fallback if Razorpay keys are not configured on backend yet
      await fetch(`${API_BASE}/api/leads`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(leadPayload),
      });
      setLeadDone(true);
    } catch {
      setLeadError('Unable to initiate payment. Please try again.');
    } finally {
      setLeadLoading(false);
    }
  };

  const shareWhatsApp = (text: string) => {
    window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, '_blank');
  };

  const formatCode = (c?: string) => (c && c.length === 8 ? `${c.slice(0, 4)}-${c.slice(4)}` : c || '----');

  const patchiToneClasses = (tone: string) => {
    if (tone === 'emerald') return 'bg-emerald-500/15 text-emerald-400 border-emerald-500/40';
    if (tone === 'gold') return 'bg-amber-500/15 text-amber-400 border-amber-500/40';
    if (tone === 'crimson') return 'bg-rose-500/15 text-rose-400 border-rose-500/40';
    if (tone === 'amber') return 'bg-orange-500/15 text-orange-400 border-orange-500/40';
    return 'bg-slate-500/15 text-slate-300 border-slate-500/40';
  };

  const quickQuestions: Record<Lang, string[]> = {
    ta: ['என் வேலை மற்றும் தொழில் வளர்ச்சி எப்படி இருக்கும்?', 'திருமண காலம் மற்றும் பொருத்தம் பற்றி சொல்லுங்கள்', 'இன்று எனக்கு என்ன பரிகாரம் சிறந்தது?'],
    en: ['How is my career & financial phase right now?', 'What does my chart say about marriage timing?', 'What simple remedy fits my current Dasa?'],
    tanglish: ['En career & job growth ippo epdi irukkum?', 'Marriage timing & Porutham epdi irukku?', 'Innaikku enakku enna simple pariharam best?'],
  };

  const activeRasiPalan = panchangam?.rasi_palan.find((r) => r.idx === selectedRasiIdx);

  return (
    <div className="min-h-screen pb-24 max-w-lg mx-auto relative">
      {/* 4-Second Cosmic Mandala Splash Screen */}
      {showSplash && (
        <div
          className={`fixed inset-0 z-50 flex flex-col items-center justify-center bg-[#0B0F19] text-[#F8FAFC] px-6 transition-opacity duration-500 ${
            splashFading ? 'opacity-0 pointer-events-none' : 'opacity-100'
          }`}
        >
          <div className="relative w-48 h-48 flex items-center justify-center mb-5">
            <div className="absolute inset-0 rounded-full bg-[#D4AF37]/10 blur-2xl animate-pulse" />
            <JothidamEmblem variant="mandala" className="w-48 h-48 animate-spin-slow drop-shadow-[0_0_24px_rgba(212,175,55,0.35)]" />
          </div>

          <h1 className="text-2xl font-bold tracking-wide text-[#D4AF37]">நட்சத்திரம் · Nakshatra</h1>
          <p className="text-xs text-[#94A3B8] mt-1.5 text-center">
            {lang === 'ta'
              ? 'உங்கள் தனிப்பட்ட தமிழ் ஜோதிடர் · ஜாதகம் & பஞ்ச பட்சி'
              : lang === 'en'
              ? 'Your Personal Tamil Jothidar · Jothidam & Pancha Patchi'
              : 'Unga Personal Tamil Jothidar · Jothidam & Pancha Patchi'}
          </p>

          {/* 4-Second Progress Bar */}
          <div className="w-48 h-1 rounded-full bg-white/10 overflow-hidden mt-7">
            <div className="h-full bg-gradient-to-r from-[#D4AF37] to-[#F59E0B] animate-splash-fill" />
          </div>

          <button
            onClick={() => setShowSplash(false)}
            className="mt-5 text-[13px] text-[#94A3B8] hover:text-[#D4AF37] transition"
          >
            Skip →
          </button>
        </div>
      )}

      {/* Sticky Header */}
      <header className="sticky top-0 z-30 backdrop-blur-md bg-[var(--bg-page)]/90 border-b border-[var(--border-gold)] px-3 py-2.5">
        {installPrompt && (
          <div className="mb-2 px-3 py-1.5 rounded-xl bg-[#D4AF37]/15 border border-[#D4AF37]/40 flex items-center justify-between gap-2 text-[11px]">
            <span className="text-[var(--accent-gold)] font-medium truncate">
              {lang === 'ta'
                ? 'நட்சத்திரம் ஆப்-ஐ மொபைலில் நிறுவுங்கள்'
                : lang === 'en'
                ? 'Install Nakshatra App on your home screen'
                : 'Nakshatra App-a mobile-la install pannunga'}
            </span>
            <div className="flex items-center gap-1.5 shrink-0">
              <button
                onClick={async () => {
                  await installPrompt.prompt();
                  await installPrompt.userChoice;
                  setInstallPrompt(null);
                }}
                className="px-2.5 py-1 rounded-lg bg-[#D4AF37] text-[#0B0F19] font-bold"
              >
                {lang === 'ta' ? 'நிறுவு' : 'Install'}
              </button>
              <button onClick={() => setInstallPrompt(null)} className="text-[var(--text-muted)] px-1">
                ✕
              </button>
            </div>
          </div>
        )}
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2 min-w-0">
            <div className="w-9 h-9 shrink-0 rounded-full bg-[#0B0F19] border border-[#D4AF37]/70 flex items-center justify-center text-[#D4AF37] shadow-[0_0_14px_rgba(212,175,55,0.22)]">
              <JothidamEmblem className="w-7 h-7" />
            </div>
            <div className="min-w-0">
              <h1 className="text-sm font-bold leading-tight text-[var(--accent-gold)] truncate">{t.appTitle}</h1>
              <p className="text-[11px] text-[var(--text-muted)] truncate">{t.appSubtitle}</p>
            </div>
          </div>

          <div className="flex items-center gap-1 shrink-0">
            {/* 3-Way Language Toggle */}
            <div className="flex rounded-lg p-0.5 cosmic-card text-[11px] font-medium">
              {(['ta', 'en', 'tanglish'] as Lang[]).map((l) => (
                <button
                  key={l}
                  onClick={() => setLang(l)}
                  className={`px-1.5 py-1 rounded-md transition whitespace-nowrap ${
                    lang === l
                      ? 'bg-[#D4AF37] text-[#0B0F19] font-semibold'
                      : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'
                  }`}
                >
                  {l === 'ta' ? 'தமிழ்' : l === 'en' ? 'EN' : 'Tanglish'}
                </button>
              ))}
            </div>

            {/* Theme Toggle */}
            <button
              onClick={() => setIvoryTheme(!ivoryTheme)}
              className="p-1.5 rounded-lg cosmic-card text-[var(--accent-gold)]"
              title="Toggle Midnight / Palm-Leaf Theme"
            >
              {ivoryTheme ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4" />}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="px-4 pt-4 space-y-4">
        {/* ================= ONBOARDING SCREEN ================= */}
        {!isOnboarded && (
          <section className="cosmic-card rounded-2xl p-5 space-y-4 mt-4">
            <div className="text-center space-y-1.5">
              <JothidamEmblem variant="mandala" className="w-20 h-20 mx-auto" />
              <h2 className="text-lg font-bold text-[var(--accent-gold)]">{t.onboardTitle}</h2>
              <p className="text-xs text-[var(--text-muted)] leading-relaxed">{t.onboardDesc}</p>
            </div>

            <form onSubmit={handleCompleteOnboarding} className="space-y-3 text-xs">
              <div>
                <label className="text-[13px] text-[var(--text-muted)]">{t.nameLabel}</label>
                <input
                  required
                  value={profile.name}
                  onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                  placeholder="Karthik / Kavya..."
                  className="w-full mt-1 px-3 py-2.5 rounded-xl cosmic-card-alt outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-2.5">
                <div>
                  <label className="text-[13px] text-[var(--text-muted)]">{t.dobLabel}</label>
                  <input
                    required
                    type="date"
                    value={profile.dob}
                    onChange={(e) => setProfile({ ...profile, dob: e.target.value })}
                    className="w-full mt-1 px-3 py-2.5 rounded-xl cosmic-card-alt outline-none"
                  />
                </div>
                <div>
                  <label className="text-[13px] text-[var(--text-muted)]">{t.tobLabel}</label>
                  <input
                    required
                    type="time"
                    value={profile.tob}
                    onChange={(e) => setProfile({ ...profile, tob: e.target.value })}
                    className="w-full mt-1 px-3 py-2.5 rounded-xl cosmic-card-alt outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2.5">
                <div>
                  <label className="text-[13px] text-[var(--text-muted)]">{t.cityLabel}</label>
                  <select
                    value={profile.city}
                    onChange={(e) => {
                      const c = CITIES.find((x) => x.label === e.target.value);
                      if (c) setProfile({ ...profile, city: c.label, lat: c.lat, lon: c.lon, tz: c.tz });
                    }}
                    className="w-full mt-1 px-3 py-2.5 rounded-xl cosmic-card-alt outline-none"
                  >
                    {CITIES.map((c) => (
                      <option key={c.label} value={c.label}>
                        {c.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="text-[13px] text-[var(--text-muted)]">{t.ayanamsaLabel}</label>
                  <select
                    value={profile.ayanamsa}
                    onChange={(e) => setProfile({ ...profile, ayanamsa: e.target.value as 'lahiri' | 'raman' | 'kp' })}
                    className="w-full mt-1 px-3 py-2.5 rounded-xl cosmic-card-alt outline-none"
                  >
                    <option value="lahiri">Thirukanidam (Lahiri)</option>
                    <option value="raman">B.V. Raman</option>
                    <option value="kp">KP Ayanamsa</option>
                  </select>
                </div>
              </div>

              <button
                type="submit"
                className="w-full py-3 rounded-xl bg-gradient-to-r from-[#D4AF37] to-[#F59E0B] text-[#0B0F19] font-bold text-sm shadow-lg"
              >
                {t.onboardBtn}
              </button>
            </form>
          </section>
        )}

        {/* ================= TODAY TAB ================= */}
        {isOnboarded && tab === 'today' && (
          <>
            {/* Personal Greeting Card */}
            <section className="cosmic-card rounded-2xl p-4 space-y-2">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-[var(--text-muted)]">{panchangam?.date || 'Today'}</p>
                  <h2 className="text-lg font-bold">
                    {t.greetingPrefix}, {profile.name}!
                  </h2>
                </div>
                <div className="text-right space-y-1">
                  {jathagam && (
                    <span className="inline-block text-[13px] px-2.5 py-1 rounded-full bg-[#D4AF37]/15 text-[var(--accent-gold)] border border-[var(--border-gold)] font-medium">
                      {jathagam.rasi.name} · {jathagam.nakshatram.name}
                    </span>
                  )}
                  <div>
                    <button
                      onClick={() => setIsOnboarded(false)}
                      className="text-[13px] text-[var(--text-muted)] underline hover:text-[var(--accent-gold)]"
                    >
                      {t.editProfileBtn}
                    </button>
                  </div>
                </div>
              </div>

              {panchangam?.is_user_chandrashtamam && (
                <div className="flex items-start gap-2 p-2.5 rounded-xl bg-rose-500/15 border border-rose-500/40 text-rose-300 text-xs">
                  <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                  <span>{t.chandrashtamamWarn}</span>
                </div>
              )}

              {jathagam && (
                <p className="text-xs text-[var(--text-muted)] leading-relaxed pt-1">
                  <strong className="text-[var(--accent-gold)]">{t.pulipaniTitle}:</strong> {jathagam.pulipani_insight}
                </p>
              )}
            </section>

            {/* Live Pancha Patchi Saasthiram Card */}
            {panchangam && (
              <section className="cosmic-card rounded-2xl p-4 space-y-3">
                <div className="flex items-center justify-between gap-2">
                  <h3 className="text-sm font-bold flex items-center gap-1.5 text-[var(--accent-gold)]">
                    <span>{panchangam.pancha_patchi.bird.emoji}</span>
                    {t.patchiTitle}
                  </h3>
                  <div className="flex items-center gap-1.5 text-[12px]">
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 font-mono">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                      {nowTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                    </span>
                    <span className="text-[var(--text-muted)]">{panchangam.pancha_patchi.paksham}</span>
                  </div>
                </div>

                {(() => {
                  const jamamProg = getJamamProgress(
                    panchangam.pancha_patchi.current.start,
                    panchangam.pancha_patchi.current.end
                  );
                  const barFill =
                    panchangam.pancha_patchi.current.tone === 'emerald'
                      ? 'bg-gradient-to-r from-emerald-500 to-teal-400'
                      : panchangam.pancha_patchi.current.tone === 'gold'
                      ? 'bg-gradient-to-r from-[#D4AF37] to-amber-400'
                      : panchangam.pancha_patchi.current.tone === 'crimson'
                      ? 'bg-gradient-to-r from-rose-600 to-rose-400'
                      : panchangam.pancha_patchi.current.tone === 'amber'
                      ? 'bg-gradient-to-r from-orange-500 to-amber-400'
                      : 'bg-gradient-to-r from-sky-600 to-cyan-400';
                  return (
                    <div className="cosmic-card-alt rounded-xl p-3.5 space-y-2.5">
                      <div>
                        <p className="text-[13px] text-[var(--text-muted)]">{t.patchiBird}</p>
                        <p className="text-lg font-bold">{panchangam.pancha_patchi.bird.name}</p>
                      </div>

                      {/* Sketch-Matched State + Time Remaining + Live Progress Bar */}
                      <div className="space-y-1.5 pt-1">
                        <div className="flex items-end justify-between gap-2">
                          <span
                            className={`text-xs font-semibold px-2.5 py-1 rounded-full border ${patchiToneClasses(
                              panchangam.pancha_patchi.current.tone
                            )}`}
                          >
                            {panchangam.pancha_patchi.current.label}
                          </span>
                          <div className="text-right leading-tight">
                            <p className="text-[12px] text-[var(--text-muted)]">Time remaining</p>
                            <p className="text-base font-mono font-bold tabular-nums text-[var(--accent-gold)]">
                              {jamamProg.remainingText}
                            </p>
                          </div>
                        </div>

                        <div className="w-full h-3.5 rounded-full bg-black/35 border border-[var(--border-gold)] overflow-hidden p-0.5">
                          <div
                            className={`h-full rounded-full transition-all duration-700 ${barFill}`}
                            style={{ width: `${jamamProg.progressPct}%` }}
                          />
                        </div>
                      </div>

                      <p className="text-xs leading-relaxed">{panchangam.pancha_patchi.current.advice}</p>

                  {/* Now / Next / Best Upcoming Summary */}
                  <div className="grid grid-cols-3 gap-2 pt-2 border-t border-[var(--border-gold)] text-[13px]">
                    <div className="p-2 rounded-lg bg-[#D4AF37]/10 border border-[#D4AF37]/30">
                      <p className="text-[12px] text-[var(--accent-gold)] font-semibold uppercase">{t.patchiNowLabel}</p>
                      <p className="font-bold mt-0.5">{panchangam.pancha_patchi.current.state}</p>
                      <p className="text-[12px] text-[var(--text-muted)]">{panchangam.pancha_patchi.current.start}</p>
                    </div>
                    <div className="p-2 rounded-lg cosmic-card border border-[var(--border-gold)]">
                      <p className="text-[12px] text-[var(--text-muted)] font-semibold uppercase">{t.patchiNextLabel}</p>
                      <p className="font-bold mt-0.5">{panchangam.pancha_patchi.next_jamam.state}</p>
                      <p className="text-[12px] text-[var(--text-muted)]">{panchangam.pancha_patchi.next_jamam.start}</p>
                    </div>
                    <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/30">
                      <p className="text-[12px] text-emerald-400 font-semibold uppercase">{t.patchiBestUpcoming}</p>
                      <p className="font-bold text-emerald-300 mt-0.5">{panchangam.pancha_patchi.next_best.state}</p>
                      <p className="text-[12px] text-emerald-400/80">
                        {panchangam.pancha_patchi.next_best.start} – {panchangam.pancha_patchi.next_best.end}
                      </p>
                    </div>
                  </div>
                </div>
                  );
                })()}

                {/* Visual Live Timeline */}
                <div className="space-y-1.5 pt-1">
                  <p className="text-[13px] font-semibold text-[var(--text-muted)]">{t.patchiTimelineTitle}</p>
                  <div className="relative pl-4 space-y-2 border-l-2 border-[#D4AF37]/30 ml-2">
                    {panchangam.pancha_patchi.timeline.map((jm, idx) => {
                      const isBest = jm.state === 'Arasu';
                      return (
                        <div key={`tl-${idx}`} className="relative flex items-center justify-between gap-2 text-xs">
                          <span
                            className={`absolute -left-[21px] w-2.5 h-2.5 rounded-full border-2 ${
                              jm.is_current
                                ? 'bg-[#D4AF37] border-[#0B0F19] ring-2 ring-[#D4AF37]/50'
                                : isBest
                                ? 'bg-emerald-400 border-[#0B0F19]'
                                : 'bg-slate-500 border-[#0B0F19]'
                            }`}
                          />
                          <div className="min-w-0">
                            <span className={`font-semibold ${jm.is_current ? 'text-[var(--accent-gold)]' : ''}`}>
                              {jm.is_current ? `${t.patchiNowLabel}: ` : idx === 1 ? `${t.patchiNextLabel}: ` : ''}
                              {jm.start} – {jm.end}
                            </span>
                            <span className="ml-1.5 text-[12px] text-[var(--text-muted)]">
                              ({jm.period === 'night' ? 'Night' : 'Day'} {jm.jamam})
                            </span>
                          </div>
                          <span className={`shrink-0 px-2 py-0.5 rounded-full text-[12px] font-semibold border ${patchiToneClasses(jm.tone)}`}>
                            {jm.label}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>

                <button
                  onClick={() => setShowAllJamams(!showAllJamams)}
                  className="w-full text-xs font-medium py-2 rounded-xl border border-[var(--border-gold)] text-[var(--accent-gold)] hover:bg-[#D4AF37]/10 transition"
                >
                  {t.patchiProNote} {showAllJamams ? '▲' : '▼'}
                </button>

                {showAllJamams && (
                  <div className="space-y-1.5 pt-1">
                    {panchangam.pancha_patchi.day_jamams.map((jm) => (
                      <div
                        key={`d-${jm.jamam}`}
                        className={`flex items-center justify-between text-xs px-3 py-2 rounded-lg border ${
                          jm.is_current ? 'border-[#D4AF37] bg-[#D4AF37]/10' : 'border-transparent cosmic-card-alt'
                        }`}
                      >
                        <span className="text-[var(--text-muted)]">
                          Day {jm.jamam}: {jm.start} – {jm.end}
                        </span>
                        <span className={`px-2 py-0.5 rounded-full text-[13px] border ${patchiToneClasses(jm.tone)}`}>
                          {jm.state}
                        </span>
                      </div>
                    ))}
                    {panchangam.pancha_patchi.night_jamams.map((jm) => (
                      <div
                        key={`n-${jm.jamam}`}
                        className={`flex items-center justify-between text-xs px-3 py-2 rounded-lg border ${
                          jm.is_current ? 'border-[#D4AF37] bg-[#D4AF37]/10' : 'border-transparent cosmic-card-alt'
                        }`}
                      >
                        <span className="text-[var(--text-muted)]">
                          Night {jm.jamam}: {jm.start} – {jm.end}
                        </span>
                        <span className={`px-2 py-0.5 rounded-full text-[13px] border ${patchiToneClasses(jm.tone)}`}>
                          {jm.state}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </section>
            )}

            {/* Today's Panchangam Card */}
            {panchangam && (
              <section className="cosmic-card rounded-2xl p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-[var(--accent-gold)] flex items-center gap-1.5">
                    <Calendar className="w-4 h-4" />
                    {t.panchangamTitle}
                  </h3>
                  <span className="text-[13px] text-[var(--text-muted)]">
                    ☀ {panchangam.sunrise} · 🌇 {panchangam.sunset}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-2.5 text-xs">
                  <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30">
                    <p className="text-[13px] text-emerald-400 font-semibold">{t.nallaNeram}</p>
                    <p className="font-bold mt-0.5">{panchangam.nalla_neram}</p>
                  </div>
                  <div className="p-2.5 rounded-xl bg-orange-500/10 border border-orange-500/30">
                    <p className="text-[13px] text-orange-400 font-semibold">{t.rahuKalam}</p>
                    <p className="font-bold mt-0.5">{panchangam.rahu_kalam}</p>
                  </div>
                  <div className="p-2.5 rounded-xl cosmic-card-alt">
                    <p className="text-[13px] text-[var(--text-muted)]">{t.yemagandam}</p>
                    <p className="font-semibold mt-0.5">{panchangam.yemagandam}</p>
                  </div>
                  <div className="p-2.5 rounded-xl cosmic-card-alt">
                    <p className="text-[13px] text-[var(--text-muted)]">{t.todayStar}</p>
                    <p className="font-semibold mt-0.5">
                      {panchangam.nakshatram.name} (P{panchangam.nakshatram.pada})
                    </p>
                  </div>
                </div>
              </section>
            )}

            {/* Precision Customized Personal Palan + WhatsApp Share */}
            {panchangam && (
              <section className="cosmic-card rounded-2xl p-4 space-y-3">
                <div className="flex items-center justify-between gap-2">
                  <h3 className="text-sm font-bold text-[var(--accent-gold)]">{t.personalPalanTitle}</h3>
                  {panchangam.personal_palan && (
                    <span
                      className={`shrink-0 text-[12px] font-semibold px-2 py-0.5 rounded-full border ${
                        panchangam.personal_palan.tara_balam.good
                          ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/40'
                          : 'bg-amber-500/15 text-amber-400 border-amber-500/40'
                      }`}
                    >
                      {panchangam.personal_palan.tara_balam.score}% Match
                    </span>
                  )}
                </div>

                {panchangam.personal_palan && (
                  <div className="p-3.5 rounded-xl cosmic-card-alt space-y-2.5 text-xs">
                    <div className="flex flex-wrap items-center gap-1.5">
                      <span className="px-2 py-0.5 rounded-full bg-[#D4AF37]/15 text-[var(--accent-gold)] border border-[var(--border-gold)] text-[12px] font-semibold">
                        {panchangam.personal_palan.age_rule_note}
                      </span>
                      {panchangam.personal_palan.dasa_summary && (
                        <span className="px-2 py-0.5 rounded-full bg-indigo-500/15 text-indigo-300 border border-indigo-500/30 text-[12px] font-semibold">
                          Dasa: {panchangam.personal_palan.dasa_summary}
                        </span>
                      )}
                    </div>

                    {panchangam.personal_palan.transit_notes && panchangam.personal_palan.transit_notes.length > 0 && (
                      <div className="p-2.5 rounded-lg cosmic-card space-y-1 text-[13px] border border-[var(--border-gold)]">
                        {panchangam.personal_palan.transit_notes.map((note, idx) => (
                          <p key={idx} className="leading-snug text-[var(--text-primary)]">
                            • {note}
                          </p>
                        ))}
                      </div>
                    )}

                    <div className="grid grid-cols-2 gap-2 text-[13px]">
                      <div className="p-2 rounded-lg cosmic-card">
                        <p className="text-[12px] text-[var(--text-muted)]">Tara Balam</p>
                        <p className="font-bold mt-0.5">{panchangam.personal_palan.tara_balam.name}</p>
                        {panchangam.personal_palan.tara_balam.valid_till && (
                          <div className="mt-1.5 pt-1.5 border-t border-[var(--border-gold)] space-y-0.5 text-[12px]">
                            {panchangam.personal_palan.tara_balam.valid_from && (
                              <p className="text-[var(--text-muted)]">
                                {lang === 'ta' ? 'தொடக்கம்: ' : 'Starts: '}
                                <span className="text-[var(--text-primary)] font-medium">
                                  {panchangam.personal_palan.tara_balam.valid_from}
                                </span>
                              </p>
                            )}
                            <p className="text-[var(--text-muted)]">
                              {lang === 'ta' ? 'முடிவு: ' : 'Ends: '}
                              <span className="text-[var(--accent-gold)] font-medium">
                                {panchangam.personal_palan.tara_balam.valid_till}
                              </span>
                            </p>
                          </div>
                        )}
                      </div>
                      <div className="p-2 rounded-lg cosmic-card">
                        <p className="text-[12px] text-[var(--text-muted)]">Moon Transit</p>
                        <p className="font-bold mt-0.5">
                          Rasi H{panchangam.personal_palan.rasi_house} · Lagnam H{panchangam.personal_palan.lagnam_house}
                        </p>
                      </div>
                    </div>

                    <p className="text-sm font-semibold leading-snug text-[var(--text-primary)]">
                      {panchangam.personal_palan.headline}
                    </p>
                    {panchangam.personal_palan.daily_details && panchangam.personal_palan.daily_details.length > 0 ? (
                      <div className="space-y-1.5 leading-relaxed text-[var(--text-muted)]">
                        {panchangam.personal_palan.daily_details.map((line, idx) => (
                          <p key={idx}>{line}</p>
                        ))}
                      </div>
                    ) : (
                      <p className="leading-relaxed text-[var(--text-muted)]">
                        {panchangam.personal_palan.action_advice}
                      </p>
                    )}

                    <button
                      onClick={() =>
                        shareWhatsApp(
                          `✨ *${t.appTitle} - ${profile.name}*\n${panchangam.personal_palan?.age_rule_note}\n⭐ ${panchangam.personal_palan?.tara_balam.name}\n📌 ${panchangam.personal_palan?.action_advice}\n🕊️ ${panchangam.pancha_patchi.bird.name}: ${panchangam.pancha_patchi.current.label}`
                        )
                      }
                      className="inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-400 hover:underline pt-1"
                    >
                      <Share2 className="w-3.5 h-3.5" />
                      {t.shareWhatsApp}
                    </button>
                  </div>
                )}

                {/* Secondary: Check Another Rasi */}
                <div className="pt-2 border-t border-[var(--border-gold)] flex items-center justify-between gap-2 text-xs">
                  <span className="text-[13px] text-[var(--text-muted)]">{t.otherRasiCheck}</span>
                  <select
                    value={selectedRasiIdx}
                    onChange={(e) => setSelectedRasiIdx(Number(e.target.value))}
                    className="text-xs rounded-lg px-2.5 py-1 cosmic-card-alt outline-none"
                  >
                    {panchangam.rasi_palan.map((r) => (
                      <option key={r.idx} value={r.idx}>
                        {r.name}
                      </option>
                    ))}
                  </select>
                </div>
                {activeRasiPalan && selectedRasiIdx !== jathagam?.rasi.idx && (
                  <p className="text-xs text-[var(--text-muted)] px-1">{activeRasiPalan.summary}</p>
                )}
              </section>
            )}
          </>
        )}

        {/* ================= JATHAGAM TAB ================= */}
        {isOnboarded && tab === 'jathagam' && (
          <>
            <section className="cosmic-card rounded-2xl p-4 space-y-3">
              <h2 className="text-sm font-bold text-[var(--accent-gold)]">{t.jathagamTitle}</h2>

              <div className="grid grid-cols-2 gap-2.5 text-xs">
                <div className="col-span-2">
                  <label className="text-[13px] text-[var(--text-muted)]">{t.nameLabel}</label>
                  <input
                    value={profile.name}
                    onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                    className="w-full mt-1 px-3 py-2 rounded-xl cosmic-card-alt outline-none"
                  />
                </div>
                <div>
                  <label className="text-[13px] text-[var(--text-muted)]">{t.dobLabel}</label>
                  <input
                    type="date"
                    value={profile.dob}
                    onChange={(e) => setProfile({ ...profile, dob: e.target.value })}
                    className="w-full mt-1 px-3 py-2 rounded-xl cosmic-card-alt outline-none"
                  />
                </div>
                <div>
                  <label className="text-[13px] text-[var(--text-muted)]">{t.tobLabel}</label>
                  <input
                    type="time"
                    value={profile.tob}
                    onChange={(e) => setProfile({ ...profile, tob: e.target.value })}
                    className="w-full mt-1 px-3 py-2 rounded-xl cosmic-card-alt outline-none"
                  />
                </div>
                <div>
                  <label className="text-[13px] text-[var(--text-muted)]">{t.cityLabel}</label>
                  <select
                    value={profile.city}
                    onChange={(e) => {
                      const c = CITIES.find((x) => x.label === e.target.value);
                      if (c) setProfile({ ...profile, city: c.label, lat: c.lat, lon: c.lon, tz: c.tz });
                    }}
                    className="w-full mt-1 px-3 py-2 rounded-xl cosmic-card-alt outline-none"
                  >
                    {CITIES.map((c) => (
                      <option key={c.label} value={c.label}>
                        {c.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="text-[13px] text-[var(--text-muted)]">{t.ayanamsaLabel}</label>
                  <select
                    value={profile.ayanamsa}
                    onChange={(e) => setProfile({ ...profile, ayanamsa: e.target.value as 'lahiri' | 'raman' | 'kp' })}
                    className="w-full mt-1 px-3 py-2 rounded-xl cosmic-card-alt outline-none"
                  >
                    <option value="lahiri">Thirukanidam (Lahiri)</option>
                    <option value="raman">B.V. Raman</option>
                    <option value="kp">KP Ayanamsa</option>
                  </select>
                </div>
              </div>

              <label className="flex items-center gap-2 text-xs text-[var(--text-muted)] cursor-pointer">
                <input
                  type="checkbox"
                  checked={profile.privacyMode}
                  onChange={(e) => setProfile({ ...profile, privacyMode: e.target.checked })}
                  className="accent-[#D4AF37]"
                />
                <Lock className="w-3.5 h-3.5 text-[#D4AF37]" />
                <span>{t.privacyLabel}</span>
              </label>

              <button
                onClick={handleCalculateJathagam}
                className="w-full py-2.5 rounded-xl bg-gradient-to-r from-[#D4AF37] to-[#F59E0B] text-[#0B0F19] font-bold text-sm shadow-lg"
              >
                {t.calcBtn}
              </button>
            </section>

            {jathagam && (
              <>
                {/* 8-Digit Privacy Code Card */}
                <section className="cosmic-card rounded-2xl p-4 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-[var(--accent-gold)]">{t.codeTitle}</span>
                    <span className="text-[12px] px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400">
                      {jathagam.privacy_mode ? 'Privacy ON' : 'Public'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between p-3 rounded-xl cosmic-card-alt">
                    <span className="text-xl font-mono font-bold tracking-widest text-[#D4AF37]">
                      {formatCode(jathagam.code)}
                    </span>
                    <div className="flex gap-2">
                      <button
                        onClick={() => {
                          navigator.clipboard.writeText(jathagam.code);
                          setCopiedCode(true);
                          setTimeout(() => setCopiedCode(false), 1800);
                        }}
                        className="px-2.5 py-1.5 rounded-lg bg-[#D4AF37]/15 text-[#D4AF37] text-xs font-semibold flex items-center gap-1"
                      >
                        <Copy className="w-3.5 h-3.5" />
                        {copiedCode ? 'Copied!' : t.copyCode}
                      </button>
                      <button
                        onClick={() =>
                          shareWhatsApp(
                            `✨ My Nakshatra Jathagam Code: *${formatCode(jathagam.code)}*\nCheck our 10-Point Thirumana Porutham safely without sharing birth time/phone!`
                          )
                        }
                        className="px-2.5 py-1.5 rounded-lg bg-emerald-500/15 text-emerald-400 text-xs font-semibold flex items-center gap-1"
                      >
                        <Share2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                  <p className="text-[13px] text-[var(--text-muted)]">{t.codeDesc}</p>
                </section>

                {/* Borderline Alert & Manual Paper Jathagam Override */}
                {jathagam.borderline_alert && (
                  <div className="p-3 rounded-xl bg-amber-500/15 border border-amber-500/40 text-amber-300 text-xs flex items-start gap-2">
                    <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                    <span>{t.borderlineWarn}</span>
                  </div>
                )}

                <section className="cosmic-card rounded-2xl p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex gap-1 p-0.5 rounded-lg cosmic-card-alt text-xs">
                      <button
                        onClick={() => setChartMode('rasi')}
                        className={`px-3 py-1 rounded-md font-semibold ${
                          chartMode === 'rasi' ? 'bg-[#D4AF37] text-[#0B0F19]' : 'text-[var(--text-muted)]'
                        }`}
                      >
                        {t.rasiChart}
                      </button>
                      <button
                        onClick={() => setChartMode('navamsam')}
                        className={`px-3 py-1 rounded-md font-semibold ${
                          chartMode === 'navamsam' ? 'bg-[#D4AF37] text-[#0B0F19]' : 'text-[var(--text-muted)]'
                        }`}
                      >
                        {t.navamsamChart}
                      </button>
                    </div>
                    <button
                      onClick={() => setShowOverride(!showOverride)}
                      className="text-[13px] text-[var(--accent-gold)] underline"
                    >
                      {t.overrideBtn}
                    </button>
                  </div>

                  {showOverride && (
                    <div className="p-3 rounded-xl cosmic-card-alt space-y-2 text-xs">
                      <div className="grid grid-cols-3 gap-2">
                        <div>
                          <label className="text-[12px] text-[var(--text-muted)]">Lagnam</label>
                          <select
                            value={profile.overrideLagnamIdx ?? jathagam.lagnam.idx}
                            onChange={(e) => setProfile({ ...profile, overrideLagnamIdx: Number(e.target.value) })}
                            className="w-full mt-1 p-1.5 rounded-lg cosmic-card outline-none"
                          >
                            {rasis.map((r) => (
                              <option key={r.idx} value={r.idx}>
                                {r.name}
                              </option>
                            ))}
                          </select>
                        </div>
                        <div>
                          <label className="text-[12px] text-[var(--text-muted)]">Rasi</label>
                          <select
                            value={profile.overrideRasiIdx ?? jathagam.rasi.idx}
                            onChange={(e) => setProfile({ ...profile, overrideRasiIdx: Number(e.target.value) })}
                            className="w-full mt-1 p-1.5 rounded-lg cosmic-card outline-none"
                          >
                            {rasis.map((r) => (
                              <option key={r.idx} value={r.idx}>
                                {r.name}
                              </option>
                            ))}
                          </select>
                        </div>
                        <div>
                          <label className="text-[12px] text-[var(--text-muted)]">Nakshatram</label>
                          <select
                            value={profile.overrideNakIdx ?? jathagam.nakshatram.idx}
                            onChange={(e) => setProfile({ ...profile, overrideNakIdx: Number(e.target.value) })}
                            className="w-full mt-1 p-1.5 rounded-lg cosmic-card outline-none"
                          >
                            {nakshatrams.map((n) => (
                              <option key={n.idx} value={n.idx}>
                                {n.name}
                              </option>
                            ))}
                          </select>
                        </div>
                      </div>
                      <div className="flex gap-2 pt-1">
                        <button
                          onClick={() => {
                            fetchCoreData(profile, lang);
                            setShowOverride(false);
                          }}
                          className="px-3 py-1.5 rounded-lg bg-[#D4AF37] text-[#0B0F19] font-semibold"
                        >
                          Apply
                        </button>
                        <button
                          onClick={() => {
                            const reset = {
                              ...profile,
                              overrideLagnamIdx: null,
                              overrideRasiIdx: null,
                              overrideNakIdx: null,
                            };
                            setProfile(reset);
                            fetchCoreData(reset, lang);
                            setShowOverride(false);
                          }}
                          className="px-3 py-1.5 rounded-lg cosmic-card text-[var(--text-muted)]"
                        >
                          Reset Auto
                        </button>
                      </div>
                    </div>
                  )}

                  <SouthIndianChart
                    grahas={jathagam.grahas}
                    mode={chartMode}
                    centerTitle={chartMode === 'rasi' ? t.rasiChart : t.navamsamChart}
                  />

                  {/* Dasa & Pulipani Insight */}
                  <div className="p-3 rounded-xl cosmic-card-alt space-y-2 text-xs">
                    <div className="flex justify-between items-start gap-2">
                      <span className="text-[var(--text-muted)]">{t.dasaTitle}:</span>
                      <div className="text-right">
                        <span className="font-bold text-[var(--accent-gold)]">
                          {jathagam.dasa.maha} / {jathagam.dasa.bhukti}{jathagam.dasa.anthar ? ` / ${jathagam.dasa.anthar}` : ''} ({jathagam.dasa.years_remaining}y)
                        </span>
                        {jathagam.dasa.maha_end && (
                          <p className="text-[12px] text-[var(--text-muted)] mt-0.5">
                            Maha Dasa till {jathagam.dasa.maha_end} · Bhukti till {jathagam.dasa.bhukti_end} · Anthar till {jathagam.dasa.anthar_end}
                          </p>
                        )}
                      </div>
                    </div>
                    {jathagam.pulipani_palangal ? (
                      <div className="space-y-1.5 pt-2 border-t border-[var(--border-gold)] leading-relaxed">
                        <p className="font-bold text-[var(--accent-gold)]">{t.pulipaniTitle}:</p>
                        <p>• {jathagam.pulipani_palangal.career}</p>
                        <p>• {jathagam.pulipani_palangal.wealth}</p>
                        <p>• {jathagam.pulipani_palangal.family}</p>
                        <p>• {jathagam.pulipani_palangal.dasa_effect}</p>
                        <p className="text-[var(--text-muted)] pt-1">🙏 {jathagam.pulipani_palangal.pariharam}</p>
                      </div>
                    ) : (
                      <p className="leading-relaxed pt-1 border-t border-[var(--border-gold)]">
                        <strong className="text-[var(--accent-gold)]">{t.pulipaniTitle}:</strong> {jathagam.pulipani_insight}
                      </p>
                    )}
                  </div>
                </section>
              </>
            )}
          </>
        )}

        {/* ================= PORUTHAM TAB ================= */}
        {isOnboarded && tab === 'porutham' && (
          <section className="cosmic-card rounded-2xl p-4 space-y-4">
            <h2 className="text-sm font-bold text-[var(--accent-gold)] flex items-center gap-1.5">
              <HeartHandshake className="w-4 h-4" />
              {t.poruthamTitle}
            </h2>

            {/* Bride */}
            <div className="p-3 rounded-xl cosmic-card-alt space-y-2 text-xs">
              <p className="font-semibold text-[var(--accent-gold)]">{t.brideSection}</p>
              <input
                placeholder={t.useCodePlaceholder}
                value={brideCode}
                onChange={(e) => setBrideCode(e.target.value)}
                className="w-full px-3 py-2 rounded-lg cosmic-card outline-none font-mono"
              />
              {!brideCode.trim() && (
                <div className="grid grid-cols-2 gap-2">
                  <select
                    value={brideRasi}
                    onChange={(e) => setBrideRasi(Number(e.target.value))}
                    className="px-2.5 py-2 rounded-lg cosmic-card outline-none"
                  >
                    {rasis.map((r) => (
                      <option key={r.idx} value={r.idx}>
                        {r.name}
                      </option>
                    ))}
                  </select>
                  <select
                    value={brideNak}
                    onChange={(e) => setBrideNak(Number(e.target.value))}
                    className="px-2.5 py-2 rounded-lg cosmic-card outline-none"
                  >
                    {nakshatrams.map((n) => (
                      <option key={n.idx} value={n.idx}>
                        {n.name}
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>

            {/* Groom */}
            <div className="p-3 rounded-xl cosmic-card-alt space-y-2 text-xs">
              <p className="font-semibold text-[var(--accent-gold)]">{t.groomSection}</p>
              <input
                placeholder={t.useCodePlaceholder}
                value={groomCode}
                onChange={(e) => setGroomCode(e.target.value)}
                className="w-full px-3 py-2 rounded-lg cosmic-card outline-none font-mono"
              />
              {!groomCode.trim() && (
                <div className="grid grid-cols-2 gap-2">
                  <select
                    value={groomRasi}
                    onChange={(e) => setGroomRasi(Number(e.target.value))}
                    className="px-2.5 py-2 rounded-lg cosmic-card outline-none"
                  >
                    {rasis.map((r) => (
                      <option key={r.idx} value={r.idx}>
                        {r.name}
                      </option>
                    ))}
                  </select>
                  <select
                    value={groomNak}
                    onChange={(e) => setGroomNak(Number(e.target.value))}
                    className="px-2.5 py-2 rounded-lg cosmic-card outline-none"
                  >
                    {nakshatrams.map((n) => (
                      <option key={n.idx} value={n.idx}>
                        {n.name}
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>

            {poruthamErr && <p className="text-xs text-rose-400">{poruthamErr}</p>}

            <button
              onClick={handleCheckPorutham}
              className="w-full py-2.5 rounded-xl bg-gradient-to-r from-[#D4AF37] to-[#F59E0B] text-[#0B0F19] font-bold text-sm"
            >
              {t.checkMatchBtn}
            </button>

            {porutham && (
              <div className="space-y-3 pt-2 border-t border-[var(--border-gold)]">
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold text-[#D4AF37]">
                    {porutham.score} / {porutham.total}
                  </span>
                  <button
                    onClick={() => shareWhatsApp(`💍 *10-Porutham Result:* ${porutham.verdict}`)}
                    className="text-xs text-emerald-400 flex items-center gap-1 font-semibold"
                  >
                    <Share2 className="w-3.5 h-3.5" />
                    {t.shareWhatsApp}
                  </button>
                </div>
                <p className="text-xs leading-relaxed">{porutham.verdict}</p>

                <div className="grid grid-cols-1 gap-1.5">
                  {porutham.items.map((item) => (
                    <div
                      key={item.key}
                      className="flex items-center justify-between px-3 py-2 rounded-lg cosmic-card-alt text-xs"
                    >
                      <span className={item.critical ? 'font-semibold' : ''}>{item.label}</span>
                      {item.passed ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                      ) : (
                        <XCircle className="w-4 h-4 text-rose-400 shrink-0" />
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </section>
        )}

        {/* ================= ASK JOTHIDAR TAB ================= */}
        {isOnboarded && tab === 'ask' && (
          <>
            {/* Step & Future Goal Alignment Checker */}
            <section className="cosmic-card rounded-2xl p-4 space-y-3">
              <h2 className="text-sm font-bold text-[var(--accent-gold)] flex items-center gap-1.5">
                <Sparkles className="w-4 h-4" />
                {lang === 'ta'
                  ? 'இன்றைய முயற்சி → எதிர்கால இலக்கு'
                  : lang === 'en'
                  ? 'Will This Step Reach My Goal?'
                  : 'Indha Step En Goal-a Reach Pannuma?'}
              </h2>

              <div className="grid grid-cols-1 gap-2 text-xs">
                <select
                  value={goalKey}
                  onChange={(e) => setGoalKey(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl cosmic-card-alt outline-none"
                >
                  <option value="career">
                    {lang === 'ta' ? 'தொழில் / வேலை உயர்வு' : lang === 'en' ? 'Career / Job Growth' : 'Career / Job Switch'}
                  </option>
                  <option value="business">
                    {lang === 'ta' ? 'வியாபாரம் / வருமானம்' : lang === 'en' ? 'Business / Startup & Income' : 'Business / Money Goal'}
                  </option>
                  <option value="marriage">
                    {lang === 'ta' ? 'திருமணம் / உறவு' : lang === 'en' ? 'Marriage / Relationship' : 'Marriage / Relationship'}
                  </option>
                  <option value="property">
                    {lang === 'ta' ? 'வீடு / நிலம் / வாகனம்' : lang === 'en' ? 'Home / Property / Vehicle' : 'House / Property / Vehicle'}
                  </option>
                  <option value="abroad">
                    {lang === 'ta' ? 'வெளிநாடு / உயர்கல்வி' : lang === 'en' ? 'Abroad / Visa / Higher Studies' : 'Abroad / Visa / Studies'}
                  </option>
                </select>
                <input
                  value={stepDesc}
                  onChange={(e) => setStepDesc(e.target.value)}
                  placeholder={
                    lang === 'ta'
                      ? 'இன்று நீங்கள் எடுக்கும் முயற்சி (எ.கா: புதிய வேலைக்கு விண்ணப்பிப்பது)'
                      : lang === 'en'
                      ? 'Step you are taking now (e.g., applying for a new role)'
                      : 'Ippo edukura step (e.g., new job apply / business launch)'
                  }
                  className="w-full px-3 py-2 rounded-xl cosmic-card-alt outline-none"
                />
                <button
                  onClick={handleCheckGoal}
                  className="w-full py-2.5 rounded-xl bg-gradient-to-r from-[#D4AF37] to-[#F59E0B] text-[#0B0F19] font-bold text-xs"
                >
                  {lang === 'ta'
                    ? 'இலக்கு பொருத்தம் சரிபார்க்கவும்'
                    : lang === 'en'
                    ? 'Check Step & Goal Alignment'
                    : 'Goal Alignment Check Pannu'}
                </button>
              </div>

              {goalResult && (
                <div className="p-3 rounded-xl cosmic-card-alt space-y-2 text-xs border border-[var(--border-gold)]">
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-lg font-bold text-[var(--accent-gold)]">{goalResult.score}%</span>
                    <span
                      className={`px-2.5 py-0.5 rounded-full text-[13px] font-semibold border ${
                        goalResult.verdict_code === 'go'
                          ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/40'
                          : goalResult.verdict_code === 'time_it'
                          ? 'bg-amber-500/15 text-amber-400 border-amber-500/40'
                          : 'bg-rose-500/15 text-rose-400 border-rose-500/40'
                      }`}
                    >
                      {goalResult.verdict_label}
                    </span>
                  </div>
                  <p className="leading-relaxed">{goalResult.long_term_reason}</p>
                  <p className="leading-relaxed text-emerald-400 font-medium">{goalResult.today_step_timing}</p>
                </div>
              )}
            </section>

            <section className="cosmic-card rounded-2xl p-4 space-y-3">
            <h2 className="text-sm font-bold text-[var(--accent-gold)] flex items-center gap-1.5">
              <Compass className="w-4 h-4" />
              {t.askTitle}
            </h2>

            {/* Quick Prompt Chips */}
            <div className="flex flex-wrap gap-1.5">
              {quickQuestions[lang].map((q) => (
                <button
                  key={q}
                  disabled={askRemaining <= 0 || chatLoading}
                  onClick={() => handleAskJothidar(q)}
                  className="text-[13px] px-2.5 py-1.5 rounded-full cosmic-card-alt text-[var(--accent-gold)] border border-[var(--border-gold)] hover:bg-[#D4AF37]/15 text-left disabled:opacity-50"
                >
                  {q}
                </button>
              ))}
            </div>

            <div className="flex items-center justify-between text-[11px] px-1">
              <span className={askRemaining > 0 ? 'text-[var(--text-muted)]' : 'text-amber-400 font-semibold'}>
                {lang === 'ta'
                  ? `இன்று மீதம்: ${askRemaining} / ${DAILY_ASK_LIMIT} கேள்விகள் (தினமும் புதுப்பிக்கப்படும்)`
                  : lang === 'en'
                  ? `Today's limit: ${askRemaining} / ${DAILY_ASK_LIMIT} left (resets daily, no carry-forward)`
                  : `Innaikku meedham: ${askRemaining} / ${DAILY_ASK_LIMIT} kelvigal (daily reset, no carry-forward)`}
              </span>
            </div>

            {/* Chat Feed */}
            <div className="space-y-2.5 min-h-[200px] max-h-[340px] overflow-y-auto p-2 rounded-xl cosmic-card-alt">
              {messages.length === 0 && (
                <p className="text-xs text-[var(--text-muted)] text-center py-8">
                  {jathagam
                    ? `${jathagam.name} (${jathagam.rasi.name} · ${jathagam.dasa.maha} Dasa)`
                    : 'Ask your Personal Jothidar anything...'}
                </p>
              )}
              {messages.map((m, i) => (
                <div
                  key={i}
                  className={`p-3 rounded-xl text-xs leading-relaxed ${
                    m.role === 'user'
                      ? 'ml-8 bg-[#D4AF37] text-[#0B0F19] font-medium'
                      : 'mr-4 cosmic-card border border-[var(--border-gold)]'
                  }`}
                >
                  {m.text}
                </div>
              ))}
              {chatLoading && <p className="text-xs text-[var(--accent-gold)] animate-pulse">Jothidar checking your chart...</p>}
            </div>

            <div className="flex gap-2">
              <input
                disabled={askRemaining <= 0 || chatLoading}
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleAskJothidar()}
                placeholder={
                  askRemaining <= 0
                    ? lang === 'ta'
                      ? 'இன்றைய 3 கேள்விகள் முடிந்தன — நாளை கேளுங்கள்'
                      : lang === 'en'
                      ? 'Daily limit reached — resets tomorrow'
                      : 'Innaikku 3 kelvigal mudinjiduchu — naalaikku kelunga'
                    : t.askPlaceholder
                }
                className="flex-1 px-3 py-2.5 rounded-xl cosmic-card-alt text-xs outline-none disabled:opacity-50"
              />
              <button
                disabled={askRemaining <= 0 || chatLoading}
                onClick={() => handleAskJothidar()}
                className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-[#D4AF37] to-[#F59E0B] text-[#0B0F19] font-bold text-xs flex items-center gap-1 disabled:opacity-50"
              >
                <Send className="w-3.5 h-3.5" />
                {t.sendBtn}
              </button>
            </div>

            {/* Temporarily hidden until Jothidar tie-up is finalized */}
            {false && (
              <button
                onClick={() => {
                  setLeadDone(false);
                  setLeadModal({ open: true, type: 'detailed_report_pdf' });
                }}
                className="w-full py-2.5 rounded-xl border border-emerald-500/50 text-emerald-400 font-semibold text-xs flex items-center justify-center gap-1.5"
              >
                <UserCheck className="w-4 h-4" />
                {t.ctaCall}
              </button>
            )}
            </section>
          </>
        )}
      </main>

      {/* Bottom Navigation */}
      {isOnboarded && (
        <nav className="fixed bottom-0 left-0 right-0 max-w-lg mx-auto z-30 backdrop-blur-md bg-[var(--bg-card)]/95 border-t border-[var(--border-gold)] px-2 py-2 grid grid-cols-4 gap-1">
          {(
            [
              { id: 'today', label: t.tabToday, Icon: Sun },
              { id: 'jathagam', label: t.tabJathagam, Icon: JothidamEmblem },
              { id: 'porutham', label: t.tabPorutham, Icon: HeartHandshake },
              { id: 'ask', label: t.tabAsk, Icon: Compass },
            ] as const
          ).map(({ id, label, Icon }) => (
            <button
              key={id}
              onClick={() => setTab(id)}
              className={`flex flex-col items-center justify-center py-1 rounded-xl text-[13px] transition ${
                tab === id ? 'text-[#D4AF37] font-bold bg-[#D4AF37]/10' : 'text-[var(--text-muted)]'
              }`}
            >
              <Icon className="w-4 h-4 mb-0.5" />
              <span>{label}</span>
            </button>
          ))}
        </nav>
      )}

      {/* Lead Capture Modal */}
      {leadModal.open && (
        <div className="fixed inset-0 z-50 bg-black/70 flex items-center justify-center p-4">
          <div className="w-full max-w-sm cosmic-card rounded-2xl p-5 space-y-3 relative">
            <button
              onClick={() => setLeadModal({ ...leadModal, open: false })}
              className="absolute top-3 right-3 text-[var(--text-muted)]"
            >
              <X className="w-4 h-4" />
            </button>
            <h3 className="text-base font-bold text-[var(--accent-gold)]">{t.leadTitle}</h3>

            {leadDone ? (
              <p className="text-xs text-emerald-400 py-4">{t.leadSuccess}</p>
            ) : (
              <form onSubmit={handleLeadSubmit} className="space-y-2.5 text-xs">
                <input
                  required
                  placeholder={t.nameLabel}
                  value={leadName}
                  onChange={(e) => setLeadName(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl cosmic-card-alt outline-none"
                />
                <input
                  required
                  placeholder={t.leadPhone}
                  value={leadPhone}
                  onChange={(e) => setLeadPhone(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl cosmic-card-alt outline-none"
                />
                <textarea
                  placeholder="Optional question / notes..."
                  value={leadNotes}
                  onChange={(e) => setLeadNotes(e.target.value)}
                  rows={2}
                  className="w-full px-3 py-2 rounded-xl cosmic-card-alt outline-none"
                />
                {leadError && <p className="text-[11px] text-rose-400">{leadError}</p>}
                <button
                  type="submit"
                  disabled={leadLoading}
                  className="w-full py-2.5 rounded-xl bg-gradient-to-r from-[#D4AF37] to-[#F59E0B] text-[#0B0F19] font-bold disabled:opacity-60"
                >
                  {leadLoading ? '...' : t.leadSubmit}
                </button>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
