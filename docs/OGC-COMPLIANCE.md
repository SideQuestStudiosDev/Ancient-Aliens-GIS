# OGC conformance

What this project implements, what it does not, and why.

---

## 1. The constraint that shapes everything

GitHub Pages is a static file host. It serves bytes from disk over HTTP GET.
It has no servlet container, no CGI, no database, and no way to act on a
query string. Every OGC service standard that requires request-time
behaviour — filtering by `bbox`, honouring `limit`, evaluating a CQL2
`filter` — is therefore outside what Pages can do, by construction rather
than by omission.

Two options follow. Claim conformance anyway and hope nobody checks, or
publish exactly what is true and supply the conformant deployment
separately. This project does the second.

---

## 2. OGC API — Features, Part 1: Core

### Resource tree

The static deployment publishes the full Core resource model. Paths carry an
explicit `.json` suffix because a file server resolves paths, not
negotiated resources.

| Core resource | Static path | GeoServer path |
|---|---|---|
| Landing page | `data/index.json` | `/ogc/features/v1/` |
| Conformance | `data/conformance.json` | `/ogc/features/v1/conformance` |
| API definition | `data/api.json` | `/ogc/features/v1/api` |
| Collections | `data/collections/index.json` | `/ogc/features/v1/collections` |
| Collection | `data/collections/sites/index.json` | `/ogc/features/v1/collections/sites` |
| Features | `data/collections/sites/items.json` | `/ogc/features/v1/collections/sites/items` |
| Feature | `data/collections/sites/items/{id}.json` | `/ogc/features/v1/collections/sites/items/{id}` |
| Queryables | `data/collections/sites/queryables.json` | `/ogc/features/v1/collections/sites/queryables` |

### Declared conformance classes

```
http://www.opengis.net/spec/ogcapi-common-1/1.0/conf/core
http://www.opengis.net/spec/ogcapi-common-1/1.0/conf/landing-page
http://www.opengis.net/spec/ogcapi-common-1/1.0/conf/json
http://www.opengis.net/spec/ogcapi-common-2/1.0/conf/collections
http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core
http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson
http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/oas30
```

### What the static deployment does **not** do

Stated in `x-static-deployment` on both the landing page and the
conformance document, so a machine client can read it:

1. **Query parameters are accepted and ignored.** `GET …/items.json?bbox=…`
   returns the complete FeatureCollection. A client that assumes `bbox`
   filtered the response will get more features than it asked for — never
   fewer, and never wrong ones, but more. Filtering and paging happen in the
   browser client.
2. **This is practical only because the collection is small**: 246 features,
   about 687 KiB uncompressed and well under 150 KiB gzipped over the wire.
   At ten thousand features this design would be indefensible.
3. **Content negotiation does not apply.** There is one representation per
   resource, at a fixed path with a fixed media type.

For a deployment that honours Core in full, run `geoserver/`. It serves the
same features, with the same property names and the same CRS, with complete
parameter support.

### Properties

Every feature carries:

| Property | Type | Notes |
|---|---|---|
| `name`, `subtitle`, `country`, `region` | string | |
| `category`, `category_label` | string | one of 15 |
| `tags`, `aliases` | string[] | also searched |
| `claim` | string | as presented in the series |
| `context` | string | the mainstream position |
| `summary`, `summary_source` | string | Wikipedia intro, CC BY-SA 4.0 |
| `location_precision` | enum | `exact` · `approximate` · `area` · `uncertain` |
| `coordinate_source` | enum | `wikipedia` · `authored` |
| `coordinate_reference_system` | URI | OGC CRS84 |
| `latitude`, `longitude` | number | decimal degrees |
| `celestial_body` | enum | `earth` · `moon` |
| `radius_km` | number \| null | set for `area` features |
| `ground_elevation_m` | number \| null | metres above sea level, Copernicus DEM |
| `ground_elevation_source` | string | attribution for the above |
| `camera_height_m`, `camera_pitch_deg` | number | presentation hint, height is **above ground** |
| `wikipedia_title`, `wikipedia_url`, `wikipedia_verified` | | verified at build time |
| `wikidata_id` | string | QID |

