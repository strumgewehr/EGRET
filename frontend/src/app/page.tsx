import Link from 'next/link';

export default function HomePage() {
  return (
    <main className="relative min-h-[calc(100vh-4rem)] overflow-hidden">
      {/* Ambient gradient */}
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-egret-accent/5 via-transparent to-egret-gold/5" />
      <div className="egret-ticker absolute left-0 right-0 top-0 h-1" />

      <div className="relative mx-auto max-w-6xl px-6 py-20 sm:py-28">
        <div className="text-center">
          <h1 className="font-display text-5xl font-bold tracking-tight text-egret-text sm:text-7xl">
            EGRET
          </h1>
          <p className="mt-3 font-display text-xl font-medium text-egret-accent sm:text-2xl">
            Sentiment Intelligence
          </p>
          <p className="mx-auto mt-6 max-w-xl text-base text-egret-muted sm:text-lg">
            Real-time news aggregation, sentiment analysis, and bias detection. Track narrative drift and media polarization in one place.
          </p>
          <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
            <Link
              href="/dashboard"
              className="inline-flex items-center justify-center rounded-lg bg-egret-accent px-8 py-3.5 text-sm font-semibold text-white shadow-lg shadow-egret-accent/25 transition hover:bg-egret-accent/90 hover:shadow-egret-accent/30"
            >
              Open Dashboard
            </Link>
            <Link
              href="/articles"
              className="inline-flex items-center justify-center rounded-lg border border-egret-border bg-egret-surface px-8 py-3.5 text-sm font-semibold text-egret-text transition hover:border-egret-accent/50 hover:bg-egret-card"
            >
              Browse Articles
            </Link>
          </div>
        </div>

        {/* Feature ticker */}
        <div className="mt-24 flex items-center gap-8 overflow-hidden border-y border-egret-border py-4">
          <div className="flex animate-ticker gap-8 whitespace-nowrap text-sm text-egret-muted">
            {[
              'Sentiment scoring',
              'Bias detection',
              'Narrative drift',
              'Polarization heatmap',
              'Headline analysis',
              'Crisis spikes',
              'Multi-source ingestion',
              'Outlet comparison',
            ].map((label) => (
              <span key={label} className="font-medium">
                {label}
              </span>
            ))}
            {[
              'Sentiment scoring',
              'Bias detection',
              'Narrative drift',
              'Polarization heatmap',
            ].map((label) => (
              <span key={`dup-${label}`} className="font-medium">
                {label}
              </span>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}
