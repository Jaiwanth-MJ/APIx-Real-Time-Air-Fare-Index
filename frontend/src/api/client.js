import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Index queries
  getDailyIndex: (days = 30) => client.get(`/api/v1/index/daily?days=${days}`),
  getMonthlyIndex: (months = 12) => client.get(`/api/v1/index/monthly?months=${months}`),
  getWeeklyIndex: (weeks = 8) => client.get(`/api/v1/index/weekly?weeks=${weeks}`),

  // Fares & Elasticity
  getRoutes: () => client.get('/api/v1/fares/routes'),
  getRouteFares: (org, dst, days = 7) => client.get(`/api/v1/fares/route/${org}/${dst}?days=${days}`),
  getElasticity: (org, dst, days = 30) => client.get(`/api/v1/fares/elasticity/${org}/${dst}?days=${days}`),
  getCarriersComparison: (days = 30) => client.get(`/api/v1/fares/carriers/comparison?days=${days}`),
  getFareBreakdown: (org, dst) => {
    const params = org && dst ? `?origin=${org}&destination=${dst}` : '';
    return client.get(`/api/v1/fares/breakdown${params}`);
  },

  // Pipeline & Simulation
  getPipelineStatus: () => client.get('/api/v1/pipeline/status'),
  triggerScrape: (targetDate) => {
    const params = targetDate ? `?target_date=${targetDate}` : '';
    return client.post(`/api/v1/pipeline/trigger-scrape${params}`);
  },
  triggerIndexRecalc: (targetDate) => {
    const params = targetDate ? `?target_date=${targetDate}` : '';
    return client.post(`/api/v1/pipeline/trigger-index${params}`);
  },

  // Backtest & Export
  getBacktestReport: () => client.get('/api/v1/export/backtest'),
  getExportNsoUrl: (month) => {
    const params = month ? `?month=${month}` : '';
    return `${API_BASE_URL}/api/v1/export/nso${params}`;
  },
  getExportJsonUrl: () => `${API_BASE_URL}/api/v1/export/json`,
};

export default client;