### Geometry and CRS

- **CRS**: `http://www.opengis.net/def/crs/OGC/1.3/CRS84` — WGS 84 with
  longitude first, as RFC 7946 requires. Declared as both `crs` and
  `storageCrs` on the collection.
- **Point** for single locations.
- **MultiPoint** where an entry genuinely names two places — Roswell (the
  town and the Foster Ranch debris field 95 km away), Florence and Vinci,
  Montauk and Plum Island, Andrews AFB and Washington National, Antofagasta
  and Concepción, Coricancha and Lake Puray. Collapsing those to one point
  would assert something false.
- **`null` geometry** for the single off-world entry, the Sea of
  Tranquility. RFC 7946 permits a null geometry; the properties carry
  selenographic coordinates and `celestial_body: "moon"`, and the client
  lists the site without placing a marker on Earth.
- **`bbox`** on every feature and on the collection. For `area` features the
  bbox is expanded by `radius_km`, so a spatial query returns the region, not
  just its centroid.

---

## 3. OGC WMTS 1.0.0

Imagery is requested through Cesium's `WebMapTileServiceImageryProvider`
against real WMTS endpoints, using each service's published `ResourceURL`
template and `TileMatrixSet`:

| Layer | Service | TileMatrixSet | Licence |
|---|---|---|---|
| Sentinel-2 cloudless 2025 | EOX `tiles.maps.eox.at/wmts` | `GoogleMapsCompatible` | CC BY-NC-SA 4.0 — **non-commercial** |
| Terrain Light | EOX | `GoogleMapsCompatible` | CC BY-SA |
| Coastline & graticule overlay | EOX | `GoogleMapsCompatible` | CC BY-SA |
| VIIRS SNPP True Colour | NASA GIBS | `GoogleMapsCompatible_Level9` | public domain |
| Blue Marble shaded relief + bathymetry | NASA GIBS | `GoogleMapsCompatible_Level8` | public domain |
| VIIRS Black Marble | NASA GIBS | `GoogleMapsCompatible_Level8` | public domain |

The remaining base layers (Esri Dark Gray Canvas, Esri World Imagery, Esri
World Shaded Relief, OpenStreetMap, OpenTopoMap) use the XYZ slippy-tile
convention, which is a de-facto standard rather than an OGC one. The Layers
tab labels every layer with its protocol so the distinction is visible in
the product, not buried here.

> **Note on the Sentinel-2 licence.** EOX publishes s2cloudless under
> CC BY-NC-SA 4.0. It is offered here because this is a non-commercial
> reference project. Anyone forking this for commercial use must either
> remove that layer or license it from EOX.

### Verifying the services

`scripts/check_services.py` fetches three tiles from widely separated places
from every configured endpoint and asserts the bytes differ.

This is not pedantry. The project originally shipped CARTO Dark Matter as its
default basemap. Every tile returned **HTTP 200** with a valid `image/png`
body — and every tile was the same 2,513-byte "API KEY REQUIRED" watermark.
A status check passed; the globe was covered in advertising. Comparing tiles
from different coordinates catches that class of failure immediately, and
it is the reason that check exists.

---

## 4. Elevation

Two different elevation sources, for two different jobs.

**Ground elevation per site** is baked into the catalogue at build time from
the Open-Meteo elevation API (Copernicus DEM), and published as
`ground_elevation_m`. It exists because `camera_height_m` is a height
*above ground*, and resolving that at runtime is unreliable: Cesium's
`sampleTerrainMostDetailed` fetches tiles and can take seconds, while
`globe.getHeight` returns whatever coarse tile is resident and was wrong by
1,528 m at the Bighorn Medicine Wheel. With the DEM value in the catalogue
the camera is correctly placed on the first frame; the runtime sample still
runs afterwards and nudges the camera if it disagrees by more than 150 m.
Spot-checked against Cesium's own terrain, the two agree to within a few
metres (Machu Picchu 2436 against 2442; Göbekli Tepe 779 against 783).

