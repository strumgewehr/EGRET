/**
 * API client with base URL from env, retry logic, and error handling.
 */
import axios, { AxiosError } from 'axios';

const baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL,
  timeout: 7000,
  headers: { 'Content-Type': 'application/json' },
});

const MAX_RETRIES = 2;

api.interceptors.response.use(
  (res) => res,
  async (err: AxiosError) => {
    const config = err.config as { _retryCount?: number };
    config._retryCount = config._retryCount ?? 0;
    if (config._retryCount < MAX_RETRIES && err.response?.status && err.response.status >= 500) {
      config._retryCount += 1;
      await new Promise((r) => setTimeout(r, 1000));
      return api.request(config);
    }
    return Promise.reject(err);
  }
);

export type DashboardStats = {
  total_articles: number;
  articles_today: number;
  sources_active: number;
  sentiment_distribution: { label: string; value: number; percentage: number }[];
  time_series: { date: string; avg_sentiment: number; article_count: number }[];
  top_trending_topics: { topic: string; article_count: number; avg_sentiment: number; trend_direction: string }[];
  outlet_comparison: { source_id: number; source_name: string; avg_sentiment: number; article_count: number; positive_ratio: number }[];
  ingestion_status: string;
  last_ingestion_at: string | null;
};

export type ArticleItem = {
  id: number;
  source_id: number;
  title: string;
  summary: string | null;
  url: string;
  published_at: string;
  author: string | null;
  source_name: string | null;
  sentiment_score: number | null;
  sentiment_confidence: number | null;
  emotion: string | null;
  bias_index: number | null;
  is_flagged: boolean;
  headline_manipulation_score: number | null;
};

export type SourceItem = {
  id: number;
  name: string;
  slug: string;
  is_active: boolean;
  last_fetched_at: string | null;
};

export type IngestionLogItem = {
  id: number;
  source_id: number | null;
  status: string;
  articles_fetched: number;
  articles_new: number;
  articles_duplicates: number;
  error_message: string | null;
  started_at: string;
  completed_at: string | null;
  triggered_by: string;
};
