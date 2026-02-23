#!/usr/bin/env python3
import json
import pathlib
import re
from datetime import datetime

BASE_DIR = pathlib.Path(__file__).resolve().parent
TRACKS_DIR = BASE_DIR / 'tracks'
MANIFEST_PATH = BASE_DIR / 'manifest.json'
INDEX_PATH = BASE_DIR / 'index.html'

CITY_ORDER = [
    'new-york-city',
    'san-francisco',
    'west-palm-beach',
    'las-vegas',
    'dallas',
    'washington-dc',
    'los-angeles',
]

CITY_LABELS = {
    'new-york-city': 'New York City',
    'san-francisco': 'San Francisco',
    'west-palm-beach': 'West Palm Beach (Mar-a-Lago bonus)',
    'las-vegas': 'Las Vegas (Area 51 bonus)',
    'dallas': 'Dallas',
    'washington-dc': 'Washington DC',
    'los-angeles': 'Los Angeles',
}

TITLE_OVERRIDES = {
    'broadway-bubble-run': 'Broadway Bubble Run',
    'subway-spring-hop': 'Subway Spring-Hop',
    'central-park-confetti': 'Central Park Confetti',
    'midtown-power-up': 'Midtown Power-Up',
    'cable-car-candy-cruise': 'Cable Car Candy Cruise',
    'golden-gate-giggle-groove': 'Golden Gate Giggle Groove',
    'foggy-pixel-morning': 'Foggy Pixel Morning',
    'silicon-spark-parade': 'Silicon Spark Parade',
    'palm-parade-pop': 'Palm Parade Pop',
    'boardwalk-bubble-beat': 'Boardwalk Bubble Beat',
    'mar-a-lago-bonus-lounge': 'Mar-a-Lago Bonus Lounge',
    'sunset-seashell-sprint': 'Sunset Seashell Sprint',
    'neon-jackpot-jive': 'Neon Jackpot Jive',
    'strip-side-shuffle': 'Strip Side Shuffle',
    'area-51-bonus-boogie': 'Area 51 Bonus Boogie',
    'desert-starlight-spin': 'Desert Starlight Spin',
    'big-d-bounce': 'Big D Bounce',
    'rodeo-boardwalk-boogie': 'Rodeo Boardwalk Boogie',
    'skyline-saddle-pop': 'Skyline Saddle Pop',
    'fairground-funk-trail': 'Fairground Funk Trail',
    'monument-march-pop': 'Monument March Pop',
    'capitol-candy-cruise': 'Capitol Candy Cruise',
    'cherry-blossom-bounce': 'Cherry Blossom Bounce',
    'smithsonian-sprint': 'Smithsonian Sprint',
    'sunset-boulevard-bop': 'Sunset Boulevard Bop',
    'venice-beach-victory-lap': 'Venice Beach Victory Lap',
    'hollywood-power-up-parade': 'Hollywood Power-Up Parade',
    'pacific-coast-pixel-cruise': 'Pacific Coast Pixel Cruise',
    'neon-borough-bounce': 'Neon Borough Bounce',
    'golden-giggle-loop': 'Golden Giggle Loop',
    'palm-sunshine-pop': 'Palm Sunshine Pop',
    'neon-casino-comet': 'Neon Casino Comet',
    'fairway-funk-stomp': 'Fairway Funk Stomp',
    'monument-confetti-run': 'Monument Confetti Run',
    'sunset-pixel-sprint': 'Sunset Pixel Sprint',
}


def humanize_slug(slug: str) -> str:
    if slug in TITLE_OVERRIDES:
        return TITLE_OVERRIDES[slug]
    return ' '.join(part.capitalize() for part in slug.split('-'))


tracks = []
for city_slug in CITY_ORDER:
    city_dir = TRACKS_DIR / city_slug
    if not city_dir.exists():
        continue

    for p in sorted(city_dir.iterdir()):
        if p.suffix.lower() not in {'.mp3', '.wav'}:
            continue
        m = re.match(r'^(\d+)-(.+?)-(elevenlabs|minimax|gemini)\.(mp3|wav)$', p.name)
        if not m:
            continue
        track_num = int(m.group(1))
        title_slug = m.group(2)
        provider = m.group(3).capitalize() if m.group(3) != 'elevenlabs' else 'ElevenLabs'
        ext = m.group(4)
        tracks.append({
            'city_slug': city_slug,
            'city': CITY_LABELS[city_slug],
            'track_number': track_num,
            'title': humanize_slug(title_slug),
            'provider': provider,
            'filename': p.name,
            'ext': ext,
            'size_bytes': p.stat().st_size,
            'path': f'tracks/{city_slug}/{p.name}',
        })

tracks.sort(key=lambda t: (CITY_ORDER.index(t['city_slug']), t['track_number'], t['provider']))

manifest = {
    'project': 'Monopoly-Style City Music Lab',
    'generated_at': datetime.now().astimezone().isoformat(),
    'total_tracks': len(tracks),
    'tracks': tracks,
}
MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding='utf-8')


def provider_badge(p: str):
    if p == 'ElevenLabs':
        return '⚡ ElevenLabs'
    if p == 'Minimax':
        return '🟠 MiniMax'
    return '💎 Gemini'


