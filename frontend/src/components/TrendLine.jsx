import React, { useState } from 'react';
import {
  AreaChart, Area, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine
} from 'recharts';
import { Calendar, TrendingUp } from 'lucide-react';
import { formatIndex, formatDate } from '../utils/formatters';

export default function TrendLine({ data = [] }) {
  const [rangeDays, setRangeDays] = useState(30);

  // Take the last N items and reverse for chronological left-to-right display
  const chartData = [...data].slice(0, rangeDays).reverse();

  // Custom Custom Tooltip
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      return (
        <div className="bg-navy-900 border border-surface-border p-3 rounded-xl shadow-xl text-xs">
          <div className="font-semibold text-slate-300 mb-1">{formatDate(item.date)}</div>
          <div className="flex items-center gap-2">
            <span className="text-slate-400">APIx Index:</span>
            <span className="font-mono font-bold text-brand-teal text-sm">
              {formatIndex(item.apix_value)}
            </span>
          </div>
          {item.change_pct !== null && (
            <div className="text-[11px] text-slate-400 mt-1">
              DoD Change: <span className={item.change_pct > 0 ? 'text-brand-orange' : 'text-brand-teal font-semibold'}>
                {item.change_pct > 0 ? `+${item.change_pct}%` : `${item.change_pct}%`}
              </span>
            </div>
          )}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="glass-panel glass-panel-hover rounded-2xl p-6 border border-surface-border shadow-xl flex flex-col justify-between">
      {/* Header with Time Switcher */}
      <div className="flex flex-wrap items-center justify-between gap-2 mb-4">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-brand-teal" />
          <h2 className="text-sm font-semibold text-slate-200">Historical APIx Index Trend</h2>
        </div>
        <div className="flex items-center bg-navy-900 rounded-lg p-0.5 border border-surface-border text-xs">
          {[7, 15, 30].map(days => (
            <button
              key={days}
              onClick={() => setRangeDays(days)}
              className={`px-3 py-1 rounded-md text-[11px] font-semibold transition-all ${
                rangeDays === days
                  ? 'bg-brand-teal text-navy-950 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {days}D
            </button>
          ))}
        </div>
      </div>

      {/* Chart Canvas */}
      <div className="w-full h-64 mt-2">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="apix-area" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="#00C9A7" stopOpacity={0.35} />
                <stop offset="100%" stopColor="#00C9A7" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1B314D" opacity={0.6} />
            <XAxis
              dataKey="date"
              stroke="#8FA8BA"
              tick={{ fontSize: 10, fill: '#8FA8BA' }}
              tickFormatter={d => d ? d.slice(5) : ''}
            />
            <YAxis
              domain={['dataMin - 2', 'dataMax + 2']}
              stroke="#8FA8BA"
              tick={{ fontSize: 10, fill: '#8FA8BA' }}
              tickFormatter={v => Number(v).toFixed(1)}
            />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine y={100} stroke="#4D96FF" strokeDasharray="4 4" label={{ value: 'Jan 24 Base (100)', fill: '#4D96FF', fontSize: 10, position: 'insideBottomLeft' }} />
            <Area
              type="monotone"
              dataKey="apix_value"
              stroke="#00C9A7"
              strokeWidth={2.5}
              fill="url(#apix-area)"
              dot={{ r: 3, fill: '#00C9A7', strokeWidth: 1.5, stroke: '#0D1B2A' }}
              activeDot={{ r: 6, fill: '#00E5FF', stroke: '#0D1B2A', strokeWidth: 2 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Footer Notes */}
      <div className="flex items-center justify-between text-[11px] text-slate-400 mt-2 pt-2 border-t border-surface-border/40">
        <span>Laspeyres 5-Window Composite Aggregate</span>
        <span className="font-mono text-brand-cyan">Range: {chartData[0]?.date || '—'} → {chartData[chartData.length - 1]?.date || '—'}</span>
      </div>
    </div>
  );
}
