/* ==========================================================================
   Ancient Aliens GIS — configuration

   Every service below was reachable without an API key or account at the
   time of writing, and each is an open standard (OGC WMTS) or a documented
   XYZ tile scheme. Attribution strings are mandatory under the providers'
   terms and are rendered at the lower-right of the globe.
   ========================================================================== */

export const APP = {
  name: 'Ancient Aliens GIS',
  version: '1.0.0',
  /** Where the static OGC API - Features tree lives, relative to index.html. */
  dataRoot: 'data/',
  /**
   * Point this at a GeoServer OGC API - Features landing page to switch the
   * app from the static documents to a live service. The feature schema is
   * identical, so nothing else changes. See geoserver/README.md.
   *   e.g. 'https://your-host/geoserver/ogc/features/v1/'
   */
  geoserverFeatures: null,
  /** Optional Cesium ion token. Unlocks Cesium World Terrain + OSM Buildings.
   *  Everything works without it — see TERRAIN below. */
  ionToken: null,
};

/* ----------------------------------------------------------- base layers */
/* kind: 'xyz' | 'wmts'  —  proto is the badge shown in the Layers tab. */

export const BASE_LAYERS = [
  {
    id: 'esri-dark',
    name: 'Esri Dark Gray Canvas',
    meta: 'Dark reference basemap · global · z0–16',
    proto: 'XYZ',
    kind: 'xyz',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}',
    maximumLevel: 16,
    credit: 'Basemap © <a href="https://www.esri.com/" target="_blank" rel="noopener">Esri</a>, HERE, Garmin, © <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors',
    theme: 'dark',
    // Not the default: a reference basemap has no detail at site zoom, so
    // flying into rural Anatolia lands on featureless grey. Excellent for
    // the world view, misleading up close.
  },
  {
    id: 'esri-imagery',
    name: 'Esri World Imagery',
    meta: 'Satellite / aerial mosaic · global · z0–19',
    proto: 'XYZ',
    kind: 'xyz',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    maximumLevel: 19,
    credit: 'Imagery © <a href="https://www.esri.com/" target="_blank" rel="noopener">Esri</a>, Maxar, Earthstar Geographics and the GIS User Community',
    theme: 'imagery',
    // The default. It has real detail at every zoom, which a portal built
    // for flying into archaeological sites needs, and it gives the
    // Google-Earth-like opening view the brief asked for.
    default: true,
  },
  {
    id: 's2cloudless',
    name: 'Sentinel-2 cloudless 2025',
    meta: 'Copernicus Sentinel-2 · 10 m · cloud-free composite',
    proto: 'WMTS',
    kind: 'wmts',
    url: 'https://tiles.maps.eox.at/wmts',
    layer: 's2cloudless-2025_3857',
    style: 'default',
    format: 'image/jpeg',
    tileMatrixSetID: 'GoogleMapsCompatible',
    maximumLevel: 15,
    rest: 'https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-2025_3857/default/GoogleMapsCompatible/{TileMatrix}/{TileRow}/{TileCol}.jpg',
    credit: 'Sentinel-2 cloudless 2025 by <a href="https://cloudless.eox.at/" target="_blank" rel="noopener">EOX</a> (contains modified Copernicus Sentinel data 2025) — CC BY-NC-SA 4.0',
    note: 'Non-commercial licence',
    theme: 'imagery',
  },
  {
    id: 'gibs-viirs',
    name: 'NASA VIIRS True Colour',
    meta: 'Suomi NPP · 250 m · yesterday’s pass',
    proto: 'WMTS',
    kind: 'wmts',
    url: 'https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/{Layer}/default/{Time}/{TileMatrixSet}/{TileMatrix}/{TileRow}/{TileCol}.jpg',
    layer: 'VIIRS_SNPP_CorrectedReflectance_TrueColor',
    tileMatrixSetID: 'GoogleMapsCompatible_Level9',
    maximumLevel: 8,
    timeOffsetDays: -2,
    credit: 'Imagery courtesy <a href="https://worldview.earthdata.nasa.gov/" target="_blank" rel="noopener">NASA EOSDIS GIBS</a>',
    theme: 'imagery',
  },
  {
    id: 'gibs-bluemarble',
    name: 'NASA Blue Marble',
    meta: 'Shaded relief + bathymetry · 500 m',
    proto: 'WMTS',
    kind: 'wmts',
    rest: 'https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/BlueMarble_ShadedRelief_Bathymetry/default/GoogleMapsCompatible_Level8/{TileMatrix}/{TileRow}/{TileCol}.jpeg',
    layer: 'BlueMarble_ShadedRelief_Bathymetry',
    tileMatrixSetID: 'GoogleMapsCompatible_Level8',
    maximumLevel: 7,
    credit: 'Imagery courtesy <a href="https://worldview.earthdata.nasa.gov/" target="_blank" rel="noopener">NASA EOSDIS GIBS</a>',
    theme: 'imagery',
  },
  {
    id: 'osm',
    name: 'OpenStreetMap Standard',
    meta: 'Community street map · global · z0–19',
    proto: 'XYZ',
    kind: 'xyz',
    url: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
    maximumLevel: 19,
    credit: '© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors',
    theme: 'light',
  },
  {
    id: 'eox-terrain',
    name: 'EOX Terrain Light',
    meta: 'Hillshade + land cover · OGC WMTS',
    proto: 'WMTS',
    kind: 'wmts',
    rest: 'https://tiles.maps.eox.at/wmts/1.0.0/terrain-light_3857/default/GoogleMapsCompatible/{TileMatrix}/{TileRow}/{TileCol}.jpg',
    layer: 'terrain-light_3857',
    tileMatrixSetID: 'GoogleMapsCompatible',
    maximumLevel: 13,
    credit: 'Terrain Light by <a href="https://maps.eox.at/" target="_blank" rel="noopener">EOX</a> · © OpenStreetMap contributors · <a href="https://www.naturalearthdata.com/" target="_blank" rel="noopener">Natural Earth</a>',
    theme: 'light',
  },
  {
    id: 'esri-relief',
    name: 'Esri World Shaded Relief',
    meta: 'Hypsometric hillshade · global · z0–13',
    proto: 'XYZ',
    kind: 'xyz',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Shaded_Relief/MapServer/tile/{z}/{y}/{x}',
    maximumLevel: 13,
    credit: 'Relief © <a href="https://www.esri.com/" target="_blank" rel="noopener">Esri</a>',
    theme: 'light',
  },
  {
    id: 'opentopomap',
    name: 'OpenTopoMap',
    meta: 'Topographic · contours + relief · z0–16',
    proto: 'XYZ',
    kind: 'xyz',
    url: 'https://tile.opentopomap.org/{z}/{x}/{y}.png',
    maximumLevel: 16,
    credit: 'Map data © <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors · <a href="https://opentopomap.org/" target="_blank" rel="noopener">OpenTopoMap</a> (CC-BY-SA)',
    theme: 'light',
  },
];

