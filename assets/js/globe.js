/* ==========================================================================
   Cesium globe: viewer construction, OGC imagery/terrain plumbing, site
   markers, picking and camera choreography.

   Deliberate choices
   ------------------
   * No Cesium ion dependency. `baseLayer: false` plus an explicit terrain
     provider means the viewer never calls ion, so the app works with no
     account and no token. Setting APP.ionToken additionally unlocks Cesium
     World Terrain and OSM Buildings, but nothing requires it.
   * `requestRenderMode` is on. The scene renders when something changes
     rather than at 60 fps, which is the single biggest battery and thermal
     win on phones. Every programmatic change below calls requestRender().
   ========================================================================== */

import { APP, BASE_LAYERS, OVERLAYS, TERRAIN, CAMERA, categoryColor }
  from './config.js';
import { isCoarsePointer, prefersReducedMotion } from './util.js';

const C = () => window.Cesium;

export const globe = {
  viewer: null,
  scene: null,
  dataSource: null,
  layers: { base: null, baseId: null, overlays: new Map() },
  credits: new Set(),
  terrainMode: 'ellipsoid',
  /** Settles once the terrain provider is attached, successfully or not.
   *  Anything that samples elevation must await this: terrain loads
   *  after the viewer is interactive, and a sample taken before it
   *  lands silently reports sea level. */
  terrainReady: Promise.resolve(),
  pendingFlight: null,       // site id of the in-flight camera move
  entities: new Map(),       // site id -> billboard entity
  areas: new Map(),          // site id -> ellipse entity
  selectionRing: null,
  selectedId: null,        // site id the user is looking at, if any
  siteById: new Map(),     // site id -> catalogue record
  targetMode: '3D',        // mode a morph is heading for
};

const handlers = { pick: null, hover: null, camera: null, credit: null,
                   tiles: null };

/* ------------------------------------------------------------------ viewer */

export async function createGlobe(container, { onPick, onHover, onCamera,
                                               onCredits, onTiles } = {}) {
  const Cesium = C();
  if (!Cesium) throw new Error('CesiumJS failed to load from the CDN.');

  if (APP.ionToken) Cesium.Ion.defaultAccessToken = APP.ionToken;

  const coarse = isCoarsePointer();

  const viewer = new Cesium.Viewer(container, {
    baseLayer: false,                 // nothing from ion
    baseLayerPicker: false,
    geocoder: false,
    homeButton: false,
    sceneModePicker: false,
    navigationHelpButton: false,
    animation: false,
    timeline: false,
    fullscreenButton: false,
    vrButton: false,
    infoBox: false,                   // we render our own dossier
    selectionIndicator: false,
    shouldAnimate: false,
    requestRenderMode: true,
    maximumRenderTimeChange: Infinity,
    terrainProvider: new Cesium.EllipsoidTerrainProvider(),
    msaaSamples: coarse ? 1 : 4,
    contextOptions: {
      webgl: { alpha: false, powerPreference: 'high-performance',
               failIfMajorPerformanceCaveat: false },
    },
  });

  globe.viewer = viewer;
  globe.scene = viewer.scene;

  const { scene } = viewer;
  // Tiles that have not streamed in yet show this. Near-black would be
  // indistinguishable from empty space and makes a loading globe look
  // broken; a mid-slate reads as 'not here yet'.
  scene.globe.baseColor = Cesium.Color.fromCssColorString('#101d28');
  scene.backgroundColor = Cesium.Color.fromCssColorString('#04070d');
  scene.globe.showGroundAtmosphere = true;
  scene.globe.enableLighting = false;
  scene.globe.depthTestAgainstTerrain = false;
  scene.highDynamicRange = false;
  scene.fog.enabled = true;
  scene.fog.density = 0.00012;

  // Atmosphere grading.
  //
  // The GROUND atmosphere composites over the imagery itself, so a large
  // hue rotation here does not tint the halo — it repaints the whole planet.
  // An earlier -0.4 shift turned a dark-grey basemap olive. Desaturate and
  // darken it instead, and leave the hue alone.
  scene.globe.atmosphereHueShift = 0.0;
  scene.globe.atmosphereSaturationShift = -0.7;
  scene.globe.atmosphereBrightnessShift = -0.35;
  if ('atmosphereLightIntensity' in scene.globe) {
    scene.globe.atmosphereLightIntensity = 5.0;   // default 10
  }

  // The SKY atmosphere is the limb glow around the silhouette, and nothing
  // else. That is where the teal belongs.
  scene.skyAtmosphere.hueShift = -0.08;
  scene.skyAtmosphere.saturationShift = 0.35;
  scene.skyAtmosphere.brightnessShift = -0.30;
  // Cesium's default is 2.0. Going below it multiplies the number of tiles
  // requested for the same view, which on a phone or a slow link means a
  // long stretch of blurry upsampled parent tiles before anything sharp
  // appears. 2.0 desktop / 3.0 touch is the better trade for a portal
  // people fly around rather than stare at.
  scene.globe.maximumScreenSpaceError = coarse ? 3.0 : 2.0;
  scene.globe.tileCacheSize = coarse ? 120 : 300;
  scene.screenSpaceCameraController.minimumZoomDistance = CAMERA.minZoom;
  scene.screenSpaceCameraController.maximumZoomDistance = CAMERA.maxZoom;
  scene.screenSpaceCameraController.enableCollisionDetection = true;

  // Cap the device pixel ratio on phones: a 3x buffer on a 6-inch screen
  // costs a great deal of GPU for no visible gain.
  viewer.resolutionScale = Math.min(window.devicePixelRatio || 1,
                                    coarse ? 1.5 : 2);
  viewer.useBrowserRecommendedResolution = false;

  // Starfield: keep it, it sells the 3D, but dim it so pins stay legible.
  if (scene.skyBox) scene.skyBox.show = true;
  scene.sun.show = false;
  scene.moon.show = false;

  handlers.pick = onPick;
  handlers.hover = onHover;
  handlers.camera = onCamera;
  handlers.credit = onCredits;
  handlers.tiles = onTiles;

  globe.dataSource = new Cesium.CustomDataSource('aagis-sites');
  await viewer.dataSources.add(globe.dataSource);
  configureClustering(globe.dataSource);

  wireInteraction(viewer);
  wireCamera(viewer);
  wireTileProgress(viewer);

  await setBaseLayer(BASE_LAYERS.find((l) => l.default)?.id
                     ?? BASE_LAYERS[0].id);
  for (const ov of OVERLAYS) {
    if (ov.defaultOn) await setOverlay(ov.id, true);
  }

  // Terrain last: the globe is already interactive while it resolves.
  globe.terrainReady = enableTerrain().catch((err) => {
    console.warn('terrain unavailable, using a smooth ellipsoid', err);
  });

  return viewer;
}

