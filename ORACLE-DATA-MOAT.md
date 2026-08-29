# Oracle Data Moat — What to Store

## Three Linked Data Systems

```
ORACLE        "What work exists?"
WORKERKIT     "What happened when an agent tried it?"
MARKETPLACE   "What components did agents use, and did they improve results?"
```

## Oracle Data Model

### oracle.sources
```
id, name, type, url, auth_type, agent_native, last_polled_at
```

### oracle.opportunities
```
id UUIDv7, source_id, external_id, title, description, category,
reward_amount, reward_currency, reward_usd, status, deadline,
created_at_source, first_seen_at, last_seen_at, execution_mode,
skills_required[], source_url, metadata JSONB
```

### oracle.opportunity_observations (append-only)
```
id, opportunity_id, observed_at, status, reward, applicant_count,
submission_count, deadline, raw_digest, raw_blob_uri
```

### oracle.opportunity_events (append-only)
```
id, opportunity_id, event_type, event_at, data JSONB, confidence
```

### oracle.market_snapshots
```
id, source_id, snapshot_at, metrics JSONB
```

## Key Principle: Never Overwrite History

```
append-only observations → current opportunity state
```

Don't do: `UPDATE opportunities SET status='closed'`
Do: record observation that status changed
