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
- Querying preference for subscription/billing questions:
  - If Mike asks a **global/high-level** question (totals, counts, overall product breakdowns, active subscriber counts, "so far" questions), fetch the **full dataset** and paginate/dedupe properly.
  - If Mike asks about **recent transactions / latest activity**, it is fine to use a recent window or latest-page view instead of scanning everything.
- Paddle live API key was saved locally for future use in a non-git-tracked credential file at `/data/.openclaw/credentials/paddle/live_api_key`.

## Billing / Revenue Goals

- Musio subscriptions have a current business goal of reaching **$30k MRR**.
- When Mike asks about subscription progress, frame updates in terms of progress toward the **$30k MRR** target.
- Do not assume background monitoring is re-enabled just because this goal exists; regular automated checks were paused unless Mike explicitly asks to resume them.

## Backup / Clone Context

- User wants a daily full backup of this OpenClaw state so an identical Tobor can be recreated elsewhere.
- Private backup repo: `mpatti/tobor`.
- Daily rolling backup cron is enabled:
  - Job name: `Daily Tobor backup`
  - Schedule: `3:15 AM America/New_York` every day
  - Behavior: create a full backup of `/data/.openclaw` and force-push the latest rolling snapshot to `mpatti/tobor`
  - Success: stay quiet
  - Failure: alert Mike on Telegram