/* ----------------------------------------------------------------- terrain */

export async function enableTerrain() {
  const Cesium = C();
  const { viewer } = globe;

  if (APP.ionToken) {
    try {
      viewer.terrainProvider = await Cesium.createWorldTerrainAsync({
        requestVertexNormals: true, requestWaterMask: true,
      });
      globe.terrainMode = 'cesium-world';
      addCredit('Terrain © <a href="https://cesium.com/" target="_blank" rel="noopener">Cesium</a>');
      render();
      return globe.terrainMode;
    } catch (err) {
      console.warn('Cesium World Terrain unavailable, falling back', err);
    }
  }

  try {
    viewer.terrainProvider = await Cesium.ArcGISTiledElevationTerrainProvider
      .fromUrl(TERRAIN.arcgis);
    globe.terrainMode = 'arcgis';
    addCredit(TERRAIN.credit);
  } catch (err) {
    viewer.terrainProvider = new Cesium.EllipsoidTerrainProvider();
    globe.terrainMode = 'ellipsoid';
    throw err;
  }
  render();
  return globe.terrainMode;
}

export function setTerrainEnabled(enabled) {
  const Cesium = C();
  if (!enabled) {
    globe.viewer.terrainProvider = new Cesium.EllipsoidTerrainProvider();
    globe.terrainMode = 'ellipsoid';
    globe.terrainReady = Promise.resolve();
    render();
    return Promise.resolve('ellipsoid');
  }
  const attaching = enableTerrain();
  globe.terrainReady = attaching.catch(() => {});
  return attaching;
}

/* ------------------------------------------------------------------ imagery */

function hydrateTemplate(tpl) {
  const retina = (window.devicePixelRatio || 1) > 1.5;
  return String(tpl).replace(/\{r\}/g, retina ? '@2x' : '');
}

function gibsDate(offsetDays = -2) {
  const d = new Date(Date.now() + offsetDays * 86400000);
  return d.toISOString().slice(0, 10);
}

function providerFor(spec) {
  const Cesium = C();
  const credit = new Cesium.Credit(spec.credit, true);
  const tilingScheme = new Cesium.WebMercatorTilingScheme();

  if (spec.kind === 'wmts') {
    let url = hydrateTemplate(spec.rest ?? spec.url);
    url = url.replace('{Layer}', spec.layer)
             .replace('{TileMatrixSet}', spec.tileMatrixSetID)
             .replace('{Time}', gibsDate(spec.timeOffsetDays ?? -2));
    return new Cesium.WebMapTileServiceImageryProvider({
      url,
      layer: spec.layer,
      style: spec.style ?? 'default',
      format: spec.format ?? 'image/jpeg',
      tileMatrixSetID: spec.tileMatrixSetID,
      maximumLevel: spec.maximumLevel ?? 18,
      tilingScheme,
      credit,
    });
  }

  if (spec.kind === 'wms') {
    return new Cesium.WebMapServiceImageryProvider({
      url: spec.url,
      layers: spec.layer,
      parameters: { transparent: spec.transparent ?? false,
                    format: spec.format ?? 'image/png', version: '1.3.0' },
      maximumLevel: spec.maximumLevel ?? 18,
      tilingScheme,
      credit,
    });
  }

  return new Cesium.UrlTemplateImageryProvider({
    url: hydrateTemplate(spec.url),
    subdomains: spec.subdomains,
    maximumLevel: spec.maximumLevel ?? 19,
    tilingScheme,
    credit,
  });
}

