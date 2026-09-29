#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
import yaml

def load_yaml(p: Path):
    return yaml.safe_load(p.read_text(encoding="utf-8"))

def main():
    ap=argparse.ArgumentParser(description="Validate Manual Forge editable source without materializing sealed art bytes.")
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args=ap.parse_args()
    root=Path(args.root).resolve()
    errors=[]; warnings=[]
    book=load_yaml(root/'book.yaml')
    assets=load_yaml(root/book['assets'])
    asset_by_path={a['path']:a for a in assets.get('assets',[])}
    seen_ch=set(); seen_scene=set()
    for rel in book.get('frontmatter',[]):
        if not (root/rel).is_file(): errors.append(f"missing frontmatter: {rel}")
    for ch in book.get('chapters',[]):
        n=ch.get('number')
        if n in seen_ch: errors.append(f"duplicate chapter number: {n}")
        seen_ch.add(n)
        for key in ('markdown','scene'):
            rel=ch.get(key)
            if not rel or not (root/rel).is_file(): errors.append(f"chapter {n} missing {key}: {rel}")
        art=ch.get('art')
        if art:
            a=asset_by_path.get(art)
            if not a: errors.append(f"chapter {n} art absent from asset manifest: {art}")
            elif not a.get('driveFileId') or not a.get('sha256'):
                errors.append(f"chapter {n} art missing Drive/hash binding: {art}")
        scene_path=root/ch['scene']
        if scene_path.is_file():
            scene=load_yaml(scene_path)
            sid=scene.get('id')
            if not sid: errors.append(f"scene missing id: {ch['scene']}")
            elif sid in seen_scene: errors.append(f"duplicate scene id: {sid}")
            else: seen_scene.add(sid)
            if scene.get('chapter') != n: errors.append(f"scene chapter mismatch: {ch['scene']}")
            if not scene.get('dialogue'): warnings.append(f"scene has no dialogue: {ch['scene']}")
    for rel in book.get('appendices',[]):
        if not (root/rel).is_file(): errors.append(f"missing appendix: {rel}")
    for key,rel in book.get('generated',{}).items():
        if not (root/rel).is_file(): errors.append(f"missing generated {key}: {rel}")
    for a in assets.get('assets',[]):
        for key in ('path','sha256','driveFileId','widthPx','heightPx'):
            if not a.get(key): errors.append(f"asset {a.get('id')} missing {key}")
    doctrine=json.loads((root/book['generated']['doctrine']).read_text(encoding='utf-8'))
    if doctrine.get('canonicalRepository') != book.get('canonicalRepository'):
        errors.append('canonical repository mismatch')
    if doctrine.get('observedMain') != book.get('observedMain'):
        warnings.append('observed main differs; regenerate doctrine blocks')
    report={
      'schema':'luhm-os.manual-source-validation.v1',
      'bookStatus':book.get('status'),
      'chapterCount':len(book.get('chapters',[])),
      'sceneCount':len(seen_scene),
      'assetBindingCount':len(assets.get('assets',[])),
      'externalSealedAssetCount':sum(1 for a in assets.get('assets',[]) if a.get('driveFileId')),
      'errors':errors,'warnings':warnings,
      'gate':'RED' if errors else ('AMBER' if warnings else 'GREEN')
    }
    out=root/'build/source-validation-report.json'
    out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))
    raise SystemExit(2 if errors else 0)
if __name__=='__main__': main()
