# Third-party notices

Ancient Aliens GIS draws on material that **Side Quest Studios does not
own and does not license to you**. This file records what that material
is, who it belongs to and on what terms you may use it.

Read it before you redistribute this repository or deploy a copy of the
site. Two of the terms below are stricter than the project's own
licenses, and one forbids commercial use outright.

For what *is* ours, see [`LICENSE`](LICENSE) (Apache 2.0, software) and
[`NOTICE`](NOTICE) (which also covers the CC BY 4.0 authored content).

---

## 1. Encyclopaedic summaries — English Wikipedia

**CC BY-SA 4.0** · <https://creativecommons.org/licenses/by-sa/4.0/>

The `summary` field of 245 of the 246 features is an extract from the
English Wikipedia article named in that feature's `wikipedia_title`,
with `wikipedia_url` linking the source and `summary_source` recording
the provenance.

Share-alike is the part people miss: **if you adapt that text, your
adaptation must also be CC BY-SA 4.0.** It does not reach the rest of
the catalogue. The authored fields and the Wikipedia extracts sit in
distinct, separately-labelled properties of each feature, so `items.json`
is a *collection* in the Creative Commons sense rather than an adaptation
of the Wikipedia material — the BY-SA obligation travels with the
summaries, not with the file that carries them.

## 2. Map imagery and basemaps

Each layer is credited in the running application. **That attribution is
a condition of use — do not remove it.**

| Layer | Provider | Terms |
|---|---|---|
| World Imagery | Esri, Maxar, Earthstar Geographics, GIS User Community | Esri terms of use |
| Dark Gray Canvas (base + labels) | Esri, HERE, Garmin, OpenStreetMap contributors | Esri terms of use |
| World Shaded Relief | Esri | Esri terms of use |
| Terrain3D elevation mesh | Esri and its data contributors | Esri terms of use |
| **Sentinel-2 cloudless 2025** | **EOX IT Services** (modified Copernicus Sentinel data 2025) | **CC BY-NC-SA 4.0 — NON-COMMERCIAL** |
| Terrain Light, overlay | EOX IT Services · OpenStreetMap contributors · Natural Earth | EOX terms |
| VIIRS, Blue Marble, Black Marble | NASA EOSDIS GIBS | NASA imagery policy |
| OpenStreetMap standard tiles | OpenStreetMap contributors | ODbL 1.0 (data) · tile usage policy |
| OpenTopoMap | OpenStreetMap contributors · OpenTopoMap | CC BY-SA 3.0 |

Two of these deserve a second look:

- **Sentinel-2 cloudless is CC BY-NC-SA 4.0.** Non-commercial. If you
  monetise a deployment with that layer reachable, you are infringing.
  Remove it from `assets/js/config.js` first.
- **Esri layers are fetched directly from `server.arcgisonline.com`** with
  no API key and no subscription. This is common practice and widely
  done, but Esri's terms of use have historically restricted access to
  their web services through non-Esri software, and we have not obtained
  a written confirmation that this usage is permitted. Satisfy yourself
  before relying on it commercially, or switch the default base layer to
  OpenStreetMap or OpenTopoMap, which carry no such ambiguity.

## 3. Ground elevation — Open-Meteo / Copernicus DEM

**CC BY 4.0** · <https://open-meteo.com/>

The `ground_elevation_m` value baked into each feature comes from the
Open-Meteo elevation API, which serves the Copernicus Digital Elevation
Model. `ground_elevation_source` records this per feature.

## 4. Globe engine — CesiumJS

**Apache License 2.0** · <https://cesium.com/platform/cesiumjs/>

Loaded at runtime from a pinned CDN build; no CesiumJS source is
vendored into this repository.

## 5. Fonts

Inter, Rajdhani and JetBrains Mono, served by Google Fonts under the
**SIL Open Font License 1.1**.

## 6. "Ancient Aliens" — A&E Television Networks

**Trademark. Not licensed to you by anyone here.**

*Ancient Aliens* is a trademark of A&E Television Networks. This project
is an independent, unaffiliated reference work: it catalogues locations
the programme discusses and sets each on-screen claim beside the
archaeological record. It is not endorsed by, affiliated with or
produced in cooperation with the programme or its producers.

No episode content, script, footage or still is reproduced here. The
`claim` field is an original summary written for this project of a
position the series advances, not a quotation from it.

Neither the Apache License (see its section 6) nor CC BY 4.0 grants any
trademark right. A fork that keeps the name carries that exposure
itself. If you redistribute commercially, take your own advice on it.
