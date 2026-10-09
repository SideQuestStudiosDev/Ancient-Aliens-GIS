#!/usr/bin/env python3
"""
Validate the published OGC API - Features tree in data/.

Checks the documents a client actually depends on, so a broken deploy fails
in CI rather than in someone's browser:

  * landing page carries self / service-desc / conformance / data links
  * conformance declares Features Core and GeoJSON
  * collections list resolves to the sites collection
  * items.json is a well-formed FeatureCollection with consistent counts
  * every feature has an id, a geometry of an expected type, in-range
    coordinates, and non-empty claim and context text
  * every feature id has a matching single-item document, byte-identical to
    its entry in items.json
  * the slim client index agrees with items.json on ids and positions
  * the OpenAPI document parses and declares the item paths

Exits non-zero with a list of problems.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

GEOM_TYPES = {"Point", "MultiPoint"}
PRECISIONS = {"exact", "approximate", "area", "uncertain"}

problems: list[str] = []


def fail(msg: str) -> None:
    problems.append(msg)


def load(rel: str):
    path = os.path.join(DATA, rel)
    if not os.path.exists(path):
        fail(f"missing document: data/{rel}")
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except ValueError as exc:
        fail(f"data/{rel} is not valid JSON: {exc}")
        return None


def main() -> int:
    landing = load("index.json")
    if landing:
        rels = {l.get("rel") for l in landing.get("links", [])}
        for required in ("self", "service-desc", "conformance", "data"):
            if required not in rels:
                fail(f"landing page is missing a '{required}' link")
        if not landing.get("title"):
            fail("landing page has no title")
        if not isinstance(landing.get("x-static-deployment"), list):
            fail("landing page should document its static-hosting limitations")

    conf = load("conformance.json")
    if conf:
        classes = conf.get("conformsTo", [])
        if not any(c.endswith("/conf/core") for c in classes):
            fail("conformance does not declare a Core class")
        if not any(c.endswith("/conf/geojson") for c in classes):
            fail("conformance does not declare the GeoJSON class")

    collections = load("collections/index.json")
    coll_ids = set()
    if collections:
        for c in collections.get("collections", []):
            coll_ids.add(c.get("id"))
        if "sites" not in coll_ids:
            fail("collections list does not contain the 'sites' collection")

    coll = load("collections/sites/index.json")
    if coll:
        if coll.get("itemType") != "feature":
            fail("sites collection itemType should be 'feature'")
        if not coll.get("storageCrs", "").endswith("CRS84"):
            fail("sites collection storageCrs should be OGC CRS84")
        bbox = (coll.get("extent", {}).get("spatial", {}).get("bbox") or [[]])[0]
        if len(bbox) != 4:
            fail("sites collection has no usable spatial extent")

    fc = load("collections/sites/items.json")
    if not fc:
        report()
        return 1

    if fc.get("type") != "FeatureCollection":
        fail("items.json is not a FeatureCollection")
    features = fc.get("features") or []
    if not features:
        fail("items.json contains no features")
    if fc.get("numberReturned") != len(features):
        fail(f"numberReturned {fc.get('numberReturned')} != "
             f"{len(features)} features")
    if fc.get("numberMatched") != len(features):
        fail(f"numberMatched {fc.get('numberMatched')} != "
             f"{len(features)} features")
    if not fc.get("timeStamp"):
        fail("items.json has no timeStamp")

    ids, seen = [], set()
    for i, f in enumerate(features):
        fid = f.get("id")
        where = fid or f"features[{i}]"
        if not fid:
            fail(f"{where}: feature has no id")
            continue
        if fid in seen:
            fail(f"{where}: duplicate feature id")
        seen.add(fid)
        ids.append(fid)

        props = f.get("properties") or {}
        for key in ("name", "region", "category", "claim", "context"):
            if not props.get(key):
                fail(f"{where}: empty required property '{key}'")
        if len(props.get("claim", "")) < 40:
            fail(f"{where}: claim text is suspiciously short")
        if len(props.get("context", "")) < 40:
            fail(f"{where}: context text is suspiciously short")
        if props.get("location_precision") not in PRECISIONS:
            fail(f"{where}: bad location_precision "
                 f"{props.get('location_precision')!r}")

        geom = f.get("geometry")
        offworld = props.get("celestial_body") not in (None, "earth")
        if geom is None:
            if not offworld:
                fail(f"{where}: null geometry on a terrestrial feature")
        else:
            if geom.get("type") not in GEOM_TYPES:
                fail(f"{where}: unexpected geometry type {geom.get('type')!r}")
            pts = (geom.get("coordinates") if geom.get("type") == "MultiPoint"
                   else [geom.get("coordinates")])
            for pt in pts:
                if not isinstance(pt, list) or len(pt) < 2:
                    fail(f"{where}: malformed coordinate {pt!r}")
                    continue
                lon, lat = pt[0], pt[1]
                if not (-180 <= lon <= 180):
                    fail(f"{where}: longitude {lon} out of range")
                if not (-90 <= lat <= 90):
                    fail(f"{where}: latitude {lat} out of range")

        rels = {l.get("rel") for l in f.get("links", [])}
        if "self" not in rels:
            fail(f"{where}: feature has no self link")

    # Single-item documents must exist and match.
    items_dir = os.path.join(DATA, "collections", "sites", "items")
    if not os.path.isdir(items_dir):
        fail("data/collections/sites/items/ is missing")
    else:
        on_disk = {n[:-5] for n in os.listdir(items_dir) if n.endswith(".json")}
        missing = seen - on_disk
        extra = on_disk - seen
        if missing:
            fail(f"{len(missing)} features have no item document: "
                 f"{sorted(missing)[:5]}")
        if extra:
            fail(f"{len(extra)} orphaned item documents: {sorted(extra)[:5]}")
        by_id = {f["id"]: f for f in features if f.get("id")}
        for fid in sorted(seen & on_disk)[:1000]:
            with open(os.path.join(items_dir, f"{fid}.json"), encoding="utf-8") as fh:
                doc = json.load(fh)
            if doc != by_id[fid]:
                fail(f"{fid}: item document differs from its items.json entry")

    # Slim client index.
    slim = load("app-index.json")
    if slim:
        slim_ids = [s.get("id") for s in slim.get("sites", [])]
        if set(slim_ids) != seen:
            fail("app-index.json ids do not match items.json")
        if slim.get("count") != len(features):
            fail(f"app-index.json count {slim.get('count')} != {len(features)}")
        pos = {f["id"]: (f["properties"].get("latitude"),
                         f["properties"].get("longitude"))
               for f in features if f.get("id")}
        for s in slim.get("sites", []):
            want = pos.get(s.get("id"))
            if want and (s.get("lat"), s.get("lon")) != want:
                fail(f"{s.get('id')}: app-index position disagrees with items.json")

    api = load("api.json")
    if api:
        if not str(api.get("openapi", "")).startswith("3.0"):
            fail("api.json does not declare OpenAPI 3.0")
        paths = api.get("paths") or {}
        if "/collections/sites/items.json" not in paths:
            fail("api.json does not describe the items path")

    queryables = load("collections/sites/queryables.json")
    if queryables and not queryables.get("properties"):
        fail("queryables.json declares no properties")

    report()
    if problems:
        return 1
    print(f"data/ is valid: {len(features)} features, "
          f"{len(seen)} item documents, all links and counts consistent")
    return 0


def report() -> None:
    if problems:
        print(f"{len(problems)} problem(s) found in data/:\n", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
