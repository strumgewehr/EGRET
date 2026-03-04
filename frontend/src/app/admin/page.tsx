'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { api, type SourceItem, type IngestionLogItem } from '@/lib/api';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, Database, Cpu, Activity, Zap, RefreshCw, Terminal, CheckCircle2, XCircle, Clock, Newspaper } from 'lucide-react';

export default function AdminPage() {
  const [health, setHealth] = useState<{
    database_connected: boolean;
    redis_connected: boolean;
    total_articles: number;
    total_sources: number;
    last_ingestion_at: string | null;
  } | null>(null);
  const [sources, setSources] = useState<SourceItem[]>([]);
  const [logs, setLogs] = useState<IngestionLogItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [ingesting, setIngesting] = useState(false);

  const load = () => {
    setLoading(true);
    Promise.all([
      api.get('/api/admin/health').then((r) => setHealth(r.data)),
      api.get('/api/sources').then((r) => setSources(r.data)),
      api.get('/api/admin/ingestion-logs', { params: { limit: 30 } }).then((r) => setLogs(r.data)),
    ])
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const triggerIngest = () => {
    setIngesting(true);
    api
      .post('/api/admin/ingest-all')
      .then(() => load())
      .finally(() => setIngesting(false));
  };

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
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <motion.div variants={item} className="flex items-center gap-3 mb-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-egret-accent/20 border border-egret-accent/30">
              <Shield className="h-4 w-4 text-egret-accent" />
            </div>
            <span className="text-xs font-black uppercase tracking-[0.3em] text-egret-muted">System Control</span>
          </motion.div>
          <motion.h1 variants={item} className="text-4xl md:text-6xl font-black tracking-tighter text-egret-text">
            Core <span className="text-egret-accent">Admin</span>
          </motion.h1>
        </div>
        <motion.div variants={item}>
          <Button
            onClick={triggerIngest}
            disabled={ingesting}
            className="rounded-full px-8 py-6 font-black uppercase tracking-widest shadow-lg shadow-egret-accent/20 gap-3 bg-egret-accent text-white hover:bg-egret-accent/90"
          >
            <RefreshCw className={`h-5 w-5 ${ingesting ? 'animate-spin' : ''}`} />
            {ingesting ? 'Synchronizing...' : 'Trigger Sync'}
          </Button>
        </motion.div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Health Stats */}
        <motion.div variants={item} className="lg:col-span-1">
          <Card className="h-full">
            <CardHeader className="pb-6">
              <div className="flex items-center gap-2">
                <Activity className="h-4 w-4 text-egret-positive" />
                <CardTitle className="text-xl">System Vitality</CardTitle>
              </div>
              <p className="text-xs font-bold text-egret-muted uppercase tracking-wider">Operational Status</p>
            </CardHeader>
            <CardContent>
              {health ? (
                <div className="space-y-4">
                  <div className="p-4 rounded-2xl bg-egret-border/10 border border-egret-border flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Database className="h-4 w-4 text-egret-muted" />
                      <span className="text-xs font-bold uppercase text-egret-muted">PostgreSQL</span>
                    </div>
                    {health.database_connected ? (
                      <CheckCircle2 className="h-5 w-5 text-egret-positive" />
                    ) : (
                      <XCircle className="h-5 w-5 text-egret-negative" />
                    )}
                  </div>
                  <div className="p-4 rounded-2xl bg-egret-border/10 border border-egret-border flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Zap className="h-4 w-4 text-egret-muted" />
                      <span className="text-xs font-bold uppercase text-egret-muted">Redis Cache</span>
                    </div>
                    {health.redis_connected ? (
                      <CheckCircle2 className="h-5 w-5 text-egret-positive" />
                    ) : (
                      <XCircle className="h-5 w-5 text-egret-negative" />
                    )}
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 rounded-2xl bg-egret-border/10 border border-egret-border">
                      <p className="text-[10px] font-black uppercase tracking-tighter text-egret-muted mb-1">Articles</p>
                      <p className="text-2xl font-black text-egret-text">{health.total_articles.toLocaleString()}</p>
                    </div>
                    <div className="p-4 rounded-2xl bg-egret-border/10 border border-egret-border">
                      <p className="text-[10px] font-black uppercase tracking-tighter text-egret-muted mb-1">Sources</p>
                      <p className="text-2xl font-black text-egret-text">{health.total_sources}</p>
                    </div>
                  </div>
                  {health.last_ingestion_at && (
                    <div className="p-4 rounded-2xl bg-egret-accent/5 border border-egret-accent/20">
                      <p className="text-[10px] font-black uppercase tracking-tighter text-egret-accent mb-1">Last Sync Cycle</p>
                      <p className="text-sm font-bold text-egret-text">{new Date(health.last_ingestion_at).toLocaleString()}</p>
                    </div>
                  )}
                </div>
              ) : (
                <div className="h-40 flex items-center justify-center">
                  <div className="h-8 w-8 animate-spin rounded-full border-2 border-egret-accent border-t-transparent" />
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Sources List */}
        <motion.div variants={item} className="lg:col-span-2">
          <Card className="h-full">
            <CardHeader className="pb-6">
              <div className="flex items-center gap-2">
                <Cpu className="h-4 w-4 text-egret-accent" />
                <CardTitle className="text-xl">Intelligence Nodes</CardTitle>
              </div>
              <p className="text-xs font-bold text-egret-muted uppercase tracking-wider">Source Management</p>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {sources.map((source, i) => (
                  <motion.div
                    key={source.id}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.05 }}
                    className="flex items-center justify-between p-4 rounded-2xl bg-egret-border/10 border border-egret-border hover:border-egret-accent/30 transition-colors"
                  >
                    <div className="flex items-center gap-4">
                      <div className="h-10 w-10 rounded-xl bg-egret-accent/10 flex items-center justify-center">
                        <Newspaper className="h-5 w-5 text-egret-accent" />
                      </div>
                      <div>
                        <p className="text-sm font-black text-egret-text">{source.name}</p>
                        <p className="text-[10px] font-bold text-egret-muted uppercase">{source.slug}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="text-right">
                        <p className="text-[10px] font-black uppercase tracking-tighter text-egret-muted mb-1">ID</p>
                        <span className="px-2 py-0.5 rounded bg-egret-border/20 text-[8px] font-bold text-egret-text uppercase">{source.id}</span>
                      </div>
                      <div className={`h-2 w-2 rounded-full ${source.is_active ? 'bg-egret-positive shadow-[0_0_10px_rgba(var(--egret-positive),0.5)]' : 'bg-egret-muted'}`} />
                    </div>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Ingestion Logs */}
        <motion.div variants={item} className="lg:col-span-3">
          <Card>
            <CardHeader className="pb-6">
              <div className="flex items-center gap-2">
                <Terminal className="h-4 w-4 text-egret-accent" />
                <CardTitle className="text-xl">Sync Logs</CardTitle>
              </div>
              <p className="text-xs font-bold text-egret-muted uppercase tracking-wider">System Events & Traces</p>
            </CardHeader>
            <CardContent>
              <div className="rounded-3xl bg-egret-border/5 border border-egret-border overflow-hidden">
                <div className="p-4 border-b border-egret-border bg-egret-border/10 flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-red-500/50" />
                  <div className="h-3 w-3 rounded-full bg-yellow-500/50" />
                  <div className="h-3 w-3 rounded-full bg-green-500/50" />
                  <span className="ml-2 text-[10px] font-black uppercase tracking-[0.2em] text-egret-muted">egret-cli-output.log</span>
                </div>
                <div className="p-6 font-mono text-xs space-y-2 max-h-[400px] overflow-y-auto custom-scrollbar">
                  {logs.map((log) => (
                    <div key={log.id} className="flex items-start gap-4 py-1 border-b border-egret-border last:border-0">
                      <span className="text-egret-muted whitespace-nowrap">[{new Date(log.started_at).toLocaleTimeString()}]</span>
                      <span className={`font-black uppercase tracking-tighter ${log.status === 'success' ? 'text-egret-positive' : 'text-egret-negative'}`}>
                        {log.status}
                      </span>
                      <span className="text-egret-text opacity-80">{log.triggered_by}</span>
                      {log.articles_new > 0 && (
                        <span className="text-egret-accent font-bold">+{log.articles_new} items</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </motion.div>
  );
}
