/* ==========================================================================
   OGC API - Features client.

   Two deployment shapes are supported behind one interface:

     static     the generated document tree under data/ — the GitHub Pages
                deployment. Resource paths carry an explicit `.json` suffix
                because a static host serves files, not negotiated resources.

     geoserver  a live OGC API - Features service (set APP.geoserverFeatures).
                Paths follow the specification's own shape and content
                negotiation applies.

   The feature schema is identical in both, so nothing downstream cares.
   ========================================================================== */

import { APP } from './config.js';
import { appURL, getJSON } from './util.js';

const live = () => Boolean(APP.geoserverFeatures);

const root = () => (live()
  ? APP.geoserverFeatures.replace(/\/?$/, '/')
  : appURL(APP.dataRoot));

/** Resource paths differ only in the suffix a static host needs. */
const path = {
  landing:     () => (live() ? '' : 'index.json'),
  conformance: () => (live() ? 'conformance' : 'conformance.json'),
  collections: () => (live() ? 'collections' : 'collections/index.json'),
  collection:  (c) => (live() ? `collections/${c}` : `collections/${c}/index.json`),
  items:       (c) => (live() ? `collections/${c}/items?limit=1000`
                              : `collections/${c}/items.json`),
  item:    (c, id) => (live() ? `collections/${c}/items/${encodeURIComponent(id)}`
                              : `collections/${c}/items/${encodeURIComponent(id)}.json`),
  queryables:  (c) => (live() ? `collections/${c}/queryables`
                              : `collections/${c}/queryables.json`),
};

const url = (p) => new URL(p, root()).href;

export const COLLECTION = 'sites';

export const deployment = () => (live() ? 'geoserver' : 'static');

/* ----------------------------------------------------------------- loaders */

/**
 * The slim client index. This is not an OGC resource — it is a build artefact
 * that exists so the first paint does not wait on the 680 KiB
 * FeatureCollection. In GeoServer mode it is unavailable, so we derive the
 * same shape from /items on the fly.
 */
export async function loadIndex(signal) {
  if (!live()) {
    return getJSON(url('app-index.json'), { signal });
  }
  const fc = await getJSON(url(path.items(COLLECTION)), { signal, timeout: 40000 });
  return indexFromFeatureCollection(fc);
}

function indexFromFeatureCollection(fc) {
  const sites = (fc.features || []).map((f) => {
    const p = f.properties || {};
    const geom = f.geometry;
    const multi = geom?.type === 'MultiPoint'
      ? geom.coordinates.map(([lon, lat]) => [lat, lon]) : null;
    return {
      id: f.id ?? p.id,
      n: p.name, s: p.subtitle, c: p.category, r: p.region, y: p.country,
      p: p.location_precision,
      t: [...(p.tags || []), ...(p.aliases || [])],
      lat: p.latitude, lon: p.longitude,
      h: p.camera_height_m ?? 5000,
      g: p.ground_elevation_m ?? null,
      pi: p.camera_pitch_deg ?? -40,
      rk: p.radius_km ?? null,
      off: p.celestial_body && p.celestial_body !== 'earth',
      mp: multi,
    };
  });
  return {
    count: sites.length,
    bbox: fc.bbox,
    sites,
    regions: [...new Set(sites.map((s) => s.r))].sort(),
    categories: [],
    attribution: '',
    generated: fc.timeStamp || '',
  };
}

/** One full Feature document, for the dossier. Memoised per id. */
const featureCache = new Map();

export async function loadFeature(id, signal) {
  if (featureCache.has(id)) return featureCache.get(id);
  const promise = getJSON(url(path.item(COLLECTION, id)), { signal })
    .catch(async (err) => {
      // A single-item document may be absent on a partial deploy; fall back
      // to pulling it out of the full collection rather than failing the UI.
      featureCache.delete(id);
      const fc = await getJSON(url(path.items(COLLECTION)), { timeout: 40000 });
      const hit = (fc.features || []).find((f) => (f.id ?? f.properties?.id) === id);
      if (!hit) throw err;
      return hit;
    });
  featureCache.set(id, promise);
  return promise;
}

/** Service metadata for the OGC tab. Failures are reported, not thrown. */
export async function loadServiceMetadata(signal) {
  const fetchOne = async (label, p) => {
    try { return { ok: true, value: await getJSON(url(p), { signal }) }; }
    catch (err) { return { ok: false, label, error: String(err.message || err) }; }
  };
  const [landing, conformance, collection, queryables] = await Promise.all([
    fetchOne('landing page', path.landing()),
    fetchOne('conformance', path.conformance()),
    fetchOne('collection', path.collection(COLLECTION)),
    fetchOne('queryables', path.queryables(COLLECTION)),
  ]);
  return {
    deployment: deployment(),
    root: root(),
    endpoints: {
      landing: url(path.landing()),
      conformance: url(path.conformance()),
      collections: url(path.collections()),
      collection: url(path.collection(COLLECTION)),
      items: url(path.items(COLLECTION)),
      queryables: url(path.queryables(COLLECTION)),
      api: live() ? url('api') : url('api.json'),
    },
    landing, conformance, collection, queryables,
  };
}

export const featureURL = (id) => url(path.item(COLLECTION, id));
