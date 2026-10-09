# Ancient Aliens GIS

A 3D web geoportal for every location referenced in the television series
*Ancient Aliens* — **246 sites**, each presented as **Claim · Record ·
Context**: what the series asserts, what the encyclopaedic record says, and
where the two diverge.

Built on open standards, served as **OGC API — Features**, rendered with
**CesiumJS** over OGC **WMTS** imagery and a keyless global elevation mesh.
No API keys, no accounts, no build step.

**→ [Open the geoportal](https://sidequeststudiosdev.github.io/Ancient-Aliens-GIS/)**

---

## The honest part, first

**You cannot run GeoServer on GitHub Pages.** Pages serves static files: no
Java servlet container, no database, no request-time query handling. A
"GeoServer-based application hosted on GitHub Pages" is two mutually
exclusive requirements, and anything that claims otherwise is misdescribing
itself.

This repository resolves that properly rather than pretending:

| | GitHub Pages (this deploy) | GeoServer (`geoserver/`) |
|---|---|---|
| OGC API — Features resource tree | yes, fully | yes |
| GeoJSON output, CRS84 | yes | yes |
| `bbox` / `limit` / `datetime` / `filter` parameters | **no** — static files cannot filter | yes |
| WFS 2.0.0, WMS 1.3.0, SLD styling | no | yes |
| Cost to run | free | a server |

Both are generated from **one source catalogue**, so they cannot drift. The
browser client reads either: set `APP.geoserverFeatures` in
[`assets/js/config.js`](assets/js/config.js) to a live landing page and the
app switches over, because the feature schema is identical by construction.

The static deployment states its own limitations in machine-readable form —
see `x-static-deployment` in
[`data/conformance.json`](data/conformance.json). It declares what it
actually does, not what would sound better.

---

## What it does

- **Fly to any of 246 sites** on a 3D globe with real elevation, in 3D, 2.5D
  perspective, or flat 2D — one engine, three projections.
- **Search** across names, countries, categories, tags and aliases, with
  diacritic folding (`gobekli` finds *Göbekli Tepe*).
- **Filter** by 15 categories and 12 world regions; sort A–Z, by region, by
  category, or by distance from the current view.
- **Read a dossier** for every site: the claim as presented on screen, an
  encyclopaedic summary, a context note, full geographic data (coordinates in
  decimal and DMS, CRS, ground elevation, extent, positional precision), and
  links out to Wikipedia, Wikidata, OpenStreetMap, a scoped search of the
  broadcaster's own site, primary institutional sources, and the site's own
  GeoJSON.
- **Switch imagery**: 9 base layers and 3 overlays across OGC WMTS and XYZ,
  including Sentinel-2 cloudless, NASA VIIRS and Esri World Imagery.
- **Inspect the service**: a live OGC tab showing endpoints, declared
  conformance classes, extent and feature counts, read from the running
  service rather than hard-coded.
- **Deep-link anything**: `?site=gobekli-tepe&cat=megalithic&sort=region`.
- **Install it**: a PWA with an offline app shell.

### Honesty about position

Not every entry is a surveyed point, and the map never pretends otherwise.
Each feature carries `location_precision`:

| value | meaning |
|---|---|
| `exact` | the monument or structure itself, to ~100 m (161 sites) |
| `approximate` | the right valley, hill or town; the feature is not published more precisely (22 sites) |
| `area` | deliberately a region centroid, or a landscape kilometres across — a desert, a sea, a geoglyph field, a canyon. Drawn with its extent circle (60 sites) |
| `uncertain` | the series' reference could not be tied to a published place name; the position is a label, not a location (3 sites) |

136 coordinates were taken at build time from the values held by
Wikipedia/Wikidata, after checking each agreed with the authored position
to within 25 km. The rest are authored — every `area` entry by design,
since an article's point is not a region's centroid — and each feature
records which in `coordinate_source`.

### Honesty about content

The series makes claims that the archaeological record does not support.
This project maps those claims rather than endorsing them. Every dossier
separates them explicitly, and where a claim has no evidentiary basis the
context section says so and explains what the evidence actually shows.
Where a question is genuinely open — Yonaguni, the Wow! signal, Rendlesham,
the location of Punt — it says that too.

---

## Standards

| Standard | Where |
|---|---|
| **OGC API — Features, Part 1: Core** | `data/` resource tree: landing page, conformance, collections, items, per-feature documents |
| **OGC API — Features, Part 3: Filtering** | `data/collections/sites/queryables.json` (schema published; evaluation is client-side on Pages) |
| **GeoJSON (RFC 7946)** | all feature payloads, EPSG:4326 / OGC CRS84, longitude-latitude axis order |
| **OpenAPI 3.0.3** | `data/api.json`, linked as `service-desc` |
| **OGC WMTS 1.0.0** | EOX Sentinel-2 cloudless, EOX overlays, NASA GIBS VIIRS / Blue Marble / Black Marble |
| **OGC WFS 2.0.0 · WMS 1.3.0 · SLD 1.0.0** | `geoserver/` — compose file, generated data directory, scale-dependent SLD |
| **W3C WCAG 2.2 AA** | keyboard navigation throughout, visible focus, `prefers-reduced-motion` and `prefers-reduced-transparency` honoured, contrast-checked token palette |

Full detail: **[docs/OGC-COMPLIANCE.md](docs/OGC-COMPLIANCE.md)**.

---

## Architecture

```
index.html                      app shell — no framework, no bundler
assets/
  css/tokens.css                design tokens (colour, type, space, motion)
  css/base.css                  reset and primitives
  css/app.css                   layout: side panel on desktop, sheet on mobile
  js/config.js                  layer catalogue + data-source switch
  js/util.js                    helpers: geodesy, formatting, fetch
  js/ogc.js                     OGC API - Features client (static | GeoServer)
  js/store.js                   catalogue, filters, selection, URL state
  js/globe.js                   CesiumJS: viewer, imagery, terrain, markers
  js/ui.js                      all DOM rendering
  js/main.js                    bootstrap and wiring
data/                           generated OGC API - Features tree (committed)
data-source/
  catalog.py                    the authored catalogue — source of truth
  sites.json                    normalised + enriched, generated
scripts/
  build_data.py                 enrich from Wikipedia, emit data/
  build_geoserver.py            emit geoserver/data_dir and layers
  validate_data.py              assert the published tree is coherent
  check_services.py             assert every external service still works
  smoke.mjs                     CI browser check
geoserver/                      conformant deployment: compose, SLD, data dir
sw.js                           offline app shell
```

**Why no bundler.** The app is ~90 KiB of hand-written ES modules. A build
step would add a failure mode to every deploy and buy nothing: modern
browsers load ES modules natively, and CesiumJS is pinned to an exact CDN
version. What is committed is exactly what is served.

**Why CesiumJS.** It is the only mature open-source 3D globe with native OGC
WMTS/WMS providers, quantised-mesh terrain, and 3D / 2.5D / 2D projections in
one engine. `requestRenderMode` is enabled, so the scene renders on change
rather than at 60 fps — the single largest battery and thermal saving on a
phone.

---

## Mobile

Mobile was the priority, not an afterthought:

- A **drag-to-resize bottom sheet** with four snap states, sized by `height`
  rather than `transform` — a translated sheet keeps its full layout box
  off-screen, which silently makes the lower half of a scrolling list
  unreachable.
- The HUD **tracks the sheet**: tool stack and attribution move with it and
  retire when it is fully open, so nothing is ever stranded underneath.
- Attribution **collapses behind a button**, because a 12-pixel row of links
  is not a usable tap target.
- Hit boxes grow on `pointer: coarse`; the viewport uses `dvh` so iOS
  toolbar collapse does not shift the layout.
- Render resolution is capped at 1.5× and MSAA is off on touch devices.
- The site list paints before CesiumJS loads, so search works immediately.

---

## Running it

### Locally

```bash
git clone https://github.com/SideQuestStudiosDev/Ancient-Aliens-GIS.git
cd Ancient-Aliens-GIS
python3 -m http.server 8000
# http://localhost:8000
```

That is the whole setup. No install, no build.

### Rebuilding the data

```bash
python3 scripts/build_data.py            # enrich from Wikipedia, emit data/
python3 scripts/build_data.py --offline  # rebuild from cache, no network
python3 scripts/build_data.py --check    # validate the catalogue only
python3 scripts/validate_data.py         # validate the published tree
python3 scripts/check_services.py        # are the map services still alive?
```

Wikipedia responses are cached in `.cache/wikipedia.json`, so rebuilds are
reproducible and offline-safe. Delete the cache to refresh.

### With GeoServer

```bash
python3 scripts/build_data.py
python3 scripts/build_geoserver.py
cd geoserver && docker compose up
```

Then set `APP.geoserverFeatures` in `assets/js/config.js` to
`http://localhost:8080/geoserver/ogc/features/v1/`. See
[`geoserver/README.md`](geoserver/README.md).

### Deploying to Pages

Settings → Pages → Source: **GitHub Actions**. Push to `main`;
[`.github/workflows/pages.yml`](.github/workflows/pages.yml) validates the
catalogue and the published tree, then deploys. Nothing else to configure.

---

## Adding or correcting a site

Edit [`data-source/catalog.py`](data-source/catalog.py) — one `S(...)` call
per site, with the schema documented at the top of the file — then:

```bash
python3 scripts/build_data.py && python3 scripts/validate_data.py
```

Corrections to coordinates, dating or context are especially welcome. See
[CONTRIBUTING.md](CONTRIBUTING.md).

---

## Credits and licensing

Ancient Aliens GIS is designed, built and maintained by
**Side Quest Studios**.

**Use it freely — just credit us, and do not claim the parts that are
not ours.** The project is open source under two licenses, and leans on
third-party material under several more.

| What | License | What you owe |
|---|---|---|
| **Software** — the app, the build scripts, the GeoServer configuration | [Apache 2.0](LICENSE) | Keep the license and [`NOTICE`](NOTICE) with any copy you distribute |
| **Authored catalogue** — the 246 claim / context / description entries researched for this project | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | Credit Side Quest Studios |
| **Everything else** | see [`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md) | Varies, and some of it is stricter |

Apache 2.0 rather than MIT for one reason that matters here: its
[`NOTICE`](NOTICE) mechanism makes attribution travel with the code
instead of relying on a copyright line nobody reads, and its section 6
is explicit that no trademark right comes with it.

### What is not ours

Read [`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md) before
redistributing. In short:

- **Encyclopaedic summaries** are English Wikipedia, **CC BY-SA 4.0** —
  share-alike, so adaptations of that text stay BY-SA. Attributed per
  site with a link to the source article.
- **Imagery** is Esri World Imagery, OpenStreetMap and OpenTopoMap, with
  Esri label, EOX graticule and NASA Black Marble overlays. Layer
  attribution is rendered in the app and must stay there.
- **Elevation** is the Esri Terrain3D mesh, plus per-site ground
  elevation from the [Open-Meteo elevation API](https://open-meteo.com/)
  (Copernicus DEM), CC BY 4.0.
- **The globe** is [CesiumJS](https://cesium.com/platform/cesiumjs/),
  Apache 2.0, loaded from a pinned CDN build.

*Ancient Aliens* is a trademark of A&E Television Networks. This is an
independent, unaffiliated reference project and is not endorsed by the
programme or its producers. No episode content is reproduced: each
`claim` is an original summary written for this project.
