#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
from pathlib import Path

import mistune
import yaml
from PIL import Image

STATUS_ORDER = {"GREEN": 0, "AMBER": 1, "RED": 2, "UNKNOWN": 3}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def frontmatter(text: str):
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, text
    meta = yaml.safe_load(text[4:end]) or {}
    return meta, text[end + 5 :]


def validate(root: Path, book: dict, assets: dict) -> dict:
    errors, warnings = [], []
    asset_by_path = {a["path"]: a for a in assets.get("assets", [])}
    chapter_numbers = set()
    scene_ids = set()

    for rel in book.get("frontmatter", []):
        if not (root / rel).is_file():
            errors.append(f"missing frontmatter: {rel}")

    for ch in book.get("chapters", []):
        n = ch.get("number")
        if n in chapter_numbers:
            errors.append(f"duplicate chapter number: {n}")
        chapter_numbers.add(n)
        for key in ("markdown", "scene"):
            rel = ch.get(key)
            if not rel or not (root / rel).is_file():
                errors.append(f"chapter {n} missing {key}: {rel}")
        if ch.get("art") and not (root / ch["art"]).is_file():
            asset = asset_by_path.get(ch["art"])
            if asset and asset.get("driveFileId"):
                warnings.append(f"chapter {n} art not materialized locally: {ch['art']}")
            else:
                errors.append(f"chapter {n} missing art: {ch['art']}")
        if ch.get("art") and ch["art"] not in asset_by_path:
            warnings.append(f"chapter {n} art not listed in assets manifest: {ch['art']}")

        scene_path = root / ch["scene"]
        if scene_path.is_file():
            scene = load_yaml(scene_path)
            sid = scene.get("id")
            if not sid:
                errors.append(f"scene missing id: {ch['scene']}")
            elif sid in scene_ids:
                errors.append(f"duplicate scene id: {sid}")
            else:
                scene_ids.add(sid)
            if scene.get("chapter") != n:
                errors.append(f"scene chapter mismatch: {ch['scene']} -> {scene.get('chapter')} expected {n}")
            if not scene.get("dialogue"):
                warnings.append(f"scene has no dialogue: {ch['scene']}")

    for rel in book.get("appendices", []):
        if not (root / rel).is_file():
            errors.append(f"missing appendix: {rel}")

    for key, rel in book.get("generated", {}).items():
        if not (root / rel).is_file():
            errors.append(f"missing generated {key}: {rel}")

    for a in assets.get("assets", []):
        p = root / a["path"]
        if not p.is_file():
            if a.get("driveFileId"):
                warnings.append(f"sealed asset not materialized locally: {a['id']}")
                continue
            errors.append(f"missing asset: {a['path']}")
            continue
        got = sha256(p)
        if got != a.get("sha256"):
            errors.append(f"asset hash mismatch: {a['id']} expected {a.get('sha256')} got {got}")
            continue
        with Image.open(p) as im:
            if im.width != a.get("widthPx") or im.height != a.get("heightPx"):
                errors.append(f"asset dimension mismatch: {a['id']} expected {a.get('widthPx')}x{a.get('heightPx')} got {im.width}x{im.height}")

    doctrine_path = root / book["generated"]["doctrine"]
    if doctrine_path.is_file():
        d = json.loads(doctrine_path.read_text(encoding="utf-8"))
        if d.get("canonicalRepository") != book.get("canonicalRepository"):
            errors.append("canonical repository mismatch between book.yaml and current-doctrine.json")
        if d.get("observedMain") != book.get("observedMain"):
            warnings.append("observed main differs between book.yaml and current-doctrine.json; refresh generated doctrine blocks")

    return {
        "schema": "luhm-os.manual-build-report.v1",
        "bookStatus": book.get("status"),
        "chapterCount": len(book.get("chapters", [])),
        "sceneCount": len(scene_ids),
        "assetCount": len(assets.get("assets", [])),
        "errors": errors,
        "warnings": warnings,
        "gate": "RED" if errors else ("AMBER" if warnings else "GREEN"),
    }


def scene_html(scene: dict) -> str:
    rows = []
    for item in scene.get("dialogue", []):
        speaker = html.escape(str(item.get("speaker", "")))
        text = html.escape(str(item.get("text", "")))
        rows.append(f'<div class="dialogue"><b>{speaker}</b><span>{text}</span></div>')
    return (
        '<section class="scene-block">'
        f'<div class="scene-kicker">ACTED SCENE · CHAPTER {scene.get("chapter")}</div>'
        + "".join(rows)
        + "</section>"
    )


def render_markdown(md_text: str, scene: dict | None, status_md: str) -> str:
    if scene:
        md_text = re.sub(r"\{\{\s*scene:\s*[^}]+\}\}", scene_html(scene), md_text)
    md_text = re.sub(r"\{\{\s*statusBlock:\s*current\s*\}\}", status_md, md_text)
    renderer = mistune.create_markdown(escape=False, plugins=["table", "strikethrough"])
    return renderer(md_text)


def copy_asset(root: Path, out_assets: Path, rel: str):
    src = root / rel
    dst = out_assets / Path(rel).name
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return f"assets/{dst.name}"


