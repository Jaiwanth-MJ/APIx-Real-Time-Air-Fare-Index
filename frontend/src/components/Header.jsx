import React from 'react';
import { Plane, Activity, Download, FileSpreadsheet, ExternalLink, RefreshCw, ShieldCheck } from 'lucide-react';

export default function Header({ 
  lastUpdated, 
  onRefresh, 
  isRefreshing, 
  onOpenBacktest,
  onExportNSO 
}) {
  return (
    <header className="glass-panel sticky top-0 z-40 px-6 py-4 border-b border-surface-border">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        
        {/* Brand & Ministry Identity */}
        <div className="flex items-center gap-4">
          <div className="relative flex items-center justify-center w-11 h-11 rounded-xl bg-gradient-to-br from-brand-teal to-brand-cyan text-navy-950 font-bold shadow-lg shadow-brand-teal/20">
            <Plane className="w-6 h-6 transform -rotate-45" />
            <div className="absolute -top-1 -right-1 w-3.5 h-3.5 bg-brand-teal rounded-full border-2 border-navy-950 animate-ping" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-200 to-brand-teal bg-clip-text text-transparent">
                APIx
              </h1>
              <span className="px-2 py-0.5 text-[10px] font-bold tracking-wider rounded bg-brand-teal/10 text-brand-teal border border-brand-teal/30">
                PS 26056
              </span>
              <span className="px-2 py-0.5 text-[10px] font-semibold tracking-wide rounded bg-brand-cyan/10 text-brand-cyan border border-brand-cyan/30">
                MoSPI / NSO
              </span>
            </div>
            <p className="text-xs text-slate-400 font-medium">
              Real-time Airfare Price Index for India's Consumer Price Index (CPI)
            </p>
          </div>
        </div>

        {/* Action Controls & Live Status */}
        <div className="flex items-center flex-wrap gap-3">
          {/* Live Status Pill */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-navy-900 border border-surface-border text-xs text-slate-300">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-teal opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-brand-teal"></span>
            </span>
            <span className="font-mono text-[11px]">
              {lastUpdated ? `Sync: ${lastUpdated}` : 'Live Polling'}
            </span>
            <button 
              onClick={onRefresh}
              disabled={isRefreshing}
              className={`text-slate-400 hover:text-brand-teal transition-transform duration-300 ${isRefreshing ? 'animate-spin' : ''}`}
              title="Refresh Data"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Backtest Validation Button */}
          <button
            onClick={onOpenBacktest}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-navy-800 hover:bg-navy-700 text-xs font-semibold text-slate-200 border border-surface-border hover:border-brand-teal/40 transition-all duration-200 shadow-sm"
          >
            <ShieldCheck className="w-3.5 h-3.5 text-brand-teal" />
            <span>DGCA Backtest</span>
          </button>

          {/* Export NSO CSV Button */}
          <button
            onClick={onExportNSO}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-brand-teal to-brand-tealDim hover:from-brand-tealDim hover:to-brand-teal text-navy-950 font-bold text-xs shadow-md shadow-brand-teal/20 transition-all duration-200 transform hover:scale-[1.02] active:scale-[0.98]"
          >
            <Download className="w-3.5 h-3.5" />
            <span>NSO Report (.CSV)</span>
          </button>

          {/* API Docs link */}
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-navy-900 hover:bg-navy-800 text-xs font-medium text-slate-300 border border-surface-border hover:text-brand-cyan transition-colors"
          >
            <span>API Docs</span>
            <ExternalLink className="w-3 h-3 text-slate-400" />
          </a>
        </div>

      </div>
    </header>
  );
}
