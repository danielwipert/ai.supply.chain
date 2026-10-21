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

1. **The map (home page).** All 27 components in 9 tiers, with the story told on the map.
   - Wide screens (1100px and up): the chain runs left to right. "Follow the chain" steps through
     the tiers and lights each one up. Hovering a box traces everything upstream and downstream of it.
   - Phones and upright tablets: the chain runs top to bottom as a timeline, with the story text
     inside each tier. The tier in the middle of the screen lights up as you scroll.
   - Clicking or tapping a box opens a quick preview (side panel on desktop, bottom sheet on phones).
2. **Tier pages** (`/t/T1/` ... `/t/T9/`): one step of the chain and its components.
3. **Component cards** (`/c/<id>/`), layered too: a quick read at the top (summary, at-a-glance tiles,
   fed by / feeds), then the details (makers, concentration, cost, why it matters), then a fold-out
   "For experts" section (sources, confidence key, card record, JSON download).

## Files

| File | What it is |
|---|---|
| `build.py` | The builder |
| `templates/` | Jinja2 page templates (`base.html` is the shared layout) |
| `static/style.css` | All styling: colours, light/dark theme, phone/tablet/desktop layouts |
| `static/map.js` | The map: lines, story steps, hover tracing, preview panel |
| `static/site.js` | Light/dark switch |
| `../data/story.json` | The words of the story and the short box labels. Edit freely |

## Publishing

`.github/workflows/deploy-site.yml` builds and publishes the site to GitHub Pages on every push to `main`.
The build writes a `CNAME` file for `supplychain.aiautomations.ai`.
