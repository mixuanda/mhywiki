# Combat Wiki (GI + SR)

This branch keeps a combat-only subset of the original HomDGCat content while preserving the legacy page style.

## Branches

- `raw-backup`: untouched raw mirror.
- `main`: combat-only, no raw mirror committed.

## What Is Included

- Legacy-style static site: `web/legacy-site/`
- Normalized split data + tooling:
  - `combat-wiki/data/`
  - `tools/extract_from_site.py`
  - `tools/validate.py`
  - `schemas/`

## Legacy-Style Site (Recommended)

This keeps the original visual/page format while removing non-combat section routing.

### Build from local raw `site/`

```bash
python3 tools/build_legacy_site.py --site ./site --out ./web/legacy-site --clean
```

### Run locally on macOS

```bash
cd web/legacy-site
python3 -m http.server 3000
```

Open: `http://localhost:3000`

Notes:
- The generated site is CH-only by default.
- Image/static heavy assets are loaded from `https://homdgcat.wiki/` to keep repo size small.
- Yunli score routes are blocked and hidden in combat-only mode.

## Normalized Data Pipeline

### Extract

```bash
python3 tools/extract_from_site.py --site ./site --out ./combat-wiki/data --clean
```

### Validate

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r tools/requirements.txt
python tools/validate.py --data ./combat-wiki/data --schemas ./schemas
```

## Scope

Kept:
- GI: monsters/analysis, characters-weapons-artifacts, abyss/theater/youjing, banners, achievements, tutorials, change/formula, donor credits.
- SR: monsters/analysis, characters-lightcones-relics, MoC/PF/AS/AR/DU, banners, stages, glossary, achievements, change/future/formula, line-count stats.

Removed from main output routes:
- Story/lore/quest/world-exploration/admin-only sections.
- Yunli score pages (`云璃成绩`).
