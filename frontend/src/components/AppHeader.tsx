'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';

const NAV = [
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/articles', label: 'Articles' },
  { href: '/analytics', label: 'Analytics' },
  { href: '/admin', label: 'Admin' },
];

export function AppHeader() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 border-b border-white/5 bg-egret-bg/40 backdrop-blur-xl">
      <div className="mx-auto flex h-20 max-w-7xl items-center justify-between px-8">
        <Link href="/" className="group flex items-center gap-3">
          <motion.div
            whileHover={{ rotate: 180, scale: 1.1 }}
            transition={{ type: "spring", stiffness: 260, damping: 20 }}
            className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-egret-accent to-egret-secondary p-2 shadow-lg shadow-egret-accent/20"
          >
            <div className="h-full w-full rounded-md bg-egret-bg/20 backdrop-blur-sm" />
          </motion.div>
          <div className="flex flex-col">
            <span className="font-display text-2xl font-black tracking-tighter text-flashy">
              EGRET
            </span>
            <span className="hidden text-[10px] font-bold uppercase tracking-[0.2em] text-egret-muted sm:inline">
              Sentiment Intelligence
            </span>
          </div>
        </Link>
        <nav className="flex items-center gap-2 rounded-full bg-white/5 p-1.5 backdrop-blur-md">
          {NAV.map(({ href, label }) => {
            const isActive = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                className={`relative px-5 py-2 text-sm font-bold transition-colors ${
                  isActive ? 'text-white' : 'text-egret-muted hover:text-white'
                }`}
              >
                {isActive && (
                  <motion.div
                    layoutId="nav-pill"
                    className="absolute inset-0 z-0 rounded-full bg-gradient-to-r from-egret-accent/80 to-egret-secondary/80 shadow-lg shadow-egret-accent/20"
                    transition={{ type: 'spring', bounce: 0.25, duration: 0.5 }}
                  />
                )}
                <span className="relative z-10">{label}</span>
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
