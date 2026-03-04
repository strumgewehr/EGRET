# EGRET – API Reference

Base URL: `http://localhost:8000` (or `NEXT_PUBLIC_API_URL`)

## General

- **GET /** – Service info and version
- **GET /health** – Liveness (returns `{"status": "ok"}`)
- **GET /docs** – Swagger UI

## Articles

- **GET /api/articles**  
  Query: `date_from`, `date_to`, `source_id`, `topic`, `sentiment_min`, `sentiment_max`, `page`, `page_size`  
  Returns: `{ items: Article[], total, page, page_size }`

- **GET /api/articles/{article_id}**  
  Returns: Single article with sentiment and headline flag

## Sources

- **GET /api/sources**  
  Query: `active_only` (optional)  
  Returns: List of sources

- **GET /api/sources/{source_id}**  
  Returns: Single source

- **POST /api/sources**  
  Body: `{ name, slug, base_url?, feed_url?, api_endpoint?, fetch_interval_minutes? }`  
  Returns: Created source

- **PATCH /api/sources/{source_id}**  
  Body: `{ name?, is_active?, feed_url?, fetch_interval_minutes? }`  
  Returns: Updated source

- **POST /api/sources/{source_id}/ingest**  
  Triggers ingestion for one source. Returns: `{ status, articles_new, articles_duplicates }`

- **POST /api/sources/ingest-all**  
  Triggers ingestion for all active sources

## Dashboard

- **GET /api/dashboard/stats**  
  Query: `days` (default 7)  
  Returns: `DashboardStats` (total_articles, articles_today, sources_active, sentiment_distribution, time_series, top_trending_topics, outlet_comparison, ingestion_status, last_ingestion_at)

## Analytics

- **GET /api/analytics/narrative-drift**  
  Query: `topic`, `source_ids?` (comma-separated), `days`  
  Returns: Time series of sentiment per source for topic

- **POST /api/analytics/narrative-drift/compute**  
  Query: `topic`, `period_hours`, `lookback_days`  
  Computes and stores drift snapshots

- **GET /api/analytics/polarization**  
  Query: `topic`, `days`  
  Returns: Per-outlet sentiment for topic (heatmap data)

- **GET /api/analytics/crisis-spikes**  
  Query: `limit`  
  Returns: List of crisis spike events

- **POST /api/analytics/crisis-spikes/detect**  
  Runs crisis spike detection job

- **GET /api/analytics/similarity**  
  Query: `article_id?`, `threshold`, `limit`  
  Returns: Article similarity pairs

## Admin

- **GET /api/admin/health**  
  Returns: `{ database_connected, redis_connected, total_articles, total_sources, last_ingestion_at }`

- **GET /api/admin/ingestion-logs**  
  Query: `source_id?`, `limit`  
  Returns: List of ingestion logs

- **POST /api/admin/ingest-all**  
  Triggers full ingestion run

- **POST /api/admin/articles/{article_id}/flag**  
  Body: `{ reason }`  
  Manually flag article

- **POST /api/admin/articles/{article_id}/unflag**  
  Clear flag

- **POST /api/admin/articles/{article_id}/reanalyze**  
  Re-run sentiment and bias analysis

## HTTP Status Codes

- 200 – Success
- 201 – Created
- 400 – Bad request / validation error
- 404 – Not found
- 429 – Rate limit exceeded
- 500 – Server error

Errors return `{ "detail": "..." }` (and optionally `"type"` for 500).
