import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: 'class',
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        display: ['var(--font-display)', 'system-ui', 'sans-serif'],
        sans: ['var(--font-display)', 'system-ui', 'sans-serif'],
      },
      colors: {
        egret: {
          bg: 'hsl(var(--egret-bg))',
          surface: 'hsl(var(--egret-surface))',
          card: 'hsl(var(--egret-card))',
          border: 'hsl(var(--egret-border))',
          text: 'hsl(var(--egret-text))',
          muted: 'hsl(var(--egret-muted))',
          accent: 'hsl(var(--egret-accent))',
          gold: 'hsl(var(--egret-gold))',
          positive: 'hsl(var(--egret-positive))',
          negative: 'hsl(var(--egret-negative))',
          neutral: 'hsl(var(--egret-neutral))',
        },
      },
      animation: {
        'ticker': 'ticker 30s linear infinite',
      },
      keyframes: {
        ticker: {
          '0%': { transform: 'translateX(0)' },
          '100%': { transform: 'translateX(-50%)' },
        },
      },
    },
  },
  plugins: [],
};

export default config;
