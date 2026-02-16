---
title: "Automated Budget Tracker"
date: 2025-08-15
type: "portfolio"
summary: "A Python CLI tool that categorizes bank transactions and generates monthly spending reports."
tags:
  - python
  - cli
  - automation

project_url: "https://github.com/jacksong17/budget-tracker"
---

## Overview

I built this to replace the spreadsheet I was using to track spending. It reads CSV exports from my bank, categorizes transactions using a rules file, and generates a monthly summary.

## How It Works

The core is pretty simple:

1. **Import** — Drop a CSV from your bank into the `imports/` directory. The tool auto-detects the format (Chase, Ally, or generic CSV with configurable column mapping).
2. **Categorize** — Transactions are matched against a YAML rules file. Rules support exact match, substring, and regex patterns. Anything unmatched goes to "Uncategorized" for manual review.
3. **Report** — Generates a markdown summary with totals by category, month-over-month comparison, and a flagged list of large transactions (configurable threshold).

## What I Learned

The hardest part was handling the variety of CSV formats across banks. Date parsing alone required handling four different formats. I ended up writing a format detection layer that samples the first few rows and picks the right parser.

The categorization rules are the part I keep tweaking. I started with about 20 rules and I'm up to about 80 now. It covers maybe 95% of transactions automatically.

## Stack

- Python 3.11
- Click (CLI framework)
- PyYAML (rules config)
- Tabulate (terminal output)
