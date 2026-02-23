#!/usr/bin/env python3
import asyncio
import pathlib
import re
import time
import wave
from dataclasses import dataclass

from google import genai
from google.genai import types

TOOLS_PATH = pathlib.Path('/data/.openclaw/workspace/TOOLS.md')
BASE_DIR = pathlib.Path(__file__).resolve().parent
TRACKS_DIR = BASE_DIR / 'tracks'

SAMPLE_RATE = 48000
CHANNELS = 2
SAMPLE_WIDTH = 2  # 16-bit PCM
TARGET_SECONDS = 30
TARGET_BYTES = SAMPLE_RATE * CHANNELS * SAMPLE_WIDTH * TARGET_SECONDS
MODEL = 'models/lyria-realtime-exp'


def get_gemini_key() -> str:
    text = TOOLS_PATH.read_text(encoding='utf-8')
    m = re.search(r"\*\*Google Gemini\*\*:\s*`([^`]+)`", text)
    if not m:
        raise RuntimeError('Google Gemini key not found in TOOLS.md')
    return m.group(1).strip()


@dataclass
class GeminiTrack:
    city_slug: str
    filename: str
    prompt: str
    bpm: int


TRACKS = [
    GeminiTrack(
        city_slug='new-york-city',
        filename='05-neon-borough-bounce-gemini.wav',
        prompt='New York City cartoon board-game soundtrack, bubbly upbeat instrumental only, playful brass, marimba, pizzicato strings, arcade sparkle, no vocals, no singing, no voices',
        bpm=122,
    ),
    GeminiTrack(
        city_slug='san-francisco',
        filename='05-golden-giggle-loop-gemini.wav',
        prompt='San Francisco coastal cartoon board-game loop, bubbly and cheerful instrumental only, funky guitar chops, synth bells, handclaps, no vocals, no singing, no voices',
        bpm=118,
    ),
    GeminiTrack(
        city_slug='west-palm-beach',
        filename='05-palm-sunshine-pop-gemini.wav',
        prompt='West Palm Beach resort cartoon board-game music, tropical bubbly instrumental only, marimba, steel pan flavor, bright pop groove, no vocals, no singing, no voices',
        bpm=116,
    ),
    GeminiTrack(
        city_slug='las-vegas',
        filename='05-neon-casino-comet-gemini.wav',
        prompt='Las Vegas cartoon board-game soundtrack, glitzy bubbly instrumental only, disco pulse, synth arpeggios, brass hits, playful sci-fi blips, no vocals, no singing, no voices',
        bpm=124,
    ),
    GeminiTrack(
        city_slug='dallas',
        filename='05-fairway-funk-stomp-gemini.wav',
        prompt='Dallas cartoon board-game soundtrack, upbeat bubbly instrumental only, banjo plucks, claps, funky bass, bright keys, no vocals, no singing, no voices',
        bpm=120,
    ),
    GeminiTrack(
        city_slug='washington-dc',
        filename='05-monument-confetti-run-gemini.wav',
        prompt='Washington DC cartoon board-game soundtrack, uplifting bubbly instrumental only, snare cadence, brass fanfare, glockenspiel sparkle, no vocals, no singing, no voices',
        bpm=121,
    ),
    GeminiTrack(
        city_slug='los-angeles',
        filename='05-sunset-pixel-sprint-gemini.wav',
        prompt='Los Angeles cartoon board-game soundtrack, sunny bubbly instrumental only, west coast funk guitar, synth plucks, bright drums, no vocals, no singing, no voices',
        bpm=123,
    ),
]


async def generate_one(client: genai.Client, track: GeminiTrack):
    city_dir = TRACKS_DIR / track.city_slug
    city_dir.mkdir(parents=True, exist_ok=True)
    out_path = city_dir / track.filename

    if out_path.exists() and out_path.stat().st_size > 10000:
        print(f'⏭️  exists: {out_path.relative_to(BASE_DIR)}')
        return

    print(f'🎵 generating: {track.city_slug}/{track.filename}')

    for attempt in range(1, 4):
        audio = bytearray()
        try:
            async with client.aio.live.music.connect(model=MODEL) as session:
                await session.set_weighted_prompts(
                    prompts=[types.WeightedPrompt(text=track.prompt, weight=1.0)]
                )
                await session.set_music_generation_config(
                    config=types.LiveMusicGenerationConfig(bpm=track.bpm, temperature=1.0)
                )
                await session.play()

                start = time.time()
                async for message in session.receive():
                    if message.server_content and message.server_content.audio_chunks:
                        for chunk in message.server_content.audio_chunks:
                            audio.extend(chunk.data)

                    if len(audio) >= TARGET_BYTES:
                        await session.stop()
                        break

                    # Safety timeout
                    if time.time() - start > 95:
                        await session.stop()
                        break

            if len(audio) < 100000:
                raise RuntimeError(f'Audio too short ({len(audio)} bytes)')

            # Trim exactly 30s for clean references
            audio = audio[:TARGET_BYTES]

            with wave.open(str(out_path), 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(SAMPLE_WIDTH)
                wf.setframerate(SAMPLE_RATE)
                wf.writeframes(audio)

            print(f'✅ saved: {out_path.relative_to(BASE_DIR)} ({len(audio)} bytes raw PCM)')
            return

        except Exception as e:
            print(f'⚠️ attempt {attempt} failed for {track.filename}: {e}')
            await asyncio.sleep(2 * attempt)

    raise RuntimeError(f'Failed to generate {track.filename} after retries')


async def main():
    api_key = get_gemini_key()
    client = genai.Client(api_key=api_key, http_options={'api_version': 'v1alpha'})

    for t in TRACKS:
        await generate_one(client, t)


if __name__ == '__main__':
    asyncio.run(main())
