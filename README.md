# IEUK Task 2025 – Log Analyser

A tiny Python CLI tool (Typer-based) that parses a web access log, aggregates counts by **IP** and **endpoint**, caches the results to `results.json`, and lets you query the summary either locally or from Docker.

---

## Features

* Parse log lines to extract: IP, 2‑char region code, request endpoint, status code.
* Aggregate counts and persist to `results.json` for fast repeat lookups.
* CLI: show **top N IPs/endpoints** or drill into a specific IP or endpoint.
* Containerized (Python 3.11‑slim base image).

---

## Project Layout

```
.
├── analyser.py          # main script / CLI
├── sample-log.log       # example input log (edit or mount your own)
├── results.json         # created/updated after first parse
├── requirements.txt     # deps: typer, typing_extensions, etc.
├── Dockerfile
```

---

## Install & Run Locally

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Build the cache (happens automatically on first run)

The script looks for `sample-log.log`. Put your log there (or replace that file).

### CLI Usage

**Syntax:**

```bash
python analyser.py TERM LIMIT
```

* `TERM` = IP (e.g., `203.0.113.42`) **or** endpoint (e.g., `/search`).
* Use an **empty string** (`""`) to show overall top counts.
* `LIMIT` = max rows to show (default 10).

**Examples:**

```bash
# Show top 10 overall IPs & endpoints
python analyser.py "" 10

# Show top 5 for endpoint /search
python analyser.py /search 5

# Show top 20 stats for a specific IP
python analyser.py 203.0.113.42 20
```

Example output:

```python
{'endpoints': [('/search', 125), ('/login', 90)],
 'ips': [('203.0.113.42', 140), ('198.51.100.7', 60)]}
```

(Exact numbers depend on your log.)

---

## Docker

### Build Image

```bash
docker build -t ieuk-task .
```

### Run (top results)

```bash
docker run --rm ieuk-task "" 10
```

### Run (endpoint /search, top 5)

```bash
docker run --rm ieuk-task '/search' 5
```

---

## Expected Log Format

The regex expects lines roughly like (Nginx/ELB style):

```
198.51.100.7 - US - - [12/Jul/2025:10:00:01 +0000] "GET /search?q=foo HTTP/1.1" 200 512 "-" "Mozilla/5.0"
```

Only these fields are parsed: IP, region (2 chars between `- XX -`), method + path, status code.

---

## How It Works (short)

1. **build()** reads the log, parses each line, accumulates raw lists in in‑memory `defaultdict`s.
2. **store()** collapses lists to `(value, count)` pairs and writes `results.json`.
3. **search\_table()** loads `results.json` and prints:

   * Top N IPs & endpoints (if TERM empty), or
   * Field breakdown for a given IP/endpoint.

---

## Troubleshooting

**`File not found!`** – `sample-log.log` missing; add or mount one.
**`exec: "/search": stat /search`** – Docker treated `/search` as the command; see Docker section above.
**No results?** Ensure the log lines match the regex patterns.