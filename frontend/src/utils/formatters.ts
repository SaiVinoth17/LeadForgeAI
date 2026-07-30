export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount);
}

export function formatConfidence(score: number): string {
  return `${Math.min(99, Math.max(1, score))}%`;
}
