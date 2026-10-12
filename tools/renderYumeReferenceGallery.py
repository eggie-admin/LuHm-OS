#!/usr/bin/env python3
"""Render the checked-in catalog as a portable gallery; no network or asset downloads."""
import argparse
import html
import json
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / 'media/yumeReferenceGalleryV1.json'
TEMPLATE = ROOT / 'frontEnd/yumeReferenceGallery.template.html'
OUTPUT = ROOT / 'frontEnd/yumeReferenceGallery.html'


def validate(data):
    cards = data['cards']
    if len(cards) < 24:
        raise ValueError('At least 24 exact source cards are required')
    for key in ('id', 'url'):
        if len({c[key] for c in cards}) != len(cards):
            raise ValueError('Duplicate ' + key)
    allowed = {'github.com', 'www.nexusmods.com', 'sketchfab.com'}
    for card in cards:
        for field in ('id', 'title', 'url', 'game', 'kind', 'lesson', 'registry', 'creator', 'verification'):
            if not isinstance(card.get(field), str) or not card[field].strip():
                raise ValueError('Missing card field: ' + field)
        url = urlsplit(card['url'])
        if url.scheme != 'https' or url.hostname not in allowed or url.username or url.password:
            raise ValueError('Untrusted source URL')
        if url.hostname == 'www.nexusmods.com' and not url.path.split('/')[-1].isdigit():
            raise ValueError('Nexus cards require an exact mod ID')
        if 'thumbnail' in card:
            thumb = urlsplit(card['thumbnail'])
            if thumb.scheme != 'https' or thumb.hostname != 'media.sketchfab.com':
                raise ValueError('Untrusted thumbnail')
        if 'creatorUrl' in card:
            author = urlsplit(card['creatorUrl'])
            if author.scheme != 'https' or author.hostname != 'sketchfab.com':
                raise ValueError('Untrusted creator URL')
    return cards


def render(data):
    cards = validate(data)
    fragments = []
    e = html.escape
    for card in cards:
        visual = '<div class="typePlate"><span>' + e(card['kind']) + '</span><strong>' + e(card['game']) + '</strong><small>Open the original source for images and files</small></div>'
        if card.get('thumbnail'):
            visual = '<div class="preview"><img loading="lazy" referrerpolicy="no-referrer" src="' + e(card['thumbnail'], quote=True) + '" alt="' + e(card['title'], quote=True) + ' — source preview"><span class="imageFallback" hidden>Preview unavailable · open source</span></div>'
        credit = e(card['creator'])
        if card.get('creatorUrl'):
            credit = '<a target="_blank" rel="noopener noreferrer" href="' + e(card['creatorUrl'], quote=True) + '">' + credit + '</a>'
        search = ' '.join(str(card[k]) for k in ('title','game','kind','lesson','creator')).lower()
        fragments.append(f'''<article class="card" data-id="{e(card['id'], quote=True)}" data-game="{e(card['game'], quote=True)}" data-kind="{e(card['kind'], quote=True)}" data-search="{e(search, quote=True)}">
{visual}<div class="cardBody"><div class="eyebrow">{e(card['kind'])}</div><h2>{e(card['title'])}</h2><p class="credit">{credit}</p><p class="lesson">{e(card['lesson'])}</p><details><summary>Source record</summary><p>{e(card['verification'])}</p><p>Registry: {e(card['registry'])}</p><p>Reference only · asset approval pending</p></details><div class="actions"><a class="source" href="{e(card['url'], quote=True)}" target="_blank" rel="noopener noreferrer">Open source ↗</a><button class="save" type="button" aria-pressed="false" aria-label="Shortlist {e(card['title'], quote=True)}">＋ Shortlist</button></div></div></article>''')
    options = ''.join('<option>' + e(game) + '</option>' for game in sorted({c['game'] for c in cards}))
    payload = json.dumps(cards, ensure_ascii=False).replace('<', '\\u003c')
    return TEMPLATE.read_text().replace('{{CARDS}}', '\n'.join(fragments)).replace('{{GAMES}}', options).replace('{{COUNT}}', str(len(cards))).replace('{{DATA}}', payload)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Fail if the checked-in gallery is stale')
    args = parser.parse_args()
    page = render(json.loads(CATALOG.read_text()))
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != page:
            raise SystemExit('Gallery stale: run python3 tools/renderYumeReferenceGallery.py')
        print('Gallery catalog and generated HTML match')
    else:
        OUTPUT.write_text(page)
        print(OUTPUT)


if __name__ == '__main__':
    main()
