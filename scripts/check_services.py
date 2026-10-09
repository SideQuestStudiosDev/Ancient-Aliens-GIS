#!/usr/bin/env python3
"""
Verify that every external map service the app depends on still serves real
data without an API key.

Why this is not just a 200 check
--------------------------------
A provider that has begun requiring a key may still answer 200 — with an
identical "API KEY REQUIRED" watermark tile at every coordinate. That is how
the CARTO basemaps this project originally shipped with were caught. So the
test fetches three tiles from widely separated places and asserts the bytes
differ. Real imagery varies; a placeholder does not.

Keep the table below in step with assets/js/config.js. This script is
deliberately dependency-free and does not parse JavaScript.

  python3 scripts/check_services.py        # exits non-zero if anything fails
"""
from __future__ import annotations

import hashlib
import sys
import urllib.error
import urllib.request

UA = ("AncientAliensGIS/1.0 "
      "(+https://github.com/SideQuestStudiosDev/Ancient-Aliens-GIS)")

# z/x/y over western Europe, east Asia and the mid-Pacific.
SAMPLES = [(4, 8, 5), (4, 13, 6), (4, 1, 7)]

BASE_LAYERS = {
    "esri Dark Gray Canvas":
        "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/"
        "World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}",
    "esri World Imagery":
        "https://server.arcgisonline.com/ArcGIS/rest/services/"
        "World_Imagery/MapServer/tile/{z}/{y}/{x}",
    "eox s2cloudless-2025":
        "https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-2025_3857/default/"
        "GoogleMapsCompatible/{TileMatrix}/{TileRow}/{TileCol}.jpg",
    "gibs VIIRS true colour":
        "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/"
        "VIIRS_SNPP_CorrectedReflectance_TrueColor/default/2026-01-15/"
        "GoogleMapsCompatible_Level9/{TileMatrix}/{TileRow}/{TileCol}.jpg",
    "gibs Blue Marble":
        "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/"
        "BlueMarble_ShadedRelief_Bathymetry/default/"
        "GoogleMapsCompatible_Level8/{TileMatrix}/{TileRow}/{TileCol}.jpeg",
    "osm standard":
        "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
    "eox terrain-light":
        "https://tiles.maps.eox.at/wmts/1.0.0/terrain-light_3857/default/"
        "GoogleMapsCompatible/{TileMatrix}/{TileRow}/{TileCol}.jpg",
    "esri World Shaded Relief":
        "https://server.arcgisonline.com/ArcGIS/rest/services/"
        "World_Shaded_Relief/MapServer/tile/{z}/{y}/{x}",
    "opentopomap":
        "https://tile.opentopomap.org/{z}/{x}/{y}.png",
}

OVERLAYS = {
    "esri Dark Gray Reference":
        "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/"
        "World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}",
    "eox overlay_bright":
        "https://tiles.maps.eox.at/wmts/1.0.0/overlay_bright_3857/default/"
        "GoogleMapsCompatible/{TileMatrix}/{TileRow}/{TileCol}.png",
    "gibs Black Marble":
        "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/"
        "VIIRS_Black_Marble/default/GoogleMapsCompatible_Level8/"
        "{TileMatrix}/{TileRow}/{TileCol}.png",
}

TERRAIN = ("esri Terrain3D (LERC elevation)",
           "https://elevation3d.arcgis.com/arcgis/rest/services/"
           "WorldElevation3D/Terrain3D/ImageServer/tile/{z}/{y}/{x}")

CESIUM_CDN = ("CesiumJS 1.146.0",
              "https://cdn.jsdelivr.net/npm/cesium@1.146.0/Build/Cesium/Cesium.js")


def get(url: str, timeout: int = 30):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status, resp.headers.get("content-type", ""), resp.read()


def check_tiles(name: str, template: str) -> bool:
    digests, sizes, types = [], [], set()
    for z, x, y in SAMPLES:
        url = template.format(z=z, x=x, y=y,
                              TileMatrix=z, TileCol=x, TileRow=y)
        try:
            status, ctype, body = get(url)
        except urllib.error.HTTPError as exc:
            print(f"  FAIL {name:30s} HTTP {exc.code}")
            return False
        except Exception as exc:                       # noqa: BLE001
            print(f"  FAIL {name:30s} {type(exc).__name__}: {exc}")
            return False
        if status != 200 or not ctype.startswith("image/"):
            print(f"  FAIL {name:30s} status {status}, type {ctype!r}")
            return False
        digests.append(hashlib.sha256(body).hexdigest())
        sizes.append(len(body))
        types.add(ctype)

    distinct = len(set(digests))
    if distinct != len(SAMPLES):
        print(f"  FAIL {name:30s} {distinct}/{len(SAMPLES)} distinct tiles — "
              f"identical bytes everywhere suggests a placeholder or a "
              f"watermark, i.e. this service now needs a key")
        return False
    print(f"  ok   {name:30s} {'/'.join(str(s) for s in sizes):>22s} B  "
          f"{','.join(sorted(types))}")
    return True


def check_terrain() -> bool:
    name, template = TERRAIN
    sizes = []
    for z, x, y in SAMPLES:
        try:
            status, _, body = get(template.format(z=z, x=x, y=y))
        except Exception as exc:                       # noqa: BLE001
            print(f"  FAIL {name:30s} {type(exc).__name__}: {exc}")
            return False
        if status != 200 or len(body) < 1000:
            print(f"  FAIL {name:30s} status {status}, {len(body)} B")
            return False
        sizes.append(len(body))
    print(f"  ok   {name:30s} {'/'.join(str(s) for s in sizes):>22s} B")
    return True


def check_cdn() -> bool:
    """Confirm the pinned CesiumJS build is still on the CDN.

    A plain GET reading only the first few KiB. HEAD is no good here —
    jsdelivr serves chunked and omits content-length on HEAD — and ranged
    requests do not survive every intermediary.
    """
    name, url = CESIUM_CDN
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=40) as resp:
            head = resp.read(4096)
            total = int(resp.headers.get("content-length") or 0)
            if resp.status != 200 or len(head) < 512:
                print(f"  FAIL {name:30s} status {resp.status}, "
                      f"{len(head)} B read")
                return False
            if b"Cesium" not in head:
                print(f"  FAIL {name:30s} payload is not the Cesium bundle")
                return False
            if total and total < 1_000_000:
                print(f"  FAIL {name:30s} only {total} B — truncated build?")
                return False
    except Exception as exc:                           # noqa: BLE001
        print(f"  FAIL {name:30s} {type(exc).__name__}: {exc}")
        return False
    size = f"{total / 1024 / 1024:.1f} MiB" if total else "reachable"
    print(f"  ok   {name:30s} {size}")
    return True


def main() -> int:
    failures = []

    print("base layers")
    for name, tpl in BASE_LAYERS.items():
        if not check_tiles(name, tpl):
            failures.append(name)

    print("\noverlays")
    for name, tpl in OVERLAYS.items():
        if not check_tiles(name, tpl):
            failures.append(name)

    print("\nterrain and runtime")
    if not check_terrain():
        failures.append(TERRAIN[0])
    if not check_cdn():
        failures.append(CESIUM_CDN[0])

    total = len(BASE_LAYERS) + len(OVERLAYS) + 2
    print(f"\n{total - len(failures)}/{total} services healthy")
    if failures:
        print("failing: " + ", ".join(failures))
        print("\nFix assets/js/config.js (and this table) before deploying.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
