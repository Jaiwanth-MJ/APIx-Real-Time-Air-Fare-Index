import React, { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import APIxGauge from './components/APIxGauge';
import RouteMap from './components/RouteMap';
import TrendLine from './components/TrendLine';
import ElasticityChart from './components/ElasticityChart';
import CarrierComparison from './components/CarrierComparison';
import FareDecomposition from './components/FareDecomposition';
import RouteMatrix from './components/RouteMatrix';
import PipelineControl from './components/PipelineControl';
import BacktestModal from './components/BacktestModal';
import { api } from './api/client';

export default function App() {
  const [indexData, setIndexData] = useState([]);
  const [routesList, setRoutesList] = useState([]);
  const [selectedRoute, setSelectedRoute] = useState('DEL-BOM');
  const [elasticityData, setElasticityData] = useState([]);
  const [carrierData, setCarrierData] = useState([]);
  const [breakdownData, setBreakdownData] = useState({});
  const [pipelineStatus, setPipelineStatus] = useState({});
  const [lastUpdated, setLastUpdated] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isBacktestOpen, setIsBacktestOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch Elasticity for a specific route
  const fetchRouteElasticity = useCallback(async (routeKey) => {
    try {
      const [org, dst] = routeKey.split('-');
      const res = await api.getElasticity(org, dst);
      setElasticityData(res.data.data || []);
      const breakRes = await api.getFareBreakdown(org, dst);
      setBreakdownData(breakRes.data || {});
    } catch (e) {
      console.error('Error fetching route elasticity:', e);
    }
  }, []);

  // Fetch all core metrics
  const fetchAllData = useCallback(async () => {
    setIsRefreshing(true);
    try {
      const [idxRes, routesRes, carriersRes, statusRes] = await Promise.all([
        api.getDailyIndex(30),
        api.getRoutes(),
        api.getCarriersComparison(30),
        api.getPipelineStatus(),
      ]);

      setIndexData(idxRes.data.data || []);
      setRoutesList(routesRes.data.routes || []);
      setCarrierData(carriersRes.data.data || []);
      setPipelineStatus(statusRes.data || {});
      setLastUpdated(new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
      setError(null);

      // Fetch elasticity for selected route
      await fetchRouteElasticity(selectedRoute);
    } catch (e) {
      console.error('APIx Fetch Error:', e);
      setError('Could not connect to APIx backend server. Please verify FastAPI is running.');
    } finally {
      setIsRefreshing(false);
      setLoading(false);
    }
  }, [selectedRoute, fetchRouteElasticity]);

  // Initial load & 5-minute auto-refresh interval
  useEffect(() => {
    fetchAllData();
    const interval = setInterval(fetchAllData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [fetchAllData]);

  // Handler for route change
  const handleSelectRoute = (routeKey) => {
    setSelectedRoute(routeKey);
    fetchRouteElasticity(routeKey);
  };

  // Handler for NSO export
  const handleExportNSO = () => {
    const currentMonth = new Date().toISOString().slice(0, 7);
    window.open(api.getExportNsoUrl(currentMonth), '_blank');
  };

  const latestIndex = indexData[0] || {};
  const routeSnapshot = latestIndex.routes || {};

  return (
    <div className="min-h-screen bg-navy-950 text-slate-100 flex flex-col selection:bg-brand-teal selection:text-navy-950">
      
      {/* Top Navigation Bar */}
      <Header
        lastUpdated={lastUpdated}
        onRefresh={fetchAllData}
        isRefreshing={isRefreshing}
        onOpenBacktest={() => setIsBacktestOpen(true)}
        onExportNSO={handleExportNSO}
      />

      {/* Main Dashboard Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-6 space-y-6">
        
        {/* Error Alert if API is down */}
        {error && (
          <div className="p-4 rounded-xl bg-brand-red/10 border border-brand-red/30 text-brand-red flex items-center justify-between text-xs font-semibold">
            <span>⚠️ {error}</span>
            <button onClick={fetchAllData} className="px-3 py-1 bg-brand-red text-white rounded-md text-[11px] font-bold">
              Retry Connection
            </button>
          </div>
        )}

        {/* Row 1: Headline Gauge + Interactive India Route Map */}
        <section className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-4">
            <APIxGauge
              latestData={latestIndex}
              meta={{ routes_count: routesList.length }}
            />
          </div>
          <div className="lg:col-span-8">
            <RouteMap
              routeSnapshot={routeSnapshot}
              selectedRoute={selectedRoute}
              onSelectRoute={handleSelectRoute}
            />
          </div>
        </section>

        {/* Row 2: Live Pipeline Operations Panel */}
        <section>
          <PipelineControl onPipelineComplete={fetchAllData} />
        </section>

        {/* Row 3: 30-Day Index Trend + Lead-Time Elasticity Curve */}
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <TrendLine data={indexData} />
          <ElasticityChart
            elasticityData={elasticityData}
            selectedRoute={selectedRoute}
            onRouteChange={handleSelectRoute}
          />
        </section>

        {/* Row 4: Carrier Price Competitiveness + Fare Component Decomposition */}
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <CarrierComparison carrierData={carrierData} />
          <FareDecomposition breakdown={breakdownData} />
        </section>

        {/* Row 5: Detailed Route Basket Matrix Table */}
        <section>
          <RouteMatrix
            routes={routesList}
            routeSnapshot={routeSnapshot}
            selectedRoute={selectedRoute}
            onSelectRoute={handleSelectRoute}
          />
        </section>

      </main>

      {/* Backtest Validation Modal */}
      <BacktestModal
        isOpen={isBacktestOpen}
        onClose={() => setIsBacktestOpen(false)}
      />

      {/* Footer */}
      <footer className="border-t border-surface-border py-6 text-center text-xs text-slate-400 bg-navy-950">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className="font-bold text-white">APIx Platform</span>
            <span>· Smart India Hackathon 2026 · PS ID: 26056</span>
          </div>
          <div>
            <span>Ministry of Statistics and Programme Implementation (MoSPI) · NSO</span>
          </div>
        </div>
      </footer>

    </div>
  );
}
