'use client';

import { useEffect, useState } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { api } from '@/lib/api';
import { motion, AnimatePresence } from 'framer-motion';
import { BarChart3, AlertTriangle, TrendingDown, Target, Search, Zap } from 'lucide-react';

export default function AnalyticsPage() {
  const [topic, setTopic] = useState('economy');
  const [polarization, setPolarization] = useState<{ topic: string; outlets: { source_name: string; avg_sentiment: number; article_count: number; positive_count: number; negative_count: number; neutral_count: number }[] } | null>(null);
  const [crisisSpikes, setCrisisSpikes] = useState<{ events: { keyword: string; severity: number; detected_at: string }[] } | null>(null);
  const [loading, setLoading] = useState(false);

  const loadPolarization = () => {
    if (!topic.trim()) return;
    setLoading(true);
    api
      .get('/api/analytics/polarization', { params: { topic: topic.trim(), days: 7 } })
      .then((r) => setPolarization(r.data))
      .catch(() => setPolarization(null))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    api.get('/api/analytics/crisis-spikes', { params: { limit: 20 } }).then((r) => setCrisisSpikes(r.data)).catch(() => setCrisisSpikes(null));
    loadPolarization();
  }, []);

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
      className="space-y-10"
    >
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <motion.div variants={item} className="flex items-center gap-3 mb-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-egret-accent/20 border border-egret-accent/30">
              <BarChart3 className="h-4 w-4 text-egret-accent" />
            </div>
            <span className="text-xs font-black uppercase tracking-[0.3em] text-egret-muted">Deep Analysis</span>
          </motion.div>
          <motion.h1 variants={item} className="text-4xl md:text-6xl font-black tracking-tighter text-white">
            Narrative <span className="text-flashy">Intelligence</span>
          </motion.h1>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Polarization Heatmap */}
        <motion.div variants={item} className="lg:col-span-2">
          <Card className="h-full">
            <CardHeader className="pb-8">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <Target className="h-4 w-4 text-egret-secondary" />
                    <CardTitle className="text-xl">Media Polarization Heatmap</CardTitle>
                  </div>
                  <p className="text-xs font-bold text-egret-muted uppercase tracking-wider">Per-outlet sentiment for target topics</p>
                </div>
                <div className="flex items-center gap-3">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-egret-muted" />
                    <Input
                      id="pol-topic"
                      value={topic}
                      onChange={(e) => setTopic(e.target.value)}
                      placeholder="Target topic..."
                      className="pl-9 h-10 w-48 rounded-full border-white/10 bg-black/20 text-white placeholder:text-egret-muted focus:ring-egret-accent text-xs font-bold"
                    />
                  </div>
                  <Button
                    onClick={loadPolarization}
                    disabled={loading}
                    size="sm"
                    className="rounded-full px-6 font-black uppercase tracking-tighter"
                  >
                    {loading ? 'Analyzing...' : 'Execute'}
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {polarization && polarization.outlets.length > 0 ? (
                <div className="space-y-8">
                  {/* Visual Heatmap / Stacked Bar Chart */}
                  <div className="h-[400px] w-full bg-white/5 rounded-3xl p-6 border border-white/10">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        data={polarization.outlets}
                        layout="vertical"
                        margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
                        <XAxis type="number" stroke="rgba(255,255,255,0.3)" fontSize={10} />
                        <YAxis 
                          dataKey="source_name" 
                          type="category" 
                          stroke="rgba(255,255,255,0.5)" 
                          fontSize={10} 
                          width={100}
                        />
                        <Tooltip
                          cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                          contentStyle={{
                            backgroundColor: 'rgba(10, 10, 15, 0.95)',
                            borderColor: 'rgba(255,255,255,0.1)',
                            borderRadius: '16px',
                            fontSize: '11px',
                            color: '#fff'
                          }}
                        />
                        <Legend wrapperStyle={{ fontSize: '10px', paddingTop: '20px' }} />
                        <Bar dataKey="positive_count" name="Positive" stackId="a" fill="#10b981" radius={[0, 0, 0, 0]} />
                        <Bar dataKey="neutral_count" name="Neutral" stackId="a" fill="#64748b" radius={[0, 0, 0, 0]} />
                        <Bar dataKey="negative_count" name="Negative" stackId="a" fill="#ef4444" radius={[0, 4, 4, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>

                  {/* Individual Source Cards */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <AnimatePresence>
                      {polarization.outlets.map((o, idx) => {
                        const isPos = o.avg_sentiment > 0.1;
                        const isNeg = o.avg_sentiment < -0.1;
                        const colorClass = isPos ? 'text-egret-positive' : isNeg ? 'text-egret-negative' : 'text-egret-neutral';
                        const bgClass = isPos ? 'bg-egret-positive/5 border-egret-positive/20' : isNeg ? 'bg-egret-negative/5 border-egret-negative/20' : 'bg-egret-neutral/5 border-egret-neutral/20';
                        
                        return (                    <motion.div
                            key={o.source_name}
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: idx * 0.05 }}
                            className={`p-5 rounded-3xl border ${bgClass} group hover:scale-[1.02] transition-transform`}
                          >
                            <div className="flex justify-between items-start mb-4">
                              <span className="text-[10px] font-black uppercase tracking-widest text-egret-muted">{o.source_name}</span>
                              <div className="px-2 py-0.5 rounded-full bg-white/5 text-[8px] font-bold text-egret-muted uppercase border border-white/5">
                                {o.article_count} reports
                              </div>
                            </div>
                            <div className="flex items-end justify-between">
                              <div className="space-y-1">
                                <p className="text-[10px] font-black uppercase tracking-tighter text-egret-muted">Bias Index</p>
                                <p className={`text-3xl font-black tracking-tighter ${colorClass}`}>
                                  {o.avg_sentiment.toFixed(3)}
                                </p>
                              </div>
                              <div className="h-12 w-12 rounded-full border-4 border-white/5 flex items-center justify-center">
                                <div 
                                  className={`h-8 w-8 rounded-full animate-pulse`} 
                                  style={{ backgroundColor: `hsl(var(--egret-${isPos ? 'positive' : isNeg ? 'negative' : 'neutral'}))` }}
                                />
                              </div>
                            </div>
                          </motion.div>
                        );
                      })}
                    </AnimatePresence>
                  </div>
                </div>
              ) : polarization ? (
                <div className="h-[200px] flex flex-col items-center justify-center gap-4 rounded-3xl border border-dashed border-white/10 bg-white/5">
                  <Search className="h-8 w-8 text-egret-muted opacity-20" />
                  <p className="text-xs font-bold text-egret-muted uppercase tracking-[0.2em]">No data for "{topic}" in last 7 days</p>
                </div>
              ) : (
                <div className="h-[200px] flex flex-col items-center justify-center gap-4 rounded-3xl border border-dashed border-white/10 bg-white/5">
                  <Target className="h-8 w-8 text-egret-muted opacity-20" />
                  <p className="text-xs font-bold text-egret-muted uppercase tracking-[0.2em]">Awaiting Target Selection</p>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Crisis Spike Detector */}
        <motion.div variants={item} className="lg:col-span-1">
          <Card className="h-full">
            <CardHeader className="pb-6">
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-egret-negative" />
                <CardTitle className="text-xl">Crisis Spike Detector</CardTitle>
              </div>
              <p className="text-xs font-bold text-egret-muted uppercase tracking-wider">Algorithmic Anomaly Detection</p>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {crisisSpikes?.events?.length ? (
                  crisisSpikes.events.slice(0, 8).map((e, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.1 }}
                      className="flex items-center justify-between p-4 rounded-2xl bg-white/5 border border-white/5 hover:border-egret-negative/30 transition-colors group"
                    >
                      <div className="flex items-center gap-4">
                        <div className="h-10 w-10 rounded-xl bg-egret-negative/10 flex items-center justify-center group-hover:scale-110 transition-transform">
                          <TrendingDown className="h-5 w-5 text-egret-negative" />
                        </div>
                        <div>
                          <p className="text-sm font-black text-white">{e.keyword}</p>
                          <p className="text-[10px] font-bold text-egret-muted uppercase">{new Date(e.detected_at).toLocaleString()}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-[10px] font-black uppercase tracking-tighter text-egret-muted mb-1">Severity</p>
                        <span className="px-3 py-1 rounded-full bg-egret-negative/20 text-egret-negative text-[10px] font-black uppercase">
                          {(e.severity * 100).toFixed(0)}%
                        </span>
                      </div>
                    </motion.div>
                  ))
                ) : (
                  <div className="h-[200px] flex flex-col items-center justify-center gap-4">
                    <Zap className="h-8 w-8 text-egret-muted opacity-20" />
                    <p className="text-xs font-bold text-egret-muted uppercase tracking-[0.2em]">No Active Crises Detected</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Narrative Drift Placeholder */}
        <motion.div variants={item} className="lg:col-span-1">
          <Card className="h-full bg-gradient-to-br from-egret-accent/10 to-transparent border-egret-accent/20">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Zap className="h-4 w-4 text-egret-gold" />
                <CardTitle className="text-xl">Narrative Drift</CardTitle>
              </div>
              <p className="text-xs font-bold text-egret-muted uppercase tracking-wider">Under Construction</p>
            </CardHeader>
            <CardContent className="flex flex-col items-center justify-center h-[300px] text-center gap-4">
              <div className="h-20 w-20 rounded-full border-4 border-dashed border-egret-gold/30 flex items-center justify-center animate-spin-slow">
                <Target className="h-10 w-10 text-egret-gold/50" />
              </div>
              <div>
                <p className="text-sm font-black text-white uppercase tracking-widest">Quantum Engine Initializing</p>
                <p className="text-xs text-egret-muted mt-2">Aggregating multi-vector sentiment flows...</p>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </motion.div>
  );
}
