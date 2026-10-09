# GeoServer deployment

The conformant half of this project. GitHub Pages publishes the OGC API —
Features *resource tree*; GeoServer publishes the same data as a real
service with full query-parameter support, plus WFS and WMS.

Both are generated from `data-source/catalog.py`, so they cannot drift.

## Quick start

```bash
# from the repository root
python3 scripts/build_data.py          # enrich + emit data/ and data-source/sites.json
python3 scripts/build_geoserver.py     # emit geoserver/layers/ and geoserver/data_dir/
cd geoserver && docker compose up
```

First boot takes two or three minutes while GeoServer installs the
`ogcapi-features` extension. Then:

| Service | URL |
|---|---|
| Admin UI | <http://localhost:8080/geoserver> (`admin` / `change-me-now`) |
| OGC API — Features | <http://localhost:8080/geoserver/ogc/features/v1> |
| Conformance | <http://localhost:8080/geoserver/ogc/features/v1/conformance> |
| Collection | <http://localhost:8080/geoserver/ogc/features/v1/collections/aagis:sites> |
| Items | <http://localhost:8080/geoserver/ogc/features/v1/collections/aagis:sites/items?limit=10> |
| WFS capabilities | <http://localhost:8080/geoserver/wfs?service=WFS&version=2.0.0&request=GetCapabilities> |
| WMS capabilities | <http://localhost:8080/geoserver/wms?service=WMS&version=1.3.0&request=GetCapabilities> |

**Change the admin password** in `docker-compose.yml` before exposing this
anywhere. The default is deliberately conspicuous.

## What you get that Pages cannot give you

```bash
# bbox filtering — the Mediterranean and the Near East
curl "http://localhost:8080/geoserver/ogc/features/v1/collections/aagis:sites/items\
?bbox=20,30,50,45&limit=50&f=application/geo%2Bjson"

# CQL2 filtering — every megalithic site in Europe
curl "http://localhost:8080/geoserver/ogc/features/v1/collections/aagis:sites/items\
?filter-lang=cql2-text&filter=category%3D'megalithic'%20AND%20region%3D'Europe'"

# WFS 2.0.0 with a GML response
curl "http://localhost:8080/geoserver/wfs?service=WFS&version=2.0.0\
&request=GetFeature&typeNames=aagis:sites&count=5"

# WMS rendering with the project's SLD
curl -o map.png "http://localhost:8080/geoserver/wms?service=WMS&version=1.3.0\
&request=GetMap&layers=aagis:sites&styles=ancient-aliens-sites\
&bbox=-25,30,50,72&crs=EPSG:4326&width=1200&height=800&format=image/png\
&transparent=true"
```

## Pointing the browser client at it

In `assets/js/config.js`:

```js
export const APP = {
  // …
  geoserverFeatures: 'http://localhost:8080/geoserver/ogc/features/v1/',
};
```

The client detects the live service and switches its request paths — no
other change. `assets/js/ogc.js` holds both path shapes behind one
interface, and the OGC tab will report `LIVE` instead of `STATIC`.

Cross-origin requests need CORS, which `docker-compose.yml` already enables
(`CORS_ALLOWED_ORIGINS: "*"` — tighten that for anything public).

## What is generated

```
layers/sites.geojson     245 features, EPSG:4326, OGR/GeoJSON-datastore ready
layers/sites.csv         same data with WKT, for a datastore-free import
data_dir/
  global.xml             service-wide settings
  service/wfs/wfs.xml    WFS 2.0.0 enabled, COMPLETE service level
  service/wms/wms.xml    WMS 1.3.0 enabled
  workspaces/aagis/
    workspace.xml        workspace + namespace
    styles/              the SLD, copied from ../sld (single source)
    aagis_sites/
      datastore.xml      GeoJSON datastore pointing at /opt/aagis_layers
      sites/
        featuretype.xml  typed attributes, bbox, abstract, keywords
        layer.xml        default style binding
```

245 rather than 246: the Sea of Tranquility has a null geometry, which is
not a simple feature. It stays in the static tree.

## Styling

`sld/ancient-aliens-sites.sld` is SLD 1.0.0 with three scale-dependent
rules:

| Rule | Scale denominator | Rendering |
|---|---|---|
| `world-dots` | > 1:12,000,000 | 7 px dots, category-coloured |
| `regional-pins` | 1:250,000 – 1:12,000,000 | 14 px ringed pins |
| `local-labelled` | < 1:250,000 | 20 px pins with haloed labels |

Category colours come from an SE `Recode` function over the `category`
attribute, using the same hex values as `assets/css/tokens.css`, so WMS
output and the 3D client agree.

To change the symbology, edit the SLD and re-run
`python3 scripts/build_geoserver.py` — the script copies it into the data
directory rather than keeping a second copy.

## Other deployments

The generated GeoJSON is plain OGR-readable data, so it loads anywhere:

```bash
# PostGIS
ogr2ogr -f PostgreSQL "PG:dbname=gis" geoserver/layers/sites.geojson \
        -nln aagis_sites -lco GEOMETRY_NAME=geom -t_srs EPSG:4326

# GeoPackage
ogr2ogr -f GPKG sites.gpkg geoserver/layers/sites.geojson

# QGIS: open layers/sites.geojson directly
```

pygeoapi is another route to a conformant OGC API — Features service over
the same file, if a Python stack suits better than a Java one.
