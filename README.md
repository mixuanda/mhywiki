# HomDGCat Combat Wiki (Legacy-Style)

This repository keeps a combat-only subset for:
- Genshin Impact (GI)
- Honkai: Star Rail (SR)

The output site keeps the original legacy page style/routes for kept sections.

## Repository Layout

- `web/`: deployable legacy web root (static site)
- `combat-wiki/data/`: canonical normalized data (one entity per file)
- `tools/`: extraction, ingest, sync, validation, verification, admin server
- `schemas/`: JSON schemas for canonical data validation

## Build Legacy Web From Local Raw `site/`

```bash
python3 tools/build_legacy_site.py \
  --site ./site \
  --out ./web \
  --clean \
  --locales CH,EN \
  --asset-mode remote
```

Notes:
- `--asset-mode remote`: rewrites heavy assets to `https://homdgcat.wiki/` to keep repo light.
- `--asset-mode local`: copies `images/`, `homdgcat-res/`, `EnemyChart/`, `SREnemyChart/` into `web/`.
- Serve `web/` as document root (do not serve repo root then visit `/web`).

## Canonical Extraction

```bash
python3 tools/extract_from_site.py --site ./site --out ./combat-wiki/data --clean
```

## Validate Canonical Data

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r tools/requirements.txt
python tools/validate.py --data ./combat-wiki/data --schemas ./schemas
```

## Human Text -> Entity Workflow (Codex CLI Friendly)

You can paste free-form text and write directly into canonical JSON + legacy files:

```bash
python tools/ingest_human_text.py \
  --game gi \
  --kind character \
  --id 199001 \
  --name "Test Avatar" \
  --text-file ./my_avatar_notes.txt \
  --apply \
  --pretty
```

Supported kinds:
- `character`, `weapon`, `artifact`, `enemy`, `banner` (GI)
- `character`, `lightcone`, `relic`, `enemy`, `banner` (SR)

## Canonical -> Legacy Sync (Single Entity)

```bash
python tools/generate_legacy_from_canonical.py \
  --data ./combat-wiki/data \
  --web ./web \
  --game sr \
  --kind character \
  --id 1001
```

## Local Verification

Run route/resource/detail checks:

```bash
python tools/verify_web.py --web ./web
```

## Run Local Web (Static)

```bash
cd web
python3 -m http.server 3000
```

Open: `http://localhost:3000`

## Run Local Admin Web + API

Password-gated local admin with ingest/sync endpoints:

```bash
export ADMIN_PASSWORD='your-password'
python tools/admin_server.py \
  --project-root . \
  --web ./web \
  --data ./combat-wiki/data \
  --port 3000
```

Open:
- `http://localhost:3000/admin/`

Admin features:
- Parse free-form text into entity draft
- Save canonical JSON
- Sync legacy runtime files/routes
- Optional GitHub PR creation from changed local files (`/api/github/pr-from-local`)

## Vercel Deployment

Deploy static `web/` directly:

```bash
cd web
vercel --prod
```

After deploy, verify core routes and pages manually, then run smoke checks against the live URL.
