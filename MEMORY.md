# MEMORY.md

## User Preferences

- For website/app work, the user expects completion to include deployment outcomes, not just local code edits.
- Preferred delivery workflow for relevant web projects:
  1) commit changes,
  2) push to GitHub,
  3) publish/update GitHub Pages.
- For Telegram scheduled sends, use a numeric chat target (chat id) instead of username aliases like `mpatti`.

## Known Messaging Target

- Telegram DM chat id: `7444832077`
- Canonical inbound id format often appears as: `telegram:7444832077`

## Billing / Paddle Context

- User may ask again for subscription analytics from Paddle in the coming weeks.
- Important nuance: Paddle dashboard "Active Subscribers" does not exactly match a raw API count of subscriptions with `status=active`.
- On 2026-03-28:
  - Paddle dashboard screenshot showed **3,466 active subscribers**.
  - Strict API count was about **3,426–3,427 active**.
  - Non-canceled-ish current customers (`active + past_due + paused`) were about **3,483**.
- Best answer rule: if the user asks for the number that matches what Paddle shows on the dashboard, use **3,466** unless newer data is fetched.
- Do not rely on old truncated API samples; paginate/dedupe properly when querying Paddle.
