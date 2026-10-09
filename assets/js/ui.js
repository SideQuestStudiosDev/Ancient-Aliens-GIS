/* ==========================================================================
   All DOM rendering. Reads from store.js, drives globe.js, owns no state of
   its own beyond view concerns (which tab is open, how far the mobile sheet
   is pulled up, how many list rows have been materialised).
   ========================================================================== */

import { $, $$, el, esc, highlight, debounce, clamp, toDMS, fmtDeg,
         fmtDistance, fmtKm, hostOf, isCoarsePointer } from './util.js';
import { BASE_LAYERS, OVERLAYS, APP } from './config.js';
import * as store from './store.js';
import * as G from './globe.js';
import { loadServiceMetadata, featureURL } from './ogc.js';

const CATEGORY_META = {
  megalithic: ['Megalithic', '--cat-megalithic'],
  pyramid: ['Pyramid / Temple', '--cat-pyramid'],
  geoglyph: ['Geoglyph', '--cat-geoglyph'],
  underground: ['Subterranean', '--cat-underground'],
  underwater: ['Submerged', '--cat-underwater'],
  ufo: ['UFO Incident', '--cat-ufo'],
  military: ['Military / Secure', '--cat-military'],
  research: ['Research Centre', '--cat-research'],
  sacred: ['Sacred Site', '--cat-sacred'],
  anomaly: ['Anomaly Zone', '--cat-anomaly'],
  landform: ['Landform', '--cat-landform'],
  city: ['Ancient City', '--cat-city'],
  artifact: ['Artefact Locus', '--cat-artifact'],
  region: ['Broad Region', '--cat-region'],
  offworld: ['Beyond Earth', '--cat-offworld'],
};

const PRECISION_NOTE = {
  exact: ['Surveyed point', 'Coordinates locate the monument or structure itself.'],
  approximate: ['Approximate', 'The right valley, hill or settlement; the specific feature is not published to better than a few kilometres.'],
  area: ['Region centroid', 'This entry describes an area, not a point. The circle on the globe shows its approximate extent.'],
  uncertain: ['Unresolved reference', 'The series’ reference could not be tied to a published place name. Treat the position as a label, not a location.'],
};

const ICON = {
  out: '<svg width="13" height="13" viewBox="0 0 14 14" fill="none" aria-hidden="true"><path d="M5.5 2.5H2.5v9h9v-3M8.5 2.5h3v3M11.5 2.5 6 8" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  wiki: '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M1.6 4.4h3M11.4 4.4h3M4.6 4.4 7 11.6l1.6-4.4M8 4.4l2 7.2 2.4-7.2" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  official: '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M8 1.8 13.6 4v4c0 3-2.3 5.2-5.6 6.2C4.7 13.2 2.4 11 2.4 8V4L8 1.8Z" stroke="currentColor" stroke-width="1.3"/><path d="m5.8 7.9 1.6 1.7 3-3.3" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>',
  data: '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true"><ellipse cx="8" cy="4" rx="5" ry="2.1" stroke="currentColor" stroke-width="1.3"/><path d="M3 4v8c0 1.2 2.2 2.1 5 2.1s5-.9 5-2.1V4M3 8c0 1.2 2.2 2.1 5 2.1s5-.9 5-2.1" stroke="currentColor" stroke-width="1.3"/></svg>',
  ref: '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M3 2.6h7l3 3v7.8H3V2.6Z" stroke="currentColor" stroke-width="1.3"/><path d="M5.4 7.4h5.2M5.4 10h3.4" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>',
};

const dom = {};
const view = { tab: 'sites', rendered: 0, pageSize: 48, hoverId: null };

/* ========================================================================= */
/* boot                                                                      */
/* ========================================================================= */

export function cacheDom() {
  Object.assign(dom, {
    app: $('#app'),
    boot: $('#boot'), bootMsg: $('#bootMsg'),
    panel: $('#panel'), grab: $('#panelGrab'),
    tabs: $$('.panel__tab'), panes: $$('.tabpane'),
    searchCombo: $('#searchCombo'), searchInput: $('#searchInput'),
    searchResults: $('#searchResults'), searchClear: $('#searchClear'),
    filterRegion: $('#filterRegion'), sortBy: $('#sortBy'),
    categoryChips: $('#categoryChips'), resultCount: $('#resultCount'),
    btnResetFilters: $('#btnResetFilters'),
    sitelist: $('#sitelist'), detail: $('#detail'),
    layersPane: $('#layersPane'), servicesPane: $('#servicesPane'),
    readout: $('#readout'), roLat: $('#roLat'), roLon: $('#roLon'),
    roElev: $('#roElev'), roCam: $('#roCam'), roScene: $('#roScene'),
    tilesBusy: $('#tilesBusy'), tilesBusyText: $('#tilesBusyText'),
    attrib: $('#attrib'), attribBody: $('#attribBody'),
    attribToggle: $('#attribToggle'), toasts: $('#toasts'),
    helpModal: $('#helpModal'), helpClose: $('#helpClose'), btnHelp: $('#btnHelp'),
    btnPanel: $('#btnPanel'), btnHome: $('#btnHome'), btnFx: $('#btnFx'),
    btnGeolocate: $('#btnGeolocate'),
  });
}

export function bootMessage(text) {
  if (dom.bootMsg) dom.bootMsg.textContent = text;
}

export function hideBoot() {
  dom.boot?.setAttribute('hidden', '');
  setTimeout(() => dom.boot?.remove(), 600);
}

/* ========================================================================= */
/* toasts                                                                    */
/* ========================================================================= */