/**
 * Colour grading per layer class.
 *
 * A dark UI with a bright basemap is unreadable, and tinting satellite
 * imagery is dishonest — people read true-colour imagery as data. So:
 * dark reference maps get a small push toward cyan, imagery is left
 * essentially alone, and light maps are darkened and desaturated enough to
 * sit in the same scene without blowing it out.
 */
const THEME_GRADE = {
  dark:    { brightness: 1.10, contrast: 1.14, saturation: 0.85, hue: -0.05, gamma: 1.00 },
  imagery: { brightness: 0.92, contrast: 1.08, saturation: 1.00, hue:  0.00, gamma: 1.00 },
  light:   { brightness: 0.60, contrast: 1.18, saturation: 0.50, hue: -0.04, gamma: 1.12 },
};

/** User brightness multiplier from the Layers tab, applied on top. */
let brightnessScale = 1;

function applyGrade(layer, spec) {
  const g = THEME_GRADE[spec.theme] ?? THEME_GRADE.imagery;
  layer.brightness = g.brightness * brightnessScale;
  layer.contrast = g.contrast;
  layer.saturation = g.saturation;
  layer.hue = g.hue;
  layer.gamma = g.gamma;
}

export async function setBaseLayer(id) {
  const spec = BASE_LAYERS.find((l) => l.id === id);
  if (!spec) return null;
  const { viewer } = globe;
  const layers = viewer.imageryLayers;

  const next = layers.addImageryProvider(providerFor(spec), 0);
  next.alpha = 1;
  applyGrade(next, spec);
  if (globe.layers.base) layers.remove(globe.layers.base, true);
  globe.layers.base = next;
  globe.layers.baseId = id;
  layers.lowerToBottom(next);
  rebuildCredits();
  render();
  return spec;
}

export async function setOverlay(id, on) {
  const spec = OVERLAYS.find((o) => o.id === id);
  if (!spec) return;
  const { viewer } = globe;
  const existing = globe.layers.overlays.get(id);

  if (!on) {
    if (existing) {
      viewer.imageryLayers.remove(existing, true);
      globe.layers.overlays.delete(id);
    }
  } else if (!existing) {
    const layer = viewer.imageryLayers.addImageryProvider(providerFor(spec));
    layer.alpha = spec.alpha ?? 1;
    globe.layers.overlays.set(id, layer);
  }
  rebuildCredits();
  render();
}

export function setOverlayAlpha(id, alpha) {
  const layer = globe.layers.overlays.get(id);
  if (layer) { layer.alpha = alpha; render(); }
}

export function setBaseBrightness(value) {
  brightnessScale = value;
  const spec = BASE_LAYERS.find((l) => l.id === globe.layers.baseId);
  if (globe.layers.base && spec) { applyGrade(globe.layers.base, spec); render(); }
}

/* --------------------------------------------------------------- credits */

const extraCredits = new Set();
export const addCredit = (html) => { extraCredits.add(html); rebuildCredits(); };

function rebuildCredits() {
  const out = [];
  const base = BASE_LAYERS.find((l) => l.id === globe.layers.baseId);
  if (base) out.push(base.credit);
  for (const id of globe.layers.overlays.keys()) {
    const ov = OVERLAYS.find((o) => o.id === id);
    if (ov) out.push(ov.credit);
  }
  out.push(...extraCredits);
  out.push('Globe © <a href="https://cesium.com/platform/cesiumjs/" target="_blank" rel="noopener">CesiumJS</a>');
  handlers.credit?.([...new Set(out)]);
}

/* ------------------------------------------------------------------- pins */

const pinCache = new Map();

/** Draw a teardrop pin with a neon rim and an inner glyph dot. */
function pinImage(hex, { selected = false } = {}) {
  const key = `${hex}|${selected}`;
  if (pinCache.has(key)) return pinCache.get(key);

  const S = 96, cvs = document.createElement('canvas');
  cvs.width = cvs.height = S;
  const g = cvs.getContext('2d');
  const cx = S / 2, cy = S * 0.40, r = S * 0.255;

  // outer glow
  g.save();
  g.shadowColor = hex;
  g.shadowBlur = selected ? S * 0.30 : S * 0.17;

  // teardrop body
  g.beginPath();
  g.moveTo(cx, S * 0.925);
  g.quadraticCurveTo(cx - r * 0.92, cy + r * 0.92, cx - r, cy);
  g.arc(cx, cy, r, Math.PI, 0, false);
  g.quadraticCurveTo(cx + r * 0.92, cy + r * 0.92, cx, S * 0.925);
  g.closePath();
  g.fillStyle = 'rgba(7, 11, 20, 0.92)';
  g.fill();
  g.lineWidth = selected ? S * 0.055 : S * 0.040;
  g.strokeStyle = hex;
  g.stroke();
  g.restore();

  // inner dot
  g.beginPath();
  g.arc(cx, cy, r * (selected ? 0.50 : 0.42), 0, Math.PI * 2);
  g.fillStyle = hex;
  g.fill();

  if (selected) {
    g.beginPath();
    g.arc(cx, cy, r * 0.74, 0, Math.PI * 2);
    g.lineWidth = S * 0.022;
    g.strokeStyle = 'rgba(255,255,255,0.85)';
    g.stroke();
  }

  const url = cvs.toDataURL('image/png');
  pinCache.set(key, url);
  return url;
}

