'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { api, type ArticleItem } from '@/lib/api';
import { formatDate, sentimentColor } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Filter, Calendar, Newspaper, ExternalLink, ArrowLeft, ArrowRight } from 'lucide-react';

export default function ArticlesPage() {
  const [items, setItems] = useState<ArticleItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [topic, setTopic] = useState('');
  const [sourceId, setSourceId] = useState('');
  const [sentimentMin, setSentimentMin] = useState('');
  const [sentimentMax, setSentimentMax] = useState('');

  const pageSize = 20;

  const fetchArticles = () => {
    setLoading(true);
    const params: Record<string, string | number> = { page, page_size: pageSize };
    if (topic) params.topic = topic.trim();
    if (sourceId) params.source_id = parseInt(sourceId, 10);
    if (sentimentMin !== '') params.sentiment_min = parseFloat(sentimentMin);
    if (sentimentMax !== '') params.sentiment_max = parseFloat(sentimentMax);
    api
      .get<{ items: ArticleItem[]; total: number; page: number; page_size: number }>('/api/articles', { params })
      .then((res) => {
        setItems(res.data.items);
        setTotal(res.data.total);
        setError(null);
      })
      .catch((err) => {
        console.error('Fetch articles error:', err);
        setError(err.message || 'Failed to load articles');
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchArticles();
  }, [page]);

  const handleApply = () => {
    if (page === 1) {
      fetchArticles();
    } else {
      setPage(1); // This will trigger the useEffect above
    }
  };

  const totalPages = Math.ceil(total / pageSize) || 1;

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.05
      }
    }
  };

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
  };

  return (
    <div className="space-y-10">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-egret-secondary/20 border border-egret-secondary/30">
              <Newspaper className="h-4 w-4 text-egret-secondary" />
            </div>
            <span className="text-xs font-black uppercase tracking-[0.3em] text-egret-muted">Archives</span>
          </div>
          <h1 className="text-4xl md:text-6xl font-black tracking-tighter text-white">
            Intelligence <span className="text-flashy">Vault</span>
          </h1>
        </div>
      </div>

      {/* Filters */}
      <Card className="border-white/5 bg-white/5 backdrop-blur-md">
        <CardHeader className="pb-4">
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-egret-accent" />
            <CardTitle className="text-xs font-black uppercase tracking-widest text-egret-muted">Search Filters</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 gap-6 md:grid-cols-4">
            <div className="space-y-2">
              <Label htmlFor="topic" className="text-[10px] font-black uppercase tracking-wider text-egret-muted">Topic</Label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-egret-muted" />
                <Input
                  id="topic"
                  placeholder="Filter by keyword..."
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  className="pl-10 h-11 rounded-xl border-white/10 bg-black/20 text-white placeholder:text-egret-muted focus:ring-egret-accent"
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="source" className="text-[10px] font-black uppercase tracking-wider text-egret-muted">Source Node</Label>
              <Input
                id="source"
                placeholder="Source ID..."
                value={sourceId}
                onChange={(e) => setSourceId(e.target.value)}
                className="h-11 rounded-xl border-white/10 bg-black/20 text-white focus:ring-egret-accent"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="sentMin" className="text-[10px] font-black uppercase tracking-wider text-egret-muted">Sentiment Min</Label>
              <Input
                id="sentMin"
                type="number"
                step="0.1"
                min={-1}
                max={1}
                placeholder="-1.0"
                value={sentimentMin}
                onChange={(e) => setSentimentMin(e.target.value)}
                className="h-11 rounded-xl border-white/10 bg-black/20 text-white focus:ring-egret-accent"
              />
            </div>
            <div className="flex items-end gap-3">
              <div className="flex-1 space-y-2">
                <Label htmlFor="sentMax" className="text-[10px] font-black uppercase tracking-wider text-egret-muted">Sentiment Max</Label>
                <Input
                  id="sentMax"
                  type="number"
                  step="0.1"
                  min={-1}
                  max={1}
                  placeholder="1.0"
                  value={sentimentMax}
                  onChange={(e) => setSentimentMax(e.target.value)}
                  className="h-11 rounded-xl border-white/10 bg-black/20 text-white focus:ring-egret-accent"
                />
              </div>
              <Button 
                onClick={handleApply}
                className="h-11 rounded-xl shadow-lg shadow-egret-accent/20"
              >
                Apply
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {error && <p className="mb-4 text-egret-negative">{error}</p>}

      {/* Articles Grid */}
      {loading ? (
        <div className="flex justify-center py-20">
          <div className="h-12 w-12 animate-spin rounded-full border-2 border-egret-accent border-t-transparent" />
        </div>
      ) : items.length > 0 ? (
        <motion.div 
          variants={container}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 gap-4 lg:grid-cols-2"
        >
          <AnimatePresence>
            {items.map((article) => {
              const sColor = sentimentColor(article.sentiment_score);
              return (
                <motion.div key={article.id} variants={item} layout>
                  <Card className="h-full group hover:border-white/20 transition-all">
                    <CardContent className="p-6 space-y-4">
                      <div className="flex items-start justify-between gap-4">
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <span className="text-[10px] font-black uppercase tracking-widest text-egret-accent">
                              {article.source_name}
                            </span>
                            <span className="text-[10px] text-egret-muted">•</span>
                            <div className="flex items-center gap-1 text-[10px] font-bold text-egret-muted">
                              <Calendar className="h-3 w-3" />
                              {formatDate(article.published_at)}
                            </div>
                          </div>
                          <h3 className="text-lg font-bold leading-snug text-white group-hover:text-flashy transition-colors">
                            <a href={article.url} target="_blank" rel="noopener noreferrer">
                              {article.title}
                            </a>
                          </h3>
                        </div>
                        <div 
                          className="flex flex-col items-center justify-center p-3 rounded-2xl bg-white/5 border border-white/10"
                          style={{ boxShadow: `0 0 20px -5px hsla(${sColor} / 0.4)` }}
                        >
                          <span className="text-[10px] font-black uppercase tracking-tighter text-egret-muted mb-1">Score</span>
                          <span className="text-lg font-black tabular-nums" style={{ color: `hsl(${sColor})` }}>
                            {article.sentiment_score?.toFixed(2) ?? '0.00'}
                          </span>
                        </div>
                      </div>
                      
                      <div className="flex items-center justify-between pt-2">
                        <div className="flex gap-2">
                          {article.topic && (
                            <span className="px-3 py-1 rounded-full bg-white/5 border border-white/5 text-[10px] font-black uppercase tracking-wider text-egret-muted">
                              #{article.topic}
                            </span>
                          )}
                        </div>
                        <Button variant="ghost" size="sm" className="rounded-full gap-2 text-xs font-bold" asChild>
                          <a href={article.url} target="_blank" rel="noopener noreferrer">
                            Read Full <ExternalLink className="h-3 w-3" />
                          </a>
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </motion.div>
      ) : (
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="flex flex-col items-center justify-center py-24 text-center space-y-6 rounded-[2rem] border-2 border-dashed border-white/5 bg-white/[0.02]"
        >
          <div className="relative">
            <div className="absolute inset-0 blur-2xl bg-egret-accent/20 rounded-full animate-pulse" />
            <div className="relative h-20 w-20 rounded-full border-2 border-egret-accent/30 flex items-center justify-center">
              <Search className="h-10 w-10 text-egret-accent/50" />
            </div>
          </div>
          <div className="space-y-2">
            <h3 className="text-2xl font-black text-white uppercase tracking-tighter">No Intel Found</h3>
            <p className="text-sm text-egret-muted max-w-xs mx-auto">
              The Vault contains no records matching "<span className="text-white font-bold">{topic}</span>". Try broader keywords or different filters.
            </p>
          </div>
          <Button 
            variant="outline" 
            onClick={() => { setTopic(''); handleApply(); }}
            className="rounded-full border-white/10 hover:bg-white/5"
          >
            Clear Filters
          </Button>
        </motion.div>
      )}

      {/* Pagination */}
      {!loading && totalPages > 1 && (
        <div className="flex items-center justify-center gap-4 pt-10">
          <Button
            variant="outline"
            disabled={page === 1}
            onClick={() => setPage((p) => p - 1)}
            className="rounded-full gap-2 border-white/10"
          >
            <ArrowLeft className="h-4 w-4" /> Prev
          </Button>
          <div className="px-6 py-2 rounded-full bg-white/5 border border-white/10 text-sm font-black text-white">
            {page} <span className="text-egret-muted mx-1">/</span> {totalPages}
          </div>
          <Button
            variant="outline"
            disabled={page === totalPages}
            onClick={() => setPage((p) => p + 1)}
            className="rounded-full gap-2 border-white/10"
          >
            Next <ArrowRight className="h-4 w-4" />
          </Button>
        </div>
      )}
    </div>
  );
}