export function toast(message, { kind = 'info', ms = 4200 } = {}) {
  const node = el('div', { class: 'toast', dataset: { kind }, role: 'status' },
                  message);
  dom.toasts.append(node);
  setTimeout(() => {
    node.style.transition = 'opacity .3s, transform .3s';
    node.style.opacity = '0';
    node.style.transform = 'translateY(-6px)';
    setTimeout(() => node.remove(), 320);
  }, ms);
  return node;
}

/* ========================================================================= */
/* tabs                                                                      */
/* ========================================================================= */

export function showTab(name) {
  view.tab = name;
  const map = { sites: 'tabSites', detail: 'tabDetail',
                layers: 'tabLayers', services: 'tabServices' };
  for (const tab of dom.tabs) {
    const on = tab.id === map[name];
    tab.setAttribute('aria-selected', String(on));
  }
  for (const pane of dom.panes) {
    pane.classList.toggle('is-active',
      pane.id.toLowerCase() === `pane${name}`.toLowerCase());
  }
  if (name === 'services' && !dom.servicesPane.dataset.loaded) renderServices();
  if (isCoarsePointer() && dom.panel.dataset.snap === 'peek') snapSheet('half');
}

function wireTabs() {
  const map = { tabSites: 'sites', tabDetail: 'detail',
                tabLayers: 'layers', tabServices: 'services' };
  for (const tab of dom.tabs) {
    tab.addEventListener('click', () => showTab(map[tab.id]));
    tab.addEventListener('keydown', (e) => {
      const order = dom.tabs;
      const i = order.indexOf(tab);
      let next = null;
      if (e.key === 'ArrowRight') next = order[(i + 1) % order.length];
      if (e.key === 'ArrowLeft') next = order[(i - 1 + order.length) % order.length];
      if (next) { e.preventDefault(); next.focus(); next.click(); }
    });
  }
}

/* ========================================================================= */
/* mobile bottom sheet                                                       */
/* ========================================================================= */

const SNAPS = ['hidden', 'peek', 'half', 'full'];

export function snapSheet(snap) {
  if (!SNAPS.includes(snap)) return;
  dom.panel.dataset.snap = snap;
  dom.panel.classList.remove('is-dragging');
  dom.panel.style.removeProperty('--sheet-h');
}

function wireSheet() {
  const grab = dom.grab;
  if (!grab) return;

  // Snap heights in px, resolved against the live viewport so they track
  // dvh changes when a mobile browser's toolbars collapse.
  const heightFor = (snap) => {
    const vh = window.innerHeight;
    return { hidden: 56, peek: 148, half: vh * 0.52, full: vh * 0.88 }[snap] ?? 148;
  };
  const MIN = 56;
  const max = () => window.innerHeight * 0.88;

  let startY = 0, startH = 0, dragging = false;

  const onDown = (e) => {
    if (window.innerWidth >= 900) return;
    dragging = true;
    startY = e.clientY;
    startH = dom.panel.getBoundingClientRect().height;
    dom.panel.classList.add('is-dragging');
    grab.setPointerCapture?.(e.pointerId);
  };

  const onMove = (e) => {
    if (!dragging) return;
    // Dragging up (negative dy) grows the sheet.
    const h = clamp(startH - (e.clientY - startY), MIN, max());
    dom.panel.style.setProperty('--sheet-h', `${h}px`);
  };

  const onUp = (e) => {
    if (!dragging) return;
    dragging = false;
    const dy = e.clientY - startY;
    const h = clamp(startH - dy, MIN, max());
    // Pick the nearest snap, nudged by the flick direction so a deliberate
    // swipe always changes state even if it stopped short.
    const biased = h + (dy < -40 ? 60 : dy > 40 ? -60 : 0);
    let best = 'peek', bestGap = Infinity;
    for (const snap of ['peek', 'half', 'full']) {
      const gap = Math.abs(heightFor(snap) - biased);
      if (gap < bestGap) { bestGap = gap; best = snap; }
    }
    snapSheet(best);
    G.resize();
  };

  grab.addEventListener('pointerdown', onDown);
  grab.addEventListener('pointermove', onMove);
  grab.addEventListener('pointerup', onUp);
  grab.addEventListener('pointercancel', onUp);
  grab.addEventListener('keydown', (e) => {
    if (e.key !== 'Enter' && e.key !== ' ') return;
    e.preventDefault();
    const order = ['peek', 'half', 'full'];
    const i = order.indexOf(dom.panel.dataset.snap);
    snapSheet(order[(i + 1) % order.length]);
    G.resize();
  });
  grab.addEventListener('dblclick', () => { snapSheet('peek'); G.resize(); });

  // A snap expressed in dvh has to be re-resolved when the viewport changes.
  window.addEventListener('resize', () => {
    if (!dragging) dom.panel.style.removeProperty('--sheet-h');
  }, { passive: true });
}

export function togglePanel() {
  if (window.innerWidth >= 900) {
    dom.panel.classList.toggle('is-collapsed');
    dom.btnPanel.setAttribute('aria-pressed',
      String(!dom.panel.classList.contains('is-collapsed')));
  } else {
    const order = ['hidden', 'peek', 'half', 'full'];
    const i = order.indexOf(dom.panel.dataset.snap);
    snapSheet(order[(i + 1) % order.length]);
  }
  G.resize();
}

/* ========================================================================= */
/* filters                                                                   */
/* ========================================================================= */

