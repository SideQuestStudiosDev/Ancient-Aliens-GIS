#!/usr/bin/env python3
"""
Generate a GeoServer data directory that publishes the same catalogue the
static tree does.

  python3 scripts/build_data.py          # first: enrich + build data-source/sites.json
  python3 scripts/build_geoserver.py     # then: emit geoserver/data_dir + layers
  cd geoserver && docker compose up

Why both exist
--------------
GitHub Pages serves static files, so it can publish an OGC API - Features
*resource tree* but cannot honour the Core parameter requirements (bbox,
limit, datetime, filter). GeoServer can. This script derives the GeoServer
side from the identical source catalogue so the two never diverge: same ids,
same property names, same CRS.

Output
------
geoserver/layers/sites.geojson      the feature data (OGR-readable)
geoserver/layers/sites.csv          same, for a quick import without OGR
geoserver/data_dir/                 workspace, datastore, featuretype, style
geoserver/README.md is written separately and documents the endpoints.

Only the Python standard library is used: no geopandas, no OGR bindings.
GeoServer reads GeoJSON directly through its OGR or GeoJSON datastore, and
the generated catalogue XML wires it up.
"""
from __future__ import annotations

import json
import os
import sys
import csv
from datetime import datetime, timezone
from xml.sax.saxutils import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data-source", "sites.json")
GS = os.path.join(ROOT, "geoserver")
LAYERS = os.path.join(GS, "layers")
DD = os.path.join(GS, "data_dir")

WS = "aagis"
NS_URI = "https://sidequeststudiosdev.github.io/Ancient-Aliens-GIS"
STORE = "aagis_sites"
LAYER = "sites"
STYLE = "ancient-aliens-sites"

# Shapefile-safe field names (<=10 chars) are kept as aliases in the CSV so an
# operator importing via shapefile does not silently lose column meaning.
FIELDS = [
    # (geojson property,        csv/shp name, xml type,           shp alias)
    ("id",                      "site_id",    "java.lang.String", "site_id"),
    ("name",                    "name",       "java.lang.String", "name"),
    ("subtitle",                "subtitle",   "java.lang.String", "subtitle"),
    ("country",                 "country",    "java.lang.String", "country"),
    ("region",                  "region",     "java.lang.String", "region"),
    ("category",                "category",   "java.lang.String", "category"),
    ("category_label",          "cat_label",  "java.lang.String", "cat_label"),
    ("location_precision",      "precision",  "java.lang.String", "precision"),
    ("coordinate_source",       "coord_src",  "java.lang.String", "coord_src"),
    ("celestial_body",          "body",       "java.lang.String", "body"),
    ("latitude",                "latitude",   "java.lang.Double", "latitude"),
    ("longitude",               "longitude",  "java.lang.Double", "longitude"),
    ("radius_km",               "radius_km",  "java.lang.Double", "radius_km"),
    ("wikipedia_title",         "wiki_title", "java.lang.String", "wiki_title"),
    ("wikipedia_url",           "wiki_url",   "java.lang.String", "wiki_url"),
    ("wikidata_id",             "wikidata",   "java.lang.String", "wikidata"),
    ("claim",                   "claim",      "java.lang.String", "claim"),
    ("context",                 "context",    "java.lang.String", "context"),
    ("summary",                 "summary",    "java.lang.String", "summary"),
    ("tags",                    "tags",       "java.lang.String", "tags"),
]


def mkdirp(p):
    os.makedirs(p, exist_ok=True)


def write(path, text):
    mkdirp(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text if text.endswith("\n") else text + "\n")
    return len(text)


def load_catalogue():
    if not os.path.exists(SRC):
        sys.exit(f"missing {SRC} — run scripts/build_data.py first")
    with open(SRC, encoding="utf-8") as fh:
        return json.load(fh)["sites"]