def build_preview(root: Path, book: dict, report: dict) -> Path:
    out = root / "dist" / "preview"
    if out.exists():
        shutil.rmtree(out)
    (out / "assets").mkdir(parents=True)
    status_md = (root / book["generated"]["status"]).read_text(encoding="utf-8")

    parts = []
    cover = next((a for a in load_yaml(root / book["assets"])["assets"] if a.get("role") == "cover"), None)
    if cover:
        cover_rel = copy_asset(root, out / "assets", cover["path"])
        parts.append(f'<section class="hero"><img src="{cover_rel}" alt="LuHm OS Field Manual cover"></section>')

    for rel in book.get("frontmatter", []):
        text = (root / rel).read_text(encoding="utf-8")
        _, body = frontmatter(text)
        parts.append(f'<section class="chapter frontmatter">{render_markdown(body, None, status_md)}</section>')

    for ch in book.get("chapters", []):
        md = (root / ch["markdown"]).read_text(encoding="utf-8")
        _, body = frontmatter(md)
        scene = load_yaml(root / ch["scene"])
        art_html = ""
        if ch.get("art"):
            art_rel = copy_asset(root, out / "assets", ch["art"])
            art_html = f'<figure class="chapter-art"><img src="{art_rel}" alt="{html.escape(ch["title"])}"></figure>'
        content = render_markdown(body, scene, status_md)
        parts.append(f'<section class="chapter" id="chapter-{ch["number"]}">{art_html}{content}</section>')

    for rel in book.get("appendices", []):
        text = (root / rel).read_text(encoding="utf-8")
        _, body = frontmatter(text)
        parts.append(f'<section class="chapter appendix">{render_markdown(body, None, status_md)}</section>')

    css = """
:root{--bg:#0c1214;--panel:#111b1e;--paper:#f3ead8;--ink:#171717;--cyan:#27d6d1;--red:#ed4038;--muted:#9db0b3}
*{box-sizing:border-box} body{margin:0;background:var(--bg);color:#ecf5f4;font-family:system-ui,-apple-system,Segoe UI,sans-serif;line-height:1.55}
.hero,.chapter{width:min(1180px,calc(100% - 32px));margin:24px auto;border:1px solid #284247;background:var(--panel);box-shadow:0 16px 45px #0008}
.hero img,.chapter-art img{display:block;width:100%;height:auto}.chapter{padding:38px}.chapter-art{margin:-38px -38px 28px}.chapter h1,.chapter h2{font-family:Impact,Haettenschweiler,'Arial Narrow Bold',sans-serif;letter-spacing:.03em}.chapter h1{font-size:clamp(2rem,5vw,4.6rem);line-height:.98;border-bottom:5px solid var(--red);padding-bottom:.15em}.chapter h2{color:var(--cyan);margin-top:1.6em}.chapter blockquote{margin:1.2em 0;padding:1em 1.2em;border-left:6px solid var(--red);background:#0b1517}.scene-block{margin:1.5em 0;padding:18px;border:2px solid var(--cyan);background:#091315}.scene-kicker{font-size:.8rem;letter-spacing:.16em;color:var(--cyan);margin-bottom:12px}.dialogue{display:grid;grid-template-columns:minmax(90px,150px) 1fr;gap:14px;padding:10px 0;border-top:1px solid #234044}.dialogue:first-of-type{border-top:0}.dialogue b{color:#ff6d64}.dialogue span{color:#fff}code,pre{background:#071012;border:1px solid #29484c}pre{padding:14px;overflow:auto}table{border-collapse:collapse;width:100%}td,th{border:1px solid #35555a;padding:8px;text-align:left}.frontmatter{border-style:dashed}.appendix{background:#101719}.build-footer{width:min(1180px,calc(100% - 32px));margin:18px auto 50px;color:var(--muted);font-size:.9rem}
@media print{body{background:#fff;color:#000}.hero,.chapter{box-shadow:none;border:0;page-break-after:always;margin:0;width:100%;background:#fff;color:#000}.scene-block{background:#fff;color:#000}.dialogue span{color:#000}}
"""
    doc = f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(book['title'])}</title><style>{css}</style></head><body>{''.join(parts)}<div class="build-footer">Manual Forge preview · validation gate {report['gate']} · {report['chapterCount']} chapters · {report['assetCount']} sealed plates</div></body></html>'''
    (out / "index.html").write_text(doc, encoding="utf-8")
    return out / "index.html"


def main():
    ap = argparse.ArgumentParser(description="Validate and preview the LuHm OS Manual Forge source project.")
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    ap.add_argument("--validate-only", action="store_true")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    book = load_yaml(root / "book.yaml")
    assets = load_yaml(root / book["assets"])
    report = validate(root, book, assets)
    build_dir = root / "build"
    build_dir.mkdir(exist_ok=True)
    (build_dir / "build-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if report["errors"]:
        raise SystemExit(2)
    if not args.validate_only:
        preview = build_preview(root, book, report)
        print(f"preview: {preview}")


if __name__ == "__main__":
    main()
