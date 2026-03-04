"""Initial schema - articles, sources, sentiment, ingestion, unique features.

Revision ID: 001
Revises:
Create Date: 2025-03-01

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("slug", sa.String(128), nullable=False),
        sa.Column("base_url", sa.String(1024), nullable=True),
        sa.Column("feed_url", sa.String(2048), nullable=True),
        sa.Column("api_endpoint", sa.String(2048), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("fetch_interval_minutes", sa.Integer(), default=60),
        sa.Column("last_fetched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sources_slug", "sources", ["slug"], unique=True)

    op.create_table(
        "topics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("slug", sa.String(256), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_topics_name", "topics", ["name"], unique=True)
    op.create_index("ix_topics_slug", "topics", ["slug"], unique=True)

    op.create_table(
        "articles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("external_id", sa.String(512), nullable=True),
        sa.Column("title", sa.String(1024), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("url", sa.String(2048), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("author", sa.String(256), nullable=True),
        sa.Column("image_url", sa.String(2048), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("is_flagged", sa.Boolean(), default=False),
        sa.Column("flag_reason", sa.String(512), nullable=True),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_articles_external_id", "articles", ["external_id"], unique=True)
    op.create_index("ix_articles_source_id", "articles", ["source_id"], unique=False)
    op.create_index("ix_articles_published_at", "articles", ["published_at"], unique=False)
    op.create_index("ix_articles_published_at_source", "articles", ["published_at", "source_id"], unique=False)

    op.create_table(
        "article_topics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("article_id", sa.Integer(), nullable=False),
        sa.Column("topic_id", sa.Integer(), nullable=False),
        sa.Column("relevance", sa.Float(), default=1.0),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["topic_id"], ["topics.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_article_topics_article_id", "article_topics", ["article_id"], unique=False)
    op.create_index("ix_article_topics_topic_id", "article_topics", ["topic_id"], unique=False)

    op.create_table(
        "sentiment_results",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("article_id", sa.Integer(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("emotion", sa.String(32), nullable=True),
        sa.Column("bias_index", sa.Float(), nullable=True),
        sa.Column("raw_response", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sentiment_results_article_id", "sentiment_results", ["article_id"], unique=True)

    op.create_table(
        "ingestion_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("articles_fetched", sa.Integer(), default=0),
        sa.Column("articles_new", sa.Integer(), default=0),
        sa.Column("articles_duplicates", sa.Integer(), default=0),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("triggered_by", sa.String(32), default="scheduler"),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ingestion_logs_source_id", "ingestion_logs", ["source_id"], unique=False)

    op.create_table(
        "narrative_drift_snapshots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("topic", sa.String(256), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("avg_sentiment", sa.Float(), nullable=False),
        sa.Column("article_count", sa.Integer(), default=0),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_narrative_drift_topic_period", "narrative_drift_snapshots", ["topic", "period_start"], unique=False)

    op.create_table(
        "crisis_spike_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("keyword", sa.String(256), nullable=False),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("severity", sa.Float(), nullable=False),
        sa.Column("article_count", sa.Integer(), default=0),
        sa.Column("avg_sentiment_before", sa.Float(), nullable=True),
        sa.Column("avg_sentiment_during", sa.Float(), nullable=True),
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_crisis_spike_events_keyword", "crisis_spike_events", ["keyword"], unique=False)
    op.create_index("ix_crisis_spike_events_detected_at", "crisis_spike_events", ["detected_at"], unique=False)

    op.create_table(
        "headline_flags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("article_id", sa.Integer(), nullable=False),
        sa.Column("manipulation_score", sa.Float(), nullable=False),
        sa.Column("trigger_words", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_headline_flags_article_id", "headline_flags", ["article_id"], unique=True)

    op.create_table(
        "article_similarities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("article_id_1", sa.Integer(), nullable=False),
        sa.Column("article_id_2", sa.Integer(), nullable=False),
        sa.Column("similarity_score", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["article_id_1"], ["articles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["article_id_2"], ["articles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("article_id_1", "article_id_2", name="uq_article_similarity_pair"),
    )
    op.create_index("ix_article_similarities_article_id_1", "article_similarities", ["article_id_1"], unique=False)
    op.create_index("ix_article_similarities_article_id_2", "article_similarities", ["article_id_2"], unique=False)


def downgrade() -> None:
    op.drop_table("article_similarities")
    op.drop_table("headline_flags")
    op.drop_table("crisis_spike_events")
    op.drop_table("narrative_drift_snapshots")
    op.drop_table("ingestion_logs")
    op.drop_table("sentiment_results")
    op.drop_table("article_topics")
    op.drop_table("articles")
    op.drop_table("topics")
    op.drop_table("sources")
