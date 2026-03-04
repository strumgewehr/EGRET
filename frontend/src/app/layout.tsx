import type { Metadata } from 'next';
import { Space_Grotesk } from 'next/font/google';
import './globals.css';
import { Toaster } from '@/components/ui/toaster';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { AppHeader } from '@/components/AppHeader';
import MeshBackdrop from '@/components/MeshBackdrop';
import PageTransition from '@/components/PageTransition';

const spaceGrotesk = Space_Grotesk({
  subsets: ['latin'],
  variable: '--font-display',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'EGRET — Sentiment Intelligence',
  description: 'Newsroom-grade sentiment analysis, bias detection, and narrative tracking',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${spaceGrotesk.variable} min-h-screen bg-egret-bg font-display text-egret-text antialiased selection:bg-egret-accent selection:text-white`}>
        <ErrorBoundary>
          <MeshBackdrop />
          <AppHeader />
          <PageTransition>
            <main className="relative z-10 px-4 md:px-8 max-w-7xl mx-auto py-6">
              {children}
            </main>
          </PageTransition>
          <Toaster />
        </ErrorBoundary>
      </body>
    </html>
  );
}