export function renderFilters() {
  // Derived from the catalogue so the placeholder can never go stale.
  dom.searchInput.placeholder =
    `Search ${store.state.count} sites, countries, categories…`;

  const regionSel = dom.filterRegion;
  regionSel.replaceChildren(
    el('option', { value: 'all' }, `All regions (${store.state.count})`),
    ...store.state.regions.map((r) => {
      const n = store.state.sites.filter((s) => s.r === r).length;
      return el('option', { value: r }, `${r} (${n})`);
    }),
  );
  regionSel.value = store.state.region;
  dom.sortBy.value = store.state.sort;

  const counts = new Map();
  for (const s of store.state.sites) {
    counts.set(s.c, (counts.get(s.c) ?? 0) + 1);
  }
  const order = [...counts.keys()].sort((a, b) =>
    (CATEGORY_META[a]?.[0] ?? a).localeCompare(CATEGORY_META[b]?.[0] ?? b));
  store.setCategoryOrder(order);

  dom.categoryChips.replaceChildren(...order.map((id) => {
    const [label, token] = CATEGORY_META[id] ?? [id, '--cat-megalithic'];
    const on = store.state.activeCategories.has(id);
    return el('button', {
      class: 'toggle', type: 'button',
      'aria-pressed': String(on),
      dataset: { cat: id },
      title: `${label} — ${counts.get(id)} site${counts.get(id) === 1 ? '' : 's'}`,
      style: { '--tog-color': `var(${token})` },
      onClick: () => store.toggleCategory(id),
    }, [el('span', { class: 'toggle__dot' }), label]);
  }));

  regionSel.onchange = () => store.setRegion(regionSel.value);
  dom.sortBy.onchange = () => store.setSort(dom.sortBy.value);
  dom.btnResetFilters.onclick = () => {
    store.resetFilters();
    dom.searchInput.value = '';
    dom.searchClear.hidden = true;
  };
}

function syncChips() {
  for (const chip of $$('[data-cat]', dom.categoryChips)) {
    chip.setAttribute('aria-pressed',
      String(store.state.activeCategories.has(chip.dataset.cat)));
  }
  dom.filterRegion.value = store.state.region;
  dom.sortBy.value = store.state.sort;
}

/* ========================================================================= */
/* site list                                                                 */
/* ========================================================================= */

function pinSvg(cat) {
  const token = (CATEGORY_META[cat] ?? [, '--cat-megalithic'])[1];
  return el('span', {
    class: 'site-row__pin',
    style: { color: `var(${token})` },
    html: `<svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">
             <path d="M9 16.2s5.4-5 5.4-9A5.4 5.4 0 0 0 3.6 7.2c0 4 5.4 9 5.4 9Z"
                   fill="rgba(7,11,20,.9)" stroke="currentColor" stroke-width="1.5"/>
             <circle cx="9" cy="7" r="2.1" fill="currentColor"/>
           </svg>`,
  });
}

function siteRow(site) {
  const [catLabel] = CATEGORY_META[site.c] ?? [site.c];
  const sub = [site.s || site.y, catLabel].filter(Boolean).join(' · ');
  const row = el('button', {
    class: 'site-row', type: 'button', role: 'listitem',
    dataset: { id: site.id },
    'aria-current': String(store.state.selectedId === site.id),
    onClick: () => store.select(site.id, { origin: 'list' }),
    onMouseenter: () => G.render(),
  }, [
    pinSvg(site.c),
    el('span', { class: 'site-row__main' }, [
      el('span', { class: 'site-row__name', html: highlight(site.n, store.state.query) }),
      el('span', { class: 'site-row__sub', text: sub }),
    ]),
    el('span', { class: 'site-row__tail' }, [
      site.p !== 'exact'
        ? el('span', { class: 'chip', title: PRECISION_NOTE[site.p]?.[1] },
             PRECISION_NOTE[site.p]?.[0] ?? site.p)
        : null,
      store.state.sort === 'distance' && Number.isFinite(site._dist)
        ? el('span', { class: 'site-row__dist', text: fmtKm(site._dist) })
        : null,
    ]),
  ]);
  return row;
}

export function renderList({ reset = true } = {}) {
  const list = store.state.visible;
  dom.resultCount.textContent = list.length === store.state.count
    ? `${list.length} sites`
    : `${list.length} of ${store.state.count} sites`;

  if (reset) {
    view.rendered = 0;
    dom.sitelist.replaceChildren();
    dom.sitelist.scrollTop = 0;
  }
  if (!list.length) {
    dom.sitelist.replaceChildren(el('div', { class: 'empty-state' }, [
      el('p', {}, 'No sites match these filters.'),
      el('button', { class: 'btn btn--sm', type: 'button',
                     onClick: () => dom.btnResetFilters.click() }, 'Clear filters'),
    ]));
    return;
  }
  appendRows();
}

function appendRows() {
  const list = store.state.visible;
  const end = Math.min(view.rendered + view.pageSize, list.length);
  if (end <= view.rendered) return;
  const frag = document.createDocumentFragment();
  let lastGroup = null;

  // Group headings only make sense for the grouped sorts.
  const grouped = store.state.sort === 'region' || store.state.sort === 'category';
  if (grouped && view.rendered > 0) {
    const prev = list[view.rendered - 1];
    lastGroup = store.state.sort === 'region'
      ? prev.r : (CATEGORY_META[prev.c]?.[0] ?? prev.c);
  }

  for (let i = view.rendered; i < end; i++) {
    const site = list[i];
    if (grouped) {
      const g = store.state.sort === 'region'
        ? site.r : (CATEGORY_META[site.c]?.[0] ?? site.c);
      if (g !== lastGroup) {
        frag.append(el('div', { class: 'sitelist__group-label eyebrow', text: g }));
        lastGroup = g;
      }
    }
    frag.append(siteRow(site));
  }
  dom.sitelist.append(frag);
  view.rendered = end;
}

function wireListScroll() {
  dom.sitelist.addEventListener('scroll', () => {
    const { scrollTop, clientHeight, scrollHeight } = dom.sitelist;
    if (scrollHeight - (scrollTop + clientHeight) < 400) appendRows();
  }, { passive: true });
}

