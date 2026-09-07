import React from 'react';
import { TrendingUp, TrendingDown, Layers, Database, BarChart3, AlertCircle } from 'lucide-react';
import { formatIndex, formatPct } from '../utils/formatters';

export default function APIxGauge({ latestData, meta }) {
  const apixVal = latestData?.apix_value || 132.48;
  const changePct = latestData?.change_pct ?? 0.0;
  const changeAbs = latestData?.change_abs ?? 0.0;
  const isSurge = changePct > 0;
  const sampleSize = latestData?.sample_size || 80;

  // Calculate percentage along range (e.g. 80 to 180)
  const minVal = 80;
  const maxVal = 180;
  const pct = Math.min(100, Math.max(0, ((apixVal - minVal) / (maxVal - minVal)) * 100));

  return (
    <div className="glass-panel glass-panel-hover rounded-2xl p-6 flex flex-col justify-between relative overflow-hidden border border-surface-border shadow-xl">
      {/* Background Accent Glow */}
      <div className="absolute -top-16 -right-16 w-44 h-44 bg-brand-teal/10 rounded-full blur-3xl pointer-events-none" />

      {/* Card Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <span className="text-[11px] font-bold tracking-wider text-brand-teal uppercase">
            Headline Price Index
          </span>
          <h2 className="text-sm font-semibold text-slate-200">Current APIx Value</h2>
        </div>
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-navy-900 border border-surface-border text-[11px] text-slate-300 font-mono">
          <Database className="w-3 h-3 text-brand-cyan" />
          <span>Base: Jan 2024 = 100</span>
        </div>
      </div>

      {/* Gauge Value Display */}
      <div className="my-2 flex flex-col items-center justify-center text-center">
        {/* Radial Arc Indicator */}
        <div className="relative w-48 h-24 flex items-end justify-center mb-3">
          <svg className="w-48 h-24 overflow-visible" viewBox="0 0 100 50">
            {/* Background Arc */}
            <path
              d="M 10 45 A 40 40 0 0 1 90 45"
              fill="none"
              stroke="#1B314D"
              strokeWidth="8"
              strokeLinecap="round"
            />
            {/* Value Indicator Arc */}
            <path
              d="M 10 45 A 40 40 0 0 1 90 45"
              fill="none"
              stroke="url(#gauge-gradient)"
              strokeWidth="8"
              strokeDasharray="125.6"
              strokeDashoffset={125.6 - (125.6 * pct) / 100}
              strokeLinecap="round"
              className="transition-all duration-1000 ease-out"
            />
            <defs>
              <linearGradient id="gauge-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#00E5FF" />
                <stop offset="50%" stopColor="#00C9A7" />
                <stop offset="100%" stopColor="#FF9F43" />
              </linearGradient>
            </defs>
          </svg>
          <div className="absolute -bottom-1 flex flex-col items-center">
            <span className="text-4xl font-extrabold tracking-tight font-mono text-white">
              {formatIndex(apixVal)}
            </span>
          </div>
        </div>

        {/* Day-over-Day Delta Pill */}
        <div className="flex items-center gap-2 mt-2">
          <div className={`flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold ${
            isSurge 
              ? 'bg-brand-orange/15 text-brand-orange border border-brand-orange/30' 
              : 'bg-brand-teal/15 text-brand-teal border border-brand-teal/30'
          }`}>
            {isSurge ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
            <span>{formatPct(changePct)}</span>
            <span className="text-[10px] text-slate-400 font-normal">({changeAbs > 0 ? `+${changeAbs}` : changeAbs} pts)</span>
          </div>
          <span className="text-[11px] text-slate-400">vs yesterday</span>
        </div>
      </div>

      {/* Footer Metrics Grid */}
      <div className="mt-5 pt-4 border-t border-surface-border grid grid-cols-3 gap-2 text-center text-[11px]">
        <div className="bg-navy-900/60 rounded-lg p-2 border border-surface-border/50">
          <div className="text-slate-400 text-[10px] uppercase font-semibold">CPI Weight</div>
          <div className="font-mono font-bold text-slate-200 mt-0.5">0.39%</div>
        </div>
        <div className="bg-navy-900/60 rounded-lg p-2 border border-surface-border/50">
          <div className="text-slate-400 text-[10px] uppercase font-semibold">Routes</div>
          <div className="font-mono font-bold text-brand-teal mt-0.5">8 DGCA</div>
        </div>
        <div className="bg-navy-900/60 rounded-lg p-2 border border-surface-border/50">
          <div className="text-slate-400 text-[10px] uppercase font-semibold">Daily Samples</div>
          <div className="font-mono font-bold text-brand-cyan mt-0.5">{sampleSize * 5}+</div>
        </div>
      </div>
    </div>
  );
}
