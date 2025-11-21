-- infra/create_bigquery_table.sql
-- Creates a partitioned & clustered table to store processed reviews.
-- Table: e-pulsar-478805-s9.consumer_sense_ai.consumer_reviews

CREATE TABLE IF NOT EXISTS `e-pulsar-478805-s9.consumer_sense_ai.consumer_reviews` (
  review_id STRING,
  text STRING,
  sentiment STRING,
  score FLOAT64,
  themes ARRAY<STRING>,
  action_items ARRAY<STRING>,
  intent STRING,
  confidence FLOAT64,
  source STRING,
  model STRING,
  created_at TIMESTAMP,
  processed_at TIMESTAMP,
  processing_latency_ms INT64,
  metadata STRUCT<
    app_version STRING,
    region STRING,
    upload_method STRING
  >
)
PARTITION BY DATE(processed_at)
-- CLUSTER BY must only reference column names (no expressions). Use columns useful for analytics.
CLUSTER BY sentiment, model
OPTIONS (
  description="Consumer Sense AI processed reviews for analytics (created via infra/create_bigquery_table.sql)"
);