export function markSelectedRow(id) {
  for (const row of $$('.site-row', dom.sitelist)) {
    row.setAttribute('aria-current', String(row.dataset.id === id));
  }
  const row = dom.sitelist.querySelector(`.site-row[data-id="${CSS.escape(id ?? '')}"]`);
  row?.scrollIntoView({ block: 'nearest' });
}

/** Ensure a selected site is materialised even if it is past the render window. */
export function ensureRowVisible(id) {
  const idx = store.state.visible.findIndex((s) => s.id === id);
  if (idx < 0) return;
  while (view.rendered <= idx && view.rendered < store.state.visible.length) {
    appendRows();
  }
  markSelectedRow(id);
}

/* ========================================================================= */
/* search type-ahead                                                         */
/* ========================================================================= */

let activeHit = -1;

function closeSearch() {
  dom.searchResults.hidden = true;
  dom.searchCombo.setAttribute('aria-expanded', 'false');
  activeHit = -1;
}

function renderSearchHits(hits, query) {
  if (!query.trim()) { closeSearch(); return; }
  if (!hits.length) {
    dom.searchResults.replaceChildren(
      el('div', { class: 'search__empty' },
         `Nothing matches “${query}”. Try a country, a category, or an alias.`));
  } else {
    dom.searchResults.replaceChildren(...hits.map((s, i) => el('button', {
      class: 'search__hit', type: 'button', role: 'option',
      id: `hit-${i}`, 'aria-selected': 'false',
      dataset: { id: s.id },
      onClick: () => {
        dom.searchInput.value = s.n;
        closeSearch();
        store.select(s.id, { origin: 'search' });
      },
    }, [
      pinSvg(s.c),
      el('span', {}, [
        el('span', { class: 'search__hit-name', html: highlight(s.n, query) }),
        el('br'),
        el('span', { class: 'search__hit-meta',
                     text: [s.y || s.r, CATEGORY_META[s.c]?.[0]]
                       .filter(Boolean).join(' · ') }),
      ]),
    ])));
  }
  dom.searchResults.hidden = false;
  dom.searchCombo.setAttribute('aria-expanded', 'true');
  activeHit = -1;
}

function moveHit(delta) {
  const hits = $$('.search__hit', dom.searchResults);
  if (!hits.length) return;
  if (activeHit >= 0) hits[activeHit]?.setAttribute('aria-selected', 'false');
  activeHit = (activeHit + delta + hits.length + 1) % (hits.length + 1) - 1;
  if (activeHit < 0) {
    dom.searchInput.removeAttribute('aria-activedescendant');
    return;
  }
  const hit = hits[activeHit];
  hit.setAttribute('aria-selected', 'true');
  hit.scrollIntoView({ block: 'nearest' });
  dom.searchInput.setAttribute('aria-activedescendant', hit.id);
}

function wireSearch() {
  const run = debounce(() => {
    const q = dom.searchInput.value;
    store.setQuery(q);
    renderSearchHits(store.rank(q), q);
  }, 110);

  dom.searchInput.addEventListener('input', () => {
    dom.searchClear.hidden = !dom.searchInput.value;
    run();
  });

  dom.searchInput.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowDown') { e.preventDefault(); moveHit(1); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); moveHit(-1); }
    else if (e.key === 'Enter') {
      const hits = $$('.search__hit', dom.searchResults);
      const pick = hits[activeHit] ?? hits[0];
      if (pick) { e.preventDefault(); pick.click(); }
    } else if (e.key === 'Escape') {
      if (!dom.searchResults.hidden) { e.stopPropagation(); closeSearch(); }
      else { dom.searchInput.value = ''; dom.searchClear.hidden = true; run(); }
    }
  });

  dom.searchClear.addEventListener('click', () => {
    dom.searchInput.value = '';
    dom.searchClear.hidden = true;
    dom.searchInput.focus();
    store.setQuery('');
    closeSearch();
  });

  document.addEventListener('pointerdown', (e) => {
    if (!dom.searchCombo.contains(e.target)) closeSearch();
  });
}

export const focusSearch = () => {
  dom.searchInput.focus();
  dom.searchInput.select();
};

/* ========================================================================= */
/* dossier                                                                   */
/* ========================================================================= */

function section(title, children, { accent } = {}) {
  return el('section', { class: 'section' }, [
    el('div', { class: 'section__head' }, [
      el('h3', { text: title }),
      el('span', { class: 'section__rule' }),
    ]),
    children,
  ]);
}

function callout(kind, label, text) {
  return el('div', { class: `callout callout--${kind}` }, [
    el('div', { class: 'callout__label' }, label),
    el('p', { text }),
  ]);
}

function linkRow(label, url, kind) {
  const icon = kind === 'wikipedia' ? ICON.wiki
    : kind === 'official' ? ICON.official
    : kind === 'data' ? ICON.data : ICON.ref;
  return el('a', { href: url, target: '_blank', rel: 'noopener noreferrer' }, [
    el('span', { class: 'linklist__icon', html: icon }),
    el('span', {}, [
      el('span', { class: 'linklist__label', text: label }), el('br'),
      el('span', { class: 'linklist__host', text: hostOf(url) }),
    ]),
    el('span', { class: 'linklist__out', html: ICON.out }),
  ]);
}

export function renderDetailPlaceholder() {
  dom.detail.replaceChildren(el('div', { class: 'empty-state' }, [
    el('svg', { width: '44', height: '44', viewBox: '0 0 24 24', fill: 'none',
                style: { color: 'var(--ink-dim)' },
                html: '<circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.2"/><ellipse cx="12" cy="12" rx="9" ry="3.4" stroke="currentColor" stroke-width="1"/><path d="M12 3v18" stroke="currentColor" stroke-width="1"/>' }),
    el('p', {}, 'Pick a site from the list, search for one, or tap a marker on the globe to open its dossier.'),
  ]));
}