def feature_of(site, cat_labels):
    """Flatten one site to a GeoServer-friendly Feature.

    GeoServer's simple-feature model has no array type, so `tags` is joined.
    Off-world entries carry a null geometry, which WFS represents as an
    absent geometry property; they are excluded from the published layer and
    remain available in the static tree only.
    """
    props = {
        "id": site["id"],
        "name": site["name"],
        "subtitle": site["subtitle"],
        "country": site["country"],
        "region": site["region"],
        "category": site["category"],
        "category_label": cat_labels.get(site["category"], site["category"]),
        "location_precision": site["precision"],
        "coordinate_source": site.get("coord_source", "authored"),
        "celestial_body": "moon" if site["offworld"] else "earth",
        "latitude": round(site["lat"], 6),
        "longitude": round(site["lon"], 6),
        "radius_km": float(site["radius_km"] or 0),
        "wikipedia_title": site.get("wikipedia_title", ""),
        "wikipedia_url": site.get("wikipedia_url", ""),
        "wikidata_id": site.get("wikidata", ""),
        "claim": site["claim"],
        "context": site["context"],
        "summary": site.get("summary", ""),
        "tags": "; ".join(site["tags"]),
    }
    if site["geometry"] == "multipoint" and site["points"]:
        geom = {"type": "MultiPoint",
                "coordinates": [[round(lon, 6), round(lat, 6)]
                                for lat, lon in site["points"]]}
    else:
        geom = {"type": "Point",
                "coordinates": [round(site["lon"], 6), round(site["lat"], 6)]}
    return {"type": "Feature", "id": site["id"], "geometry": geom,
            "properties": props}


# --------------------------------------------------------------------------- #
# GeoServer catalogue XML
# --------------------------------------------------------------------------- #

def workspace_xml():
    return f"""<workspace>
  <id>ws_{WS}</id>
  <name>{WS}</name>
  <isolated>false</isolated>
</workspace>"""


def namespace_xml():
    return f"""<namespace>
  <id>ns_{WS}</id>
  <prefix>{WS}</prefix>
  <uri>{escape(NS_URI)}</uri>
  <isolated>false</isolated>
</namespace>"""


def datastore_xml():
    return f"""<dataStore>
  <id>ds_{STORE}</id>
  <name>{STORE}</name>
  <description>Ancient Aliens GIS site catalogue (GeoJSON, EPSG:4326)</description>
  <type>GeoJSON</type>
  <enabled>true</enabled>
  <workspace>
    <id>ws_{WS}</id>
  </workspace>
  <connectionParameters>
    <entry key="namespace">{escape(NS_URI)}</entry>
    <entry key="file">file:/opt/aagis_layers/sites.geojson</entry>
  </connectionParameters>
  <__default>true</__default>
  <dateCreated>{datetime.now(timezone.utc).isoformat()}</dateCreated>
</dataStore>"""


def featuretype_xml(bbox, count):
    attrs = "\n".join(f"""    <attribute>
      <name>{name}</name>
      <minOccurs>0</minOccurs>
      <maxOccurs>1</maxOccurs>
      <nillable>true</nillable>
      <binding>{binding}</binding>
    </attribute>""" for _, name, binding, _ in FIELDS)
    minx, miny, maxx, maxy = bbox
    return f"""<featureType>
  <id>ft_{LAYER}</id>
  <name>{LAYER}</name>
  <nativeName>sites</nativeName>
  <title>Ancient Aliens locations</title>
  <abstract>{count} locations referenced in the television series Ancient
Aliens. Each feature carries the claim made on screen (claim), a summary of
the encyclopaedic record (summary, from Wikipedia under CC BY-SA 4.0), and
context noting where the two diverge (context). The location_precision
property states whether a position is a surveyed monument, an approximation,
a region centroid, or an unresolved reference.</abstract>
  <keywords>
    <string>ancient aliens</string>
    <string>archaeology</string>
    <string>archaeoastronomy</string>
    <string>features</string>
    <string>OGC API</string>
  </keywords>
  <nativeCRS>EPSG:4326</nativeCRS>
  <srs>EPSG:4326</srs>
  <nativeBoundingBox>
    <minx>{minx}</minx><maxx>{maxx}</maxx>
    <miny>{miny}</miny><maxy>{maxy}</maxy>
    <crs>EPSG:4326</crs>
  </nativeBoundingBox>
  <latLonBoundingBox>
    <minx>{minx}</minx><maxx>{maxx}</maxx>
    <miny>{miny}</miny><maxy>{maxy}</maxy>
    <crs>GEOGCS["WGS84(DD)", DATUM["WGS84", SPHEROID["WGS84", 6378137.0, 298.257223563]], PRIMEM["Greenwich", 0.0], UNIT["degree", 0.017453292519943295], AXIS["Geodetic longitude", EAST], AXIS["Geodetic latitude", NORTH]]</crs>
  </latLonBoundingBox>
  <projectionPolicy>FORCE_DECLARED</projectionPolicy>
  <enabled>true</enabled>
  <metadata>
    <entry key="cachingEnabled">false</entry>
  </metadata>
  <store class="dataStore">
    <id>ds_{STORE}</id>
  </store>
  <serviceConfiguration>false</serviceConfiguration>
  <attributes>
{attrs}
  </attributes>
</featureType>"""


