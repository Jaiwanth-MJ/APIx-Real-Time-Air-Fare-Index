import React, { useState } from 'react';
import { Play, CheckCircle2, AlertCircle, RefreshCw, Cpu, Database, Zap } from 'lucide-react';
import { api } from '../api/client';

export default function PipelineControl({ onPipelineComplete }) {
  const [loading, setLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState(null);
  const [statusType, setStatusType] = useState('info'); // 'info', 'success', 'error'

  const handleRunFullScrape = async () => {
    setLoading(true);
    setStatusMsg('Running Playwright & Scrapy collection across 5 airlines & 6 OTAs...');
    setStatusType('info');

    try {
      const res = await api.triggerScrape();
      setStatusMsg(`Success! Collected ${res.data.raw_quotes_scraped} new fare quotes. Updated APIx Index to ${res.data.new_apix_value}.`);
      setStatusType('success');
      if (onPipelineComplete) onPipelineComplete();
    } catch (e) {
      setStatusMsg(`Pipeline error: ${e.response?.data?.message || e.message}`);
      setStatusType('error');
    } finally {
      setLoading(false);
    }
  };

  const handleRecalcIndex = async () => {
    setLoading(true);
    setStatusMsg('Recalculating Laspeyres index and rolling aggregations...');
    setStatusType('info');

    try {
      const res = await api.triggerIndexRecalc();
      setStatusMsg(`Success! Recomputed APIx: ${res.data.apix_value} across ${Object.keys(res.data.routes_snapshot || {}).length} routes.`);
      setStatusType('success');
      if (onPipelineComplete) onPipelineComplete();
    } catch (e) {
      setStatusMsg(`Index calculation error: ${e.response?.data?.message || e.message}`);
      setStatusType('error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel glass-panel-hover rounded-2xl p-6 border border-surface-border shadow-xl">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        
        {/* Left Info */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-brand-teal/15 text-brand-teal flex items-center justify-center border border-brand-teal/30">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-white">Live Pipeline Operations Panel</h3>
              <span className="px-2 py-0.5 rounded bg-brand-teal/20 text-brand-teal text-[10px] font-mono font-bold">
                Airflow / Daemon Engine
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Trigger automated real-time scraping, IQR cleaning, and index recalculation on demand
            </p>
          </div>
        </div>

        {/* Action Triggers */}
        <div className="flex items-center flex-wrap gap-2.5">
          <button
            onClick={handleRecalcIndex}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-navy-900 hover:bg-navy-800 text-slate-200 text-xs font-semibold border border-surface-border hover:border-brand-cyan/40 transition-all disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-brand-cyan ${loading ? 'animate-spin' : ''}`} />
            <span>Recalculate Index</span>
          </button>

          <button
            onClick={handleRunFullScrape}
            disabled={loading}
            className="flex items-center gap-2 px-5 py-2 rounded-xl bg-gradient-to-r from-brand-teal via-brand-tealDim to-brand-teal text-navy-950 text-xs font-extrabold shadow-lg shadow-brand-teal/25 hover:shadow-brand-teal/40 transition-all transform hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50"
          >
            <Zap className={`w-4 h-4 fill-current ${loading ? 'animate-bounce' : ''}`} />
            <span>{loading ? 'Ingesting Batch...' : 'Trigger Live Scrape & ETL'}</span>
          </button>
        </div>

      </div>

      {/* Status Output Bar */}
      {statusMsg && (
        <div className={`mt-4 p-3 rounded-xl flex items-center gap-2.5 text-xs font-medium border ${
          statusType === 'success' ? 'bg-brand-teal/10 text-brand-teal border-brand-teal/30' :
          statusType === 'error' ? 'bg-brand-red/10 text-brand-red border-brand-red/30' :
          'bg-brand-cyan/10 text-brand-cyan border-brand-cyan/30'
        }`}>
          {statusType === 'success' ? <CheckCircle2 className="w-4 h-4 shrink-0" /> :
           statusType === 'error' ? <AlertCircle className="w-4 h-4 shrink-0" /> :
           <RefreshCw className="w-4 h-4 shrink-0 animate-spin" />}
          <span>{statusMsg}</span>
        </div>
      )}
    </div>
  );
}
