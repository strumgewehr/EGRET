'use client';

import { useEffect, useState } from 'react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  AreaChart,
  Area,
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { api, type DashboardStats } from '@/lib/api';
import { motion } from 'framer-motion';
import { Activity, Newspaper, Globe, Zap, TrendingUp } from 'lucide-react';

const PIE_COLORS = ['hsl(var(--egret-positive))', 'hsl(var(--egret-neutral))', 'hsl(var(--egret-negative))'];

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    const fallback: DashboardStats = {
      total_articles: 0,
      articles_today: 0,
      sources_active: 0,
      sentiment_distribution: [
        { label: 'positive', value: 0, percentage: 0 },
        { label: 'neutral', value: 0, percentage: 0 },
        { label: 'negative', value: 0, percentage: 0 },
      ],
      time_series: Array.from({ length: 7 }).map((_, i) => {
        const d = new Date();
        d.setDate(d.getDate() - (6 - i));
        return { date: d.toISOString(), avg_sentiment: 0, article_count: 0 };
      }),
      top_trending_topics: [],
      outlet_comparison: [],
      ingestion_status: 'offline',
      last_ingestion_at: null,
    };
    api
      .get<DashboardStats>('/api/dashboard/stats', { params: { days: 7 } })
      .then((res) => {
        if (!cancelled) setStats(res.data);
      })
      .catch((err) => {
        if (!cancelled) {
          setError(null);
          setStats(fallback);
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, []);

  if (loading) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center gap-6">
        <div className="relative">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            className="h-16 w-16 rounded-full border-t-2 border-b-2 border-egret-accent shadow-[0_0_20px_rgba(var(--egret-accent),0.3)]"
          />
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="h-8 w-8 animate-pulse rounded-full bg-egret-secondary/20" />
          </div>
        </div>
        <p className="text-sm font-bold uppercase tracking-[0.2em] text-flashy animate-pulse">Synchronizing Intelligence</p>
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center gap-6 px-6">
        <div className="rounded-2xl bg-egret-negative/10 p-6 text-center border border-egret-negative/20">
          <p className="text-egret-negative font-bold">{error ?? 'No data connection'}</p>
        </div>
        <button
          onClick={() => window.location.reload()}
          className="rounded-full bg-white/5 px-8 py-3 text-sm font-bold text-white hover:bg-white/10 transition-all border border-white/10"
        >
          Re-establish Link
        </button>
      </div>
    );
  }

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
  };

  return (
    <motion.div 
      variants={container}
      initial="hidden"
      animate="show"
      className="mx-auto max-w-7xl px-6 py-8 space-y-10"
    >
      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <motion.div variants={item} className="flex items-center gap-3 mb-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-egret-accent/20 border border-egret-accent/30">
              <Activity className="h-4 w-4 text-egret-accent egret-live" />
            </div>
            <span className="text-xs font-black uppercase tracking-[0.3em] text-egret-muted">Real-time Feed Active</span>
          </motion.div>
          <motion.h1 variants={item} className="text-4xl md:text-6xl font-black tracking-tighter text-white">
            Global <span className="text-flashy">Sentiment</span>
          </motion.h1>
        </div>
        <motion.div variants={item} className="flex gap-2">
          <div className="glass-card px-4 py-2 rounded-full flex items-center gap-2 border-white/5">
            <div className="h-1.5 w-1.5 rounded-full bg-egret-positive egret-live" />
            <span className="text-xs font-bold text-egret-muted uppercase">Systems Green</span>
          </div>
        </motion.div>
      </div>

      {/* Bento Grid Stats */}
      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: 'Intelligence Stream', value: stats.total_articles, icon: Newspaper, color: 'text-egret-accent' },
          { label: 'Daily Capture', value: stats.articles_today, icon: Zap, color: 'text-egret-secondary' },
          { label: 'Active Nodes', value: stats.sources_active, icon: Globe, color: 'text-egret-neutral' },
          { label: 'Latest Sync', value: stats.ingestion_status, icon: Activity, color: 'text-egret-positive', sub: stats.last_ingestion_at ? new Date(stats.last_ingestion_at).toLocaleTimeString() : 'N/A' },
        ].map((stat, i) => (
          <motion.div key={stat.label} variants={item}>
            <Card className="h-full group">
              <CardContent className="p-6 flex flex-col justify-between h-full">
                <div className="flex items-start justify-between mb-4">
                  <div className={`p-2 rounded-xl bg-white/5 border border-white/10 group-hover:border-egret-accent/50 transition-colors`}>
                    <stat.icon className={`h-5 w-5 ${stat.color}`} />
                  </div>
                  {stat.sub && <span className="text-[10px] font-bold text-egret-muted uppercase">{stat.sub}</span>}
                </div>
                <div>
                  <p className="text-xs font-bold uppercase tracking-widest text-egret-muted mb-1">{stat.label}</p>
                  <p className="text-3xl font-black tracking-tight text-white tabular-nums">
                    {typeof stat.value === 'number' ? stat.value.toLocaleString() : stat.value}
                  </p>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </section>

      {/* Main Analytics Grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Sentiment Area Chart */}
        <motion.div variants={item} className="lg:col-span-2">
          <Card className="h-full">
            <CardHeader className="flex flex-row items-center justify-between pb-8">
              <div className="space-y-1">
                <CardTitle className="text-xl">Volume & Drift</CardTitle>
                <p className="text-xs font-bold text-egret-muted uppercase tracking-wider">7-Day Analysis Window</p>
              </div>
              <div className="p-2 rounded-full bg-egret-accent/10">
                <TrendingUp className="h-4 w-4 text-egret-accent" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="h-[300px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={stats.time_series}>
                    <defs>
                      <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="hsl(var(--egret-accent))" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="hsl(var(--egret-accent))" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                    <XAxis 
                      dataKey="date" 
                      stroke="rgba(255,255,255,0.3)" 
                      fontSize={10} 
                      fontWeight="bold"
                      axisLine={false}
                      tickLine={false}
                      tickFormatter={(val) => new Date(val).toLocaleDateString(undefined, { weekday: 'short' })}
                    />
                    <YAxis 
                      stroke="rgba(255,255,255,0.3)" 
                      fontSize={10} 
                      fontWeight="bold"
                      axisLine={false}
                      tickLine={false}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: 'rgba(10, 10, 15, 0.9)', 
                        borderColor: 'rgba(255,255,255,0.1)',
                        borderRadius: '16px',
                        backdropFilter: 'blur(8px)',
                        fontSize: '12px',
                        fontWeight: 'bold'
                      }}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="avg_sentiment" 
                      stroke="hsl(var(--egret-accent))" 
                      strokeWidth={4}
                      fillOpacity={1} 
                      fill="url(#colorValue)" 
                      animationDuration={2000}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Sentiment Distribution Pie */}
        <motion.div variants={item}>
          <Card className="h-full">
            <CardHeader className="pb-8">
              <div className="space-y-1">
                <CardTitle className="text-xl">Bias Matrix</CardTitle>
                <p className="text-xs font-bold text-egret-muted uppercase tracking-wider">Overall Polarization</p>
              </div>
            </CardHeader>
            <CardContent>
              <div className="h-[240px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={stats.sentiment_distribution}
                      innerRadius={70}
                      outerRadius={90}
                      paddingAngle={8}
                      dataKey="value"
                      animationBegin={500}
                      animationDuration={1500}
                    >
                      {stats.sentiment_distribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} stroke="none" />
                      ))}
                    </Pie>
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: 'rgba(10, 10, 15, 0.9)', 
                        borderColor: 'rgba(255,255,255,0.1)',
                        borderRadius: '16px',
                        backdropFilter: 'blur(8px)',
                        fontSize: '12px',
                        fontWeight: 'bold'
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="mt-8 space-y-3">
                {stats.sentiment_distribution.map((d, i) => (
                  <div key={d.label} className="flex items-center justify-between p-3 rounded-2xl bg-white/5 border border-white/5 hover:border-white/10 transition-colors">
                    <div className="flex items-center gap-3">
                      <div className="h-2 w-2 rounded-full" style={{ backgroundColor: PIE_COLORS[i] }} />
                      <span className="text-xs font-bold text-egret-muted uppercase">{d.label}</span>
                    </div>
                    <span className="text-sm font-black text-white">{d.percentage}%</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </motion.div>
  );
}
