import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { PieChart as PieIcon, Info } from 'lucide-react';
import { formatINR } from '../utils/formatters';

const COLORS = ['#00C9A7', '#4D96FF', '#FF9F43', '#FF5252'];

export default function FareDecomposition({ breakdown = {} }) {
  const data = [
    { name: 'Base Fare', value: breakdown.base_fare || 3600, pct: breakdown.proportions?.base_pct || 68 },
    { name: 'Taxes & GST (5%)', value: breakdown.taxes || 950, pct: breakdown.proportions?.taxes_pct || 18 },
    { name: 'User Dev Fee (UDF)', value: breakdown.udf || 450, pct: breakdown.proportions?.udf_pct || 8 },
    { name: 'Convenience Fee', value: breakdown.convenience_fee || 300, pct: breakdown.proportions?.fee_pct || 6 },
  ];

  const total = breakdown.total_fare || 5300;

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const d = payload[0].payload;
      return (
        <div className="bg-navy-900 border border-surface-border p-3 rounded-xl shadow-xl text-xs space-y-1">
          <div className="font-bold text-white text-sm">{d.name}</div>
          <div className="flex justify-between items-center gap-4 text-slate-300">
            <span>Average Amount:</span>
            <span className="font-mono font-bold text-brand-teal text-sm">{formatINR(d.value)}</span>
          </div>
          <div className="text-[11px] text-brand-cyan">
            Share of Ticket: <span className="font-bold">{d.pct}%</span>
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
          <PieIcon className="w-4 h-4 text-brand-teal" />
          <h2 className="text-sm font-semibold text-slate-200">Fare Component Decomposition</h2>
        </div>
        <span className="text-[11px] font-mono text-slate-400">Total: {formatINR(total)}</span>
      </div>

      {/* Visual Pie + Legend Grid */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-2 items-center my-auto">
        {/* Donut Chart */}
        <div className="md:col-span-5 h-44 flex items-center justify-center relative">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={45}
                outerRadius={68}
                paddingAngle={4}
                dataKey="value"
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
          <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
            <span className="text-[10px] text-slate-400 uppercase font-semibold">Base</span>
            <span className="text-sm font-mono font-bold text-white">{data[0].pct}%</span>
          </div>
        </div>

        {/* Legend List */}
        <div className="md:col-span-7 space-y-2 text-xs">
          {data.map((item, idx) => (
            <div key={item.name} className="flex items-center justify-between bg-navy-900/60 p-2 rounded-lg border border-surface-border/40">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: COLORS[idx] }} />
                <span className="text-slate-300 font-medium">{item.name}</span>
              </div>
              <div className="flex items-center gap-2 font-mono">
                <span className="text-slate-400 text-[11px]">{item.pct}%</span>
                <span className="font-bold text-white">{formatINR(item.value)}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer policy note */}
      <div className="flex items-center justify-between text-[11px] text-slate-400 pt-2 border-t border-surface-border/40">
        <span>Separates base ticket prices from statutory airport user development charges</span>
      </div>
    </div>
  );
}
