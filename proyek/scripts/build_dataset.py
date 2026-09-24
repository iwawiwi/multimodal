#!/usr/bin/env python3
"""
Builds the SEA-VL Indonesian cultural retrieval dataset used by the capstone
project ("Proyek Akhir Multimodal").

Pipeline
--------
  1. Download the SEA-VL crowdsourcing parquet shards from Hugging Face
     (the redistributed Indonesian subset, 3,096 rows).
  2. Filter to Indonesian cultural locations (`culture_relevant_loc`).
  3. Optional quality filters (cultural relevance / caption fit / image quality).
  4. Deduplicate identical images by MD5 of the raw bytes.
  5. Coarse cultural category labelling (keyword based, deliberately simple).
  6. Convert every image to RGB and cap its long side (normalises the 667
     distinct source resolutions and removes RGBA / palette / MPO edge cases).
  7. Deterministic stratified train / val / test split. The test split is the
     private held-out set: it must NOT be distributed to students before the
     evaluation week.
  8. Write manifests, an attribution notice and a statistics report.

Source
------
  Dataset : KORIKA-AI/sea-vl_crowdsourcing_id  (CC BY-SA 4.0)
  Upstream: SEACrowd/sea-vl_crowdsourcing
  Paper   : Cahyawijaya et al., "Crowdsource, Crawl, or Generate? Creating
            SEA-VL, a Multicultural Vision-Language Dataset for Southeast Asia",
            ACL 2025.

Usage
-----
    # full build (downloads ~1.6 GB once, writes images + manifests)
    python3 proyek/scripts/build_dataset.py --out proyek/data/sea-vl-id

    # inspect only, write nothing
    python3 proyek/scripts/build_dataset.py --verify-only

    # small smoke test
    python3 proyek/scripts/build_dataset.py --limit 120 --out /tmp/svl-smoke

    # distributable bundle for students (train + val only, no test)
    python3 proyek/scripts/build_dataset.py --export /tmp/svl-dist
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import random
import shutil
import sys
import time
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

try:
    import pyarrow.parquet as pq
except ImportError:  # pragma: no cover
    sys.exit("pyarrow is required -> pip install -r proyek/scripts/requirements.txt")

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    sys.exit("Pillow is required -> pip install -r proyek/scripts/requirements.txt")

# --------------------------------------------------------------------------- #
# Source
# --------------------------------------------------------------------------- #

HF_REPO = "KORIKA-AI/sea-vl_crowdsourcing_id"
HF_BASE = f"https://huggingface.co/datasets/{HF_REPO}/resolve/main/data/"
SHARDS = [f"train-{i:05d}-of-00004.parquet" for i in range(4)]

# Coarse cultural categories. Deliberately keyword based: the upstream dataset
# ships no taxonomy, so this is a starting point for the lecturer to refine.
# Multi-label in reality; we keep the first matching category by priority order.
CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "kuliner": [
        "makanan", "hidangan", "kuliner", "kue", "sate", "nasi", "rendang",
        "gado", "bakso", "soto", "food", "dish", "cuisine", "cake", "noodle",
        "restaurant", "warung", "jajanan", "minuman",
    ],
    "tarian": [
        "tari", "penari", "dance", "dancer", "sendratari", "pementasan",
        "pertunjukan", "performance",
    ],
    "pakaian/tekstil": [
        "pakaian", "adat", "kebaya", "batik", "tenun", "songket", "kain",
        "busana", "attire", "clothing", "fabric", "costume", "sarung",
    ],
    "arsitektur/bangunan": [
        "rumah", "candi", "masjid", "gereja", "pura", "bangunan", "gedung",
        "monumen", "arsitektur", "temple", "mosque", "building",
        "architecture", "monument", "house", "istana",
    ],
    "tempat/alam": [
        "gunung", "pantai", "danau", "taman", "hutan", "pemandangan",
        "sungai", "air terjun", "mountain", "beach", "lake", "park",
        "landscape", "waterfall", "island", "sawah",
    ],
    "upacara/ritual": [
        "upacara", "ritual", "prosesi", "adat istiadat", "ceremony",
        "procession", "pernikahan", "wedding",
    ],
    "alat musik": [
        "musik", "gamelan", "angklung", "kendang", "instrument", "music",
        "gong", "alat musik",
    ],
    "wayang/seni": [
        "wayang", "lukisan", "patung", "seni", "ukiran", "painting",
        "sculpture", "art", "carving", "topeng", "mask",
    ],
    "transportasi": [
        "bus", "kereta", "becak", "angkot", "kapal", "train", "vehicle",
        "station", "airport", "stasiun", "bandara", "ojek",
    ],
    "flora/fauna": [
        "bunga", "tanaman", "hewan", "burung", "kucing", "anjing", "flower",
        "plant", "animal", "bird", "cat", "dog", "pohon", "buah",
    ],
}

MANIFEST_FIELDS = [
    "image_id", "file", "caption_en", "caption_id", "native_lang", "loc",
    "category", "relevance", "caption_fit", "img_quality", "n_annotator",
    "width", "height", "split",
]


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def log(msg: str) -> None:
    print(msg, flush=True)


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if abs(n) < 1024 or unit == "GB":
            return f"{n:.1f} {unit}"
        n /= 1024.0
    return f"{n:.1f} GB"


def coarse_category(*texts: str) -> str:
    """First matching cultural category, else 'lain-lain'."""
    blob = " ".join(t or "" for t in texts).lower()
    for name, words in CATEGORY_KEYWORDS.items():
        if any(w in blob for w in words):
            return name
    return "lain-lain"


def download(url: str, dest: Path) -> None:
    """Download with a simple progress line; skips an already-complete file."""
    if dest.exists() and dest.stat().st_size > 0:
        log(f"  cached   {dest.name} ({human(dest.stat().st_size)})")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    with urllib.request.urlopen(url) as r, open(tmp, "wb") as f:
        total = int(r.headers.get("Content-Length") or 0)
        got = 0
        t0 = time.time()
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            f.write(chunk)
            got += len(chunk)
            if total:
                pct = got / total * 100
                speed = got / max(time.time() - t0, 1e-6)
                print(
                    f"\r  {dest.name}  {pct:5.1f}%  {human(got)}/{human(total)}"
                    f"  {human(speed)}/s   ",
                    end="",
                    flush=True,
                )
    print()
    tmp.replace(dest)


def fetch_shards(cache: Path) -> list[Path]:
    cache.mkdir(parents=True, exist_ok=True)
    log(f"1. Source shards -> {cache}")
    paths = []
    for name in SHARDS:
        dest = cache / name
        download(HF_BASE + name, dest)
        paths.append(dest)
    return paths


def iter_rows(paths: list[Path], batch_size: int = 32):
    """Stream (index, row-dict) tuples without holding all image bytes at once."""
    for path in paths:
        pf = pq.ParquetFile(path)
        base = 0
        for batch in pf.iter_batches(batch_size=batch_size):
            cols = batch.to_pydict()
            n = batch.num_rows
            for i in range(n):
                yield {
                    "index": base + i,
                    "id": cols["id"][i],
                    "image": cols["image"][i]["bytes"],
                    "caption_en": cols["caption"][i],
                    "caption_id": cols["caption_native_lang"][i],
                    "loc": cols["culture_relevant_loc"][i],
                    "native_lang": cols["native_lang"][i],
                    "relevance": cols["avg_cultural_relevance"][i],
                    "caption_fit": cols["avg_caption_fit"][i],
                    "img_quality": cols["avg_img_quality"][i],
                    "n_annotator": cols["n_annotator"][i],
                }
            base += n


# --------------------------------------------------------------------------- #
# Split
# --------------------------------------------------------------------------- #

def stratified_split(rows: list[dict], val_frac: float, test_frac: float,
                     seed: int, key: str) -> dict[str, str]:
    """Deterministic stratified split; returns {image_id: split}."""
    rng = random.Random(seed)
    groups: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        groups[r[key]].append(r)

    assign: dict[str, str] = {}
    for _, members in sorted(groups.items()):
        members.sort(key=lambda r: r["image_id"])
        rng.shuffle(members)
        n = len(members)
        n_test = int(round(n * test_frac))
        n_val = int(round(n * val_frac))
        # guarantee at least one val row in non-trivial groups
        if n >= 10 and n_val == 0:
            n_val = 1
        for i, r in enumerate(members):
            if i < n_test:
                assign[r["image_id"]] = "test"
            elif i < n_test + n_val:
                assign[r["image_id"]] = "val"
            else:
                assign[r["image_id"]] = "train"
    return assign


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #

def build(args) -> int:
    out = Path(args.out).expanduser().resolve()
    cache = Path(args.cache).expanduser().resolve()
    rows: list[dict] = []
    seen: dict[str, str] = {}          # md5 -> image_id (dedup)
    counters: Counter = Counter()
    dims: list[tuple[int, int]] = []
    source_formats: Counter = Counter()
    source_modes: Counter = Counter()
    written_bytes = 0

    if not args.verify_only:
        (out / "images").mkdir(parents=True, exist_ok=True)
        log(f"1. Output -> {out}")

    paths = fetch_shards(cache)

    log("2. Filter, deduplicate, convert and write images")
    t0 = time.time()
    for src in iter_rows(paths):
        if args.limit and counters["total"] >= args.limit:
            break
        counters["total"] += 1

        # --- location filter -------------------------------------------- #
        if args.loc_filter and args.loc_filter.lower() not in (src["loc"] or "").lower():
            counters["drop_loc"] += 1
            continue

        # --- quality filters -------------------------------------------- #
        if (src["relevance"] or 0) < args.min_relevance:
            counters["drop_relevance"] += 1
            continue
        if (src["caption_fit"] or 0) < args.min_fit:
            counters["drop_fit"] += 1
            continue
        if (src["img_quality"] or 0) < args.min_quality:
            counters["drop_quality"] += 1
            continue

        # --- language check (optional) ---------------------------------- #
        if args.lang_check:
            lang = detect_lang(src["caption_id"])
            if lang not in ("id", "unknown"):
                counters["drop_lang"] += 1
                continue

        # --- deduplicate on raw bytes ------------------------------------ #
        raw = src["image"]
        md5 = hashlib.md5(raw).hexdigest()
        if md5 in seen:
            counters["drop_duplicate"] += 1
            continue
        seen[md5] = str(src["id"])

        # --- image conversion -------------------------------------------- #
        image_id = f"svl_{src['id']}"
        try:
            im = Image.open(io.BytesIO(raw))
            source_formats[im.format or "?"] += 1
            source_modes[im.mode] += 1
            im = im.convert("RGB")
            if args.max_side and max(im.size) > args.max_side:
                im.thumbnail((args.max_side, args.max_side), Image.LANCZOS)
        except Exception as exc:  # noqa: BLE001
            counters["drop_broken"] += 1
            log(f"   ! {image_id}: {exc}")
            continue

        ext = "webp" if args.format == "webp" else "jpg"
        rel = f"images/{image_id}.{ext}"
        if not args.verify_only:
            path = out / rel
            if not path.exists():
                if args.format == "webp":
                    im.save(path, "WEBP", quality=args.quality, method=4)
                else:
                    im.save(path, "JPEG", quality=args.quality, optimize=True)
            written_bytes += path.stat().st_size
            dims.append(im.size)

        rows.append({
            "image_id": image_id,
            "file": rel,
            "caption_en": (src["caption_en"] or "").strip(),
            "caption_id": (src["caption_id"] or "").strip(),
            "native_lang": src["native_lang"],
            "loc": src["loc"],
            "category": coarse_category(src["caption_en"], src["caption_id"]),
            "relevance": round(float(src["relevance"] or 0), 3),
            "caption_fit": round(float(src["caption_fit"] or 0), 3),
            "img_quality": round(float(src["img_quality"] or 0), 3),
            "n_annotator": int(src["n_annotator"] or 0),
            "width": im.width,
            "height": im.height,
            "split": "",
        })
        counters["kept"] += 1
        if counters["kept"] % 250 == 0:
            print(f"\r   kept {counters['kept']:5d}  ({time.time()-t0:.0f}s)   ",
                  end="", flush=True)
    print()

    if not rows:
        log("Nothing left after filtering. Aborting.")
        return 1

    # --- split ---------------------------------------------------------- #
    key = args.stratify if args.stratify in ("category", "loc") else "category"
    if args.stratify == "none":
        key = "native_lang"  # single bucket -> plain random split
    assign = stratified_split(rows, args.val_frac, args.test_frac, args.seed, key)
    for r in rows:
        r["split"] = assign[r["image_id"]]
    rows.sort(key=lambda r: r["image_id"])

    # --- write manifests ------------------------------------------------ #
    if not args.verify_only:
        log("3. Writing manifests")
        with open(out / "manifest.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=MANIFEST_FIELDS)
            w.writeheader()
            w.writerows(rows)
        for split in ("train", "val", "test"):
            subset = [r for r in rows if r["split"] == split]
            with open(out / f"{split}.csv", "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=MANIFEST_FIELDS)
                w.writeheader()
                w.writerows(subset)

        (out / "ATTRIBUTION.md").write_text(ATTRIBUTION.format(
            repo=HF_REPO, n=len(rows)), encoding="utf-8")

    # --- statistics ------------------------------------------------------ #
    split_counts = Counter(r["split"] for r in rows)
    cat_counts = Counter(r["category"] for r in rows)
    loc_counts = Counter(r["loc"] for r in rows)
    stats = {
        "source": HF_REPO,
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "args": {k: v for k, v in vars(args).items()},
        "pipeline": dict(counters),
        "kept": len(rows),
        "splits": dict(split_counts),
        "categories": dict(cat_counts.most_common()),
        "top_locations": dict(loc_counts.most_common(15)),
        "native_lang": dict(Counter(r["native_lang"] for r in rows)),
        "source_image_formats": dict(source_formats),
        "source_image_modes": dict(source_modes),
        "written_image_bytes": written_bytes,
        "mean_relevance": round(sum(r["relevance"] for r in rows) / len(rows), 3),
        "mean_caption_fit": round(sum(r["caption_fit"] for r in rows) / len(rows), 3),
        "mean_img_quality": round(sum(r["img_quality"] for r in rows) / len(rows), 3),
    }
    if not args.verify_only:
        (out / "stats.json").write_text(
            json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")

    # --- report ---------------------------------------------------------- #
    log("")
    log("=" * 66)
    log(f"  rows read              : {counters['total']}")
    log(f"  dropped (location)     : {counters['drop_loc']}")
    log(f"  dropped (relevance)    : {counters['drop_relevance']}")
    log(f"  dropped (caption fit)  : {counters['drop_fit']}")
    log(f"  dropped (img quality)  : {counters['drop_quality']}")
    log(f"  dropped (language)     : {counters['drop_lang']}")
    log(f"  dropped (duplicate)    : {counters['drop_duplicate']}")
    log(f"  dropped (broken image) : {counters['drop_broken']}")
    log(f"  KEPT                   : {len(rows)}")
    log("-" * 66)
    log(f"  splits                 : " + "  ".join(
        f"{k}={v}" for k, v in sorted(split_counts.items())))
    log(f"  categories             :")
    for k, v in cat_counts.most_common():
        log(f"      {v:5d}  ({v/len(rows)*100:5.1f}%)  {k}")
    log(f"  source formats/modes   : {dict(source_formats)} / {dict(source_modes)}")
    log(f"  images written         : {human(written_bytes)}")
    log(f"  mean relevance / fit   : {stats['mean_relevance']} / {stats['mean_caption_fit']}")
    log("=" * 66)
    if not args.verify_only:
        log(f"  manifest : {out / 'manifest.csv'}")
        log(f"  test set : {out / 'test.csv'}  <-- PRIVATE, do not distribute")
        log(f"  stats    : {out / 'stats.json'}")

    # --- export ---------------------------------------------------------- #
    if args.export:
        export_dir = Path(args.export).expanduser().resolve()
        log("")
        log(f"4. Exporting distributable bundle (train + val) -> {export_dir}")
        (export_dir / "images").mkdir(parents=True, exist_ok=True)
        n = 0
        for r in rows:
            if r["split"] == "test":
                continue
            src = out / r["file"]
            if src.exists():
                shutil.copy2(src, export_dir / r["file"])
                n += 1
        for split in ("train", "val"):
            shutil.copy2(out / f"{split}.csv", export_dir / f"{split}.csv")
        shutil.copy2(out / "ATTRIBUTION.md", export_dir / "ATTRIBUTION.md")
        with open(export_dir / "README.txt", "w", encoding="utf-8") as f:
            f.write(EXPORT_README.format(n=n))
        log(f"  {n} images copied (test set withheld)")
        log(f"  bundle   : {export_dir}")

    return 0


# --------------------------------------------------------------------------- #
# Optional language detection
# --------------------------------------------------------------------------- #

def detect_lang(text: str) -> str:
    try:
        from langdetect import detect, DetectorFactory
        DetectorFactory.seed = 0
        return detect(text or "")
    except Exception:  # noqa: BLE001
        return "unknown"


# --------------------------------------------------------------------------- #
# Text assets
# --------------------------------------------------------------------------- #

ATTRIBUTION = """# Attribution — SEA-VL Indonesian subset