function clusterImage(count, hex = '#22e0f2') {
  const key = `cluster|${count}|${hex}`;
  if (pinCache.has(key)) return pinCache.get(key);
  const S = 96, cvs = document.createElement('canvas');
  cvs.width = cvs.height = S;
  const g = cvs.getContext('2d');
  const cx = S / 2, r = S * 0.36;

  g.save();
  g.shadowColor = hex; g.shadowBlur = S * 0.22;
  g.beginPath(); g.arc(cx, cx, r, 0, Math.PI * 2);
  g.fillStyle = 'rgba(7, 11, 20, 0.90)'; g.fill();
  g.lineWidth = S * 0.045; g.strokeStyle = hex; g.stroke();
  g.restore();

  g.beginPath(); g.arc(cx, cx, r * 1.22, 0, Math.PI * 2);
  g.lineWidth = S * 0.018;
  g.strokeStyle = 'rgba(34, 224, 242, 0.35)'; g.stroke();

  g.fillStyle = '#e8f4f8';
  g.font = `700 ${S * (count > 99 ? 0.26 : 0.32)}px "Rajdhani", system-ui, sans-serif`;
  g.textAlign = 'center'; g.textBaseline = 'middle';
  g.fillText(String(count), cx, cx + S * 0.015);

  const url = cvs.toDataURL('image/png');
  pinCache.set(key, url);
  return url;
}

function configureClustering(ds) {
  const Cesium = C();
  const cl = ds.clustering;
  cl.enabled = true;
  cl.pixelRange = isCoarsePointer() ? 44 : 34;
  cl.minimumClusterSize = 3;
  cl.clusterBillboards = true;
  cl.clusterLabels = false;
  cl.clusterPoints = true;
  cl.clusterEvent.addEventListener((entities, cluster) => {
    cluster.label.show = false;
    cluster.point.show = false;
    cluster.billboard.show = true;
    cluster.billboard.id = { cluster: true, ids: entities.map((e) => e.id) };
    cluster.billboard.image = clusterImage(entities.length);
    cluster.billboard.verticalOrigin = Cesium.VerticalOrigin.CENTER;
    cluster.billboard.heightReference = Cesium.HeightReference.NONE;
    cluster.billboard.width = 38;
    cluster.billboard.height = 38;
    cluster.billboard.disableDepthTestDistance = Number.POSITIVE_INFINITY;
  });
}

export function setClustering(enabled) {
  if (globe.dataSource) {
    globe.dataSource.clustering.enabled = enabled;
    render();
  }
}

/* ----------------------------------------------------------------- markers */

const CATEGORY_TOKEN = {
  megalithic: '--cat-megalithic', pyramid: '--cat-pyramid',
  geoglyph: '--cat-geoglyph', underground: '--cat-underground',
  underwater: '--cat-underwater', ufo: '--cat-ufo',
  military: '--cat-military', research: '--cat-research',
  sacred: '--cat-sacred', anomaly: '--cat-anomaly',
  landform: '--cat-landform', city: '--cat-city',
  artifact: '--cat-artifact', region: '--cat-region',
  offworld: '--cat-offworld',
};

export const colorForCategory = (cat) =>
  categoryColor(CATEGORY_TOKEN[cat] ?? '--cat-megalithic');

