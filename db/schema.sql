CREATE TABLE source_dataset (
  source_id TEXT PRIMARY KEY,
  authority TEXT NOT NULL,
  country_code CHAR(2) NOT NULL,
  domain TEXT NOT NULL,
  public_data BOOLEAN NOT NULL CHECK (public_data)
);

CREATE TABLE observation (
  observation_id TEXT PRIMARY KEY,
  source_id TEXT NOT NULL REFERENCES source_dataset(source_id),
  station_id TEXT NOT NULL,
  observed_at TIMESTAMPTZ NOT NULL,
  metric TEXT NOT NULL,
  value DOUBLE PRECISION NOT NULL,
  unit TEXT NOT NULL,
  latitude DOUBLE PRECISION,
  longitude DOUBLE PRECISION,
  provenance JSONB NOT NULL,
  context JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX observation_station_time_idx ON observation(station_id, observed_at DESC);
CREATE INDEX observation_metric_time_idx ON observation(metric, observed_at DESC);

CREATE TABLE finding (
  finding_id TEXT PRIMARY KEY,
  rule_id TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status = 'requires-expert-review'),
  created_at TIMESTAMPTZ NOT NULL,
  scope JSONB NOT NULL,
  evidence JSONB NOT NULL,
  alternatives JSONB NOT NULL,
  limitations JSONB NOT NULL,
  uncertainty DOUBLE PRECISION NOT NULL CHECK (uncertainty BETWEEN 0 AND 1)
);

CREATE TABLE expert_review (
  review_id BIGSERIAL PRIMARY KEY,
  finding_id TEXT NOT NULL REFERENCES finding(finding_id),
  reviewer TEXT NOT NULL,
  decision TEXT NOT NULL CHECK (decision IN ('acknowledged','needs-more-data','rejected','corrected')),
  comment TEXT NOT NULL DEFAULT '',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