/* -------------------------------------------------------------- overlays */

export const OVERLAYS = [
  {
    id: 'labels',
    name: 'Place names & borders',
    meta: 'Esri Dark Gray reference layer · XYZ',
    proto: 'XYZ',
    kind: 'xyz',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}',
    maximumLevel: 16,
    credit: 'Labels © <a href="https://www.esri.com/" target="_blank" rel="noopener">Esri</a>, HERE, Garmin, © <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors',
    defaultOn: true,
    alpha: 0.9,
  },
  {
    id: 'eox-overlay',
    name: 'Coastline & graticule',
    meta: 'EOX overlay · OGC WMTS',
    proto: 'WMTS',
    kind: 'wmts',
    rest: 'https://tiles.maps.eox.at/wmts/1.0.0/overlay_bright_3857/default/GoogleMapsCompatible/{TileMatrix}/{TileRow}/{TileCol}.png',
    layer: 'overlay_bright_3857',
    tileMatrixSetID: 'GoogleMapsCompatible',
    maximumLevel: 13,
    credit: 'Overlay by <a href="https://maps.eox.at/" target="_blank" rel="noopener">EOX</a> · © OpenStreetMap contributors',
    defaultOn: false,
    alpha: 0.75,
  },
  {
    id: 'night',
    name: 'Night lights',
    meta: 'VIIRS Black Marble · OGC WMTS',
    proto: 'WMTS',
    kind: 'wmts',
    rest: 'https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_Black_Marble/default/GoogleMapsCompatible_Level8/{TileMatrix}/{TileRow}/{TileCol}.png',
    layer: 'VIIRS_Black_Marble',
    tileMatrixSetID: 'GoogleMapsCompatible_Level8',
    maximumLevel: 7,
    credit: 'Black Marble courtesy <a href="https://worldview.earthdata.nasa.gov/" target="_blank" rel="noopener">NASA EOSDIS GIBS</a>',
    defaultOn: false,
    alpha: 0.6,
  },
];

/* --------------------------------------------------------------- terrain */

export const TERRAIN = {
  /** Keyless global quantised elevation. Verified reachable without a token. */
  arcgis: 'https://elevation3d.arcgis.com/arcgis/rest/services/WorldElevation3D/Terrain3D/ImageServer',
  credit: 'Elevation © <a href="https://www.esri.com/" target="_blank" rel="noopener">Esri</a> and its data contributors',
};

/* ---------------------------------------------------------------- camera */

export const CAMERA = {
  /** Opening view: the Old World centred, enough tilt to read the terrain. */
  home: { lon: 18, lat: 22, height: 18_000_000, heading: 0, pitch: -89 },
  flyDuration: 2.6,
  minZoom: 120,
  maxZoom: 40_000_000,
};

/** Pin colours, resolved from the CSS custom properties in tokens.css so the
 *  globe and the UI can never drift apart. */
export function categoryColor(token, fallback = '#7dd3e8') {
  const v = getComputedStyle(document.documentElement)
    .getPropertyValue(token).trim();
  return v || fallback;
}
