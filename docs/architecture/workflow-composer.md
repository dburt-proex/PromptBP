# Workflow Composer

## Purpose

The Workflow Composer dynamically assembles execution workflows from the Capability Registry based on intent, complexity, risk, and required output. It replaces static prompt chains with adaptive, fitness-based capability sequencing.

## Design Principles

1. **Fitness over fixed order**: Choose capabilities based on what the task needs, not a predetermined sequence.
2. **Minimal path**: Include only capabilities that add value for this specific intent.
3. **Risk-proportional depth**: Higher risk triggers more validation, simulation, and review capabilities.
4. **Composable**: Any capability can be added, removed, or reordered without breaking the workflow.

## Composition Rules

### Rule 1: Intent Determines Shape

| Intent Type | Core Path |
|-------------|-----------|
| audit | context_broker → reasoning_engine → risk_scanner → validation_engine → scoring_engine |
| build | context_broker → constraint_resolver → builder_generator → validation_engine → scoring_engine |
| research | context_broker → research_retrieval → reasoning_engine → scoring_engine |
| review | context_broker → reasoning_engine → risk_scanner → validation_engine → scoring_engine |
| strategy | context_broker → constraint_resolver → simulation_layer → reasoning_engine → risk_scanner → scoring_engine |

### Rule 2: Complexity Adds Depth

| Complexity | Additional Capabilities |
|------------|------------------------|
| low | None — use core path only |
| medium | Add compression_engine before delivery |
| high | Add simulation_layer + risk_scanner |
| critical | Add all scanning + require human gate |

### Rule 3: Risk Adds Gates

| Risk Level | Added Gates |
|------------|------------|
| low | scoring_engine only |
| medium | validation_engine + scoring_engine |
| high | risk_scanner + validation_engine + scoring_engine |
| critical | simulation_layer + risk_scanner + validation_engine + human_approval_gate + scoring_engine |

### Rule 4: Always Present

These capabilities are included in every workflow:
- `intent_router` (first)
- `scoring_engine` (penultimate)
- `delivery_formatter` (last, if output goes to user)
- `evaluation_store` (post-delivery, async)

### Rule 5: Looper Integration

The `looper` capability is not part of the composed workflow. It wraps the workflow and triggers re-entry into specific capabilities when scores fail.

## Composition Algorithm

```
1. Receive: intent_type, complexity, risk_level, constraints
2. Select core path based on intent_type
3. Apply complexity modifiers (add depth capabilities)
4. Apply risk modifiers (add gate capabilities)
5. Apply constraint modifiers:
   - If token_budget is tight → add compression_engine
   - If citation_required → add research_retrieval
   - If human_approval_needed → add approval gate
6. Check dependency ordering (capability.dependencies must precede it)
7. Remove duplicates while preserving first occurrence position
8. Validate: no incompatible capabilities in same workflow
9. Return: ordered capability list
```

## Example Compositions

### Simple Build (low complexity, low risk)

```yaml
intent: build
complexity: low
risk: low
workflow:
  - intent_router
  - context_broker
  - constraint_resolver
  - builder_generator
  - scoring_engine
  - delivery_formatter
```

### Critical Strategy (high complexity, critical risk)

```yaml
intent: strategy
complexity: high
risk: critical
workflow:
  - intent_router
  - context_broker
  - constraint_resolver
  - research_retrieval
  - simulation_layer
  - reasoning_engine
  - risk_scanner
  - validation_engine
  - human_approval_gate
  - compression_engine
  - scoring_engine
  - delivery_formatter
```

### Research with Citations (medium complexity, low risk)

```yaml
intent: research
complexity: medium
risk: low
workflow:
  - intent_router
  - context_broker
  - research_retrieval
  - reasoning_engine
  - compression_engine
  - scoring_engine
  - delivery_formatter
```

## Overrides

The composer accepts manual overrides for advanced users:

```yaml
overrides:
  force_include: [simulation_layer]    # always include these
  force_exclude: [compression_engine]  # never include these
  force_order: []                      # specific ordering constraints
  max_capabilities: 8                  # cap workflow length
```

## Failure Handling

If the composer cannot build a valid workflow:
1. Log the failure with inputs
2. Fall back to the default workflow for the intent type
3. Flag the execution as "degraded composition" in the state object
4. Include composition failure in evaluation store for future learning
