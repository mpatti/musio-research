# Musio Asset Builder

A browser-based image pack generator for Musio-style marketplace assets.

## What it does

Input: one square source image (plus optional pack name text)

Automatically generates:

- CardImage (200x200)
- WideCardImage (439x90)
- SlotImage (200x200)
- BannerImage (484x130)
- instPanelImage (554x450)
- cartImage (142x80)
- instPanelBackgroundImage (554x450)
- instPanelTextImage (554x182)

## Features

- Auto focal-point detection (saliency-based)
- Manual focal control by clicking/dragging source image
- Real-time preview updates
- Per-pack naming and automatic file naming
- Download individual PNGs, all PNGs, or ZIP package

## Run locally

```bash
cd musio-asset-builder
python3 -m http.server 8080
```

Open: http://localhost:8080
