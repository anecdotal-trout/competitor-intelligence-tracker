# Competitor Intelligence Tracker

Tracks competitor pricing changes, feature launches, and go-to-market moves over time. Built for growth and strategy teams that need to brief leadership on competitive dynamics and spot market trends early.

## What it does

- Tracks pricing changes across competitors over multiple snapshots
- Identifies market-wide pricing trends (rising, falling, or flat)
- Compares feature parity across tiers (voice cloning, API access, analytics, enterprise readiness)
- Logs and categorises competitive activity (feature launches, pricing changes, partnerships, hiring)
- Generates a feature launch timeline with impact ratings
- Produces strategic insights from the data

## Quick start

```bash
pip install -r requirements.txt
python competitor_tracker.py
```

## How it works

1. **Pricing snapshots**: Periodic captures of each competitor's pricing page (stored as CSV). In production, you'd automate this with a scraper on a cron job.
2. **Changelog**: Manual log of competitive moves — feature launches, pricing changes, partnerships, hiring signals. Sourced from product blogs, press releases, and social media.
3. **SQL analysis**: Joins snapshots over time to calculate price changes, aggregates activity by competitor and type.
4. **Feature parity check**: Parses feature lists to flag capabilities across competitors.
5. **Strategic synthesis**: Rule-based insights drawn from the data patterns.

## Data

| File | Description |
|------|-------------|
| `pricing_snapshots.csv` | Three snapshots (Jan, Mar, Jun 2025) of competitor pricing across tiers |
| `changelog.csv` | 20 competitive events with date, type, category, description, and impact level |

## Context

The data models the AI voice synthesis market (think ElevenLabs, PlayHT, Murf, etc.) but the structure works for any competitive landscape. The point is showing the analytical framework, not the specific data.

In practice, the data collection would be automated (scraping pricing pages, monitoring RSS feeds and Twitter). This project focuses on the analysis layer — what do you do with the data once you have it?

## Tech

- **Python** — pandas for feature parity analysis and trend calculations
- **SQL** (SQLite) — pricing change tracking, activity aggregations, timeline queries

## Other projects

- [ai-api-cost-calculator](https://github.com/anecdotal-trout/ai-api-cost-calculator) — AI model pricing comparison across providers
- [b2b-pipeline-analyzer](https://github.com/anecdotal-trout/b2b-pipeline-analyzer) — Marketing spend → pipeline ROI
- [startup-comp-screener](https://github.com/anecdotal-trout/startup-comp-screener) — Startup comparable screening and scoring

