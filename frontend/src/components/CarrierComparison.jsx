import React from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell
} from 'recharts';
import { PlaneTakeoff, Award } from 'lucide-react';
import { formatINR } from '../utils/formatters';

const CARRIER_COLORS = {
  '6E': '#00C9A7', // IndiGo Teal
  'AI': '#FF5252', // Air India Red
  'QP': '#FF9F43', // Akasa Orange
  'SG': '#FFC107', // SpiceJet Yellow
  'I5': '#00E5FF', // AIX Cyan
};

export default function CarrierComparison({ carrierData = [] }) {
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const d = payload[0].payload;
      return (
        <div className="bg-navy-900 border border-surface-border p-3 rounded-xl shadow-xl text-xs space-y-1">
          <div className="font-bold text-white text-sm">{d.name} ({d.carrier})</div>
          <div className="flex justify-between items-center gap-4 text-slate-300">
            <span>Average Total Fare:</span>
            <span className="font-mono font-bold text-brand-teal text-sm">{formatINR(d.avg_fare)}</span>
          </div>
          <div className="text-[10px] text-slate-400">
            Observed Samples: <span className="font-mono text-slate-200">{d.sample_count}</span> quotes
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="glass-panel glass-panel-hover rounded-2xl p-6 border border-surface-border shadow-xl flex flex-col justify-between">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <PlaneTakeoff className="w-4 h-4 text-brand-teal" />
          <h2 className="text-sm font-semibold text-slate-200">Domestic Airline Price Competitiveness</h2>
        </div>
        <span className="text-[11px] font-mono text-slate-400">30-Day Median Basket</span>
      </div>

      {/* Chart */}
      <div className="w-full h-56 mt-2">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={carrierData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1B314D" opacity={0.6} />
            <XAxis
              dataKey="name"
              stroke="#8FA8BA"
              tick={{ fontSize: 11, fill: '#8FA8BA' }}
            />
            <YAxis
              stroke="#8FA8BA"
              tick={{ fontSize: 10, fill: '#8FA8BA' }}
              tickFormatter={v => `₹${(v / 1000).toFixed(1)}k`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="avg_fare" radius={[6, 6, 0, 0]}>
              {carrierData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={CARRIER_COLORS[entry.carrier] || '#00C9A7'}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Carrier Badges Footer */}
      <div className="grid grid-cols-5 gap-1.5 pt-3 border-t border-surface-border/40 text-center text-[10px]">
        {carrierData.map(c => (
          <div key={c.carrier} className="bg-navy-900/60 rounded p-1 border border-surface-border/40">
            <span className="font-bold text-slate-300">{c.carrier}</span>
            <div className="font-mono text-slate-400 mt-0.5">{formatINR(c.avg_fare)}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