/** Build every marker once. Filtering only toggles `show`. */
export function addSites(sites) {
  const Cesium = C();
  const ds = globe.dataSource;
  ds.entities.suspendEvents();
  ds.entities.removeAll();
  globe.entities.clear();
  globe.areas.clear();
  globe.siteById.clear();

  for (const s of sites) {
    if (s.off || s.lat == null) continue;        // off-world sites have no pin
    globe.siteById.set(s.id, s);
    const hex = colorForCategory(s.c);
    const positions = s.mp?.length
      ? s.mp.map(([lat, lon]) => Cesium.Cartesian3.fromDegrees(lon, lat))
      : [Cesium.Cartesian3.fromDegrees(s.lon, s.lat)];

    positions.forEach((position, i) => {
      const entity = ds.entities.add({
        id: i === 0 ? s.id : `${s.id}#${i}`,
        position,
        billboard: {
          image: pinImage(hex),
          width: 30,
          height: 30,
          verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
          heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
          disableDepthTestDistance: Number.POSITIVE_INFINITY,
          scaleByDistance: new Cesium.NearFarScalar(
            5.0e5, 1.0, 2.2e7, 0.52),
          translucencyByDistance: new Cesium.NearFarScalar(
            1.0e6, 1.0, 3.6e7, 0.72),
        },
        label: {
          text: s.n,
          font: '600 13px "Rajdhani", system-ui, sans-serif',
          fillColor: Cesium.Color.fromCssColorString('#e8f4f8'),
          outlineColor: Cesium.Color.fromCssColorString('#04070d'),
          outlineWidth: 3,
          style: Cesium.LabelStyle.FILL_AND_OUTLINE,
          verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
          pixelOffset: new Cesium.Cartesian2(0, -34),
          heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
          disableDepthTestDistance: Number.POSITIVE_INFINITY,
          distanceDisplayCondition:
            new Cesium.DistanceDisplayCondition(0, 9.0e5),
          show: i === 0,
        },
        properties: { siteId: s.id, category: s.c },
      });
      if (i === 0) globe.entities.set(s.id, entity);
    });

    // Region-scale entries get a footprint, so an "area" pin never reads as
    // a surveyed point.
    if (s.rk) {
      const ring = ds.entities.add({
        id: `${s.id}::area`,
        position: Cesium.Cartesian3.fromDegrees(s.lon, s.lat),
        ellipse: {
          semiMajorAxis: s.rk * 1000,
          semiMinorAxis: s.rk * 1000,
          material: Cesium.Color.fromCssColorString(hex).withAlpha(0.055),
          outline: true,
          outlineColor: Cesium.Color.fromCssColorString(hex).withAlpha(0.45),
          outlineWidth: 2,
          height: 0,
          granularity: Cesium.Math.toRadians(1.5),
        },
        properties: { siteId: s.id, area: true },
      });
      globe.areas.set(s.id, ring);
    }
  }
  ds.entities.resumeEvents();
  render();
}

/** Show only the filtered subset. */
export function showOnly(ids) {
  const keep = ids instanceof Set ? ids : new Set(ids);
  for (const entity of globe.dataSource.entities.values) {
    const sid = entity.properties?.siteId?.getValue?.();
    if (sid) entity.show = keep.has(sid);
  }
  render();
}

/* --------------------------------------------------------------- selection */

let pulseStop = null;

