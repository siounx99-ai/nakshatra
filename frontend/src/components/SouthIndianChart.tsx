import type { GrahaItem } from '../types';

interface Props {
  grahas: GrahaItem[];
  mode: 'rasi' | 'navamsam';
  centerTitle: string;
}

// 4x4 grid coordinates -> Rasi index (0=Mesham/Aries .. 11=Meenam/Pisces), null for center 2x2
const GRID_CELLS: (number | null)[][] = [
  [11, 0, 1, 2],
  [10, null, null, 3],
  [9, null, null, 4],
  [8, 7, 6, 5],
];

const SHORT_RASI = ['மே/Ar', 'ரி/Ta', 'மி/Ge', 'க/Ca', 'சி/Le', 'கன்/Vi', 'து/Li', 'வி/Sc', 'த/Sa', 'ம/Cp', 'கு/Aq', 'மீ/Pi'];

export function SouthIndianChart({ grahas, mode, centerTitle }: Props) {
  const getPlanetsInBox = (rasiIdx: number) =>
    grahas.filter((g) => (mode === 'rasi' ? g.rasi_idx === rasiIdx : g.navamsam_idx === rasiIdx));

  return (
    <div className="w-full max-w-[360px] mx-auto aspect-square grid grid-cols-4 grid-rows-4 rounded-xl overflow-hidden border-2 border-[#D4AF37]/60 bg-[#0B0F19]/40">
      {GRID_CELLS.map((row, rIdx) =>
        row.map((rasiIdx, cIdx) => {
          // Render merged center 2x2 once at (1,1)
          if (rIdx === 1 && cIdx === 1) {
            return (
              <div
                key="center"
                className="col-span-2 row-span-2 flex flex-col items-center justify-center p-2 border border-[#D4AF37]/30 text-center"
              >
                <span className="text-xs uppercase tracking-widest text-[#D4AF37] font-semibold">
                  {centerTitle}
                </span>
                <span className="text-[11px] opacity-60 mt-1">South Indian</span>
              </div>
            );
          }
          if (rasiIdx === null) return null;

          const planets = getPlanetsInBox(rasiIdx);
          const hasAsc = planets.some((p) => p.key === 'Ascendant');

          return (
            <div
              key={`${rIdx}-${cIdx}`}
              className={`relative border border-[#D4AF37]/30 p-1.5 flex flex-col justify-between min-h-[72px] ${
                hasAsc ? 'bg-[#D4AF37]/10' : ''
              }`}
            >
              <span className="text-[9px] opacity-45 leading-none">{SHORT_RASI[rasiIdx]}</span>
              <div className="flex flex-wrap gap-1 items-center justify-center my-auto">
                {planets.map((p) => (
                  <span
                    key={p.key}
                    className={`text-[11px] font-semibold px-1 py-0.5 rounded ${
                      p.key === 'Ascendant'
                        ? 'bg-[#D4AF37] text-[#0B0F19]'
                        : p.key === 'Moon'
                        ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                        : 'text-[#F59E0B]'
                    }`}
                  >
                    {p.short}
                    {p.retrograde ? '*' : ''}
                  </span>
                ))}
              </div>
            </div>
          );
        })
      )}
    </div>
  );
}
