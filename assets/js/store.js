/* ==========================================================================
   Application state: the site catalogue, the active filters, the selection,
   and the URL that reflects them.

   A tiny event bus keeps the globe and the panel in step without either
   importing the other.
   ========================================================================== */

import { fold, haversineKm } from './util.js';
import { loadIndex, loadFeature } from './ogc.js';

const listeners = new Map();

export function on(event, fn) {
  if (!listeners.has(event)) listeners.set(event, new Set());
  listeners.get(event).add(fn);
  return () => listeners.get(event).delete(fn);
}

function emit(event, detail) {
  for (const fn of listeners.get(event) ?? []) {
    try { fn(detail); } catch (err) { console.error(`[${event}]`, err); }
  }
}

/* ------------------------------------------------------------------- state */

export const state = {
  ready: false,
  count: 0,
  bbox: null,
  regions: [],
  categories: [],
  attribution: '',
  generated: '',
  /** All sites, in catalogue order. */
  sites: [],
  byId: new Map(),
  /** Filters. */
  query: '',
  region: 'all',
  activeCategories: new Set(),   // empty === show everything
  sort: 'name',
  /** Selection + camera. */
  selectedId: null,
  cameraCenter: null,            // {lat, lon} — drives 'nearest to view'
  /** Derived. */
  visible: [],
};

/* ------------------------------------------------------------------ search */

/** Build one folded haystack per site so filtering stays allocation-free. */
function indexSite(s) {
  s._hay = fold([s.n, s.s, s.y, s.r, s.c, ...(s.t || [])].join(' '));
  s._foldName = fold(s.n);
  return s;
}

export async function init(signal) {
  const idx = await loadIndex(signal);
  state.count = idx.count ?? idx.sites.length;
  state.bbox = idx.bbox ?? null;
  state.regions = idx.regions ?? [];
  state.categories = idx.categories ?? [];
  state.attribution = idx.attribution ?? '';
  state.generated = idx.generated ?? '';
  state.sites = (idx.sites || []).map(indexSite);
  state.byId = new Map(state.sites.map((s) => [s.id, s]));
  state.ready = true;
  recompute();
  emit('ready', state);
  return state;
}

/* ------------------------------------------------------------------ filter */

const CATEGORY_RANK = new Map();

export function setCategoryOrder(ids) {
  CATEGORY_RANK.clear();
  ids.forEach((id, i) => CATEGORY_RANK.set(id, i));
}

function matches(s) {
  if (state.region !== 'all' && s.r !== state.region) return false;
  if (state.activeCategories.size && !state.activeCategories.has(s.c)) return false;
  if (state.query) {
    const q = fold(state.query);
    // Multi-word queries must match every term, in any field.
    for (const term of q.split(/\s+/)) {
      if (term && !s._hay.includes(term)) return false;
    }
  }
  return true;
}

function distanceFromCamera(s) {
  const c = state.cameraCenter;
  if (!c || s.lat == null) return Number.POSITIVE_INFINITY;
  return haversineKm(c.lat, c.lon, s.lat, s.lon);
}

function recompute() {
  const list = state.sites.filter(matches);
  const byName = (a, b) => a._foldName.localeCompare(b._foldName);
  switch (state.sort) {
    case 'region':
      list.sort((a, b) => a.r.localeCompare(b.r) || byName(a, b));
      break;
    case 'category':
      list.sort((a, b) =>
        (CATEGORY_RANK.get(a.c) ?? 99) - (CATEGORY_RANK.get(b.c) ?? 99)
        || byName(a, b));
      break;
    case 'distance':
      list.forEach((s) => { s._dist = distanceFromCamera(s); });
      list.sort((a, b) => a._dist - b._dist || byName(a, b));
      break;
    default:
      list.sort(byName);
  }
  state.visible = list;
  emit('filtered', list);
}

/* ------------------------------------------------------------------ setters */

export function setQuery(q) {
  if (q === state.query) return;
  state.query = q;
  recompute();
  syncURL();
}

export function setRegion(r) {
  if (r === state.region) return;
  state.region = r;
  recompute();
  syncURL();
}

export function toggleCategory(id) {
  const set = state.activeCategories;
  if (set.has(id)) set.delete(id); else set.add(id);
  recompute();
  syncURL();
  emit('categories', set);
}

export function setSort(mode) {
  if (mode === state.sort) return;
  state.sort = mode;
  recompute();
  syncURL();
}

export function resetFilters() {
  state.query = '';
  state.region = 'all';
  state.activeCategories.clear();
  state.sort = 'name';
  recompute();
  syncURL();
  emit('categories', state.activeCategories);
  emit('reset');
}

export function setCameraCenter(lat, lon) {
  state.cameraCenter = { lat, lon };
  if (state.sort === 'distance') recompute();
}

/* ---------------------------------------------------------------- selection */

/** Search ranked for the type-ahead: name prefix > name substring > any. */
export function rank(query, limit = 12) {
  const q = fold(query.trim());
  if (!q) return [];
  const terms = q.split(/\s+/).filter(Boolean);
  const scored = [];
  for (const s of state.sites) {
    if (!terms.every((t) => s._hay.includes(t))) continue;
    let score = 400;
    if (s._foldName.startsWith(q)) score = 0;
    else if (s._foldName.includes(q)) score = 100 + s._foldName.indexOf(q);
    else if (fold(s.y || '').startsWith(q)) score = 250;
    else if ((s.t || []).some((t) => fold(t).startsWith(q))) score = 300;
    scored.push([score, s]);
  }
  scored.sort((a, b) => a[0] - b[0] || a[1]._foldName.localeCompare(b[1]._foldName));
  return scored.slice(0, limit).map(([, s]) => s);
}

/**
 * Select a site. `origin` tells listeners who asked, so the globe can skip
 * re-flying when the click came from the globe itself.
 */
export function select(id, { origin = 'ui', fly = true } = {}) {
  const site = id ? state.byId.get(id) : null;
  if (id && !site) return null;
  state.selectedId = site ? site.id : null;
  syncURL();
  emit('selected', { site, origin, fly });
  return site;
}

/** The full OGC Feature for the dossier, fetched on demand. */
export function feature(id, signal) {
  return loadFeature(id, signal);
}

/* -------------------------------------------------------------------- URL */

let suppressURL = false;

function syncURL() {
  if (suppressURL) return;
  const p = new URLSearchParams();
  if (state.selectedId) p.set('site', state.selectedId);
  if (state.query) p.set('q', state.query);
  if (state.region !== 'all') p.set('region', state.region);
  if (state.activeCategories.size) {
    p.set('cat', [...state.activeCategories].join(','));
  }
  if (state.sort !== 'name') p.set('sort', state.sort);
  const qs = p.toString();
  const next = location.pathname + (qs ? `?${qs}` : '') + location.hash;
  history.replaceState(null, '', next);
}

/** Apply ?site=&q=&region=&cat=&sort= from the address bar. */
export function applyURL() {
  const p = new URLSearchParams(location.search);
  suppressURL = true;
  state.query = p.get('q') ?? '';
  const region = p.get('region');
  state.region = region && state.regions.includes(region) ? region : 'all';
  state.activeCategories = new Set(
    (p.get('cat') ?? '').split(',').filter(Boolean));
  const sort = p.get('sort');
  state.sort = ['name', 'region', 'category', 'distance'].includes(sort)
    ? sort : 'name';
  recompute();
  suppressURL = false;
  emit('categories', state.activeCategories);
  const site = p.get('site');
  return site && state.byId.has(site) ? site : null;
}
