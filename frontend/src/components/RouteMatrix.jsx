import React from 'react';
import { Table, ArrowRight, ExternalLink } from 'lucide-react';
import { formatIndex, formatINR } from '../utils/formatters';

export default function RouteMatrix({ routes = [], routeSnapshot = {}, selectedRoute, onSelectRoute }) {
  return (
    <div className="glass-panel glass-panel-hover rounded-2xl p-6 border border-surface-border shadow-xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Table className="w-4 h-4 text-brand-teal" />
          <h2 className="text-sm font-semibold text-slate-200">DGCA Route Basket Sub-Index Breakdown</h2>
        </div>
        <span className="text-[11px] font-mono text-slate-400">Total Weight: 100.0%</span>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-surface-border text-slate-400 uppercase text-[10px] tracking-wider">
              <th className="pb-3 font-semibold">Rank</th>
              <th className="pb-3 font-semibold">Corridor</th>
              <th className="pb-3 font-semibold">DGCA Weight ($w_r$)</th>
              <th className="pb-3 font-semibold">Sub-Index</th>
              <th className="pb-3 font-semibold">Est. Route Fare</th>
              <th className="pb-3 font-semibold text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-surface-border/40">
            {routes.map((r) => {
              const routeKey = `${r.origin}-${r.destination}`;
              const subIndex = routeSnapshot[routeKey] || 132.0;
              const isSelected = selectedRoute === routeKey;

              const getBadgeColor = (val) => {
                const v = parseFloat(val);
                if (v > 135) return 'bg-brand-red/15 text-brand-red border-brand-red/30';
                if (v > 125) return 'bg-brand-orange/15 text-brand-orange border-brand-orange/30';
                if (v > 105) return 'bg-brand-cyan/15 text-brand-cyan border-brand-cyan/30';
                return 'bg-brand-teal/15 text-brand-teal border-brand-teal/30';
              };

              return (
                <tr
                  key={r.id}
                  onClick={() => onSelectRoute(routeKey)}
                  className={`cursor-pointer transition-colors ${
                    isSelected ? 'bg-brand-teal/10' : 'hover:bg-navy-900/60'
                  }`}
                >
                  <td className="py-3 font-mono font-bold text-slate-400">#{r.dgca_rank}</td>
                  <td className="py-3 font-bold text-white flex items-center gap-1.5">
                    <span>{r.origin}</span>
                    <ArrowRight className="w-3 h-3 text-brand-teal" />
                    <span>{r.destination}</span>
                  </td>
                  <td className="py-3 font-mono font-semibold text-slate-300">
                    {(r.weight * 100).toFixed(0)}%
                  </td>
                  <td className="py-3 font-mono">
                    <span className={`px-2 py-0.5 rounded text-[11px] font-bold border ${getBadgeColor(subIndex)}`}>
                      {formatIndex(subIndex)}
                    </span>
                  </td>
                  <td className="py-3 font-mono font-semibold text-brand-cyan">
                    {r.latest_avg_fare ? formatINR(r.latest_avg_fare) : formatINR(4800 * (subIndex / 100))}
                  </td>
                  <td className="py-3 text-right">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectRoute(routeKey);
                      }}
                      className={`px-2.5 py-1 rounded text-[11px] font-semibold transition-colors ${
                        isSelected 
                          ? 'bg-brand-teal text-navy-950 font-bold' 
                          : 'bg-navy-800 text-slate-300 hover:text-white'
                      }`}
                    >
                      {isSelected ? 'Selected' : 'Inspect'}
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
