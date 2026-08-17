# Product Catalog Competition Environment

`sku_competition_env` is a CLI-first training environment for this workflow:

1. Query a product catalog for a specified brand.
2. Retrieve all SKU records for that brand.
3. Extract selling points, ingredients, and current pricing.
4. Generate a same-category competitor comparison report.
5. Store the extract and report in the session cache.

The environment follows the rollout/session pattern defined in `claw_env_recipe.md`:

- each rollout owns one isolated session
- mutable state is file-backed under a configurable state root
- per-session locking protects concurrent writes
- agent commands do not require `--session-id`

## Session Model

Session management is trainer-owned, not agent-owned.

- The trainer prepares one session per rollout sample.
- The trainer binds that session through environment variables.
- Agent commands read those bindings automatically.

Trainer bootstrap:

```bash
python -m without_skill.sku_competition_env.cli prepare-rollout --scenario-id sku_competition_report_apac_q2_2026 --show-bindings --show-task
```

Returned bindings:

- `WITHOUT_SKILL_SESSION_ID`
- `WITHOUT_SKILL_STATE_ROOT`
- `WITHOUT_SKILL_SCENARIO_ID`

## Agent Commands

After rollout preparation, the agent uses the CLI without session arguments:

```bash
python -m without_skill.sku_competition_env.cli task
python -m without_skill.sku_competition_env.cli list-brands --query LuminaSkin
python -m without_skill.sku_competition_env.cli list-skus --brand-id brand_luminaskin
python -m without_skill.sku_competition_env.cli list-price-books --current-only
python -m without_skill.sku_competition_env.cli get-price-book --price-book-id pb_apac_q2_2026_live
python -m without_skill.sku_competition_env.cli list-attachments
python -m without_skill.sku_competition_env.cli read-attachment --attachment-path current_pricebook_notice.md
python -m without_skill.sku_competition_env.cli extract-brand-catalog --brand-id brand_luminaskin --price-book-id pb_apac_q2_2026_live
python -m without_skill.sku_competition_env.cli generate-category-report --brand-id brand_luminaskin --price-book-id pb_apac_q2_2026_live
python -m without_skill.sku_competition_env.cli list-cache
python -m without_skill.sku_competition_env.cli get-cache-entry --entry-id cache_000007
python -m without_skill.sku_competition_env.cli session-summary
```

## Data Layout

- `data/accounts.json`: workspace account profile and permissions.
- `data/contacts.json`: operating stakeholders.
- `data/attachments.json`: attachment manifest for scenario reading.
- `data/brands/brands.json`: brand profiles and positioning.
- `data/skus/skus.json`: product catalog rows with ingredients and selling points.
- `data/pricing/price_books.json`: current and archived price books.
- `data/attachments/*.md`: notices and templates the agent may need to read.
- `data/scenarios/*.json`: scenario prompts and evaluation metadata.

## Cache Model

Generated artifacts are stored in session cache:

- `brand_catalog_extract`
- `category_competition_report`

Use `list-cache` to inspect metadata and `get-cache-entry` to inspect full payloads.

## Concurrency Test

Use the stress script to validate session isolation and locking:

```bash
python -m without_skill.sku_competition_env.concurrency_test --mode both --executor processes --sessions 16 --workers 8 --contention-loops 4 --report-json ./.tmp/without_skill_report.json
```

It checks both:

- isolated parallel sessions
- multi-worker contention on a shared session
