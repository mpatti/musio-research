#!/usr/bin/env python3
import html
import pathlib
import re
from datetime import datetime

BASE = pathlib.Path(__file__).resolve().parent
MD = BASE / "PROJECTS.md"
OUT = BASE / "index.html"


def parse_projects(md_text: str):
    section = None
    projects = []
    current = None

    lines = md_text.splitlines()
    for line in lines:
        s = line.strip()

        if s.startswith("## "):
            sec = s[3:].strip()
            if sec in {"Active", "Backlog", "Waiting", "Done"}:
                section = sec
            continue

        m = re.match(r"^###\s+\[(P-\d+)\]\s+(.+)$", s)
        if m:
            current = {
                "id": m.group(1),
                "title": m.group(2).strip(),
                "lane": section or "Backlog",
                "status": "",
                "owner": "",
                "notes": [],
                "next": "",
                "output": [],
            }
            projects.append(current)
            continue

        if not current:
            continue

        if s.startswith("- **Status:**"):
            current["status"] = s.split("**Status:**", 1)[1].strip()
        elif s.startswith("- **Owner:**"):
            current["owner"] = s.split("**Owner:**", 1)[1].strip()
        elif s.startswith("- **Next step:**"):
            current["next"] = s.split("**Next step:**", 1)[1].strip()
        elif s.startswith("- **Notes:**"):
            pass
        elif s.startswith("- **Output:**"):
            pass
        elif s.startswith("- "):
            item = s[2:].strip()
            # heuristic: if we've already got next step empty and this looks like output link, store in notes still
            current["notes"].append(item)

    return projects


def card(p):
    notes = "".join(f"<li>{html.escape(n)}</li>" for n in p.get("notes", []))
    next_step = (
        f"<p class='next'><strong>Next:</strong> {html.escape(p['next'])}</p>"
        if p.get("next")
        else ""
    )
    return f"""
    <article class='card'>
      <div class='head'>
        <span class='pid'>{html.escape(p['id'])}</span>
        <span class='status'>{html.escape(p.get('status') or p.get('lane') or '')}</span>
      </div>
      <h3>{html.escape(p['title'])}</h3>
      <p class='owner'>Owner: {html.escape(p.get('owner') or '—')}</p>
      <ul>{notes}</ul>
      {next_step}
    </article>
    """


def main():
    txt = MD.read_text(encoding="utf-8")
    projects = parse_projects(txt)

    lanes = {"Active": [], "Waiting": [], "Backlog": [], "Done": []}
    for p in projects:
        lane = p.get("lane") or p.get("status") or "Backlog"
        lane = lane if lane in lanes else "Backlog"
        lanes[lane].append(p)

    updated = datetime.now().astimezone().strftime("%Y-%m-%d %I:%M %p %Z")

    lane_html = []
    for lane in ["Active", "Waiting", "Backlog", "Done"]:
        cards = "\n".join(card(p) for p in lanes[lane]) or "<p class='empty'>No items.</p>"
        lane_html.append(
            f"""
            <section class='lane'>
              <h2>{lane} <span>{len(lanes[lane])}</span></h2>
              {cards}
            </section>
            """
        )

    page = f"""<!doctype html>
<html lang='en'>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>Mike + Tobor Project Board</title>
  <style>
    :root {{ --bg:#0b1020; --panel:#11182d; --line:#253253; --text:#edf2ff; --muted:#b9c5e8; --accent:#8fd3ff; }}
    * {{ box-sizing: border-box; }}
    body {{ margin:0; font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif; background:linear-gradient(180deg,#0a0f1e,#0d1327); color:var(--text); }}
    .wrap {{ width:min(1400px,94vw); margin:20px auto 40px; }}
    .top {{ border:1px solid var(--line); border-radius:16px; padding:16px 18px; background:rgba(255,255,255,.03); }}
    h1 {{ margin:0 0 6px; font-size:1.55rem; }}
    .meta {{ color:var(--muted); font-size:.92rem; }}
    .grid {{ margin-top:18px; display:grid; grid-template-columns:repeat(4,minmax(250px,1fr)); gap:12px; align-items:start; }}
    .lane {{ border:1px solid var(--line); border-radius:14px; padding:10px; background:var(--panel); min-height:180px; }}
    .lane h2 {{ margin:2px 4px 10px; font-size:1rem; display:flex; justify-content:space-between; align-items:center; }}
    .lane h2 span {{ background:#1f2f53; border:1px solid #2e4578; border-radius:999px; padding:2px 8px; font-size:.8rem; color:#c8d8ff; }}
    .card {{ border:1px solid #2a3d68; border-radius:11px; padding:10px; background:#0f1730; margin:8px 0; }}
    .head {{ display:flex; justify-content:space-between; gap:8px; }}
    .pid {{ font-weight:700; color:var(--accent); font-size:.85rem; }}
    .status {{ font-size:.74rem; color:#b7d0ff; border:1px solid #35538b; border-radius:999px; padding:2px 7px; }}
    .card h3 {{ margin:8px 0 6px; font-size:1rem; line-height:1.2; }}
    .owner {{ margin:0 0 6px; color:var(--muted); font-size:.85rem; }}
    ul {{ margin:0; padding-left:18px; color:#d8e4ff; font-size:.88rem; }}
    .next {{ margin-top:8px; color:#d8e4ff; font-size:.86rem; }}
    .empty {{ color:var(--muted); font-size:.9rem; margin:6px; }}
    @media (max-width: 1100px) {{ .grid {{ grid-template-columns:repeat(2,minmax(220px,1fr)); }} }}
    @media (max-width: 700px) {{ .grid {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body>
  <main class='wrap'>
    <header class='top'>
      <h1>Mike + Tobor Project Board</h1>
      <p class='meta'>Visual view generated from PROJECTS.md · Updated {updated}</p>
    </header>
    <section class='grid'>
      {''.join(lane_html)}
    </section>
  </main>
</body>
</html>
"""
    OUT.write_text(page, encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
