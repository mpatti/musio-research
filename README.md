# Mike + Tobor Project Tracker

Private, lightweight project board for ongoing collaboration.

## Files
- `PROJECTS.md` → canonical task/project list
- `index.html` → visual board view
- `render_projects_html.py` → regenerates `index.html` from `PROJECTS.md`

## Update workflow
Whenever `PROJECTS.md` changes:

```bash
python3 render_projects_html.py
```

Then commit + push.

## Why this setup
- Free
- Private (private GitHub repo)
- Works on desktop + mobile
- Human-readable source of truth
