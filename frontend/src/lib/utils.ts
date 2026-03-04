import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(s: string): string {
  try {
    const d = new Date(s);
    return d.toLocaleDateString(undefined, { dateStyle: 'short' }) + ' ' + d.toLocaleTimeString(undefined, { timeStyle: 'short' });
  } catch {
    return s;
  }
}

export function sentimentColor(score: number | null): string {
  if (score == null) return 'var(--egret-muted)';
  if (score > 0.1) return 'var(--egret-positive)';
  if (score < -0.1) return 'var(--egret-negative)';
  return 'var(--egret-neutral)';
}

export function sentimentClass(score: number | null): string {
  if (score == null) return 'text-egret-muted';
  if (score > 0.1) return 'text-egret-positive';
  if (score < -0.1) return 'text-egret-negative';
  return 'text-egret-neutral';
}
