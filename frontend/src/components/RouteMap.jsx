import React, { useState } from 'react';
import { MapPin, Navigation, Compass, Layers, Info } from 'lucide-react';
import { formatIndex, formatINR } from '../utils/formatters';

// Geolocation coordinates mapped to a 500x520 viewport for India
const AIRPORTS = {
  DEL: { x: 200, y: 140, name: 'Delhi (IGI)', code: 'DEL' },
  BOM: { x: 130, y: 310, name: 'Mumbai (CSMI)', code: 'BOM' },
  BLR: { x: 215, y: 430, name: 'Bengaluru (KIA)', code: 'BLR' },
  CCU: { x: 385, y: 240, name: 'Kolkata (NSCBI)', code: 'CCU' },
  HYD: { x: 235, y: 350, name: 'Hyderabad (RGIA)', code: 'HYD' },
  MAA: { x: 255, y: 445, name: 'Chennai (MAA)', code: 'MAA' }
};

const DGCA_ROUTES = [
  { id: 'DEL-BOM', from: 'DEL', to: 'BOM', weight: 0.22, rank: 1, baseFare: 4800 },
  { id: 'DEL-BLR', from: 'DEL', to: 'BLR', weight: 0.18, rank: 2, baseFare: 5400 },
  { id: 'BOM-BLR', from: 'BOM', to: 'BLR', weight: 0.14, rank: 3, baseFare: 3900 },
  { id: 'DEL-CCU', from: 'DEL', to: 'CCU', weight: 0.12, rank: 4, baseFare: 4600 },
  { id: 'BLR-HYD', from: 'BLR', to: 'HYD', weight: 0.10, rank: 5, baseFare: 3200 },
  { id: 'MAA-DEL', from: 'MAA', to: 'DEL', weight: 0.09, rank: 6, baseFare: 5600 },
  { id: 'BOM-CCU', from: 'BOM', to: 'CCU', weight: 0.08, rank: 7, baseFare: 5100 },
  { id: 'DEL-MAA', from: 'DEL', to: 'MAA', weight: 0.07, rank: 8, baseFare: 5500 },
];

