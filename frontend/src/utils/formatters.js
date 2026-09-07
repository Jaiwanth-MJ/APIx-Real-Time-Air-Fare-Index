/**
 * Format currency in Indian format (₹4,820)
 */
export function formatINR(val) {
  if (val === null || val === undefined || isNaN(val)) return '—';
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(val);
}

/**
 * Format index decimal value
 */
export function formatIndex(val) {
  if (val === null || val === undefined || isNaN(val)) return '—';
  return Number(val).toFixed(2);
}

/**
 * Format percentage (+1.82%)
 */
export function formatPct(val) {
  if (val === null || val === undefined || isNaN(val)) return '—';
  const prefix = val > 0 ? '+' : '';
  return `${prefix}${Number(val).toFixed(2)}%`;
}

/**
 * Format date string (2026-09-07 -> 07 Sep 2026)
 */
export function formatDate(dateStr) {
  if (!dateStr) return '—';
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  } catch (e) {
    return dateStr;
  }
}