def layer_xml():
    return f"""<layer>
  <id>l_{LAYER}</id>
  <name>{LAYER}</name>
  <type>VECTOR</type>
  <defaultStyle>
    <id>style_{STYLE}</id>
    <name>{STYLE}</name>
  </defaultStyle>
  <resource class="featureType">
    <id>ft_{LAYER}</id>
  </resource>
  <enabled>true</enabled>
  <advertised>true</advertised>
  <queryable>true</queryable>
  <opaque>false</opaque>
</layer>"""


def style_xml():
    return f"""<style>
  <id>style_{STYLE}</id>
  <name>{STYLE}</name>
  <workspace>
    <id>ws_{WS}</id>
  </workspace>
  <format>sld</format>
  <languageVersion>
    <version>1.0.0</version>
  </languageVersion>
  <filename>{STYLE}.sld</filename>
</style>"""


def global_xml():
    return """<global>
  <settings>
    <charset>UTF-8</charset>
    <numDecimals>8</numDecimals>
    <verbose>false</verbose>
    <verboseExceptions>false</verboseExceptions>
    <localWorkspaceIncludesPrefix>false</localWorkspaceIncludesPrefix>
  </settings>
  <jai>
    <allowInterpolation>false</allowInterpolation>
    <memoryCapacity>0.5</memoryCapacity>
  </jai>
  <featureTypeCacheSize>100</featureTypeCacheSize>
  <globalServices>true</globalServices>
  <xmlPostRequestLogBufferSize>1024</xmlPostRequestLogBufferSize>
</global>"""


def wfs_xml():
    return """<wfs>
  <id>wfs</id>
  <enabled>true</enabled>
  <name>WFS</name>
  <title>Ancient Aliens GIS — Web Feature Service</title>
  <abstract>OGC WFS 2.0.0 access to the Ancient Aliens site catalogue.</abstract>
  <keywords>
    <string>WFS</string><string>ancient aliens</string><string>archaeology</string>
  </keywords>
  <versions>
    <org.geotools.util.Version><version>1.0.0</version></org.geotools.util.Version>
    <org.geotools.util.Version><version>1.1.0</version></org.geotools.util.Version>
    <org.geotools.util.Version><version>2.0.0</version></org.geotools.util.Version>
  </versions>
  <citeCompliant>false</citeCompliant>
  <schemaBaseURL>http://schemas.opengis.net</schemaBaseURL>
  <gml>
    <entry>
      <version>V_20</version>
      <gml><srsNameStyle>URN2</srsNameStyle><overrideGMLAttributes>false</overrideGMLAttributes></gml>
    </entry>
  </gml>
  <serviceLevel>COMPLETE</serviceLevel>
  <maxFeatures>1000</maxFeatures>
  <featureBounding>true</featureBounding>
  <encodeFeatureMember>false</encodeFeatureMember>
  <hitsIgnoreMaxFeatures>true</hitsIgnoreMaxFeatures>
</wfs>"""


def wms_xml():
    return """<wms>
  <id>wms</id>
  <enabled>true</enabled>
  <name>WMS</name>
  <title>Ancient Aliens GIS — Web Map Service</title>
  <abstract>OGC WMS 1.3.0 rendering of the Ancient Aliens site catalogue, styled
to match the 3D web client.</abstract>
  <versions>
    <org.geotools.util.Version><version>1.1.1</version></org.geotools.util.Version>
    <org.geotools.util.Version><version>1.3.0</version></org.geotools.util.Version>
  </versions>
  <citeCompliant>false</citeCompliant>
  <schemaBaseURL>http://schemas.opengis.net</schemaBaseURL>
  <watermark><enabled>false</enabled><position>BOT_RIGHT</position><transparency>100</transparency></watermark>
  <interpolation>Nearest</interpolation>
  <getFeatureInfoMimeTypeCheckingEnabled>false</getFeatureInfoMimeTypeCheckingEnabled>
  <maxBuffer>25</maxBuffer>
  <maxRequestMemory>65536</maxRequestMemory>
  <maxRenderingTime>60</maxRenderingTime>
  <maxRequestedDimensionValues>100</maxRequestedDimensionValues>
</wms>"""