export function highlight(siteId) {
  const Cesium = C();
  globe.selectedId = siteId || null;

  for (const [id, entity] of globe.entities) {
    const cat = entity.properties?.category?.getValue?.();
    const hex = colorForCategory(cat);
    const isSel = id === siteId;
    entity.billboard.image = pinImage(hex, { selected: isSel });
    entity.billboard.width = isSel ? 44 : 30;
    entity.billboard.height = isSel ? 44 : 30;
    if (entity.label) {
      entity.label.show = true;
      entity.label.distanceDisplayCondition = isSel
        ? new Cesium.DistanceDisplayCondition(0, 4.0e7)
        : new Cesium.DistanceDisplayCondition(0, 9.0e5);
    }
  }

  if (globe.selectionRing) {
    globe.dataSource.entities.remove(globe.selectionRing);
    globe.selectionRing = null;
  }
  pulseStop?.();
  pulseStop = null;

  if (!siteId) { render(); return; }
  const target = globe.entities.get(siteId);
  if (!target) { render(); return; }

  // A short, bounded pulse: enough flourish to read as a lock-on, then it
  // stops so requestRenderMode can let the GPU idle again.
  if (!prefersReducedMotion()) {
    const t0 = performance.now();
    let raf = 0;
    const tick = (t) => {
      const k = (t - t0) / 1100;
      if (k >= 1) { pulseStop = null; render(); return; }
      const scale = 1 + 0.18 * Math.sin(k * Math.PI * 3) * (1 - k);
      target.billboard.width = 44 * scale;
      target.billboard.height = 44 * scale;
      render();
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    pulseStop = () => {
      cancelAnimationFrame(raf);
      target.billboard.width = 44;
      target.billboard.height = 44;
    };
  }
  render();
}

/* ------------------------------------------------------------------ camera */

/**
 * Camera placement over real terrain.
 *
 * Cartesian3.fromDegrees() measures height from the WGS84 *ellipsoid*, not
 * from the ground. With terrain loaded, flying to Machu Picchu at "1500 m"
 * puts the camera 930 m inside the mountain, because the ridge is at
 * 2430 m — the screen goes black. The same applies to Kailash, Denali, the
 * Altiplano, Tibet, the Bighorn Medicine Wheel and every other site on high
 * ground, which is a large share of this catalogue. So each site's `height`
 * is treated as height above ground level.
 *
 * Getting the ground elevation is the awkward part:
 *
 *   scene.globe.getHeight()        instant, but reads whatever level of
 *                                  detail is resident — at the Bighorn
 *                                  Medicine Wheel a coarse tile reported
 *                                  1410 m against an actual 2938 m.
 *   sampleTerrainMostDetailed()    correct, but fetches tiles, so it can
 *                                  take seconds on a slow connection.
 *
 * Waiting for the accurate value before moving makes every selection feel
 * broken; using only the fast one flies into hillsides. So: move at once
 * with the coarse estimate, then correct when the accurate sample arrives,
 * and only if the correction is big enough to be worth a second move and
 * the user has not picked something else meanwhile.
 */
/**
 * Best ground elevation available without waiting.
 *
 * Preference order:
 *   1. the value baked into the catalogue at build time (Copernicus DEM via
 *      the Open-Meteo elevation API) — always present, always instant, and
 *      within a few metres of what Cesium's terrain reports;
 *   2. whatever Cesium has resident, which is wrong by hundreds of metres
 *      in steep country when only a coarse tile has loaded;
 *   3. sea level.
 */
function coarseGround(site, lon, lat) {
  const Cesium = C();
  if (globe.terrainMode === 'ellipsoid') return 0;
  if (Number.isFinite(site?.g)) return site.g;
  const h = globe.scene.globe.getHeight(
    Cesium.Cartographic.fromDegrees(lon, lat));
  return Number.isFinite(h) ? h : 0;
}

async function accurateGround(lon, lat) {
  const Cesium = C();
  // The terrain provider attaches after the viewer is interactive, so a
  // flight triggered by a deep link can start before it exists. Without
  // this wait the sample returns sea level, no correction is issued, and
  // the camera stays inside the mountain once terrain finally appears.
  await globe.terrainReady;
  if (globe.terrainMode === 'ellipsoid') return 0;
  try {
    const [s] = await Cesium.sampleTerrainMostDetailed(
      globe.viewer.terrainProvider,
      [Cesium.Cartographic.fromDegrees(lon, lat)]);
    return Number.isFinite(s?.height) ? s.height : null;
  } catch {
    return null;
  }
}

/** Minimum separation between the camera and the ground, in metres. */
const MIN_CLEARANCE = 250;

export function flyToSite(site, { duration } = {}) {
  const Cesium = C();
  const { viewer } = globe;
  if (!site || site.off || site.lat == null) return Promise.resolve();

  globe.pendingFlight = site.id;
  const d = duration ?? (prefersReducedMotion() ? 0 : CAMERA.flyDuration);
  const above = Math.max(400, site.h ?? 3000);
  const pitch = Cesium.Math.toRadians(CAMERA.sitePitch);

  // Region entries frame their whole extent from far enough out that
  // terrain is immaterial.
  if (site.rk) {
    viewer.camera.flyToBoundingSphere(
      new Cesium.BoundingSphere(
        Cesium.Cartesian3.fromDegrees(site.lon, site.lat), site.rk * 1400),
      { duration: d,
        offset: new Cesium.HeadingPitchRange(0, pitch, 0) });
    render();
    return Promise.resolve();
  }

  // Fly to the SITE, not to a position above it. flyTo places the camera
  // and then aims it, so at any pitch other than straight down the thing
  // you asked for ends up off screen by height / tan(pitch).
  // flyToBoundingSphere is given the target and solves for the camera, so
  // the site is centred whatever the pitch.
  const goTo = (ground, seconds) => {
    const target = Math.max(ground + above, ground + MIN_CLEARANCE);
    viewer.camera.flyToBoundingSphere(
      new Cesium.BoundingSphere(
        Cesium.Cartesian3.fromDegrees(site.lon, site.lat, ground), 0),
      {
        duration: seconds,
        offset: new Cesium.HeadingPitchRange(0, pitch, target - ground),
        easingFunction: Cesium.EasingFunction.QUADRATIC_IN_OUT,
      });
    render();
    return target;
  };

  const estimate = coarseGround(site, site.lon, site.lat);
  const flown = goTo(estimate, d);

  // Correct once the real elevation is known.
  return accurateGround(site.lon, site.lat).then((ground) => {
    if (ground == null) return;
    if (globe.pendingFlight !== site.id) return;      // superseded
    const target = Math.max(ground + above, ground + MIN_CLEARANCE);
    if (Math.abs(target - flown) < 150) return;        // close enough
    goTo(ground, prefersReducedMotion() ? 0 : 0.9);
  });
}

export function flyHome() {
  const Cesium = C();
  globe.viewer.camera.flyTo({
    destination: Cesium.Cartesian3.fromDegrees(
      CAMERA.home.lon, CAMERA.home.lat, CAMERA.home.height),
    orientation: {
      heading: 0,
      pitch: Cesium.Math.toRadians(CAMERA.home.pitch),
      roll: 0,
    },
    duration: prefersReducedMotion() ? 0 : 2.2,
  });
  render();
}

export function flyToCoords(lat, lon, height = 2_000_000) {
  const Cesium = C();
  globe.viewer.camera.flyTo({
    destination: Cesium.Cartesian3.fromDegrees(lon, lat, height),
    duration: prefersReducedMotion() ? 0 : 2.0,
  });
  render();
}

/** Where the view is currently pointed, as ground coordinates plus a
 *  height above them.
 *
 *  A morph preserves the camera, not the subject. Going 3D -> 2D that is
 *  not the same question: the projections disagree about what a camera
 *  position means, and Cesium resolves it by backing out to the whole
 *  world. Capturing the subject first and restoring it afterwards is the
 *  only way the location survives the change. */
function viewFocus() {
  const Cesium = C();
  const { scene, camera } = globe.viewer;
  // positionCartographic, NOT Cartographic.fromCartesian(positionWC).
  // In 2D and Columbus the camera lives in the projection's own frame, so
  // reading positionWC as geocentric returns nonsense — measured: a
  // height of 8,790 km while framing a 3,942 m view. Cesium's accessor
  // is projection-aware and right in all three modes.
  const carto = camera.positionCartographic;
  const height = Math.min(
    Math.max(carto?.height ?? 2_000_000, CAMERA.minZoom), CAMERA.maxZoom);

  // A selected site is the honest answer to "what are you looking at".
  const entity = globe.selectedId && globe.entities.get(globe.selectedId);
  const pos = entity?.position?.getValue?.(Cesium.JulianDate.now());
  if (pos) {
    const c = Cesium.Cartographic.fromCartesian(pos);
    return { lon: Cesium.Math.toDegrees(c.longitude),
             lat: Cesium.Math.toDegrees(c.latitude), height };
  }

  // Otherwise, whatever the middle of the screen is over. Falls back to
  // the camera's own ground track when the centre ray misses the globe,
  // which it does whenever the horizon is in shot.
  const centre = new Cesium.Cartesian2(scene.canvas.clientWidth / 2,
                                       scene.canvas.clientHeight / 2);
  const ray = camera.getPickRay(centre);
  const hit = ray && scene.globe.pick(ray, scene);
  const c = hit ? Cesium.Cartographic.fromCartesian(hit) : carto;
  // (hit is a genuine world-space point from globe.pick, so converting
  //  that one IS correct; carto is already cartographic.)
  if (!c) return null;
  return { lon: Cesium.Math.toDegrees(c.longitude),
           lat: Cesium.Math.toDegrees(c.latitude), height };
}

function restoreFocus(focus) {
  const Cesium = C();
  try {
    // When a site is selected, re-fly to it rather than reconstructing a
    // camera. flyToSite already solves for a centred target and handles
    // ground elevation, and is the same path the rest of the app uses —
    // hand-placing the camera agreed with it in 3D and Columbus but not
    // in 2D, where the projection makes a camera position mean something
    // different.
    const site = globe.selectedId && globe.siteById.get(globe.selectedId);
    const lon = site ? site.lon : focus?.lon;
    const lat = site ? site.lat : focus?.lat;
    if (lon == null || lat == null) return;

    // 2D is orthographic: the frustum decides what you see, not where the
    // camera sits. Flying a camera into it re-enters the transitioner and
    // wedges the scene — measured, scene.mode stayed MORPHING for ten
    // seconds. Framing a rectangle is the operation Cesium provides.
    if (globe.scene.mode === Cesium.SceneMode.SCENE2D) {
      const half = Math.max(0.002,
        ((focus?.height ?? 3000) / 111_320) * 0.6);
      globe.viewer.camera.setView({
        destination: Cesium.Rectangle.fromDegrees(
          lon - half, lat - half, lon + half, lat + half),
      });
      render();
      return;
    }

    if (site) { flyToSite(site, { duration: 0 }); return; }

    if (!focus) return;
    globe.viewer.camera.setView({
      destination: Cesium.Cartesian3.fromDegrees(
        focus.lon, focus.lat, focus.height),
      orientation: {
        heading: 0,
        pitch: Cesium.Math.toRadians(CAMERA.sitePitch),
        roll: 0,
      },
    });
    render();
  } catch (err) {
    // A failed restore must never leave the camera mid-transition.
    console.warn('scene morph: could not restore the view', err);
  }
}

export function setSceneMode(mode) {
  const { scene } = globe;
  const dur = prefersReducedMotion() ? 0 : 1.4;
  const focus = viewFocus();
  globe.targetMode = mode;

  // morphComplete is raised BEFORE Cesium finishes restoring its own
  // camera state, so anything set in that handler is overwritten a
  // moment later — measured: the camera ended 8,790 km from the subject.
  // Waiting one rendered frame puts the restore after Cesium's own.
  const onDone = () => {
    scene.morphComplete.removeEventListener(onDone);
    const afterFrame = () => {
      scene.postRender.removeEventListener(afterFrame);
      restoreFocus(focus);
    };
    scene.postRender.addEventListener(afterFrame);
    render();
  };
  scene.morphComplete.addEventListener(onDone);

  if (mode === '2D') scene.morphTo2D(dur);
  else if (mode === 'COLUMBUS') scene.morphToColumbusView(dur);
  else scene.morphTo3D(dur);

  // A zero-duration morph can complete before the listener is useful.
  if (dur === 0) restoreFocus(focus);
  render();
  return mode;
}

export const sceneModeName = () => {
  const Cesium = C();
  switch (globe.scene?.mode) {
    case Cesium.SceneMode.SCENE2D: return '2D';
    case Cesium.SceneMode.COLUMBUS_VIEW: return 'COLUMBUS';
    case Cesium.SceneMode.SCENE3D: return '3D';
    // MORPHING has no case of its own and used to fall through to '3D',
    // so the readout claimed 3D while the scene was halfway to 2D.
    // Report where the morph is heading instead of a wrong answer.
    default: return globe.targetMode ?? '3D';
  }
};

/* ------------------------------------------------------------- interaction */

function siteIdFromPick(picked) {
  if (!picked) return null;
  if (picked.id?.cluster) return picked.id.ids?.[0]?.id ?? null;
  const entity = picked.id;
  const sid = entity?.properties?.siteId?.getValue?.();
  return sid ?? (typeof entity?.id === 'string'
    ? entity.id.split(/[#:]/)[0] : null);
}

function wireInteraction(viewer) {
  const Cesium = C();
  const handler = new Cesium.ScreenSpaceEventHandler(viewer.canvas);

  handler.setInputAction((movement) => {
    const picked = viewer.scene.pick(movement.position);
    if (picked?.id?.cluster) {
      // Tapping a cluster zooms into it rather than guessing a member.
      const first = picked.id.ids?.[0];
      const sid = first?.properties?.siteId?.getValue?.();
      handlers.pick?.(sid ?? null, { cluster: true });
      return;
    }
    handlers.pick?.(siteIdFromPick(picked), { cluster: false });
  }, Cesium.ScreenSpaceEventType.LEFT_CLICK);

  // Hover readout — pointer devices only; it is noise on touch.
  if (!isCoarsePointer()) {
    let lastId = null;
    handler.setInputAction((movement) => {
      const picked = viewer.scene.pick(movement.endPosition);
      const sid = picked?.id?.cluster ? '::cluster' : siteIdFromPick(picked);
      viewer.canvas.style.cursor = sid ? 'pointer' : '';
      if (sid !== lastId) {
        lastId = sid;
        handlers.hover?.(sid === '::cluster' ? null : sid);
      }
      const carto = readCartographic(movement.endPosition);
      if (carto) handlers.camera?.(carto);
    }, Cesium.ScreenSpaceEventType.MOUSE_MOVE);
  }
}

function readCartographic(windowPosition) {
  const Cesium = C();
  const { scene } = globe;
  const ray = scene.camera.getPickRay(windowPosition);
  if (!ray) return null;
  const cart = scene.globe.pick(ray, scene);
  if (!cart) return null;
  const c = Cesium.Cartographic.fromCartesian(cart);
  return {
    lat: Cesium.Math.toDegrees(c.latitude),
    lon: Cesium.Math.toDegrees(c.longitude),
    elevation: scene.globe.getHeight(c) ?? null,
  };
}

/**
 * Tell the UI when imagery is still streaming.
 *
 * Without this a slow link looks like a broken globe: the surface is drawn
 * in the base colour, nothing moves, and there is no signal that anything
 * is happening. Cesium raises this event with the number of outstanding
 * tile requests.
 */
function wireTileProgress(viewer) {
  let last = -1;
  viewer.scene.globe.tileLoadProgressEvent.addEventListener((queued) => {
    // Only report meaningful transitions, not every decrement.
    const busy = queued > 0;
    if (busy === (last > 0) && Math.abs(queued - last) < 8) return;
    last = queued;
    handlers.tiles?.(queued);
  });
}

function wireCamera(viewer) {
  const Cesium = C();
  const report = () => {
    const c = Cesium.Cartographic.fromCartesian(viewer.camera.positionWC);
    handlers.camera?.({
      cameraHeight: c.height,
      cameraLat: Cesium.Math.toDegrees(c.latitude),
      cameraLon: Cesium.Math.toDegrees(c.longitude),
      sceneMode: sceneModeName(),
    });
  };
  viewer.camera.changed.addEventListener(report);
  viewer.camera.percentageChanged = 0.1;
  viewer.scene.morphComplete.addEventListener(report);
  report();
}

/* -------------------------------------------------------------------- misc */

export function render() {
  globe.scene?.requestRender();
}

export function resize() {
  globe.viewer?.resize();
  render();
}

export function setFx(on) {
  const { scene } = globe;
  if (!scene) return;
  scene.fog.enabled = on;
  scene.globe.showGroundAtmosphere = on;
  if (scene.skyAtmosphere) scene.skyAtmosphere.show = on;
  if (scene.skyBox) scene.skyBox.show = on;
  render();
}
