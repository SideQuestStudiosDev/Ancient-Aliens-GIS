/* ==========================================================================
   Small shared helpers. No dependencies.
   ========================================================================== */

export const $  = (sel, root = document) => root.querySelector(sel);
export const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

/** Create an element. `attrs.class`, `.dataset`, `.aria`, `on*` handlers. */
export function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v == null || v === false) continue;
    if (k === 'class') node.className = v;
    else if (k === 'html') node.innerHTML = v;
    else if (k === 'text') node.textContent = v;
    else if (k === 'dataset') Object.assign(node.dataset, v);
    else if (k === 'style' && typeof v === 'object') Object.assign(node.style, v);
    else if (k.startsWith('on') && typeof v === 'function') {
      node.addEventListener(k.slice(2).toLowerCase(), v);
    } else node.setAttribute(k, v === true ? '' : v);
  }
  for (const child of [children].flat(3)) {
    if (child == null || child === false) continue;
    node.append(child.nodeType ? child : document.createTextNode(String(child)));
  }
  return node;
}

export const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => (
  { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

export function debounce(fn, ms = 150) {
  let t;
  const wrapped = (...args) => {
    clearTimeout(t);
    t = setTimeout(() => fn(...args), ms);
  };
  wrapped.cancel = () => clearTimeout(t);
  return wrapped;
}

export const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));

/* ---------------------------------------------------------------- geodesy */

/** Great-circle distance in km (mean-Earth sphere). */
export function haversineKm(lat1, lon1, lat2, lon2) {
  const R = 6371.0088, rad = Math.PI / 180;
  const dLat = (lat2 - lat1) * rad;
  const dLon = (lon2 - lon1) * rad;
  const a = Math.sin(dLat / 2) ** 2
    + Math.cos(lat1 * rad) * Math.cos(lat2 * rad) * Math.sin(dLon / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(a));
}

/** Decimal degrees → degrees/minutes/seconds with hemisphere letter. */
export function toDMS(value, axis) {
  if (value == null || Number.isNaN(value)) return '—';
  const hemi = axis === 'lat' ? (value >= 0 ? 'N' : 'S') : (value >= 0 ? 'E' : 'W');
  const abs = Math.abs(value);
  const d = Math.floor(abs);
  const mFloat = (abs - d) * 60;
  const m = Math.floor(mFloat);
  const s = ((mFloat - m) * 60).toFixed(1);
  return `${d}° ${String(m).padStart(2, '0')}′ ${String(s).padStart(4, '0')}″ ${hemi}`;
}

export const fmtDeg = (v, places = 5) =>
  v == null || Number.isNaN(v) ? '—' : v.toFixed(places) + '°';

/** Metres → a short human string (m / km, thousands separated). */
export function fmtDistance(m) {
  if (m == null || !Number.isFinite(m)) return '—';
  if (Math.abs(m) < 1000) return `${Math.round(m)} m`;
  const km = m / 1000;
  return `${km < 20 ? km.toFixed(1) : Math.round(km).toLocaleString('en')} km`;
}

export const fmtKm = (km) => fmtDistance(km * 1000);

/* ------------------------------------------------------------------ search */

/** Fold diacritics and case so "Gobekli" matches "Göbekli". */
export const fold = (s) => String(s ?? '')
  .normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();

/** Wrap each match of `needle` in <b>. Input is escaped first. */
export function highlight(haystack, needle) {
  const safe = esc(haystack);
  if (!needle) return safe;
  const f = fold(haystack), n = fold(needle);
  const at = f.indexOf(n);
  if (at < 0) return safe;
  // Indices are valid against the original because fold() is 1:1 per char here.
  const head = esc(haystack.slice(0, at));
  const mid  = esc(haystack.slice(at, at + needle.length));
  const tail = esc(haystack.slice(at + needle.length));
  return `${head}<b>${mid}</b>${tail}`;
}

/* ------------------------------------------------------------------ misc */

export const hostOf = (url) => {
  try { return new URL(url).host.replace(/^www\./, ''); }
  catch { return url; }
};

export const prefersReducedMotion = () =>
  window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false;

export const isCoarsePointer = () =>
  window.matchMedia?.('(pointer: coarse)').matches ?? false;

/** Fetch JSON with a timeout and a useful error message. */
export async function getJSON(url, { timeout = 20000, signal } = {}) {
  const ctl = new AbortController();
  const timer = setTimeout(() => ctl.abort(new Error('timeout')), timeout);
  signal?.addEventListener('abort', () => ctl.abort(signal.reason));
  try {
    const resp = await fetch(url, { signal: ctl.signal, cache: 'default' });
    if (!resp.ok) throw new Error(`${resp.status} ${resp.statusText} — ${url}`);
    return await resp.json();
  } finally {
    clearTimeout(timer);
  }
}

/** Resolve a path against the document, so the app works from any subpath. */
export const appURL = (path) => new URL(path, document.baseURI).href;
