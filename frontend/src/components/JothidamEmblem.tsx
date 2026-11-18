interface Props {
  className?: string;
  variant?: 'icon' | 'mandala';
}

/** Sacred Lotus + 12-Spoke Zodiac + Golden Sun line illustration emblem. */
export function JothidamEmblem({ className = 'w-6 h-6', variant = 'icon' }: Props) {
  const spokes = Array.from({ length: 12 }, (_, i) => i * 30);
  const petals8 = Array.from({ length: 8 }, (_, i) => i * 45);

  if (variant === 'mandala') {
    return (
      <svg
        viewBox="0 0 200 200"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className={className}
        aria-hidden="true"
      >
        <defs>
          <radialGradient id="sunOrb" cx="40%" cy="35%" r="65%">
            <stop offset="0%" stopColor="#FDE68A" />
            <stop offset="55%" stopColor="#D4AF37" />
            <stop offset="100%" stopColor="#92400E" />
          </radialGradient>
        </defs>

        {/* 12 Radial Zodiac Spokes */}
        {spokes.map((deg) => (
          <g key={`spoke-${deg}`} transform={`rotate(${deg} 100 100)`}>
            <line x1="100" y1="6" x2="100" y2="28" stroke="#D4AF37" strokeWidth="0.9" strokeOpacity="0.55" />
            <circle cx="100" cy="21" r="1.4" fill="#F59E0B" fillOpacity="0.85" />
          </g>
        ))}

        {/* Outer Concentric Zodiac Ring */}
        <circle cx="100" cy="100" r="72" stroke="#D4AF37" strokeWidth="1.2" strokeOpacity="0.85" />
        <circle cx="100" cy="100" r="67" stroke="#D4AF37" strokeWidth="0.7" strokeOpacity="0.45" />

        {/* Outer 12 Lotus Petals (Line Illustration) */}
        {spokes.map((deg) => (
          <path
            key={`op-${deg}`}
            d="M100 32 C108 48, 110 62, 100 72 C90 62, 92 48, 100 32 Z"
            transform={`rotate(${deg + 15} 100 100)`}
            stroke="#D4AF37"
            strokeWidth="1.05"
            strokeOpacity="0.65"
            fill="#D4AF37"
            fillOpacity="0.06"
          />
        ))}

        {/* Inner 8 Sacred Lotus Petals */}
        {petals8.map((deg) => (
          <path
            key={`ip-${deg}`}
            d="M100 44 C110 58, 111 72, 100 80 C89 72, 90 58, 100 44 Z"
            transform={`rotate(${deg} 100 100)`}
            stroke="#F8FAFC"
            strokeWidth="1.15"
            strokeOpacity="0.85"
            fill="#D4AF37"
            fillOpacity="0.12"
          />
        ))}

        {/* Inner Concentric Rings */}
        <circle cx="100" cy="100" r="24" stroke="#D4AF37" strokeWidth="1.3" />
        <circle cx="100" cy="100" r="20" stroke="#F8FAFC" strokeWidth="0.8" strokeDasharray="2 2.5" strokeOpacity="0.75" />

        {/* Central Golden Sun Orb */}
        <circle cx="100" cy="100" r="14" fill="url(#sunOrb)" stroke="#FDE68A" strokeWidth="1" />
      </svg>
    );
  }

  // Clean, airy, non-clumsy Zodiac Dial + Crescent Moon & Sun Star icon
  return (
    <svg
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-hidden="true"
    >
      {/* 12 Zodiac Dial Ticks */}
      {spokes.map((deg) => (
        <line
          key={`tk-${deg}`}
          x1="16"
          y1="2.2"
          x2="16"
          y2="4.4"
          transform={`rotate(${deg} 16 16)`}
          stroke="currentColor"
          strokeWidth="1.35"
          strokeLinecap="round"
          strokeOpacity="0.85"
        />
      ))}
      {/* Inner Sacred Ring */}
      <circle cx="16" cy="16" r="9.6" stroke="currentColor" strokeWidth="1.2" strokeOpacity="0.45" />
      {/* Crescent Moon */}
      <path
        d="M17.8 9.8 A6.4 6.4 0 1 0 22.2 20.6 A5.2 5.2 0 1 1 17.8 9.8 Z"
        fill="currentColor"
      />
      {/* Nakshatra Star / Sun */}
      <circle cx="19.5" cy="14" r="2.1" fill="currentColor" />
    </svg>
  );
}
