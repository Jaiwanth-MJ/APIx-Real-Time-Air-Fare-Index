import React from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, Area
} from 'recharts';
import { Clock, HelpCircle, ArrowUpRight } from 'lucide-react';
import { formatINR } from '../utils/formatters';

const DGCA_ROUTES = [
  'DEL-BOM', 'DEL-BLR', 'BOM-BLR', 'DEL-CCU',
  'BLR-HYD', 'MAA-DEL', 'BOM-CCU', 'DEL-MAA'
];

export default function ElasticityChart({
  elasticityData = [],
  selectedRoute = 'DEL-BOM',
  onRouteChange
}) {
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-navy-900 border border-surface-border p-3 rounded-xl shadow-xl text-xs space-y-1">
          <div className="font-bold text-brand-cyan mb-1.5 flex items-center justify-between">
            <span>Advance Window: {label}</span>
          </div>
          {payload.map((entry, index) => (
            <div key={index} className="flex justify-between items-center gap-4 text-[11px]">
              <span className="flex items-center gap-1.5" style={{ color: entry.color }}>
                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
                {entry.name}:
              </span>
              <span className="font-mono font-bold text-slate-100">
                {formatINR(entry.value)}
              </span>
            </div>
          ))}
          <div className="text-[10px] text-slate-400 mt-2 pt-1 border-t border-surface-border">
            IQR Spread: {formatINR((payload.find(p => p.dataKey === 'p75_fare')?.value || 0) - (payload.find(p => p.dataKey === 'p25_fare')?.value || 0))}
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="glass-panel glass-panel-hover rounded-2xl p-6 border border-surface-border shadow-xl flex flex-col justify-between">
      
      {/* Header & Route Selector */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
        <div>
          <div className="flex items-center gap-1.5">
            <Clock className="w-4 h-4 text-brand-cyan" />
            <h2 className="text-sm font-semibold text-slate-200">Lead-Time Fare Elasticity Curve</h2>
          </div>
          <p className="text-[11px] text-slate-400 mt-0.5">
            Dynamic pricing variance from T+1 (Last Minute) to T+45 (Early Bird)
          </p>
        </div>

        {/* Route Dropdown Selector */}
        <div className="flex items-center gap-2">
          <label className="text-[11px] text-slate-400 font-medium">Route:</label>
          <select
            value={selectedRoute}
            onChange={(e) => onRouteChange(e.target.value)}
            className="bg-navy-900 border border-surface-border text-slate-200 text-xs font-mono font-bold rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-brand-teal"
          >
            {DGCA_ROUTES.map(r => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Chart Canvas */}
      <div className="w-full h-64 mt-1">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={elasticityData} margin={{ top: 10, right: 15, left: -10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1B314D" opacity={0.6} />
            <XAxis
              dataKey="label"
              stroke="#8FA8BA"
              tick={{ fontSize: 11, fill: '#8FA8BA' }}
            />
            <YAxis
              stroke="#8FA8BA"
              tick={{ fontSize: 10, fill: '#8FA8BA' }}
              tickFormatter={v => `₹${(v / 1000).toFixed(1)}k`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ fontSize: 11, paddingTop: 6 }}
              formatter={(value) => <span className="text-slate-300 font-medium">{value}</span>}
            />

            {/* 75th Percentile Line */}
            <Line
              type="monotone"
              dataKey="p75_fare"
              name="75th Percentile (Peak Fares)"
              stroke="#FF9F43"
              strokeDasharray="4 4"
              strokeWidth={1.8}
              dot={{ r: 3, fill: '#FF9F43' }}
            />

            {/* Median Line (Primary) */}
            <Line
              type="monotone"
              dataKey="median_fare"
              name="Median Fare"
              stroke="#00C9A7"
              strokeWidth={3}
              dot={{ r: 4, fill: '#00C9A7', stroke: '#0D1B2A', strokeWidth: 2 }}
              activeDot={{ r: 7, fill: '#00E5FF' }}
            />

            {/* 25th Percentile Line */}
            <Line
              type="monotone"
              dataKey="p25_fare"
              name="25th Percentile (Promo Fares)"
              stroke="#00E5FF"
              strokeDasharray="4 4"
              strokeWidth={1.8}
              dot={{ r: 3, fill: '#00E5FF' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Insight Callout */}
      <div className="flex items-center justify-between text-[11px] text-slate-400 mt-2 pt-2 border-t border-surface-border/40">
        <span className="flex items-center gap-1 text-slate-300">
          <ArrowUpRight className="w-3.5 h-3.5 text-brand-orange" />
          <span className="font-semibold text-brand-orange">
            {elasticityData.length >= 2 
              ? `${Math.round(((elasticityData[0]?.median_fare - elasticityData[elasticityData.length - 1]?.median_fare) / elasticityData[elasticityData.length - 1]?.median_fare) * 100)}% Surge` 
              : 'Dynamic Surge'
            }
          </span>
          on T+1 departures vs T+45 advance bookings
        </span>
        <span className="font-mono text-[10px]">DGCA Window Weights Applied</span>
      </div>
    </div>
  );
}
