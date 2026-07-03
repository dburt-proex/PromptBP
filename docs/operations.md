# PromptBP Operations

## Timeout and Retry Defaults

### Client-Side Timeouts

| Context | Timeout | Rationale |
|---------|---------|-----------|
| Simple generation | 45s | Single-turn, short output |
| Complex generation | 90s | Multi-section, long output |
| Evaluation run | 60s | Scoring pass with moderate output |
| Batch operation | 120s | Multiple items, potential queuing |

### Retry Policy

```yaml
retry:
  max_attempts: 3
  backoff: exponential
  base_delay_ms: 1000
  max_delay_ms: 30000
  jitter: true
  retryable_errors:
    - timeout
    - rate_limit
    - server_error_5xx
  non_retryable_errors:
    - invalid_request
    - auth_failure
    - content_policy_violation
```

### Circuit Breaker

If more than 5 consecutive failures occur within 60 seconds:
1. Open circuit for 30 seconds
2. Allow one probe request
3. If probe succeeds, close circuit
4. If probe fails, remain open for another 60 seconds

## Response Caching

### Cache Strategy

Cache responses keyed by:
- Prompt hash (SHA-256 of the full prompt text)
- Model identifier
- Input hash (SHA-256 of serialized inputs)
- Temperature setting

### Cache Policy

| Use Case | TTL | Invalidation |
|----------|-----|--------------|
| Evaluation/regression runs | 7 days | On prompt version change |
| Deterministic queries (temp=0) | 30 days | On prompt or input change |
| Creative generation (temp>0) | No cache | Always fresh |
| Batch deduplication | Session-scoped | End of batch |

### Storage

- Local: File-based JSON cache in `.promptbp-cache/`
- Shared: Optional Redis or object store for team environments
- Max cache size: 500MB default, configurable

## Batching Strategy

### When to Batch

- Multiple evaluations of the same prompt
- Bulk scoring against fixture sets
- Parallel capability executions within a workflow

### Safe Batch Sizes

| Provider | Max Batch Size | Notes |
|----------|---------------|-------|
| OpenAI | 20 requests | Respect per-minute token limits |
| Anthropic | 10 requests | Lower concurrent limits |
| Local models | Hardware-dependent | Monitor GPU memory |
| Generic API | 5 requests | Conservative default |

### Batching Rules

1. Never exceed provider rate limits
2. Include per-request timeout within batch
3. Fail individual items, not entire batch
4. Log batch success/failure ratio
5. Back off if batch failure rate exceeds 20%

## Input Guardrails

### Pre-Send Validation

Before issuing any LLM call, validate:

1. **Length check**: Input tokens within model context window (leave 30% for output)
2. **Required fields**: All required input fields from the prompt schema are populated
3. **Unsafe content**: Scan for known PII patterns, credential patterns, injection attempts
4. **Schema conformance**: Input matches expected types and formats
5. **Cost estimate**: Estimated token count × cost per token is within budget threshold

### Rejection Actions

| Validation Failure | Action |
|-------------------|--------|
| Input too long | Truncate or split with warning |
| Missing required field | Reject with specific error |
| Unsafe content detected | Block and log for review |
| Schema mismatch | Reject with validation details |
| Over budget | Require explicit approval |

## Telemetry

### Per-Call Metrics

Track for every LLM interaction:

```yaml
telemetry_record:
  timestamp: ISO 8601
  prompt_name: string
  prompt_version: semver
  model: string
  input_tokens: integer
  output_tokens: integer
  total_tokens: integer
  latency_ms: integer
  status: success | error | timeout
  error_type: string (if applicable)
  cache_hit: boolean
  cost_usd: float
  scores: object (if evaluation run)
```

### Aggregation Windows

- Real-time: per-request logging
- Hourly: token usage summaries
- Daily: cost, error rate, latency percentiles (p50, p95, p99)
- Weekly: prompt version comparison, regression detection

### Alerting Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| Error rate | > 5% over 1 hour | > 15% over 15 min |
| p95 latency | > 2× baseline | > 5× baseline |
| Daily cost | > 120% of budget | > 200% of budget |
| Score regression | > 5% drop | > 15% drop |

## Safety and Compliance Hooks

### Pre-Processing Hooks

```yaml
pre_hooks:
  - name: pii_scrubber
    enabled: true
    action: redact
    patterns: [email, phone, ssn, credit_card]
  - name: injection_detector
    enabled: true
    action: block
    patterns: [prompt_injection, jailbreak_attempt]
  - name: content_classifier
    enabled: false
    action: flag
    categories: [violence, hate, sexual]
```

### Post-Processing Hooks

```yaml
post_hooks:
  - name: output_pii_check
    enabled: true
    action: redact
  - name: moderation_filter
    enabled: true
    action: flag_and_review
  - name: compliance_logger
    enabled: true
    action: log
    fields: [prompt_hash, model, timestamp, classification]
```

### When to Enable

| Hook | Enable When |
|------|-------------|
| PII scrubber | Processing user-submitted content |
| Injection detector | Public-facing inputs |
| Content classifier | Generated content for external audiences |
| Output PII check | Any response that may be stored or shared |
| Moderation filter | Customer-facing deployments |
| Compliance logger | Regulated industries, audit requirements |

## Rollout Strategy

### Staged Deployment

```
1. Canary (5% traffic)
   → Monitor for 1 hour
   → Compare scores against baseline
   → If regression > 5%: rollback

2. Limited (25% traffic)
   → Monitor for 4 hours
   → Collect evaluation scores from live traffic
   → If regression > 3%: rollback to canary or previous

3. Broad (100% traffic)
   → Full deployment
   → Continue monitoring for 24 hours
   → Maintain rollback capability for 7 days
```

### Rollback Triggers

- Evaluation score drops below threshold on any critical dimension
- Error rate exceeds 10% for more than 5 minutes
- User-reported quality issues exceed 3 in first hour
- Cost per request exceeds 150% of previous version

### Rollback Process

1. Revert to last known-good prompt version (tracked via metadata.version)
2. Log rollback reason and metrics
3. Notify prompt owner
4. Create investigation ticket
5. Block re-deployment until root cause identified