export function renderDetailLoading(site) {
  dom.detail.replaceChildren(
    detailHead(site),
    el('div', { class: 'detail__scroll' }, [
      el('p', { class: 'dim mono', text: 'Loading dossier…' }),
    ]),
  );
}

function detailHead(site) {
  return el('div', { class: 'detail__head' }, [
    el('button', {
      class: 'icon-btn', type: 'button', 'aria-label': 'Back to site list',
      onClick: () => showTab('sites'),
      html: '<svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true"><path d="M11 4 6 9l5 5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    }),
    el('div', { class: 'grow truncate' }, [
      el('div', { class: 'eyebrow', text: site.r }),
      el('div', { class: 'truncate',
                  style: { fontFamily: 'var(--font-ui)', fontWeight: 600,
                           color: 'var(--ink-bright)' }, text: site.n }),
    ]),
    el('button', {
      class: 'icon-btn', type: 'button', 'aria-label': 'Fly to this site again',
      title: 'Re-centre the globe here',
      onClick: () => { G.globe.pendingFlight = site.id; G.flyToSite(site); },
      html: '<svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true"><path d="M2.5 9h3M12.5 9h3M9 2.5v3M9 12.5v3" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/><circle cx="9" cy="9" r="3.4" stroke="currentColor" stroke-width="1.4"/></svg>',
    }),
  ]);
}

export function renderDetail(site, feature) {
  const p = feature?.properties ?? {};
  const [catLabel, catToken] = CATEGORY_META[site.c] ?? [site.c, '--cat-megalithic'];
  const [precLabel, precNote] = PRECISION_NOTE[p.location_precision ?? site.p]
    ?? ['', ''];
  const offworld = p.celestial_body && p.celestial_body !== 'earth';

  const geo = el('dl', { class: 'geo-grid' });
  const addGeo = (k, v) => {
    if (v == null || v === '' ) return;
    geo.append(el('dt', { text: k }),
               v.nodeType ? el('dd', {}, v) : el('dd', { text: v }));
  };

  addGeo('Country', p.country || '—');
  addGeo('Region', p.region);
  addGeo('Category', catLabel);
  if (offworld) {
    addGeo('Body', 'The Moon');
    addGeo('Selenographic', `${fmtDeg(p.latitude ?? site.lat, 3)}, ${fmtDeg(p.longitude ?? site.lon, 3)}`);
  } else {
    addGeo('Latitude', `${fmtDeg(p.latitude)}  ${toDMS(p.latitude, 'lat')}`);
    addGeo('Longitude', `${fmtDeg(p.longitude)}  ${toDMS(p.longitude, 'lon')}`);
    addGeo('CRS', 'EPSG:4326 / OGC CRS84');
  }
  if (p.radius_km) addGeo('Extent', `≈ ${p.radius_km} km radius`);
  addGeo('Precision', el('span', {}, [
    el('span', { class: 'chip', style: { color: `var(${catToken})` } }, precLabel),
  ]));
  addGeo('Coord. source',
    p.coordinate_source === 'wikipedia' ? 'Wikidata / Wikipedia' : 'Project catalogue');
  if (feature?.geometry?.type) addGeo('Geometry', feature.geometry.type);
  if (p.wikidata_id) addGeo('Wikidata', p.wikidata_id);
  if (p.tags?.length) {
    addGeo('Tags', el('span', {}, p.tags.join(', ')));
  }

  const links = [];
  if (p.wikipedia_url) {
    links.push(linkRow(`Wikipedia — ${p.wikipedia_title}`, p.wikipedia_url,
                       'wikipedia'));
  }
  if (p.wikidata_id) {
    links.push(linkRow(`Wikidata — ${p.wikidata_id}`,
                       `https://www.wikidata.org/wiki/${p.wikidata_id}`, 'data'));
  }
  for (const link of feature?.links ?? []) {
    if (link.rel === 'self' || link.rel === 'collection'
        || link.rel === 'alternate' || link.rel === 'describedby') continue;
    links.push(linkRow(link.title ?? link.href, link.href,
                       link.rel === 'canonical' ? 'official' : 'reference'));
  }
  links.push(linkRow('Ancient Aliens — official show pages (History)',
                     'https://www.history.com/shows/ancient-aliens', 'official'));
  links.push(linkRow('Episode index (Wikipedia)',
                     'https://en.wikipedia.org/wiki/List_of_Ancient_Aliens_episodes',
                     'reference'));
  if (!offworld) {
    links.push(linkRow('OpenStreetMap at this location',
      `https://www.openstreetmap.org/?mlat=${p.latitude}&mlon=${p.longitude}#map=14/${p.latitude}/${p.longitude}`,
      'reference'));
  }
  links.push(linkRow('This site as GeoJSON (OGC API — Features)',
                     featureURL(site.id), 'data'));

  dom.detail.replaceChildren(
    detailHead(site),
    el('div', { class: 'detail__scroll scroll-y' }, [
      el('div', { class: 'detail__eyebrow' }, [
        el('span', { class: 'chip', style: { color: `var(${catToken})` } },
           [el('span', { class: 'chip__dot' }), catLabel]),
        p.country ? el('span', { class: 'chip' }, p.country) : null,
        offworld ? el('span', { class: 'chip',
                                style: { color: 'var(--cat-offworld)' } },
                      'Not on Earth') : null,
      ]),
      el('h2', { class: 'detail__title', text: p.name ?? site.n }),
      p.subtitle ? el('p', { class: 'detail__subtitle', text: p.subtitle }) : null,

      offworld ? el('div', { class: 'note', style: { marginTop: 'var(--s-3)' } },
        'This entry is not a terrestrial location, so it has no marker on the '
        + 'globe. Coordinates below are selenographic.') : null,

      section('The claim', callout('claim', [
        el('span', { html: '<svg width="13" height="13" viewBox="0 0 14 14" fill="none"><path d="M7 1.5 8.4 5l3.6.3-2.8 2.3.9 3.5L7 9.3l-3.1 1.8.9-3.5L2 5.3 5.6 5 7 1.5Z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/></svg>' }),
        'As presented in the series',
      ], p.claim ?? '')),

      p.summary ? section('The record', [
        callout('record', [
          el('span', { html: '<svg width="13" height="13" viewBox="0 0 14 14" fill="none"><rect x="2.5" y="1.8" width="9" height="10.4" rx="1" stroke="currentColor" stroke-width="1.2"/><path d="M4.8 4.6h4.4M4.8 7h4.4M4.8 9.4h2.6" stroke="currentColor" stroke-width="1.1" stroke-linecap="round"/></svg>' }),
          'Encyclopaedic summary',
        ], p.summary),
        el('p', { class: 'note' }, [
          'From the English Wikipedia article ',
          el('a', { href: p.wikipedia_url, target: '_blank', rel: 'noopener' },
             p.wikipedia_title),
          ', reused under CC BY-SA 4.0.',
        ]),
      ]) : section('The record', el('p', { class: 'note' },
        'No English Wikipedia article covers this site directly — which is '
        + 'itself informative: the location is not independently documented '
        + 'in the encyclopaedic record.')),

      section('Context', callout('context', [
        el('span', { html: '<svg width="13" height="13" viewBox="0 0 14 14" fill="none"><circle cx="7" cy="7" r="5.4" stroke="currentColor" stroke-width="1.2"/><path d="M7 4.2v.1M7 6.2v3.6" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>' }),
        'What the evidence shows',
      ], p.context ?? '')),

      section('Geographic data', [
        geo,
        precNote ? el('p', { class: 'note', text: precNote }) : null,
      ]),

      section('Sources & further reading', el('div', { class: 'linklist' }, links)),
    ]),
  );
  dom.detail.querySelector('.detail__scroll').scrollTop = 0;
}

/* ========================================================================= */
/* layers tab                                                                */
/* ========================================================================= */

export function renderLayers() {
  const baseGroup = el('div', { class: 'layer-group', role: 'radiogroup',
                                'aria-label': 'Base layer' });
  for (const spec of BASE_LAYERS) {
    baseGroup.append(el('button', {
      class: 'layer-opt', type: 'button', role: 'radio',
      'aria-checked': String(G.globe.layers.baseId === spec.id),
      dataset: { base: spec.id },
      onClick: async () => {
        await G.setBaseLayer(spec.id);
        for (const b of $$('[data-base]', dom.layersPane)) {
          b.setAttribute('aria-checked', String(b.dataset.base === spec.id));
        }
      },
    }, [
      el('span', { class: 'layer-opt__radio' }),
      el('span', {}, [
        el('span', { class: 'layer-opt__name', text: spec.name }), el('br'),
        el('span', { class: 'layer-opt__meta',
                     text: spec.meta + (spec.note ? ` · ${spec.note}` : '') }),
      ]),
      el('span', { class: 'layer-opt__badge', dataset: { proto: spec.proto },
                   text: spec.proto }),
    ]));
  }

  const overlayGroup = el('div', { class: 'layer-group' });
  for (const spec of OVERLAYS) {
    const on = G.globe.layers.overlays.has(spec.id);
    const btn = el('button', {
      class: 'switch-row', type: 'button', role: 'switch',
      'aria-checked': String(on), dataset: { overlay: spec.id },
    }, [
      el('span', { class: 'switch-row__text' }, [
        el('span', { class: 'switch-row__name', text: spec.name }),
        el('span', { class: 'switch-row__hint', text: spec.meta }),
      ]),
      el('span', { class: 'switch' }),
    ]);
    btn.addEventListener('click', async () => {
      const next = btn.getAttribute('aria-checked') !== 'true';
      btn.setAttribute('aria-checked', String(next));
      await G.setOverlay(spec.id, next);
    });
    overlayGroup.append(btn);
  }

  const slider = (label, min, max, step, value, fmt, onInput) => {
    const out = el('span', { class: 'slider-row__val', text: fmt(value) });
    const input = el('input', {
      type: 'range', min, max, step, value,
      'aria-label': label,
      onInput: (e) => {
        const v = Number(e.target.value);
        out.textContent = fmt(v);
        onInput(v);
      },
    });
    return el('div', { class: 'slider-row' }, [
      el('div', { class: 'slider-row__head' }, [
        el('span', { class: 'eyebrow', text: label }), out,
      ]),
      input,
    ]);
  };

  const sceneGroup = el('div', { class: 'layer-group' }, [
    slider('Imagery brightness', 0.3, 1.8, 0.05, 1,
           (v) => `${Math.round(v * 100)}%`, (v) => G.setBaseBrightness(v)),
    slider('Label opacity', 0, 1, 0.05, 0.9,
           (v) => `${Math.round(v * 100)}%`, (v) => G.setOverlayAlpha('labels', v)),
  ]);

  const toggles = el('div', { class: 'layer-group' });
  const switchRow = (name, hint, checked, onChange) => {
    const btn = el('button', {
      class: 'switch-row', type: 'button', role: 'switch',
      'aria-checked': String(checked),
    }, [
      el('span', { class: 'switch-row__text' }, [
        el('span', { class: 'switch-row__name', text: name }),
        el('span', { class: 'switch-row__hint', text: hint }),
      ]),
      el('span', { class: 'switch' }),
    ]);
    btn.addEventListener('click', () => {
      const next = btn.getAttribute('aria-checked') !== 'true';
      btn.setAttribute('aria-checked', String(next));
      onChange(next, btn);
    });
    toggles.append(btn);
    return btn;
  };

  switchRow('3D terrain', `Quantised elevation mesh · ${G.globe.terrainMode}`,
            G.globe.terrainMode !== 'ellipsoid', async (on, btn) => {
    const hint = btn.querySelector('.switch-row__hint');
    hint.textContent = on ? 'loading elevation service…' : 'smooth ellipsoid';
    try {
      const mode = await G.setTerrainEnabled(on);
      hint.textContent = `Quantised elevation mesh · ${mode}`;
    } catch {
      btn.setAttribute('aria-checked', 'false');
      hint.textContent = 'elevation service unavailable';
      toast('The elevation service did not respond; terrain is flat.',
            { kind: 'warn' });
    }
  });

  switchRow('Cluster nearby markers', 'Groups pins when zoomed out',
            true, (on) => G.setClustering(on));

  switchRow('Atmosphere & starfield', 'Ground haze, limb glow, star box',
            true, (on) => G.setFx(on));

  dom.layersPane.replaceChildren(
    el('div', {}, [el('div', { class: 'eyebrow', style: { marginBottom: 'var(--s-2)' } },
                      'Base layer'), baseGroup]),
    el('div', {}, [el('div', { class: 'eyebrow', style: { marginBottom: 'var(--s-2)' } },
                      'Overlays'), overlayGroup]),
    el('div', {}, [el('div', { class: 'eyebrow', style: { marginBottom: 'var(--s-2)' } },
                      'Appearance'), sceneGroup]),
    el('div', {}, [el('div', { class: 'eyebrow', style: { marginBottom: 'var(--s-2)' } },
                      'Scene'), toggles]),
    el('p', { class: 'note' },
      'Every service listed here is reachable without an API key. Protocol '
      + 'badges show how each is requested: WMTS is the OGC tiled-map '
      + 'standard; XYZ is the de-facto slippy-tile scheme.'),
  );
}

/* ========================================================================= */
/* OGC services tab                                                          */
/* ========================================================================= */

export async function renderServices() {
  dom.servicesPane.dataset.loaded = '1';
  dom.servicesPane.replaceChildren(
    el('p', { class: 'dim mono', text: 'Querying service metadata…' }));

  let meta;
  try {
    meta = await loadServiceMetadata();
  } catch (err) {
    dom.servicesPane.replaceChildren(
      el('p', { class: 'note', text: `Service metadata unavailable: ${err.message}` }));
    return;
  }

  const kv = (pairs) => el('dl', { class: 'kv' },
    pairs.flatMap(([k, v]) => v == null || v === ''
      ? [] : [el('dt', { text: k }), el('dd', {}, v.nodeType ? v : String(v))]));

  const endpoint = (label, url) => el('div', {}, [
    el('div', { class: 'eyebrow', style: { marginBottom: '2px' }, text: label }),
    el('div', { class: 'endpoint' }, [
      el('code', { text: url.replace(/^https?:\/\//, '') }),
      el('a', { href: url, target: '_blank', rel: 'noopener',
                'aria-label': `Open ${label}`, class: 'linklist__out',
                html: ICON.out }),
    ]),
  ]);

  const landing = meta.landing.ok ? meta.landing.value : null;
  const conf = meta.conformance.ok ? meta.conformance.value : null;
  const coll = meta.collection.ok ? meta.collection.value : null;

  const cards = [];

  cards.push(el('div', { class: 'svc__card' }, [
    el('header', {}, [
      el('h3', { text: 'OGC API — Features' }),
      el('span', { class: 'layer-opt__badge', dataset: { proto: 'WMTS' },
                   text: meta.deployment === 'static' ? 'STATIC' : 'LIVE' }),
    ]),
    el('div', { class: 'svc__body' }, [
      landing ? el('p', { class: 'muted', style: { fontSize: 'var(--fs-xs)' },
                          text: landing.description }) : null,
      kv([
        ['Service', landing?.title ?? '—'],
        ['Deployment', meta.deployment === 'static'
          ? 'static documents on a CDN' : 'live GeoServer'],
        ['Features', coll?.['x-feature-count'] ?? store.state.count],
        ['Storage CRS', coll?.storageCrs?.split('/').slice(-3).join('/') ?? 'CRS84'],
        ['Extent', coll?.extent?.spatial?.bbox?.[0]
          ? coll.extent.spatial.bbox[0].map((n) => n.toFixed(2)).join(', ') : '—'],
        ['Built', (landing?.['x-generated'] ?? store.state.generated ?? '')
          .replace('T', ' ').replace('Z', ' UTC')],
      ]),
      endpoint('Landing page', meta.endpoints.landing),
      endpoint('Collection', meta.endpoints.collection),
      endpoint('Items (GeoJSON)', meta.endpoints.items),
      endpoint('OpenAPI 3.0', meta.endpoints.api),
    ]),
  ]));

  if (conf?.conformsTo?.length) {
    cards.push(el('div', { class: 'svc__card' }, [
      el('header', {}, [el('h3', { text: 'Declared conformance' }),
                        el('span', { class: 'chip' },
                           `${conf.conformsTo.length} classes`)]),
      el('div', { class: 'svc__body' }, [
        el('ul', { class: 'conformance' },
           conf.conformsTo.map((c) => el('li', {},
             el('code', { text: c.replace('http://www.opengis.net/spec/', '') })))),
        ...(conf['x-static-deployment'] ?? []).map((n) =>
          el('p', { class: 'note', text: n })),
      ]),
    ]));
  }

  const imageryRows = [
    ...BASE_LAYERS.map((l) => [l, 'base']),
    ...OVERLAYS.map((l) => [l, 'overlay']),
  ];
  cards.push(el('div', { class: 'svc__card' }, [
    el('header', {}, [el('h3', { text: 'Imagery & elevation services' }),
                      el('span', { class: 'chip' },
                         `${imageryRows.length + 1} endpoints`)]),
    el('div', { class: 'svc__body' },
      imageryRows.map(([spec, role]) => el('div', {}, [
        el('div', { class: 'row', style: { justifyContent: 'space-between' } }, [
          el('span', { class: 'layer-opt__name', text: spec.name }),
          el('span', { class: 'layer-opt__badge', dataset: { proto: spec.proto },
                       text: spec.proto }),
        ]),
        el('div', { class: 'layer-opt__meta',
                    text: `${role} · ${spec.layer ?? 'tile template'} · max z${spec.maximumLevel}` }),
      ])).concat([
        el('div', {}, [
          el('div', { class: 'row', style: { justifyContent: 'space-between' } }, [
            el('span', { class: 'layer-opt__name', text: 'Esri Terrain3D elevation' }),
            el('span', { class: 'layer-opt__badge', text: 'LERC' }),
          ]),
          el('div', { class: 'layer-opt__meta',
                      text: `quantised mesh · active mode: ${G.globe.terrainMode}` }),
        ]),
      ])),
  ]));

  cards.push(el('div', { class: 'svc__card' }, [
    el('header', {}, el('h3', { text: 'Run this against GeoServer' })),
    el('div', { class: 'svc__body' }, [
      el('p', { class: 'muted', style: { fontSize: 'var(--fs-xs)' } },
        'The same catalogue is published as a GeoServer data directory with an '
        + 'SLD style, so it can be served as OGC API — Features, WFS 2.0.0 and '
        + 'WMS 1.3.0 with full query-parameter support. Point '
        + 'APP.geoserverFeatures in assets/js/config.js at the landing page and '
        + 'the client switches over — the feature schema is identical.'),
      el('div', { class: 'linklist' }, [
        linkRow('geoserver/ — data directory, SLD and compose file',
                'https://github.com/SideQuestStudiosDev/Ancient-Aliens-GIS/tree/main/geoserver',
                'data'),
        linkRow('OGC API — Features, Part 1: Core',
                'https://docs.ogc.org/is/17-069r4/17-069r4.html', 'reference'),
        linkRow('OGC WMTS 1.0.0 implementation specification',
                'https://www.ogc.org/standard/wmts/', 'reference'),
      ]),
      APP.geoserverFeatures
        ? el('p', { class: 'note', text: `Live service: ${APP.geoserverFeatures}` })
        : null,
    ]),
  ]));

  dom.servicesPane.replaceChildren(...cards);
}

/* ========================================================================= */
/* readout + attribution                                                     */
/* ========================================================================= */

const readoutState = {};

export function updateReadout(patch) {
  Object.assign(readoutState, patch);
  const r = readoutState;
  if (r.lat != null) dom.roLat.textContent = fmtDeg(r.lat, 4);
  if (r.lon != null) dom.roLon.textContent = fmtDeg(r.lon, 4);
  if ('elevation' in r) {
    dom.roElev.textContent = r.elevation == null ? '—' : fmtDistance(r.elevation);
  }
  if (r.cameraHeight != null) dom.roCam.textContent = fmtDistance(r.cameraHeight);
  if (r.sceneMode) {
    dom.roScene.textContent = { '3D': '3D GLOBE', COLUMBUS: '2.5D', '2D': '2D MAP' }[r.sceneMode];
  }
}

/** Show or hide the "streaming imagery" chip. Debounced on the way out so a
 *  brief lull between tile batches does not make it flicker. */
let tilesHideTimer = 0;

export function setTilesBusy(queued) {
  if (!dom.tilesBusy) return;
  clearTimeout(tilesHideTimer);
  if (queued > 0) {
    dom.tilesBusyText.textContent =
      `Streaming imagery… ${queued} tile${queued === 1 ? '' : 's'}`;
    dom.tilesBusy.hidden = false;
  } else {
    tilesHideTimer = setTimeout(() => { dom.tilesBusy.hidden = true; }, 700);
  }
}

export function setAttribution(parts) {
  dom.attribBody.innerHTML = parts.join(' · ');
}

function wireAttribution() {
  dom.attribToggle?.addEventListener('click', () => {
    const open = dom.attrib.dataset.open === 'true';
    dom.attrib.dataset.open = String(!open);
    dom.attribToggle.setAttribute('aria-expanded', String(!open));
    dom.attribToggle.setAttribute('aria-label',
      open ? 'Show data attribution' : 'Hide data attribution');
  });
}

/* ========================================================================= */
/* help modal                                                                */
/* ========================================================================= */

let lastFocus = null;

export function openHelp() {
  lastFocus = document.activeElement;
  dom.helpModal.removeAttribute('hidden');
  dom.helpClose.focus();
}

export function closeHelp() {
  dom.helpModal.setAttribute('hidden', '');
  lastFocus?.focus?.();
}

function wireHelp() {
  dom.btnHelp.addEventListener('click', openHelp);
  dom.helpClose.addEventListener('click', closeHelp);
  dom.helpModal.addEventListener('click', (e) => {
    if (e.target === dom.helpModal) closeHelp();
  });
  dom.helpModal.addEventListener('keydown', (e) => {
    if (e.key !== 'Tab') return;
    const focusables = $$('a[href], button, [tabindex]:not([tabindex="-1"])',
                          dom.helpModal);
    if (!focusables.length) return;
    const first = focusables[0], last = focusables.at(-1);
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault(); last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault(); first.focus();
    }
  });
}

export const helpOpen = () => !dom.helpModal.hasAttribute('hidden');

/* ========================================================================= */

export function wire() {
  wireTabs();
  wireSheet();
  wireSearch();
  wireListScroll();
  wireHelp();
  wireAttribution();
}

export { dom };
