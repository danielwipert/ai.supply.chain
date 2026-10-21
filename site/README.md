# site/

The static website (spec section 7). `build.py` reads `data/` and writes plain HTML into `site/dist/`.

## Build and preview on your computer

```bash
python site/build.py                          # 1. build the pages into site/dist/
python -m http.server -d site/dist 8000       # 2. start a tiny local web server
```

Then open http://localhost:8000 in your browser. Press `Ctrl+C` in the terminal to stop the server.

(Run `build.py` as a file, not with `python -m`: `site` is also the name of a built-in Python module.)

## How the site is layered

1. **The map (home page).** All components, top to bottom on every screen size, drawn as a river:
   - Two streams flow side by side: **Compute** (T1–T8) and **Data & models** (D1). They merge at
     model training (T9), then one trunk carries on through inference (T10) to apps (T11).
   - Phones stack the two streams, with the story text inside each tier.
   - Wide screens (1000px and up) put the story in a sticky rail on the right. It follows the tier in the
     middle of the screen, and has Next / Back buttons and a jump list.
   - Hovering a box lights up everything upstream and downstream of it.
   - Clicking a box **explodes it in place**: a detail panel opens right under its tier (makers, at-a-glance
     numbers, what feeds it and what it feeds). The URL gets `#<id>`, so an open box can be shared as a link.
2. **Tier pages** (`/t/T1/` ... `/t/T11/`, `/t/D1/`): one step of the chain and its components.
3. **Component cards** (`/c/<id>/`), layered too: a quick read at the top, then the details, then a fold-out
   "For experts" section (sources, confidence key, card record, JSON download).

## Files

| File | What it is |
|---|---|
| `build.py` | The builder |
| `templates/` | Jinja2 page templates (`base.html` is the shared layout) |
| `static/style.css` | All styling: colours, light/dark theme, phone/tablet/desktop layouts |
| `static/map.js` | The map: river spines, story rail, hover tracing, exploding boxes |
| `static/site.js` | Light/dark switch |
| `../data/story.json` | The words of the story and the short box labels. Edit freely |

## Publishing

`.github/workflows/deploy-site.yml` builds and publishes the site to GitHub Pages on every push to `main`.
While the site lives at `danielwipert.github.io/ai.supply.chain/`, the workflow builds with
`--base-url /ai.supply.chain/` (only the 404 page needs it). Once `supplychain.aiautomations.ai` is set up,
change that to `--base-url /`.
