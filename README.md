# Combat Wiki (GI + SR)

This repository is a combat-focused refactor of the original HomDGCat mirror.

Main branch goals:
- Keep only combat-relevant GI/SR sections.
- Do not commit raw mirror assets (`site/`) to `main`.
- No Git LFS required.
- Normalize data as one-entity-per-file JSON.

## Branch Strategy

- `raw-backup`: full untouched raw mirror snapshot branch.
- `main`: orphan, lightweight branch for normalized data + tools + web frontend.

## Repository Layout

```text
combat-wiki/
  data/
    gi/
    sr/
schemas/
tools/
web/
```

## 1) Download Raw `site/` Backup

The extractor reads a local `site/` folder. Keep it outside git tracking.

Recommended source (release zip/7z):
- This repository's `raw-backup` release asset (zip of `site/`)
- Or upstream source mirror releases: https://github.com/NewbieXvwu/HomDGCat/releases

Place extracted folder as:

```text
./site
```

`site/` is intentionally ignored by `.gitignore` on `main`.

## 2) Run Extraction

```bash
python3 tools/extract_from_site.py --site ./site --out ./combat-wiki/data --clean
```

Notes:
- Default locale is `CH`.
- Extraction drops story/lore/quest/admin-oriented fields.
- Output follows one-file-per-entity and one-file-per-cycle/banner patterns.

## 3) Run Validation

Create a local virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r tools/requirements.txt
```

Run validation:

```bash
source .venv/bin/activate
python tools/validate.py --data ./combat-wiki/data --schemas ./schemas
```

Checks include:
- JSON Schema compliance.
- Reference integrity (materials, enemies, banners, stage references, etc.).

## 4) Build/Serve Wiki Frontend

```bash
cd web
npm install
npm run dev
```

Then open:
- http://localhost:3000

The frontend only exposes combat-keep routes for GI/SR and excludes lore/story navigation.

## Utility Scripts

- `tools/normalize.py`: shared parsers and normalization helpers.
- `tools/extract_from_site.py`: extract/filter/normalize from local raw `site/`.
- `tools/validate.py`: schema + reference validation.
- `tools/new_entity.py`: scaffold entity JSON templates.

Example scaffold:

```bash
python3 tools/new_entity.py --out ./combat-wiki/data --game sr --kind lightcone --id 99999 --name "New Light Cone"
```

## Scope Notes

Kept sections include GI/SR monsters, characters, gear, endgame modes, banners, achievements, formula/change pages, SR glossary and line stats, GI tutorials, and GI donor credits.

Removed from main output:
- Story/lore/quest/world exploration pages.
- Admin-only or irrelevant legacy sections.
- Yunli score pages (`云璃成绩`) and related routes.
