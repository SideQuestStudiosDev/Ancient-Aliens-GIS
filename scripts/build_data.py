#!/usr/bin/env python3
"""
Build the static OGC API - Features tree for Ancient Aliens GIS.

  python3 scripts/build_data.py              # enrich from upstream, then build
  python3 scripts/build_data.py --offline    # build from the committed cache
  python3 scripts/build_data.py --check      # validate the catalogue
  python3 scripts/build_data.py --check-reproducible
                                             # assert data/ matches the source

Set SOURCE_DATE_EPOCH to pin the timestamp written into the generated
documents, which makes the build byte-for-byte reproducible.

Outputs
-------
data-source/sites.json                            normalised + enriched catalogue
data/index.json                                   OGC API landing page
data/conformance.json                             declared conformance classes
data/api.json                                     OpenAPI 3.0 service description
data/collections/index.json                       collections list
data/collections/sites/index.json                 collection metadata
data/collections/sites/items.json                 FeatureCollection (all sites)
data/collections/sites/items/<id>.json            individual Feature documents
data/collections/sites/queryables.json            OGC API Features Part 3 queryables
data/app-index.json                               slim client index (fast first paint)

Upstream lookups are cached in data-source/cache/ and committed, so
`--offline` reproduces the published tree exactly and CI needs no
network. Delete a cache file to refresh it from upstream.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "data-source"))

import catalog  # noqa: E402  (path set above)

OUT_DATA = os.path.join(ROOT, "data")
# Committed, not a scratch directory: these two files pin the upstream
# data the build depends on, so `--offline` reproduces the published
# tree byte for byte on a fresh checkout and CI needs no network.
CACHE_DIR = os.path.join(ROOT, "data-source", "cache")
CACHE_FILE = os.path.join(CACHE_DIR, "wikipedia.json")
ELEV_CACHE = os.path.join(CACHE_DIR, "elevation.json")

# Canonical public base. Overridable so forks and local previews emit correct
# absolute link hrefs without editing the script.
BASE_URL = os.environ.get(
    "AAGIS_BASE_URL", "https://sidequeststudiosdev.github.io/Ancient-Aliens-GIS"
).rstrip("/")

UA = ("AncientAliensGIS/1.0 (+https://github.com/SideQuestStudiosDev/"
      "Ancient-Aliens-GIS) python-urllib")

WIKI_API = "https://en.wikipedia.org/w/api.php"
WIKI_BATCH = 20          # titles per request (extracts cap the batch size)
WIKI_PAUSE = 1.2         # courtesy delay between requests
WIKI_RETRIES = 6         # attempts per batch before giving up
WIKI_BACKOFF = 4.0       # seconds, doubled each retry

# Ground elevation. Baked in at build time so the viewer can place the
# camera above the terrain on the first frame rather than waiting on a
# runtime elevation sample that may take seconds — or, on a slow link,
# longer than anyone will wait, leaving the camera inside a mountain.
ELEV_API = "https://api.open-meteo.com/v1/elevation"
ELEV_BATCH = 25
ELEV_PAUSE = 1.5

# Accept a Wikipedia coordinate over the authored one only when the two agree
# to within this distance. A larger gap means the article is about a different
# place (a region, a modern town) than the feature we want to pin.
COORD_AGREE_KM = 25.0


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def mkdirp(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def write_json(path: str, obj, *, compact: bool = False) -> int:
    mkdirp(os.path.dirname(path))
    if compact:
        text = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    else:
        text = json.dumps(obj, ensure_ascii=False, indent=1)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text + "\n")
    return len(text)


def clean_extract(text: str) -> str:
    """Tidy a Wikipedia plain-text intro into 1-3 readable sentences."""
    if not text:
        return ""
    text = re.sub(r"\s*\([^()]*?(?:listen|help·info|/[^()]*/)[^()]*\)", "", text)
    text = re.sub(r"\(\s*(?:;|,)\s*", "(", text)
    text = re.sub(r"\(\s*\)", "", text)
    text = re.sub(r"[ \t]+", " ", text).strip()
    paras = [p.strip() for p in text.split("\n") if p.strip()]
    text = paras[0] if paras else ""
    # Keep roughly the first three sentences, without splitting on abbreviations.
    out, count = [], 0
    for chunk in re.split(r"(?<=[.!?])\s+(?=[A-Z(\"'])", text):
        out.append(chunk)
        count += 1
        if count >= 3 or sum(len(c) for c in out) > 520:
            break
    return " ".join(out).strip()


# --------------------------------------------------------------------------- #
# Wikipedia enrichment
# --------------------------------------------------------------------------- #
def load_cache() -> dict:
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, encoding="utf-8") as fh:
                return json.load(fh)
        except (OSError, ValueError):
            pass
    return {}


def save_cache(cache: dict) -> None:
    mkdirp(CACHE_DIR)
    with open(CACHE_FILE, "w", encoding="utf-8") as fh:
        json.dump(cache, fh, ensure_ascii=False, indent=1, sort_keys=True)


def wiki_fetch(titles: list[str]) -> dict:
    """One API round-trip. Returns {requested_title: record}."""
    params = {
        "action": "query",
        "format": "json",
        "formatversion": "1",
        "redirects": "1",
        "prop": "coordinates|pageprops|extracts",
        "coprop": "globe",
        "coprimary": "primary",
        "colimit": "max",
        "exintro": "1",
        "explaintext": "1",
        "exsectionformat": "plain",
        "ppprop": "wikibase_item|wikibase-shortdesc|page_image_free",
        "titles": "|".join(titles),
    }
    url = WIKI_API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA,
                                               "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        payload = json.load(resp)

    query = payload.get("query", {})
    # Map requested title -> resolved title through redirects and normalisation.
    alias = {}
    for norm in query.get("normalized", []):
        alias[norm["from"]] = norm["to"]
    for red in query.get("redirects", []):
        alias[red["from"]] = red["to"]

    def resolve(title: str) -> str:
        seen, cur = set(), title
        while cur in alias and cur not in seen:
            seen.add(cur)
            cur = alias[cur]
        return cur

    by_title = {}
    for page in query.get("pages", []) if isinstance(query.get("pages"), list) \
            else query.get("pages", {}).values():
        by_title[page.get("title", "")] = page

    out = {}
    for requested in titles:
        page = by_title.get(resolve(requested))
        if page is None or "missing" in page:
            out[requested] = {"ok": False, "title": requested}
            continue
        props = page.get("pageprops", {}) or {}
        coords = (page.get("coordinates") or [{}])[0]
        out[requested] = {
            "ok": True,
            "title": page.get("title", requested),
            "pageid": page.get("pageid"),
            "lat": coords.get("lat"),
            "lon": coords.get("lon"),
            "globe": coords.get("globe", "earth"),
            "wikidata": props.get("wikibase_item"),
            "shortdesc": props.get("wikibase-shortdesc"),
            "image": props.get("page_image_free"),
            "extract": clean_extract(page.get("extract", "")),
        }
    return out


def wiki_fetch_retrying(titles: list[str], *, label: str = "") -> dict | None:
    """wiki_fetch with exponential backoff. Returns None if every attempt failed.

    Transient failures are deliberately NOT written to the cache, so a later
    run retries them instead of baking a gap into the build.
    """
    delay = WIKI_BACKOFF
    for attempt in range(1, WIKI_RETRIES + 1):
        try:
            return wiki_fetch(titles)
        except urllib.error.HTTPError as exc:
            retryable = exc.code in (429, 500, 502, 503, 504)
            reason = f"HTTP {exc.code}"
            hinted = exc.headers.get("Retry-After") if exc.headers else None
            if hinted and str(hinted).isdigit():
                delay = max(delay, float(hinted))
        except (urllib.error.URLError, TimeoutError, ValueError,
                ConnectionError) as exc:
            retryable, reason = True, str(exc)[:80]
        else:
            break
        if not retryable or attempt == WIKI_RETRIES:
            print(f"  ! {label} gave up ({reason})")
            return None
        print(f"  . {label} {reason}; retry {attempt}/{WIKI_RETRIES - 1} "
              f"in {delay:.0f}s")
        time.sleep(delay)
        delay = min(delay * 2, 120.0)
    return None


def enrich(sites: list[dict], *, offline: bool) -> dict:
    cache = load_cache()
    titles = sorted({s["wikipedia"] for s in sites if s["wikipedia"]})
    todo = [t for t in titles if t not in cache]

    if todo and not offline:
        print(f"  fetching {len(todo)} Wikipedia records "
              f"({len(titles) - len(todo)} cached)…")
        batches = [todo[i:i + WIKI_BATCH] for i in range(0, len(todo), WIKI_BATCH)]
        failed = 0
        for n, batch in enumerate(batches, 1):
            got = wiki_fetch_retrying(batch, label=f"batch {n}/{len(batches)}")
            if got is None:
                failed += len(batch)
            else:
                cache.update(got)
                save_cache(cache)        # checkpoint, so a later abort keeps work
            print(f"    {min(n * WIKI_BATCH, len(todo))}/{len(todo)}"
                  + ("" if got is not None else "  (skipped)"))
            time.sleep(WIKI_PAUSE)
        if failed:
            print(f"  ! {failed} titles could not be fetched; authored data "
                  f"used for those. Re-run to retry (cache keeps the rest).")
        save_cache(cache)
    elif todo:
        print(f"  offline: {len(todo)} titles unresolved, using authored data")

    stats = {"geocoded": 0, "summarised": 0, "missing": [], "moved": []}

    for site in sites:
        rec = cache.get(site["wikipedia"], {})
        site["wikipedia_title"] = rec.get("title") or site["wikipedia"]
        site["wikipedia_url"] = (
            "https://en.wikipedia.org/wiki/"
            + urllib.parse.quote(site["wikipedia_title"].replace(" ", "_"),
                                 safe="(),'!-_.~")
        ) if site["wikipedia"] else ""
        site["wikipedia_verified"] = bool(rec.get("ok"))
        site["wikidata"] = rec.get("wikidata") or ""
        site["summary"] = rec.get("extract") or ""
        site["shortdesc"] = rec.get("shortdesc") or ""
        site["image"] = rec.get("image") or ""
        site["coord_source"] = "authored"

        if not rec.get("ok"):
            if site["wikipedia"]:
                stats["missing"].append((site["id"], site["wikipedia"]))
        else:
            if site["summary"]:
                stats["summarised"] += 1
            wlat, wlon = rec.get("lat"), rec.get("lon")
            on_earth = rec.get("globe", "earth") == "earth"
            # Only exact-precision points adopt Wikipedia's coordinate, and
            # only when it agrees with the authored position. Regions and
            # areas keep their authored centroid by design.
            if (wlat is not None and wlon is not None and on_earth
                    and not site["offworld"]
                    and site["precision"] == "exact"
                    and site["geometry"] == "point"):
                gap = haversine_km(site["lat"], site["lon"], wlat, wlon)
                if gap <= COORD_AGREE_KM:
                    site["lat"], site["lon"] = round(wlat, 6), round(wlon, 6)
                    site["coord_source"] = "wikipedia"
                    stats["geocoded"] += 1
                else:
                    stats["moved"].append((site["id"], round(gap, 1)))
    return stats



# --------------------------------------------------------------------------- #
# ground elevation
# --------------------------------------------------------------------------- #
def elev_fetch(points: list[tuple[float, float]]) -> list[float] | None:
    """One batch of (lat, lon) -> metres above sea level."""
    params = {
        "latitude": ",".join(f"{lat:.5f}" for lat, _ in points),
        "longitude": ",".join(f"{lon:.5f}" for _, lon in points),
    }
    url = ELEV_API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA,
                                               "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        data = json.load(resp)
    out = data.get("elevation")
    return out if isinstance(out, list) and len(out) == len(points) else None


def elev_fetch_retrying(points, *, label=""):
    delay = WIKI_BACKOFF
    for attempt in range(1, WIKI_RETRIES + 1):
        try:
            return elev_fetch(points)
        except urllib.error.HTTPError as exc:
            retryable = exc.code in (429, 500, 502, 503, 504)
            reason = f"HTTP {exc.code}"
        except (urllib.error.URLError, TimeoutError, ValueError,
                ConnectionError) as exc:
            retryable, reason = True, str(exc)[:70]
        else:
            break
        if not retryable or attempt == WIKI_RETRIES:
            print(f"  ! {label} gave up ({reason})")
            return None
        print(f"  . {label} {reason}; retry in {delay:.0f}s")
        time.sleep(delay)
        delay = min(delay * 2, 90.0)
    return None


def add_elevation(sites: list[dict], *, offline: bool) -> int:
    """Attach `ground_m` to every terrestrial site, cached between builds."""
    cache = {}
    if os.path.exists(ELEV_CACHE):
        try:
            with open(ELEV_CACHE, encoding="utf-8") as fh:
                cache = json.load(fh)
        except (OSError, ValueError):
            cache = {}

    def key(site):
        return f"{site['lat']:.5f},{site['lon']:.5f}"

    targets = [s for s in sites if not s["offworld"]]
    todo = [s for s in targets if key(s) not in cache]

    if todo and not offline:
        print(f"  fetching ground elevation for {len(todo)} sites "
              f"({len(targets) - len(todo)} cached)…")
        batches = [todo[i:i + ELEV_BATCH]
                   for i in range(0, len(todo), ELEV_BATCH)]
        for n, batch in enumerate(batches, 1):
            got = elev_fetch_retrying(
                [(s["lat"], s["lon"]) for s in batch],
                label=f"elevation batch {n}/{len(batches)}")
            if got:
                for site, metres in zip(batch, got):
                    cache[key(site)] = round(float(metres), 1)
                with open(ELEV_CACHE, "w", encoding="utf-8") as fh:
                    json.dump(cache, fh, indent=1, sort_keys=True)
            print(f"    {min(n * ELEV_BATCH, len(todo))}/{len(todo)}"
                  + ("" if got else "  (skipped)"))
            time.sleep(ELEV_PAUSE)
    elif todo:
        print(f"  offline: {len(todo)} elevations unresolved, assuming 0 m")

    resolved = 0
    for site in sites:
        if site["offworld"]:
            site["ground_m"] = None
            continue
        value = cache.get(key(site))
        site["ground_m"] = value
        if value is not None:
            resolved += 1
    return resolved


# --------------------------------------------------------------------------- #
# GeoJSON / OGC emission
# --------------------------------------------------------------------------- #
def geometry_for(site: dict) -> dict | None:
    if site["offworld"]:
        return None          # a null geometry is valid GeoJSON
    if site["geometry"] == "multipoint" and site["points"]:
        return {"type": "MultiPoint",
                "coordinates": [[round(lon, 6), round(lat, 6)]
                                for lat, lon in site["points"]]}
    return {"type": "Point",
            "coordinates": [round(site["lon"], 6), round(site["lat"], 6)]}


def bbox_for(site: dict) -> list[float] | None:
    geom = geometry_for(site)
    if geom is None:
        return None
    pts = (geom["coordinates"] if geom["type"] == "MultiPoint"
           else [geom["coordinates"]])
    lons = [p[0] for p in pts]
    lats = [p[1] for p in pts]
    if site["radius_km"]:
        dlat = site["radius_km"] / 111.32
        clat = sum(lats) / len(lats)
        dlon = site["radius_km"] / max(1e-6, 111.32 * math.cos(math.radians(clat)))
        return [round(min(lons) - dlon, 5), round(max(-90.0, min(lats) - dlat), 5),
                round(max(lons) + dlon, 5), round(min(90.0, max(lats) + dlat), 5)]
    return [min(lons), min(lats), max(lons), max(lats)]


def feature_for(site: dict) -> dict:
    cat_label = catalog.CATEGORIES[site["category"]][0]
    links = [
        {"href": f"{BASE_URL}/data/collections/sites/items/{site['id']}.json",
         "rel": "self", "type": "application/geo+json",
         "title": f"{site['name']} — this document"},
        {"href": f"{BASE_URL}/data/collections/sites/items.json",
         "rel": "collection", "type": "application/geo+json",
         "title": "Ancient Aliens sites"},
        {"href": f"{BASE_URL}/?site={site['id']}",
         "rel": "alternate", "type": "text/html",
         "title": f"{site['name']} in the 3D geoportal"},
    ]
    if site["wikipedia_url"]:
        links.append({"href": site["wikipedia_url"], "rel": "describedby",
                      "type": "text/html",
                      "title": f"Wikipedia: {site['wikipedia_title']}"})
    if site["wikidata"]:
        links.append({"href": f"https://www.wikidata.org/wiki/{site['wikidata']}",
                      "rel": "describedby", "type": "text/html",
                      "title": f"Wikidata: {site['wikidata']}"})
    for extra in site["links"]:
        links.append({"href": extra["url"],
                      "rel": "related" if extra.get("kind") != "official"
                             else "canonical",
                      "type": "text/html", "title": extra["label"]})

    feat = {
        "type": "Feature",
        "id": site["id"],
        "geometry": geometry_for(site),
        "properties": {
            "name": site["name"],
            "subtitle": site["subtitle"],
            "country": site["country"],
            "region": site["region"],
            "category": site["category"],
            "category_label": cat_label,
            "tags": site["tags"],
            "aliases": site["aliases"],
            "claim": site["claim"],
            "context": site["context"],
            "summary": site["summary"],
            "summary_source": ("Wikipedia (CC BY-SA 4.0)" if site["summary"]
                               else ""),
            "short_description": site["shortdesc"],
            "location_precision": site["precision"],
            "coordinate_source": site["coord_source"],
            "coordinate_reference_system": "http://www.opengis.net/def/crs/OGC/1.3/CRS84",
            "latitude": None if site["offworld"] else round(site["lat"], 6),
            "longitude": None if site["offworld"] else round(site["lon"], 6),
            "celestial_body": "moon" if site["offworld"] else "earth",
            "radius_km": site["radius_km"] or None,
            "ground_elevation_m": site.get("ground_m"),
            "ground_elevation_source": (
                "Open-Meteo elevation API (Copernicus DEM)"
                if site.get("ground_m") is not None else ""),
            "camera_height_m": site["height"],
            "camera_pitch_deg": site["pitch"],
            "wikipedia_title": site["wikipedia_title"],
            "wikipedia_url": site["wikipedia_url"],
            "wikipedia_verified": site["wikipedia_verified"],
            "wikidata_id": site["wikidata"],
            "image_file": site["image"],
        },
        "links": links,
    }
    bb = bbox_for(site)
    if bb:
        feat["bbox"] = bb
    return feat


CONFORMANCE = [
    "http://www.opengis.net/spec/ogcapi-common-1/1.0/conf/core",
    "http://www.opengis.net/spec/ogcapi-common-1/1.0/conf/landing-page",
    "http://www.opengis.net/spec/ogcapi-common-1/1.0/conf/json",
    "http://www.opengis.net/spec/ogcapi-common-2/1.0/conf/collections",
    "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core",
    "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson",
    "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/oas30",
]

STATIC_LIMITATIONS = [
    "This deployment is a set of static documents on a CDN, so query "
    "parameters (bbox, limit, datetime, offset, filter) are accepted but "
    "ignored: /items always returns the complete FeatureCollection. "
    "Filtering and paging are performed by the client.",
    "The collection is small (hundreds of features, well under 1 MB "
    "gzipped), which is why returning it whole is practical.",
    "For a deployment that honours the Core parameter requirements, run the "
    "GeoServer configuration in geoserver/ — it serves the same data as "
    "OGC API - Features, WFS 2.0.0 and WMS 1.3.0 over the identical schema.",
]


# The three places a wall-clock time is written into the generated tree.
# OGC API - Features wants a real timeStamp on a FeatureCollection, so these
# stay honest rather than being frozen — and --check-reproducible ignores
# them instead, since they describe when, not what.
TIMESTAMP_FIELDS = {
    "index.json": "x-generated",
    "app-index.json": "generated",
    os.path.join("collections", "sites", "items.json"): "timeStamp",
}


def build_timestamp() -> str:
    """When this build ran. SOURCE_DATE_EPOCH pins it if set."""
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if epoch and epoch.isdigit():
        when = datetime.fromtimestamp(int(epoch), tz=timezone.utc)
    else:
        when = datetime.now(timezone.utc)
    return when.strftime("%Y-%m-%dT%H:%M:%SZ")


def build(sites: list[dict], stats: dict) -> None:
    now = build_timestamp()
    features = [feature_for(s) for s in sites]

    earthly = [f for f in features if f["geometry"] is not None]
    lons = [c[0] for f in earthly for c in
            (f["geometry"]["coordinates"] if f["geometry"]["type"] == "MultiPoint"
             else [f["geometry"]["coordinates"]])]
    lats = [c[1] for f in earthly for c in
            (f["geometry"]["coordinates"] if f["geometry"]["type"] == "MultiPoint"
             else [f["geometry"]["coordinates"]])]
    extent = [round(min(lons), 4), round(min(lats), 4),
              round(max(lons), 4), round(max(lats), 4)]

    # ---- landing page ---------------------------------------------------- #
    write_json(os.path.join(OUT_DATA, "index.json"), {
        "title": "Ancient Aliens GIS — OGC API Features",
        "description":
            "Every location referenced in the television series Ancient "
            "Aliens, published as OGC API - Features. Each feature carries "
            "the claim made on screen, a summary of the archaeological "
            "record, and context noting where the two diverge.",
        "attribution":
            "Ancient Aliens GIS, by Side Quest Studios. Descriptive summaries "
            "from Wikipedia, CC BY-SA 4.0. Claim and context text "
            "© Side Quest Studios, CC BY 4.0.",
        "links": [
            {"href": f"{BASE_URL}/data/index.json", "rel": "self",
             "type": "application/json", "title": "this document"},
            {"href": f"{BASE_URL}/data/api.json", "rel": "service-desc",
             "type": "application/vnd.oai.openapi+json;version=3.0",
             "title": "OpenAPI 3.0 description of this service"},
            {"href": f"{BASE_URL}/data/conformance.json", "rel": "conformance",
             "type": "application/json", "title": "declared conformance classes"},
            {"href": f"{BASE_URL}/data/collections/index.json", "rel": "data",
             "type": "application/json", "title": "feature collections"},
            {"href": f"{BASE_URL}/", "rel": "alternate", "type": "text/html",
             "title": "Ancient Aliens GIS 3D geoportal"},
        ],
        "x-static-deployment": STATIC_LIMITATIONS,
        "x-generated": now,
    })

    write_json(os.path.join(OUT_DATA, "conformance.json"),
               {"conformsTo": CONFORMANCE,
                "x-static-deployment": STATIC_LIMITATIONS})

    # ---- collections ----------------------------------------------------- #
    collection = {
        "id": "sites",
        "title": "Ancient Aliens locations",
        "description":
            f"{len(features)} locations referenced in Ancient Aliens, with "
            "claim, record and context for each. Coordinates are EPSG:4326 "
            "(CRS84, longitude/latitude). The location_precision property "
            "states whether a position is a surveyed monument, an "
            "approximation, a region centroid, or an unresolved reference.",
        "itemType": "feature",
        "crs": ["http://www.opengis.net/def/crs/OGC/1.3/CRS84",
                "http://www.opengis.net/def/crs/EPSG/0/4326"],
        "storageCrs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84",
        "extent": {
            "spatial": {"bbox": [extent],
                        "crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"},
        },
        "links": [
            {"href": f"{BASE_URL}/data/collections/sites/index.json",
             "rel": "self", "type": "application/json",
             "title": "Ancient Aliens locations"},
            {"href": f"{BASE_URL}/data/collections/sites/items.json",
             "rel": "items", "type": "application/geo+json",
             "title": "all features as GeoJSON"},
            {"href": f"{BASE_URL}/data/collections/sites/queryables.json",
             "rel": "http://www.opengis.net/def/rel/ogc/1.0/queryables",
             "type": "application/schema+json", "title": "queryable properties"},
            {"href": "https://creativecommons.org/licenses/by/4.0/",
             "rel": "license", "type": "text/html", "title": "CC BY 4.0"},
        ],
        "x-feature-count": len(features),
    }
    write_json(os.path.join(OUT_DATA, "collections", "index.json"), {
        "collections": [collection],
        "links": [
            {"href": f"{BASE_URL}/data/collections/index.json", "rel": "self",
             "type": "application/json", "title": "this document"},
            {"href": f"{BASE_URL}/data/index.json", "rel": "root",
             "type": "application/json", "title": "service landing page"},
        ],
    })
    write_json(os.path.join(OUT_DATA, "collections", "sites", "index.json"),
               collection)

    # ---- items ----------------------------------------------------------- #
    fc = {
        "type": "FeatureCollection",
        "bbox": extent,
        "features": features,
        "numberMatched": len(features),
        "numberReturned": len(features),
        "timeStamp": now,
        "links": [
            {"href": f"{BASE_URL}/data/collections/sites/items.json",
             "rel": "self", "type": "application/geo+json",
             "title": "this document"},
            {"href": f"{BASE_URL}/data/collections/sites/index.json",
             "rel": "collection", "type": "application/json",
             "title": "the collection description"},
        ],
    }
    size = write_json(os.path.join(OUT_DATA, "collections", "sites",
                                   "items.json"), fc, compact=True)

    items_dir = os.path.join(OUT_DATA, "collections", "sites", "items")
    if os.path.isdir(items_dir):
        for stale in os.listdir(items_dir):
            if stale.endswith(".json"):
                os.remove(os.path.join(items_dir, stale))
    for feat in features:
        write_json(os.path.join(items_dir, f"{feat['id']}.json"), feat)

    # ---- queryables (Part 3 shape) --------------------------------------- #
    write_json(os.path.join(OUT_DATA, "collections", "sites",
                            "queryables.json"), {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"{BASE_URL}/data/collections/sites/queryables.json",
        "title": "Ancient Aliens locations — queryable properties",
        "type": "object",
        "properties": {
            "name": {"type": "string", "title": "Site name"},
            "country": {"type": "string", "title": "Country or territory"},
            "region": {"type": "string", "title": "World region",
                       "enum": catalog.REGIONS},
            "category": {"type": "string", "title": "Site category",
                         "enum": sorted(catalog.CATEGORIES)},
            "location_precision": {
                "type": "string", "title": "Positional precision",
                "enum": ["exact", "approximate", "area", "uncertain"]},
            "celestial_body": {"type": "string", "enum": ["earth", "moon"]},
            "tags": {"type": "array", "items": {"type": "string"}},
        },
        "additionalProperties": False,
    })

    # ---- OpenAPI --------------------------------------------------------- #
    write_json(os.path.join(OUT_DATA, "api.json"),
               build_openapi(len(features)))

    # ---- slim client index ----------------------------------------------- #
    cats = [{"id": k, "label": v[0], "token": v[1]}
            for k, v in catalog.CATEGORIES.items()]
    slim = {
        "generated": now,
        "count": len(features),
        "regions": catalog.REGIONS,
        "categories": cats,
        "bbox": extent,
        "attribution":
            "Ancient Aliens GIS, by Side Quest Studios. Site summaries from "
            "Wikipedia (CC BY-SA 4.0); claim and context text "
            "© Side Quest Studios, CC BY 4.0.",
        "sites": [{
            "id": f["id"],
            "n": f["properties"]["name"],
            "s": f["properties"]["subtitle"],
            "c": f["properties"]["category"],
            "r": f["properties"]["region"],
            "y": f["properties"]["country"],
            "p": f["properties"]["location_precision"],
            "t": f["properties"]["tags"] + f["properties"]["aliases"],
            "lat": f["properties"]["latitude"],
            "lon": f["properties"]["longitude"],
            "h": f["properties"]["camera_height_m"],
            "g": f["properties"]["ground_elevation_m"],
            "pi": f["properties"]["camera_pitch_deg"],
            "rk": f["properties"]["radius_km"],
            "off": f["properties"]["celestial_body"] != "earth",
            "mp": ([[round(c[1], 5), round(c[0], 5)]
                    for c in f["geometry"]["coordinates"]]
                   if f["geometry"] and f["geometry"]["type"] == "MultiPoint"
                   else None),
        } for f in features],
    }
    slim_size = write_json(os.path.join(OUT_DATA, "app-index.json"), slim,
                           compact=True)

    # A sitemap, so every site dossier is independently discoverable and
    # robots.txt is not advertising a 404.
    build_sitemap(features, now)

    print(f"\n  items.json      {size / 1024:7.1f} KiB  ({len(features)} features)")
    print(f"  app-index.json  {slim_size / 1024:7.1f} KiB")
    print(f"  item documents  {len(features)}")
    print(f"  bbox            {extent}")
    print(f"\n  wikipedia: {stats['geocoded']} geocoded, "
          f"{stats['summarised']} summarised")
    print(f"  ground elevation: {stats.get('elevations', 0)} sites")
    if stats["missing"]:
        print(f"  ! {len(stats['missing'])} unresolved Wikipedia titles:")
        for sid, title in stats["missing"][:20]:
            print(f"      {sid:28s} {title}")
    if stats["moved"]:
        print(f"  i {len(stats['moved'])} authored coords kept "
              f"(Wikipedia point >{COORD_AGREE_KM:.0f} km away):")
        for sid, gap in sorted(stats["moved"], key=lambda x: -x[1])[:20]:
            print(f"      {sid:28s} {gap} km")



def build_sitemap(features, now: str) -> None:
    """One URL per dossier, plus the app root.

    Deep links are real addresses in this app (?site=<id> restores the
    selection on load), so they are worth listing.
    """
    day = now[:10]
    rows = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        f"  <url><loc>{BASE_URL}/</loc><lastmod>{day}</lastmod>"
        f"<changefreq>weekly</changefreq><priority>1.0</priority></url>",
    ]
    for feat in features:
        fid = feat["id"]
        rows.append(
            f"  <url><loc>{BASE_URL}/?site={fid}</loc>"
            f"<lastmod>{day}</lastmod><changefreq>monthly</changefreq>"
            f"<priority>0.6</priority></url>")
    rows.append("</urlset>")
    path = os.path.join(ROOT, "sitemap.xml")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(rows) + "\n")
    print(f"  sitemap.xml     {len(features) + 1} urls")


def build_openapi(count: int) -> dict:
    json_resp = {"description": "A JSON document.",
                 "content": {"application/json": {"schema": {"type": "object"}}}}
    geo_resp = {"description": "A GeoJSON document.",
                "content": {"application/geo+json": {"schema": {"type": "object"}}}}
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "Ancient Aliens GIS — OGC API Features",
            "version": "1.0.0",
            "description":
                "Static OGC API - Features service publishing "
                f"{count} locations referenced in the television series "
                "Ancient Aliens. Query parameters are accepted but ignored; "
                "see x-static-deployment on the landing page.",
            "license": {"name": "CC BY 4.0",
                        "url": "https://creativecommons.org/licenses/by/4.0/"},
            "contact": {"name": "Ancient Aliens GIS",
                        "url": f"{BASE_URL}/"},
        },
        "servers": [{"url": f"{BASE_URL}/data",
                     "description": "GitHub Pages static deployment"}],
        "tags": [{"name": "Capabilities"}, {"name": "Data"}],
        "paths": {
            "/index.json": {"get": {"tags": ["Capabilities"],
                                    "operationId": "getLandingPage",
                                    "summary": "Landing page",
                                    "responses": {"200": json_resp}}},
            "/conformance.json": {"get": {"tags": ["Capabilities"],
                                          "operationId": "getConformance",
                                          "summary": "Conformance classes",
                                          "responses": {"200": json_resp}}},
            "/collections/index.json": {"get": {"tags": ["Capabilities"],
                                                "operationId": "getCollections",
                                                "summary": "Feature collections",
                                                "responses": {"200": json_resp}}},
            "/collections/sites/index.json": {
                "get": {"tags": ["Capabilities"], "operationId": "describeSites",
                        "summary": "Describe the sites collection",
                        "responses": {"200": json_resp}}},
            "/collections/sites/items.json": {
                "get": {"tags": ["Data"], "operationId": "getSites",
                        "summary": "All site features",
                        "description":
                            "Returns the complete FeatureCollection. Static "
                            "hosting cannot filter, so bbox/limit/offset are "
                            "ignored.",
                        "responses": {"200": geo_resp}}},
            "/collections/sites/items/{featureId}.json": {
                "get": {"tags": ["Data"], "operationId": "getSite",
                        "summary": "A single site feature",
                        "parameters": [{"name": "featureId", "in": "path",
                                        "required": True,
                                        "schema": {"type": "string"},
                                        "example": "gobekli-tepe"}],
                        "responses": {"200": geo_resp,
                                      "404": {"description": "No such feature."}}}},
        },
    }



# --------------------------------------------------------------------------- #
# Service worker cache version
#
# sw.js serves its caches stale-while-revalidate, and a browser only installs
# a new worker when sw.js itself changes bytes. With a hand-written constant
# that means a release reaches returning visitors a full load late, and only
# when somebody remembered to bump it — the failure mode being a deploy that
# looks broken because the old catalogue is still on screen.
#
# So the constant is derived rather than typed: a digest of every file the
# worker precaches. Change any of them and sw.js changes with them, the
# browser installs the new worker, activate drops the stale caches, and the
# first load after a deploy is already current.
#
# sw.js is excluded by construction — a worker never precaches itself — so
# writing the digest back into it cannot perturb the digest.

SW_FILE = os.path.join(ROOT, "sw.js")
SW_VERSION_RE = re.compile(r"(?m)^(const VERSION = ')([^']*)(';)$")
SW_SHELL_RE = re.compile(r"const SHELL_FILES = \[(.*?)\];", re.S)


def sw_shell_files(text: str) -> list[str]:
    """The paths sw.js precaches, read out of sw.js so the two cannot drift."""
    found = SW_SHELL_RE.search(text)
    if not found:
        raise SystemExit("sw.js: SHELL_FILES list not found")
    return re.findall(r"'([^']+)'", found.group(1))


def shell_path(rel: str, data_root: str) -> str:
    """Resolve a sw.js precache path. Entries under data/ resolve against
    data_root, so the reproducibility check can point at its scratch build."""
    rel = rel[2:] if rel.startswith("./") else rel
    if rel in ("", "/"):
        rel = "index.html"                      # './' is served by index.html
    if rel.startswith("data/"):
        return os.path.join(data_root, rel[len("data/"):])
    return os.path.join(ROOT, rel)


def stable_bytes(path: str, data_root: str) -> bytes:
    """File content with the build timestamp removed, so a rebuild that
    changed nothing produces the same digest."""
    field = TIMESTAMP_FIELDS.get(os.path.relpath(path, data_root))
    if field:
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
        doc.pop(field, None)
        return json.dumps(doc, sort_keys=True, ensure_ascii=False).encode()
    with open(path, "rb") as fh:
        return fh.read()


def site_version(data_root: str) -> str:
    """Digest of everything the service worker precaches."""
    with open(SW_FILE, encoding="utf-8") as fh:
        shell = sw_shell_files(fh.read())
    digest = hashlib.sha256()
    for rel in sorted(shell):
        path = shell_path(rel, data_root)
        if not os.path.exists(path):
            raise SystemExit(f"sw.js precaches {rel}, which does not exist")
        digest.update(rel.encode())
        digest.update(b"\0")
        digest.update(stable_bytes(path, data_root))
        digest.update(b"\0")
    return "aagis-" + digest.hexdigest()[:12]


def read_sw_version() -> str | None:
    with open(SW_FILE, encoding="utf-8") as fh:
        found = SW_VERSION_RE.search(fh.read())
    return found.group(2) if found else None


def stamp_service_worker(version: str) -> bool:
    """Write the digest into sw.js. True when it changed."""
    with open(SW_FILE, encoding="utf-8") as fh:
        text = fh.read()
    new, count = SW_VERSION_RE.subn(
        lambda m: m.group(1) + version + m.group(3), text)
    if not count:
        raise SystemExit("sw.js: VERSION constant not found")
    if new == text:
        return False
    with open(SW_FILE, "w", encoding="utf-8") as fh:
        fh.write(new)
    return True


def check_reproducible() -> int:
    """Assert the committed data/ is what data-source/ currently generates.

    Builds into a scratch directory and compares. The three generated
    timestamps are normalised away: they record when a build ran, not what
    it produced, and no amount of SOURCE_DATE_EPOCH plumbing can make CI
    guess the clock reading that was in effect when the tree was committed.

    Everything else must match byte for byte, which is the invariant worth
    enforcing — that nobody edited data/ by hand or forgot to rebuild it
    after changing the catalogue.
    """
    import filecmp
    import shutil
    import tempfile

    global OUT_DATA
    committed = os.path.join(ROOT, "data")
    if not os.path.isdir(committed):
        print("  no data/ to compare against")
        return 1

    scratch = tempfile.mkdtemp(prefix="aagis-repro-")
    original = OUT_DATA
    try:
        OUT_DATA = os.path.join(scratch, "data")
        sites = [dict(x) for x in catalog.SITES]
        stats = enrich(sites, offline=True)
        stats["elevations"] = add_elevation(sites, offline=True)
        import io
        import contextlib
        with contextlib.redirect_stdout(io.StringIO()):
            build(sites, stats)

        def normalise(path: str, rel: str):
            field = TIMESTAMP_FIELDS.get(rel)
            with open(path, encoding="utf-8") as fh:
                doc = json.load(fh)
            if field:
                doc.pop(field, None)
            return json.dumps(doc, sort_keys=True, ensure_ascii=False)

        problems = []
        for root, _dirs, files in os.walk(OUT_DATA):
            for name in files:
                built = os.path.join(root, name)
                rel = os.path.relpath(built, OUT_DATA)
                against = os.path.join(committed, rel)
                if not os.path.exists(against):
                    problems.append(f"{rel}: generated but not committed")
                    continue
                if rel in TIMESTAMP_FIELDS:
                    if normalise(built, rel) != normalise(against, rel):
                        problems.append(f"{rel}: content differs")
                elif not filecmp.cmp(built, against, shallow=False):
                    problems.append(f"{rel}: content differs")

        for root, _dirs, files in os.walk(committed):
            for name in files:
                rel = os.path.relpath(os.path.join(root, name), committed)
                if not os.path.exists(os.path.join(OUT_DATA, rel)):
                    problems.append(f"{rel}: committed but no longer generated")

        # A forgotten rebuild shows up here as much as a hand-edited
        # document: the digest is taken over the scratch build, so it is what
        # the committed sw.js should be carrying.
        expected = site_version(OUT_DATA)
        actual = read_sw_version()
        if actual != expected:
            problems.append(
                f"sw.js: cache version is {actual or 'missing'}, "
                f"expected {expected}")

        if problems:
            print(f"  data/ is out of date — {len(problems)} difference(s):")
            for item in problems[:20]:
                print(f"    - {item}")
            if len(problems) > 20:
                print(f"    … and {len(problems) - 20} more")
            print("\n  Run: python3 scripts/build_data.py "
                  "&& git add data/ sw.js")
            return 1

        total = sum(len(f) for _, _, f in os.walk(committed))
        print(f"  data/ reproduces exactly from data-source/ "
              f"({total} files, timestamps excluded)")
        print(f"  sw.js cache version matches the tree ({expected})")
        return 0
    finally:
        OUT_DATA = original
        shutil.rmtree(scratch, ignore_errors=True)


# --------------------------------------------------------------------------- #
def validate(sites: list[dict]) -> list[str]:
    errs = []
    seen = set()
    for s in sites:
        sid = s["id"]
        if sid in seen:
            errs.append(f"{sid}: duplicate id")
        seen.add(sid)
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,60}", sid):
            errs.append(f"{sid}: id must be lowercase kebab-case")
        if s["category"] not in catalog.CATEGORIES:
            errs.append(f"{sid}: unknown category {s['category']!r}")
        if s["region"] not in catalog.REGIONS:
            errs.append(f"{sid}: unknown region {s['region']!r}")
        if s["precision"] not in ("exact", "approximate", "area", "uncertain"):
            errs.append(f"{sid}: bad precision {s['precision']!r}")
        if not s["offworld"]:
            if not -90 <= s["lat"] <= 90:
                errs.append(f"{sid}: latitude out of range ({s['lat']})")
            if not -180 <= s["lon"] <= 180:
                errs.append(f"{sid}: longitude out of range ({s['lon']})")
        if len(s["claim"]) < 40:
            errs.append(f"{sid}: claim text too short")
        if len(s["context"]) < 40:
            errs.append(f"{sid}: context text too short")
        if s["geometry"] == "multipoint" and len(s["points"]) < 2:
            errs.append(f"{sid}: multipoint needs >= 2 points")
        for link in s["links"]:
            if not link.get("url", "").startswith("https://"):
                errs.append(f"{sid}: link must be https ({link.get('url')!r})")
    return errs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true",
                    help="do not contact Wikipedia; use authored data only")
    ap.add_argument("--check", action="store_true",
                    help="validate the catalogue only, write nothing")
    ap.add_argument("--check-reproducible", action="store_true",
                    help="assert committed data/ matches what the source "
                         "generates; writes nothing")
    args = ap.parse_args()

    sites = [dict(s) for s in catalog.SITES]
    print(f"Ancient Aliens GIS — building {len(sites)} sites")
    print(f"  base url: {BASE_URL}")

    errs = validate(sites)
    if errs:
        print(f"\n  {len(errs)} validation error(s):")
        for e in errs:
            print(f"    - {e}")
        return 1
    print("  validation: ok")

    if args.check:
        print("  --check: nothing written")
        return 0

    if args.check_reproducible:
        return check_reproducible()

    stats = enrich(sites, offline=args.offline)
    stats["elevations"] = add_elevation(sites, offline=args.offline)
    write_json(os.path.join(ROOT, "data-source", "sites.json"),
               {"count": len(sites), "sites": sites})
    build(sites, stats)

    version = site_version(OUT_DATA)
    moved = stamp_service_worker(version)
    print(f"  cache version   {version}"
          f"{'  (sw.js updated)' if moved else '  (sw.js unchanged)'}")

    print("\n  done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