**3D terrain** uses Esri's Terrain3D image service via Cesium's
`ArcGISTiledElevationTerrainProvider`, which serves LERC-compressed
elevation tiles. Verified to work without a token. Chosen because the
alternative with comparable coverage — Cesium World Terrain — requires a
Cesium ion account, which would make the deployment depend on a credential.

Setting `APP.ionToken` switches to Cesium World Terrain and enables OSM
Buildings. The app degrades in a straight line: ion token → Cesium World
Terrain; no token → Esri Terrain3D; service unreachable → smooth ellipsoid,
with the Layers tab reporting which is active.

---

## 5. OGC WFS 2.0.0, WMS 1.3.0 and SLD 1.0.0

`geoserver/` contains a generated GeoServer data directory and a pinned
compose file:

```bash
python3 scripts/build_data.py
python3 scripts/build_geoserver.py
cd geoserver && docker compose up
```

- **OGC API — Features** — `/geoserver/ogc/features/v1`
- **WFS 2.0.0** — `/geoserver/wfs?service=WFS&version=2.0.0&request=GetCapabilities`
- **WMS 1.3.0** — `/geoserver/wms?service=WMS&version=1.3.0&request=GetCapabilities`

`geoserver/sld/ancient-aliens-sites.sld` is an SLD 1.0.0 document with three
scale-dependent rules (dots → ringed pins → pins with labels) and a
`Recode` function mapping the category vocabulary to the same hex values the
browser client uses, so WMS output and the 3D client agree.

The off-world entry is excluded from the GeoServer layer: a null geometry is
not a simple feature. It remains in the static tree, which is why the two
publish 245 and 246 features respectively — a documented difference, not a
discrepancy.

---

## 6. Accessibility

Targeting WCAG 2.2 AA:

- Every control reachable and operable by keyboard; `?` opens help, `/`
  focuses search, `1`/`2`/`3` switch projection, `Esc` closes.
- Visible focus rings; a skip link to the site list.
- ARIA roles throughout: `combobox`/`listbox` for search, `tablist` for the
  panel, `radiogroup` for projection and base layer, `switch` for toggles.
- Text contrast checked against its intended surface; the palette in
  `tokens.css` records the ratios.
- `prefers-reduced-motion` removes camera flights, the marker pulse and all
  transitions. `prefers-reduced-transparency` makes panels opaque.
  `prefers-contrast: more` strengthens borders and dim text.
- Touch targets are at least 28 px tall, and larger on `pointer: coarse`.

A 3D globe is inherently visual. The mitigation is that every site is fully
usable without it: the list, search, filters and complete dossiers are all
plain DOM, the globe is loaded after them, and if WebGL is unavailable the
app says so and carries on without it.

---

## 7. Known gaps

Stated plainly rather than left for someone to discover:

1. **No CQL2 filtering on Pages.** Queryables are published; evaluation is
   client-side. GeoServer does this properly.
2. **No paging on Pages.** `numberMatched` equals `numberReturned` because
   everything is returned.
3. **No temporal extent.** The features have no time dimension, so
   `datetime` is not supported and no temporal extent is declared.
4. **One collection.** Splitting by category or region would make the
   collections list more interesting and the client slower. Not worth it at
   this size.
5. **Tiles are not proxied.** The browser talks to each imagery provider
   directly, so their availability is this app's availability.
   `check_services.py` exists to catch that early.
6. **Coordinates are single-source.** 136 positions were taken from
   Wikipedia/Wikidata after checking each agreed with the authored value to
   within 25 km; the rest are authored, including every `area` entry, since
   an article's point is not a region's centroid. Where the two disagreed
   by more than 25 km the authored value was kept and the difference
   logged. One entry is in that state by design — Edinburgh Castle, where
   Wikipedia's coordinate is the Stone of Scone's origin at Scone Palace,
   52 km away. No third source was consulted for any position.