# --------------------------------------------------------------------------- #

def main():
    sites = load_catalogue()
    cat_labels = {}
    sys.path.insert(0, os.path.join(ROOT, "data-source"))
    import catalog
    cat_labels = {k: v[0] for k, v in catalog.CATEGORIES.items()}

    terrestrial = [s for s in sites if not s["offworld"]]
    features = [feature_of(s, cat_labels) for s in terrestrial]

    lons, lats = [], []
    for f in features:
        pts = (f["geometry"]["coordinates"]
               if f["geometry"]["type"] == "MultiPoint"
               else [f["geometry"]["coordinates"]])
        lons += [p[0] for p in pts]
        lats += [p[1] for p in pts]
    bbox = (round(min(lons), 6), round(min(lats), 6),
            round(max(lons), 6), round(max(lats), 6))

    mkdirp(LAYERS)
    fc = {"type": "FeatureCollection",
          "name": "sites",
          "crs": {"type": "name",
                  "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
          "bbox": list(bbox),
          "features": features}
    n = write(os.path.join(LAYERS, "sites.geojson"),
              json.dumps(fc, ensure_ascii=False, indent=1))

    # CSV fallback, for importing without a GeoJSON/OGR datastore.
    csv_path = os.path.join(LAYERS, "sites.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow([shp for _, shp, _, _ in FIELDS] + ["wkt"])
        for f in features:
            p = f["properties"]
            geom = f["geometry"]
            if geom["type"] == "MultiPoint":
                wkt = ("MULTIPOINT ("
                       + ", ".join(f"({x} {y})" for x, y in geom["coordinates"])
                       + ")")
            else:
                x, y = geom["coordinates"]
                wkt = f"POINT ({x} {y})"
            w.writerow([p.get(key, "") for key, _, _, _ in FIELDS] + [wkt])

    # Catalogue XML
    write(os.path.join(DD, "global.xml"), global_xml())
    write(os.path.join(DD, "workspaces", "default.xml"),
          f"<workspace>\n  <id>ws_{WS}</id>\n</workspace>")
    write(os.path.join(DD, "workspaces", WS, "workspace.xml"), workspace_xml())
    write(os.path.join(DD, "workspaces", WS, "namespace.xml"), namespace_xml())
    write(os.path.join(DD, "workspaces", WS, STORE, "datastore.xml"),
          datastore_xml())
    write(os.path.join(DD, "workspaces", WS, STORE, LAYER, "featuretype.xml"),
          featuretype_xml(bbox, len(features)))
    write(os.path.join(DD, "workspaces", WS, STORE, LAYER, "layer.xml"),
          layer_xml())
    write(os.path.join(DD, "workspaces", WS, "styles", f"{STYLE}.xml"),
          style_xml())
    write(os.path.join(DD, "service", "wfs", "wfs.xml"), wfs_xml())
    write(os.path.join(DD, "service", "wms", "wms.xml"), wms_xml())

    # The SLD is the single source of symbology; copy it rather than fork it.
    sld_src = os.path.join(GS, "sld", f"{STYLE}.sld")
    with open(sld_src, encoding="utf-8") as fh:
        sld = fh.read()
    write(os.path.join(DD, "workspaces", WS, "styles", f"{STYLE}.sld"), sld)

    print(f"GeoServer data directory written")
    print(f"  layers/sites.geojson   {n / 1024:.1f} KiB, {len(features)} features")
    print(f"  layers/sites.csv       {os.path.getsize(csv_path) / 1024:.1f} KiB")
    print(f"  bbox                   {bbox}")
    print(f"  workspace              {WS}  store {STORE}  layer {LAYER}")
    print(f"  style                  {STYLE} (SLD 1.0.0)")
    skipped = len(sites) - len(terrestrial)
    if skipped:
        print(f"  note: {skipped} off-world entr"
              f"{'y' if skipped == 1 else 'ies'} excluded "
              f"(null geometry is not a simple feature)")
    print("\n  next:  cd geoserver && docker compose up")
    return 0


if __name__ == "__main__":
    sys.exit(main())