This dataset is a filtered and re-packaged derivative of:

- **Dataset**: `{repo}`
  (Indonesian subset of `SEACrowd/sea-vl_crowdsourcing`)
- **Licence**: Creative Commons Attribution-ShareAlike 4.0 International
  (CC BY-SA 4.0) — https://creativecommons.org/licenses/by-sa/4.0/
- **Paper**: Cahyawijaya et al., *Crowdsource, Crawl, or Generate? Creating
  SEA-VL, a Multicultural Vision-Language Dataset for Southeast Asia*,
  ACL 2025.

## Obligations when you use this data

1. **Attribution** — credit SEA-VL / SEACrowd / KORIKA-AI and cite the paper
   above wherever results are published or presented.
2. **ShareAlike** — if you redistribute this derivative dataset (or a modified
   version of it), you must release it under the same CC BY-SA 4.0 licence.
3. **No additional restrictions** — you may not apply legal terms that
   prevent others from doing what the licence permits.

## Local modifications applied

- retained only rows whose `culture_relevant_loc` contains "Indonesia"
- removed duplicate images (identical MD5)
- converted all images to RGB and capped the long side
- added a coarse keyword-based `category` column and a `split` column

Number of retained samples: **{n}**
"""

EXPORT_README = """SEA-VL Indonesian cultural retrieval dataset — student bundle

