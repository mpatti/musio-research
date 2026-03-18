# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

## API Keys

### Web Search
- **Serper (Google search)**: `8339a1ffd9c6d69e68a7247eb72428c7586fa095`
  - Use: `curl -s -X POST "https://google.serper.dev/search" -H "X-API-KEY: <key>" -H "Content-Type: application/json" -d '{"q":"query","numResults":10}'`

### Twitter/X
- **X.com Bearer Token**: `AAAAAAAAAAAAAAAAAAAAAEAAAAIAAAAA:RxcmURAA6D7NVhl2fg4aYK3K590=ExmU9LvHof5QITvF04ONVxEBmPQPgDqAXTfsGhOINO9pHC6IO7`
  - Note: Requires proper OAuth setup — may need additional keys

## Messaging Targets

- Telegram DM (user): `7444832077`
- Use numeric chat id (or canonical `telegram:7444832077`) for cron/scheduled sends.
- Do **not** use `mpatti` as Telegram target alias for sends.

---

Add whatever helps you do your job. This is your cheat sheet.
