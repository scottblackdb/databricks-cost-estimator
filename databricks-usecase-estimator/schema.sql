-- Schema and seed data for the Databricks Workload Estimator.
-- Run this once against the Lakebase Postgres database the app is bound to
-- (resource key `postgres` in app.yaml).
--
-- All values below are lifted directly from the original hardcoded
-- Python configs in set_rates.py and the *_workload.py modules.

CREATE SCHEMA IF NOT EXISTS cost_estimator;

------------------------------------------------------------------------------
-- 1. Global rates (replaces set_rates.py).
------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cost_estimator.rates (
    name        TEXT PRIMARY KEY,
    value       DOUBLE PRECISION NOT NULL,
    description TEXT
);

INSERT INTO cost_estimator.rates (name, value, description) VALUES
    ('storage',      0.15, 'Storage $/GB/month, includes I/O.'),
    ('dw',           0.70, 'DBSQL DBU rate.'),
    ('job',          0.45, 'Jobs DBU rate.'),
    ('ap',           0.95, 'All-purpose DBU rate.'),
    ('ml',           0.55, 'ML DBU rate.'),
    ('csp_modifier', 0.00, 'CSP discount/uplift modifier.')
ON CONFLICT (name) DO NOTHING;

------------------------------------------------------------------------------
-- 2. Per-workload scalar constants (replaces the inline magic numbers in
--    each workload's create_*_estimate function).
------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cost_estimator.workload_constants (
    workload    TEXT NOT NULL,
    name        TEXT NOT NULL,
    value       DOUBLE PRECISION NOT NULL,
    description TEXT,
    PRIMARY KEY (workload, name)
);

INSERT INTO cost_estimator.workload_constants (workload, name, value, description) VALUES
    ('dw',          'base_daily_rate',  70.0, 'Base 8hr serverless DBSQL daily rate ($).'),
    ('dw',          'days_per_month',   30.5, 'Days per month used in DW formula.'),
    ('batch_etl',   'base_daily_rate',  30.0, 'Base per-run rate for serverless jobs.'),
    ('dlt',         'base_daily_rate',  20.0, 'Base daily rate for streaming/DLT.'),
    ('dlt',         'frequency',        30.0, 'Daily frequency multiplier (DLT runs daily).'),
    ('interactive', 'base_daily_rate',  60.0, 'Base daily rate for interactive analytics.'),
    ('interactive', 'days_per_month',   20.0, 'Working days per month.'),
    ('ml_training', 'base_daily_rate',  30.0, 'Base daily rate for classic CPU training.'),
    ('ml_training', 'days_per_month',   20.0, 'Working days per month.'),
    ('ml_training', 'gpu_modifier',      4.0, 'Multiplier applied when GPU training is selected.'),
    ('ml_serving',  'base_daily_rate',   7.0, 'Per-model daily rate for CPU model serving.'),
    ('ml_serving',  'model_uptime',      0.8, 'Average uptime fraction for serving endpoints.'),
    ('ml_serving',  'days_per_month',   30.0, 'Days per month used in serving formula.'),
    ('ml_serving',  'max_models',       25.0, 'Upper bound for the model-count slider.'),
    ('storage',     'base_monthly_rate', 0.15,'Storage $/GB/month including I/O & time travel.')
ON CONFLICT (workload, name) DO NOTHING;

------------------------------------------------------------------------------
-- 3. Per-workload dropdown options (replaces the inline label->multiplier
--    dicts in every workload module). sort_order preserves the order the
--    options used to appear in the original Python dicts so the UI looks
--    identical.
------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cost_estimator.workload_options (
    workload     TEXT NOT NULL,
    option_group TEXT NOT NULL,
    label        TEXT NOT NULL,
    multiplier   DOUBLE PRECISION NOT NULL,
    sort_order   INT NOT NULL,
    PRIMARY KEY (workload, option_group, label)
);

-- Data Warehouse -------------------------------------------------------------
INSERT INTO cost_estimator.workload_options
    (workload, option_group, label, multiplier, sort_order) VALUES
    ('dw', 'hours_per_day',    '1 - 2 ',         0.20, 1),
    ('dw', 'hours_per_day',    '6 - 8',          1.00, 2),
    ('dw', 'hours_per_day',    '10 - 12',        1.50, 3),
    ('dw', 'hours_per_day',    '24',             3.00, 4),

    ('dw', 'concurrent_users', '1 - 5',          1.00, 1),
    ('dw', 'concurrent_users', '5 - 10',         1.75, 2),
    ('dw', 'concurrent_users', '10 - 20',        2.50, 3),
    ('dw', 'concurrent_users', '20 - 35',        4.00, 4),
    ('dw', 'concurrent_users', '35+',            6.00, 5),

    ('dw', 'data_size',        '10GB - 100GB',   1.00, 1),
    ('dw', 'data_size',        '100GB - 500GB',  2.00, 2),
    ('dw', 'data_size',        '500GB - 1TB',    2.50, 3),
    ('dw', 'data_size',        '1TB - 10TB',     3.00, 4),
    ('dw', 'data_size',        '10TB - 50TB',    5.00, 5),
    ('dw', 'data_size',        '50TB+',          8.00, 6)
ON CONFLICT (workload, option_group, label) DO NOTHING;

-- Batch ETL ------------------------------------------------------------------
INSERT INTO cost_estimator.workload_options
    (workload, option_group, label, multiplier, sort_order) VALUES
    ('batch_etl', 'num_jobs',   '10 - 20',                              1.00, 1),
    ('batch_etl', 'num_jobs',   '20 - 49',                              2.00, 2),
    ('batch_etl', 'num_jobs',   '50 - 99',                              6.00, 3),
    ('batch_etl', 'num_jobs',   '99+',                                 12.00, 4),

    ('batch_etl', 'complexity', 'No Joins & Append Only',               1.00, 1),
    ('batch_etl', 'complexity', 'Simple Joins & Append Only',           3.00, 2),
    ('batch_etl', 'complexity', 'Complex Joins or Merge or SCD Type 2', 8.00, 3),

    ('batch_etl', 'data_size',  '100MB - 1GB',                          1.00, 1),
    ('batch_etl', 'data_size',  '1GB- 10GB',                            1.50, 2),
    ('batch_etl', 'data_size',  '10GB - 100GB',                         3.00, 3),
    ('batch_etl', 'data_size',  '100GB+',                               4.00, 4),

    ('batch_etl', 'frequency',  'Daily',                               30.00, 1),
    ('batch_etl', 'frequency',  'Weekly',                               4.00, 2),
    ('batch_etl', 'frequency',  'Monthly',                              1.00, 3)
ON CONFLICT (workload, option_group, label) DO NOTHING;

-- Streaming / DLT ------------------------------------------------------------
INSERT INTO cost_estimator.workload_options
    (workload, option_group, label, multiplier, sort_order) VALUES
    ('dlt', 'num_jobs',   '1 - 10',                              1.00, 1),
    ('dlt', 'num_jobs',   '10 - 30',                             3.00, 2),
    ('dlt', 'num_jobs',   '30 - 50',                             5.00, 3),
    ('dlt', 'num_jobs',   '50+',                                15.00, 4),

    ('dlt', 'complexity', 'No Joins & Append Only',              1.00, 1),
    ('dlt', 'complexity', 'Simple Joins & Append Only',          3.00, 2),
    ('dlt', 'complexity', 'Complex Joins or Merge or SCD Type 2',8.00, 3),

    ('dlt', 'data_size',  '100MB - 1GB',                         1.00, 1),
    ('dlt', 'data_size',  '1GB- 10GB',                           1.50, 2),
    ('dlt', 'data_size',  '10GB - 100GB',                        3.00, 3),
    ('dlt', 'data_size',  '100GB+',                              4.00, 4)
ON CONFLICT (workload, option_group, label) DO NOTHING;

-- Analytics / Data Engineers (interactive) -----------------------------------
INSERT INTO cost_estimator.workload_options
    (workload, option_group, label, multiplier, sort_order) VALUES
    ('interactive', 'num_people', '5 - 10',         1.00, 1),
    ('interactive', 'num_people', '10 - 20',        3.00, 2),
    ('interactive', 'num_people', '20 - 35',        5.00, 3),
    ('interactive', 'num_people', '35+',           15.00, 4),

    ('interactive', 'data_size',  '10GB - 100GB',   1.00, 1),
    ('interactive', 'data_size',  '100GB - 1TB',    4.00, 2),
    ('interactive', 'data_size',  '1TB - 10TB',    10.00, 3),
    ('interactive', 'data_size',  '10TB+',         20.00, 4)
ON CONFLICT (workload, option_group, label) DO NOTHING;

-- ML Training ----------------------------------------------------------------
INSERT INTO cost_estimator.workload_options
    (workload, option_group, label, multiplier, sort_order) VALUES
    ('ml_training', 'num_people', '1 - 5',          1.00, 1),
    ('ml_training', 'num_people', '5 - 15',         3.00, 2),
    ('ml_training', 'num_people', '15+',            6.00, 3),

    ('ml_training', 'data_size',  '10GB - 100GB',   1.00, 1),
    ('ml_training', 'data_size',  '100GB - 1TB',    4.00, 2),
    ('ml_training', 'data_size',  '1TB - 10TB',    10.00, 3),
    ('ml_training', 'data_size',  '10TB+',         20.00, 4)
ON CONFLICT (workload, option_group, label) DO NOTHING;