export default function RouteMap({ routeSnapshot = {}, selectedRoute, onSelectRoute }) {
  const [hoveredRoute, setHoveredRoute] = useState(null);

  // Helper for curved flight path arc
  const getCurvePath = (p1, p2, curveOffset = 25) => {
    const mx = (p1.x + p2.x) / 2;
    const my = (p1.y + p2.y) / 2;
    // Perpendicular vector for arc curve
    const dx = p2.x - p1.x;
    const dy = p2.y - p1.y;
    const len = Math.sqrt(dx * dx + dy * dy);
    const cx = mx - (dy / len) * curveOffset;
    const cy = my + (dx / len) * curveOffset;
    return `M ${p1.x} ${p1.y} Q ${cx} ${cy} ${p2.x} ${p2.y}`;
  };

  const getRouteColor = (subIndexVal) => {
    if (!subIndexVal) return '#00C9A7';
    const v = parseFloat(subIndexVal);
    if (v > 135) return '#FF5252';  // Red (Surge)
    if (v > 125) return '#FF9F43';  // Orange (High)
    if (v > 105) return '#00E5FF';  // Cyan (Moderate)
    return '#00C9A7';               // Teal (Normal/Low)
  };

  const activeRouteData = DGCA_ROUTES.find(r => r.id === (selectedRoute || hoveredRoute)) || DGCA_ROUTES[0];
  const activeSubIndex = routeSnapshot[activeRouteData.id] || 132.4;

  return (
    <div className="glass-panel glass-panel-hover rounded-2xl p-6 relative overflow-hidden border border-surface-border shadow-xl flex flex-col justify-between">
      
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Navigation className="w-4 h-4 text-brand-teal" />
          <h2 className="text-sm font-semibold text-slate-200">DGCA Route Basket Network</h2>
        </div>
        <div className="flex items-center gap-3 text-[11px] text-slate-400">
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-brand-teal"></span> &lt;105</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-brand-cyan"></span> 105–125</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-brand-orange"></span> 125–135</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-brand-red"></span> &gt;135</span>
        </div>
      </div>

      {/* Main Map Visual Area */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-center my-auto">
        
        {/* SVG India Air Corridor Visualizer */}
        <div className="lg:col-span-8 relative flex items-center justify-center py-2">
          <svg className="w-full max-w-[420px] h-[340px] overflow-visible" viewBox="50 80 400 400">
            {/* Background Map Contours */}
            <g opacity="0.18">
              <path
                d="M 180 100 L 220 110 L 250 140 L 320 170 L 380 200 L 400 250 L 370 290 L 300 340 L 270 410 L 240 470 L 210 440 L 160 380 L 120 330 L 110 270 L 130 200 Z"
                fill="#16283D"
                stroke="#223F5E"
                strokeWidth="1.5"
              />
            </g>

            {/* Flight Corridor Paths */}
            {DGCA_ROUTES.map((route, i) => {
              const p1 = AIRPORTS[route.from];
              const p2 = AIRPORTS[route.to];
              const subVal = routeSnapshot[route.id];
              const color = getRouteColor(subVal);
              const isSelected = selectedRoute === route.id;
              const isHovered = hoveredRoute === route.id;

              return (
                <g key={route.id} className="cursor-pointer" onClick={() => onSelectRoute(route.id)} onMouseEnter={() => setHoveredRoute(route.id)} onMouseLeave={() => setHoveredRoute(null)}>
                  {/* Glow path */}
                  <path
                    d={getCurvePath(p1, p2, 15 + i * 2)}
                    fill="none"
                    stroke={color}
                    strokeWidth={isSelected || isHovered ? 4 : 1.8}
                    strokeOpacity={isSelected || isHovered ? 0.9 : 0.45}
                    className="transition-all duration-300"
                  />
                  {/* Flow Animation Dash */}
                  {(isSelected || isHovered) && (
                    <path
                      d={getCurvePath(p1, p2, 15 + i * 2)}
                      fill="none"
                      stroke="#FFFFFF"
                      strokeWidth="2"
                      strokeDasharray="6 14"
                      className="animate-radar"
                    />
                  )}
                </g>
              );
            })}

            {/* Airport City Nodes */}
            {Object.entries(AIRPORTS).map(([code, p]) => (
              <g key={code} transform={`translate(${p.x}, ${p.y})`}>
                <circle r="9" fill="#00C9A7" fillOpacity="0.2" className="animate-ping" />
                <circle r="5" fill="#0D1B2A" stroke="#00C9A7" strokeWidth="2.5" />
                <text
                  x="0"
                  y="-10"
                  textAnchor="middle"
                  className="fill-slate-200 font-mono font-bold text-[11px] drop-shadow-md pointer-events-none"
                >
                  {code}
                </text>
              </g>
            ))}
          </svg>
        </div>

        {/* Selected Route Info Card */}
        <div className="lg:col-span-4 flex flex-col justify-center space-y-3 bg-navy-900/80 rounded-xl p-4 border border-surface-border">
          <div className="flex items-center justify-between pb-2 border-b border-surface-border/60">
            <div>
              <span className="text-[10px] uppercase font-bold tracking-wider text-brand-cyan">Selected Corridor</span>
              <h3 className="text-base font-extrabold text-white">{activeRouteData.id}</h3>
            </div>
            <span className="px-2 py-0.5 rounded bg-brand-teal/15 text-brand-teal font-mono text-xs font-bold">
              Rank #{activeRouteData.rank}
            </span>
          </div>

          <div className="space-y-2 text-xs">
            <div className="flex justify-between items-center text-slate-300">
              <span className="text-slate-400">DGCA Weight ($w_r$):</span>
              <span className="font-mono font-bold text-brand-teal">{(activeRouteData.weight * 100).toFixed(0)}%</span>
            </div>
            <div className="flex justify-between items-center text-slate-300">
              <span className="text-slate-400">Sub-Index Value:</span>
              <span className="font-mono font-bold text-white">{formatIndex(activeSubIndex)}</span>
            </div>
            <div className="flex justify-between items-center text-slate-300">
              <span className="text-slate-400">Base Fare (Jan 24):</span>
              <span className="font-mono text-slate-300">{formatINR(activeRouteData.baseFare)}</span>
            </div>
            <div className="flex justify-between items-center text-slate-300">
              <span className="text-slate-400">Est. Current Fare:</span>
              <span className="font-mono font-bold text-brand-cyan">{formatINR(activeRouteData.baseFare * (activeSubIndex / 100))}</span>
            </div>
          </div>

          <button
            onClick={() => onSelectRoute(activeRouteData.id)}
            className="w-full mt-2 py-1.5 px-3 rounded-lg bg-navy-800 hover:bg-navy-700 text-slate-200 text-xs font-semibold border border-surface-border transition-colors text-center"
          >
            Inspect Route Elasticity →
          </button>
        </div>

      </div>

      {/* Footer Instructions */}
      <div className="flex items-center justify-between text-[11px] text-slate-400 border-t border-surface-border/50 pt-2">
        <span className="flex items-center gap-1">
          <Info className="w-3 h-3 text-brand-cyan" />
          Click any flight corridor to filter elasticity & fare comparisons.
        </span>
        <span className="font-mono">8 Major Trunks · 86% Domestic Volume</span>
      </div>
    </div>
  );
}
