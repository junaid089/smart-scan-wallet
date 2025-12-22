import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
}

export function formatDate(dateString: string): string {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(new Date(dateString));
}

// Category colors for charts
export const categoryColors: Record<string, string> = {
  FOOD: '#22c55e',
  TRANSPORT: '#3b82f6',
  UTILITIES: '#f59e0b',
  ENTERTAINMENT: '#8b5cf6',
  HEALTH: '#ef4444',
  SHOPPING: '#ec4899',
  OTHER: '#6b7280',
};

export function getCategoryColor(category: string): string {
  return categoryColors[category.toUpperCase()] || categoryColors.OTHER;
}