city_sections = []
for city_slug in CITY_ORDER:
    city_tracks = [t for t in tracks if t['city_slug'] == city_slug]
    if not city_tracks:
        continue

    cards = []
    for t in city_tracks:
        cards.append(f"""
        <article class='track-card'>
          <div class='track-head'>
            <h4>{t['title']}</h4>
            <span class='pill {t['provider'].lower()}'>{provider_badge(t['provider'])}</span>
          </div>
          <p class='meta'>{t['city']} · Track {t['track_number']} · {t['ext'].upper()}</p>
          <audio controls preload='none' src='{t['path']}'></audio>
        </article>
        """)

    city_sections.append(f"""
    <section class='city' id='{city_slug}'>
      <h3>{CITY_LABELS[city_slug]}</h3>
      <div class='grid'>
        {''.join(cards)}
      </div>
    </section>
    """)

nav_links = ' '.join([f"<a href='#{c}'>{CITY_LABELS[c].split(' (')[0]}</a>" for c in CITY_ORDER if (TRACKS_DIR / c).exists()])

html = f"""<!doctype html>
<html lang='en'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Monopoly-Style City Music Lab</title>
  <link rel='preconnect' href='https://fonts.googleapis.com'>
  <link rel='preconnect' href='https://fonts.gstatic.com' crossorigin>
  <link href='https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;700;800&family=Manrope:wght@400;600;700&display=swap' rel='stylesheet'>
  <style>
    :root {{
      --bg:#060b1f;
      --panel:rgba(255,255,255,.08);
      --line:rgba(255,255,255,.18);
      --text:#eff7ff;
      --muted:#c4d3ea;
      --teal:#7bf3d8;
      --gold:#ffd779;
      --pink:#ff8fc7;
    }}
    * {{box-sizing:border-box}}
    body {{
      margin:0;
      font-family:'Manrope',sans-serif;
      color:var(--text);
      background:
        radial-gradient(circle at 10% 10%, #203f8f 0%, transparent 43%),
        radial-gradient(circle at 90% 15%, #6d207d 0%, transparent 42%),
        radial-gradient(circle at 30% 95%, #025350 0%, transparent 45%),
        var(--bg);
    }}
    .wrap {{width:min(1240px,92vw); margin:24px auto 60px;}}
    .hero {{
      border:1px solid var(--line);
      border-radius:24px;
      padding:22px;
      background:linear-gradient(145deg,rgba(255,255,255,.16),rgba(255,255,255,.03));
      backdrop-filter: blur(7px);
      box-shadow:0 18px 60px rgba(0,0,0,.35);
    }}
    h1,h2,h3,h4 {{font-family:'Baloo 2',sans-serif;margin:0}}
    h1 {{font-size:clamp(1.9rem,3.1vw,2.9rem);line-height:1.03}}
    .sub {{margin-top:8px;color:var(--muted)}}
    .tags {{margin-top:14px; display:flex; flex-wrap:wrap; gap:8px}}
    .tags a {{
      text-decoration:none; color:var(--text); font-weight:700; font-size:.92rem;
      border:1px solid var(--line); background:rgba(255,255,255,.07);
      padding:7px 12px; border-radius:999px;
    }}
    .legend {{margin-top:10px;color:var(--muted);font-size:.9rem}}
    .city {{margin-top:24px; border:1px solid var(--line); border-radius:20px; padding:16px; background:var(--panel)}}
    .city h3 {{font-size:1.45rem; margin-bottom:10px}}
    .grid {{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px}}
    .track-card {{border:1px solid var(--line); border-radius:14px; background:rgba(7,16,42,.72); padding:12px}}
    .track-head {{display:flex; justify-content:space-between; gap:8px; align-items:flex-start}}
    .track-head h4 {{font-size:1.03rem; line-height:1.15}}
    .pill {{font-size:.74rem; font-weight:800; border-radius:999px; padding:4px 8px; border:1px solid transparent; white-space:nowrap}}
    .pill.elevenlabs {{background:rgba(123,243,216,.18); border-color:rgba(123,243,216,.5)}}
    .pill.minimax {{background:rgba(255,215,121,.18); border-color:rgba(255,215,121,.5)}}
    .pill.gemini {{background:rgba(255,143,199,.18); border-color:rgba(255,143,199,.5)}}
    .meta {{color:var(--muted); font-size:.86rem; margin:7px 0 9px}}
    audio {{width:100%; height:34px}}
    footer {{margin-top:18px; color:var(--muted); font-size:.9rem}}
  </style>
</head>
<body>
  <main class='wrap'>
    <header class='hero'>
      <h1>🎲 Monopoly-Style City Music Lab</h1>
      <p class='sub'>Bubbly, fun, cartoonish instrumental references — 4 core tracks per city (ElevenLabs + MiniMax) plus bonus Gemini cuts.</p>
      <div class='tags'>{nav_links}</div>
      <p class='legend'>All prompts enforced: instrumental only · no lyrics · no voices · no singing</p>
    </header>
    {''.join(city_sections)}
    <footer>Generated {manifest['generated_at']} · Total tracks: {manifest['total_tracks']}</footer>
  </main>
</body>
</html>
"""

INDEX_PATH.write_text(html, encoding='utf-8')
print(f"wrote {MANIFEST_PATH}")
print(f"wrote {INDEX_PATH}")
print(f"tracks: {len(tracks)}")
