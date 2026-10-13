#!/usr/bin/env python3
"""Build the public, read-only English Challenge page.

Usage:
  python3 scripts/build.py --db <dir> [--audio <dir>]

--db     folder holding one JSON file per day (2026-10-01.json, ...), as exported
         from the tracker's "days" collection.
--audio  folder holding the downloaded audio files, each named <asset id>.<ext>.

Writes public/index.html, public/data.json and public/audio/*.
"""
import argparse
import datetime as dt
import json
import pathlib
import re
import shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "tracker.html"
OUT = ROOT / "public"

RESET = (
    ":root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);"
    "padding-bottom:env(safe-area-inset-bottom,0px)}"
    "body{margin:0;font:14px/1.5 system-ui,-apple-system,sans-serif;background:#fafafa}"
    "img{max-width:100%}[hidden]{display:none!important}"
)


def load_days(db_dir: pathlib.Path) -> dict:
    days = {}
    for f in sorted(db_dir.glob("*.json")):
        raw = json.loads(f.read_text(encoding="utf-8"))
        doc = raw.get("data", raw) if isinstance(raw, dict) else {}
        if not isinstance(doc, dict):
            continue
        days[f.stem] = {
            "c": doc.get("c") or {},
            "t": doc.get("t") or {},
            "a": doc.get("a") or {},
        }
    return days


def attach_audio(days: dict, audio_dir: pathlib.Path | None) -> list[str]:
    out_audio = OUT / "audio"
    out_audio.mkdir(parents=True, exist_ok=True)
    available = {}
    if audio_dir and audio_dir.is_dir():
        for f in audio_dir.iterdir():
            if f.is_file():
                available[f.stem] = f
    # keep files already published in earlier builds
    for f in out_audio.iterdir():
        if f.is_file() and f.name != ".gitkeep":
            available.setdefault(f.stem, f)

    missing = []
    for day in days.values():
        for recs in day["a"].values():
            for r in recs:
                src = available.get(r.get("id", ""))
                if not src:
                    missing.append(r.get("id", "?"))
                    continue
                dest = out_audio / src.name
                if src.resolve() != dest.resolve():
                    shutil.copyfile(src, dest)
                r["file"] = f"audio/{src.name}"
    return missing


def build_html() -> str:
    page = SRC.read_text(encoding="utf-8")
    head_bits = []
    for pattern in (r"<title>.*?</title>\s*", r"<link [^>]*>\s*"):
        for m in re.findall(pattern, page, flags=re.S):
            head_bits.append(m.strip())
            page = page.replace(m, "", 1)
    return (
        "<!doctype html><html lang=\"pt-BR\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1,viewport-fit=cover\">"
        "<meta name=\"robots\" content=\"noindex\">"
        + "".join(head_bits)
        + f"<style>{RESET}</style></head><body>"
        + "<script>window.__STATIC__=true</script>"
        + page
        + "</body></html>"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--audio")
    args = ap.parse_args()

    days = load_days(pathlib.Path(args.db))
    missing = attach_audio(days, pathlib.Path(args.audio) if args.audio else None)

    OUT.mkdir(exist_ok=True)
    (OUT / "index.html").write_text(build_html(), encoding="utf-8")
    data = {
        "generatedAt": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "days": days,
    }
    (OUT / "data.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

    n_audio = sum(len(r) for d in days.values() for r in d["a"].values())
    print(f"days: {len(days)} | audio entries: {n_audio} | missing audio files: {len(missing)}")
    for m in missing:
        print("  missing:", m)


if __name__ == "__main__":
    main()
