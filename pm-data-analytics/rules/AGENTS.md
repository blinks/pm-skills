# PM Data Analytics Behavioral Rules

## Core Principles
1. **Read-Only Safety**: Generated SQL queries must be strictly read-only (`SELECT`, `WITH`). Never propose queries that mutate, drop, or alter tables or data.
2. **Explicit Schema & Dialect**: Always confirm or inspect the target database dialect (PostgreSQL, BigQuery, Snowflake, MySQL) and table schema before generating queries.
3. **Cohort & Retention Rigor**: Clearly state time windows, granularity, and retention definitions (Day N, rolling retention, unbounded retention). Avoid ambiguous metric definitions.
4. **Efficiency Invariants**: Recommend appropriate partitioning and clustering filters, avoid unbounded cartesian products (`CROSS JOIN`), and limit exploratory queries.
