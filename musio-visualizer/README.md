# Musio Visualizer

A modern, audio-reactive web visualizer inspired by the Musio aesthetic.

## Features

- Drag-and-drop audio upload (MP3/WAV/M4A/OGG)
- Real-time Web Audio API analysis
- Beat-aware motion using spectral flux detection
- 3 visual scenes:
  - **Prism Arc**
  - **Nebula Pulse**
  - **Kinetic Grid**
- Playback controls (play/pause/restart/seek/fullscreen)
- Live energy metrics (low/mid/high)
- Responsive, retina-aware rendering

## Tech

- **Web Audio API** for frequency + waveform analysis
- **Canvas 2D** rendering pipeline for smooth real-time visuals
- No framework/build step required (single-page app)

## Run locally

```bash
cd musio-visualizer
python3 -m http.server 8080
```

Then open:

- http://localhost:8080

(Direct file open also works in many browsers, but a local server is recommended.)

## Notes

This version runs fully client-side (audio never leaves the browser).
