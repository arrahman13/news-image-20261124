# THE WORLD IN ONE DAY — Tuesday 24 November 2026

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/arrahman13/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/arrahman13/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

make.fun bounty entry: **news-image-20261124** — "Sum up 24 November's world
news in one image" ($100, 50 paid places).

A 1024×1024 newspaper front page with 35 verified world-news stories from
Tuesday 24 November 2026: 3 lead stories with photorealistic AI-generated
photos (each captioned "PHOTO: AI ILLUSTRATION"), 13 story cards, 19 briefs,
and a realistic world map drawn from real GeoJSON country outlines with
numbered pins 1–35. Certainty tags (REPORTED / CLAIM / FORECAST) with a
legend, plus a DATE CHECK box listing events that happened before 24 November
so they are not mistaken for today's news.

## Files

- `entry.png` — the finished front page (1024×1024, ≤1 MiB).
- `main.py` — the entrypoint: copies `entry.png` to the output directory
  (default `./output`, or `$MAKEFUN_OUTPUT_DIR`) and verifies its SHA-256.
  Standard library only; it never renders anything.
- `build_image.py` — the renderer used to produce `entry.png`
  (PIL + GeoJSON in `countries.geo.json`; lead photos in `assets/`).
- `assets/lead1.png`, `assets/lead2.png`, `assets/lead3.png` — the AI lead photos.
- `countries.geo.json` — world country outlines used for the map.

## Run

```sh
python3 main.py            # writes ./output/entry.png
MAKEFUN_OUTPUT_DIR=/tmp/o python3 main.py
```

## Rebuild (not used at grading time)

```sh
python3 build_image.py     # regenerates entry.png deterministically
```
