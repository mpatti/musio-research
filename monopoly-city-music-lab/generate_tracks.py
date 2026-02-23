#!/usr/bin/env python3
import os
import re
import json
import time
import html
import pathlib
from datetime import datetime

import requests

BASE_DIR = pathlib.Path(__file__).resolve().parent
TRACKS_DIR = BASE_DIR / "tracks"
MANIFEST_PATH = BASE_DIR / "manifest.json"
INDEX_PATH = BASE_DIR / "index.html"
TOOLS_PATH = pathlib.Path("/data/.openclaw/workspace/TOOLS.md")

MINIMAX_URL = "https://api.minimax.io/v1/music_generation"
ELEVEN_URL = "https://api.elevenlabs.io/v1/music/stream"


def slugify(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def read_keys():
    text = TOOLS_PATH.read_text(encoding="utf-8")
    mm = re.search(r"\*\*MiniMax\*\*:\s*`([^`]+)`", text)
    el = re.search(r"\*\*ElevenLabs\*\*:\s*`([^`]+)`", text)
    if not mm:
        raise RuntimeError("MiniMax API key not found in TOOLS.md")
    if not el:
        raise RuntimeError("ElevenLabs API key not found in TOOLS.md")
    return mm.group(1).strip(), el.group(1).strip()


def minimax_generate(api_key: str, prompt: str, out_path: pathlib.Path):
    payload = {
        "model": "music-2.5",
        "prompt": prompt,
        "lyrics": "[Inst]",
        "output_format": "hex",
        "audio_setting": {"sample_rate": 44100, "bitrate": 128000, "format": "mp3"},
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    for attempt in range(1, 6):
        try:
            r = requests.post(MINIMAX_URL, headers=headers, json=payload, timeout=300)
        except Exception as e:
            if attempt == 5:
                raise RuntimeError(f"MiniMax request failed: {e}")
            time.sleep(4 * attempt)
            continue

        if r.status_code >= 500:
            if attempt == 5:
                raise RuntimeError(f"MiniMax server error: {r.status_code} {r.text[:400]}")
            time.sleep(4 * attempt)
            continue

        try:
            data = r.json()
        except Exception:
            if attempt == 5:
                raise RuntimeError(f"MiniMax invalid JSON: {r.status_code} {r.text[:400]}")
            time.sleep(4 * attempt)
            continue

        base = data.get("base_resp") or {}
        status_code = base.get("status_code", -1)
        status_msg = base.get("status_msg", "")

        if status_code == 0:
            audio_hex = (data.get("data") or {}).get("audio")
            if not audio_hex:
                if attempt == 5:
                    raise RuntimeError("MiniMax success status but no audio field")
                time.sleep(2 * attempt)
                continue
            audio_bytes = bytes.fromhex(audio_hex)
            out_path.write_bytes(audio_bytes)
            extra = (data.get("data") or {}).get("extra_info") or {}
            return {
                "provider": "MiniMax",
                "bytes": len(audio_bytes),
                "music_duration_ms": extra.get("music_duration"),
                "sample_rate": extra.get("music_sample_rate"),
                "bitrate": extra.get("bitrate"),
            }

        if status_code in (1002,):
            time.sleep(5 * attempt)
            continue

        if attempt == 5:
            raise RuntimeError(f"MiniMax API error {status_code}: {status_msg}")

        time.sleep(3 * attempt)

    raise RuntimeError("MiniMax generation failed after retries")


def eleven_generate(api_key: str, prompt: str, out_path: pathlib.Path):
    payload = {
        "prompt": prompt,
        "music_length_ms": 30000,
        "model_id": "music_v1",
        "force_instrumental": True,
    }

    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
    }

    for attempt in range(1, 6):
        try:
            r = requests.post(
                ELEVEN_URL,
                params={"output_format": "mp3_44100_128"},
                headers=headers,
                json=payload,
                timeout=300,
            )
        except Exception as e:
            if attempt == 5:
                raise RuntimeError(f"ElevenLabs request failed: {e}")
            time.sleep(4 * attempt)
            continue

        if r.status_code == 200 and r.content:
            out_path.write_bytes(r.content)
            return {
                "provider": "ElevenLabs",
                "bytes": len(r.content),
                "song_id": r.headers.get("song_id") or r.headers.get("song-id"),
                "content_type": r.headers.get("content-type"),
            }

        # Retry common transient statuses
        if r.status_code in (429, 500, 502, 503, 504):
            if attempt == 5:
                raise RuntimeError(f"ElevenLabs transient error {r.status_code}: {r.text[:500]}")
            time.sleep(5 * attempt)
            continue

        # Non-retryable/auth/credits issues
        raise RuntimeError(f"ElevenLabs API error {r.status_code}: {r.text[:700]}")

    raise RuntimeError("ElevenLabs generation failed after retries")


def build_prompt(city, title, style, bonus_hint=None):
    base = (
        f"{city} themed cartoon board-game soundtrack cue titled '{title}'. "
        f"Mood/style: {style}. "
        "Bubbly, fun, replayable, catchy hook, upbeat pulse, family-friendly, loop-friendly ending. "
        "Bright arrangement with playful rhythms, polished game-music production. "
        "STRICTLY instrumental only, no lyrics, no voices, no singing, no choir, no spoken words. "
        "Target length: 30 seconds."
    )
    if bonus_hint:
        base += f" Include a subtle nod to bonus area vibe: {bonus_hint}."
    return base


def build_html(manifest):
    by_city = {}
    for t in manifest["tracks"]:
        by_city.setdefault(t["city"], []).append(t)

    city_sections = []
    for city, tracks in by_city.items():
        cards = []
        for t in tracks:
            provider_badge = "⚡ ElevenLabs" if t["provider"] == "ElevenLabs" else "🟠 MiniMax"
            cards.append(
                f"""
                <article class=\"track-card\">
                  <div class=\"track-top\">
                    <h4>{html.escape(t['title'])}</h4>
                    <span class=\"provider {slugify(t['provider'])}\">{provider_badge}</span>
                  </div>
                  <p class=\"track-meta\">{html.escape(t['city'])} · Track {t['track_number']} · 30s target</p>
                  <audio controls preload=\"none\" src=\"{html.escape(t['path'])}\"></audio>
                </article>
                """.strip()
            )

        city_sections.append(
            f"""
            <section class=\"city-section\" id=\"{slugify(city)}\">
              <h3>{html.escape(city)}</h3>
              <div class=\"grid\">{' '.join(cards)}</div>
            </section>
            """.strip()
        )

    city_links = " ".join(
        f"<a href=\"#{slugify(city)}\">{html.escape(city)}</a>" for city in by_city.keys()
    )

    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Monopoly-Style City Music Lab</title>
  <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">
  <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>
  <link href=\"https://fonts.googleapis.com/css2?family=Baloo+2:wght@400;600;700;800&family=Manrope:wght@400;600;700&display=swap\" rel=\"stylesheet\">
  <style>
    :root {{
      --bg: #080c1f;
      --panel: rgba(255, 255, 255, 0.08);
      --text: #f7fbff;
      --muted: #c1cee6;
      --accent-1: #71f6d1;
      --accent-2: #ffd768;
      --accent-3: #8fa8ff;
      --border: rgba(255,255,255,.16);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: 'Manrope', sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at 10% 10%, #223f8f 0%, transparent 40%),
        radial-gradient(circle at 90% 20%, #6f1f84 0%, transparent 40%),
        radial-gradient(circle at 30% 90%, #00625f 0%, transparent 45%),
        var(--bg);
      min-height: 100vh;
    }}
    .wrap {{
      width: min(1200px, 92vw);
      margin: 24px auto 60px;
    }}
    .hero {{
      border: 1px solid var(--border);
      background: linear-gradient(145deg, rgba(255,255,255,.16), rgba(255,255,255,.04));
      border-radius: 24px;
      padding: 24px;
      backdrop-filter: blur(8px);
      box-shadow: 0 20px 60px rgba(0,0,0,.35);
    }}
    h1,h2,h3,h4 {{ font-family: 'Baloo 2', system-ui, sans-serif; margin: 0; }}
    h1 {{ font-size: clamp(1.9rem, 3vw, 2.8rem); line-height: 1.05; }}
    .sub {{ color: var(--muted); margin-top: 8px; }}
    .chips {{ display:flex; flex-wrap: wrap; gap: 8px; margin-top: 16px; }}
    .chip {{
      border: 1px solid var(--border);
      padding: 7px 12px;
      border-radius: 999px;
      color: var(--text);
      text-decoration: none;
      background: rgba(255,255,255,.05);
      font-weight: 700;
      font-size: .9rem;
    }}
    .section-title {{ margin: 30px 0 14px; font-size: 1.7rem; }}
    .city-section {{
      margin-top: 24px;
      border: 1px solid var(--border);
      border-radius: 20px;
      background: var(--panel);
      padding: 18px;
      backdrop-filter: blur(6px);
    }}
    .city-section h3 {{ font-size: 1.45rem; margin-bottom: 10px; }}
    .grid {{ display: grid; gap: 12px; grid-template-columns: repeat(auto-fit,minmax(240px,1fr)); }}
    .track-card {{
      border: 1px solid var(--border);
      border-radius: 14px;
      background: rgba(6, 16, 43, 0.72);
      padding: 12px;
    }}
    .track-top {{ display:flex; justify-content:space-between; gap:10px; align-items:flex-start; }}
    .track-card h4 {{ font-size: 1.05rem; line-height:1.15; }}
    .provider {{
      font-size: .75rem;
      border-radius: 999px;
      padding: 4px 8px;
      border: 1px solid transparent;
      white-space: nowrap;
      font-weight: 800;
      letter-spacing: .2px;
    }}
    .provider.elevenlabs {{ background: rgba(113, 246, 209, 0.16); border-color: rgba(113, 246, 209, 0.45); }}
    .provider.minimax {{ background: rgba(255, 215, 104, 0.16); border-color: rgba(255, 215, 104, 0.45); }}
    .track-meta {{ margin: 8px 0; color: var(--muted); font-size: .86rem; }}
    audio {{ width: 100%; height: 34px; }}
    footer {{ margin-top: 20px; color: var(--muted); font-size: .9rem; }}
  </style>
</head>
<body>
  <main class=\"wrap\">
    <header class=\"hero\">
      <h1>🎲 Monopoly-Style City Music Lab</h1>
      <p class=\"sub\">28 instrumental reference cues (4 per city), generated with ElevenLabs + MiniMax for bubbly, cartoonish board-game energy.</p>
      <div class=\"chips\">{city_links}</div>
    </header>

    <h2 class=\"section-title\">Playlist</h2>
    {' '.join(city_sections)}

    <footer>
      Generated: {html.escape(manifest['generated_at'])} · Instrumental-only prompts (no vocals/singing)
    </footer>
  </main>
</body>
</html>
"""


def main():
    TRACKS_DIR.mkdir(parents=True, exist_ok=True)
    minimax_key, eleven_key = read_keys()

    cities = [
        {
            "city": "New York City",
            "bonus": None,
            "tracks": [
                ("Broadway Bubble Run", "upbeat electro-swing + cartoon jazz, bright brass stabs, plucky bass, joyful street energy"),
                ("Subway Spring-Hop", "playful funk-pop with syncopated drums, clavinet, and marimba motifs"),
                ("Central Park Confetti", "sunny orchestral pop with pizzicato strings, whistles, and glockenspiel sparkle"),
                ("Midtown Power-Up", "arcade-infused city pop groove with punchy synths and triumphant brass"),
            ],
        },
        {
            "city": "San Francisco",
            "bonus": None,
            "tracks": [
                ("Cable Car Candy Cruise", "bouncy west-coast funk with clean guitar chops and playful keys"),
                ("Golden Gate Giggle Groove", "light nu-disco with handclaps, synth bells, and breezy coastal momentum"),
                ("Foggy Pixel Morning", "chill cartoon groove with vibraphone, soft brass, and whimsical arpeggios"),
                ("Silicon Spark Parade", "techy retro-future pop with bubbly synth plucks and energetic pulse"),
            ],
        },
        {
            "city": "West Palm Beach",
            "bonus": "Mar-a-Lago bonus area: glossy resort-lounge sparkle",
            "tracks": [
                ("Palm Parade Pop", "tropical pop-funk with steel-drum flavor, marimba, and warm beach groove"),
                ("Boardwalk Bubble Beat", "sunny coastal house-pop with playful percussion and bright synth hooks"),
                ("Mar-a-Lago Bonus Lounge", "luxury cartoon lounge-pop with harp glints, smooth brass, and cheeky groove"),
                ("Sunset Seashell Sprint", "vacation-ready upbeat groove with ukulele accents and polished rhythm section"),
            ],
        },
        {
            "city": "Las Vegas",
            "bonus": "Area 51 bonus area: quirky sci-fi sparkle",
            "tracks": [
                ("Neon Jackpot Jive", "high-energy electro-swing with casino sparkle, brass hits, and fun bassline"),
                ("Strip Side Shuffle", "dance-pop groove with glitzy synth leads, claps, and playful risers"),
                ("Area 51 Bonus Boogie", "quirky sci-fi funk with theremin-style leads, synth blips, and stealthy bounce"),
                ("Desert Starlight Spin", "cinematic arcade disco with dramatic chords and sparkly neon arpeggios"),
            ],
        },
        {
            "city": "Dallas",
            "bonus": None,
            "tracks": [
                ("Big D Bounce", "modern country-pop groove with banjo plucks, slap bass, and cartoon swagger"),
                ("Rodeo Boardwalk Boogie", "funky two-step fusion with handclaps, fiddle licks, and bright keys"),
                ("Skyline Saddle Pop", "upbeat Americana-pop with brass pep, guitar twang, and playful percussion"),
                ("Fairground Funk Trail", "festival-like groove with stomps, whistles, and catchy call-and-response motifs"),
            ],
        },
        {
            "city": "Washington DC",
            "bonus": None,
            "tracks": [
                ("Monument March Pop", "heroic-but-light orchestral pop with snare cadence and brass optimism"),
                ("Capitol Candy Cruise", "clean funky groove with classy horns, piano stabs, and upbeat confidence"),
                ("Cherry Blossom Bounce", "springy melodic pop with glockenspiel, strings, and pastel groove"),
                ("Smithsonian Sprint", "curious playful orchestral-electro hybrid with marimba and brisk rhythm"),
            ],
        },
        {
            "city": "Los Angeles",
            "bonus": None,
            "tracks": [
                ("Sunset Boulevard Bop", "sun-drenched west-coast pop-funk with bright guitar and synth sparkle"),
                ("Venice Beach Victory Lap", "playful beach-disco with hand percussion, bass bounce, and colorful keys"),
                ("Hollywood Power-Up Parade", "cinematic cartoon pop with triumphant brass, strings, and punchy drums"),
                ("Pacific Coast Pixel Cruise", "retro arcade synthwave-pop with buoyant groove and glossy leads"),
            ],
        },
    ]

    manifest = {
        "project": "Monopoly-Style City Music Lab",
        "generated_at": datetime.now().astimezone().isoformat(),
        "tracks": [],
        "errors": [],
    }

    # Alternate providers: 1/3 ElevenLabs, 2/4 MiniMax
    for city_obj in cities:
        city = city_obj["city"]
        city_slug = slugify(city)
        bonus = city_obj["bonus"]
        city_dir = TRACKS_DIR / city_slug
        city_dir.mkdir(parents=True, exist_ok=True)

        for i, (title, style) in enumerate(city_obj["tracks"], start=1):
            provider = "ElevenLabs" if i in (1, 3) else "MiniMax"
            prompt = build_prompt(city, title, style, bonus_hint=bonus)
            filename = f"{i:02d}-{slugify(title)}-{slugify(provider)}.mp3"
            out_path = city_dir / filename
            rel_path = f"tracks/{city_slug}/{filename}"

            print(f"[{city}] Track {i}/4 via {provider}: {title}")
            try:
                if provider == "ElevenLabs":
                    meta = eleven_generate(eleven_key, prompt, out_path)
                else:
                    meta = minimax_generate(minimax_key, prompt, out_path)

                item = {
                    "city": city,
                    "track_number": i,
                    "title": title,
                    "provider": provider,
                    "prompt": prompt,
                    "path": rel_path,
                    "bytes": meta.get("bytes"),
                    "meta": meta,
                }
                manifest["tracks"].append(item)
                print(f"  ✅ saved {rel_path} ({meta.get('bytes')} bytes)")
            except Exception as e:
                err = {
                    "city": city,
                    "track_number": i,
                    "title": title,
                    "provider": provider,
                    "error": str(e),
                }
                manifest["errors"].append(err)
                print(f"  ❌ ERROR: {e}")

            time.sleep(1.2)

    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    INDEX_PATH.write_text(build_html(manifest), encoding="utf-8")

    print("\nDone.")
    print(f"Tracks generated: {len(manifest['tracks'])}")
    print(f"Errors: {len(manifest['errors'])}")
    print(f"Playlist page: {INDEX_PATH}")


if __name__ == "__main__":
    main()