{n} images with bilingual captions (Indonesian + English).

Files
-----
  images/          one image per row, named svl_<wikipedia_id>.jpg
  train.csv        training split
  val.csv          validation split
  ATTRIBUTION.md   licence and citation obligations (read this)

Manifest columns
----------------
  image_id     unique identifier, matches the file name in images/
  file         relative image path
  caption_en   English caption
  caption_id   Indonesian caption
  native_lang  source language label
  loc          cultural location(s) of the subject
  category     coarse cultural category (keyword based, may be refined)
  relevance    mean annotator score for cultural relevance (3.0-5.0)
  caption_fit  mean annotator score for caption/image fit (0.67-1.0)
  img_quality  mean annotator score for image quality (0.67-1.0)
  n_annotator  number of independent annotators (2-4)
  width/height stored image dimensions

The test split is deliberately withheld. It is released in the evaluation week.
"""


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main() -> int:
    p = argparse.ArgumentParser(
        description="Build the SEA-VL Indonesian cultural retrieval dataset.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--out", default="proyek/data/sea-vl-id",
                   help="output directory for images and manifests")
    p.add_argument("--cache", default="proyek/data/.cache",
                   help="directory holding the downloaded parquet shards")
    p.add_argument("--limit", type=int, default=0,
                   help="stop after N source rows (0 = no limit, for smoke tests)")
    p.add_argument("--loc-filter", default="Indonesia",
                   help="keep rows whose location contains this substring "
                        "(empty string disables the filter)")
    p.add_argument("--min-relevance", type=float, default=3.0,
                   help="minimum avg_cultural_relevance")
    p.add_argument("--min-fit", type=float, default=0.0,
                   help="minimum avg_caption_fit")
    p.add_argument("--min-quality", type=float, default=0.0,
                   help="minimum avg_img_quality")
    p.add_argument("--lang-check", action="store_true",
                   help="drop rows whose Indonesian caption is not detected as "
                        "Indonesian (requires langdetect)")
    p.add_argument("--val-frac", type=float, default=0.10, help="validation fraction")
    p.add_argument("--test-frac", type=float, default=0.15,
                   help="private test fraction")
    p.add_argument("--stratify", choices=["category", "loc", "none"],
                   default="category", help="stratification key for the split")
    p.add_argument("--seed", type=int, default=42, help="split seed")
    p.add_argument("--max-side", type=int, default=1024,
                   help="cap the long side of stored images (0 = keep original)")
    p.add_argument("--format", choices=["jpg", "webp"], default="jpg",
                   help="stored image format")
    p.add_argument("--quality", type=int, default=90,
                   help="JPEG/WebP quality for stored images")
    p.add_argument("--verify-only", action="store_true",
                   help="report statistics without writing anything")
    p.add_argument("--export", default="",
                   help="also write a distributable bundle (train + val only) here")
    args = p.parse_args()

    if args.val_frac + args.test_frac >= 1.0:
        sys.exit("--val-frac + --test-frac must be < 1.0")

    try:
        return build(args)
    except KeyboardInterrupt:
        log("\nInterrupted.")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
