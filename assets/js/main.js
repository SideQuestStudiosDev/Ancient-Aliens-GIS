/* ==========================================================================
   Ancient Aliens GIS — bootstrap.

   Order matters: the catalogue loads and the panel paints before CesiumJS is
   asked to build a globe. On a phone that means the site list is searchable
   in well under a second, while the 3D scene finishes behind it.
   ========================================================================== */

import { $ } from './util.js';
import { APP, CAMERA } from './config.js';
import * as store from './store.js';
import * as G from './globe.js';
import * as UI from './ui.js';

const boot = { globeReady: false, pendingSelect: null };

/* ------------------------------------------------------------------- start */

async function start() {
  UI.cacheDom();
  UI.wire();
  UI.renderDetailPlaceholder();
  UI.bootMessage('Loading site catalogue…');

  /* ---- 1. data -------------------------------------------------------- */
  try {
    await store.init();
  } catch (err) {
    fatal('The site catalogue could not be loaded.', err);
    return;
  }

  UI.renderFilters();
  UI.renderList();
  UI.bootMessage(`${store.state.count} sites indexed — building globe…`);

  // Wire the store BEFORE applying the URL: applyURL() emits `categories`
  // and `filtered`, and those have to reach the panel or a deep link like
  // ?cat=geoglyph would filter the data without ever lighting up its chip.
  wireStore();
  wireChrome();
  wireKeyboard();

  const initialId = store.applyURL();
  if (initialId) boot.pendingSelect = initialId;
  UI.dom.searchInput.value = store.state.query;
  UI.dom.searchClear.hidden = !store.state.query;
  UI.renderFilters();
  UI.renderList();

  /* ---- 2. globe ------------------------------------------------------- */
  try {
    await G.createGlobe($('#globe'), {
      onPick: onGlobePick,
      onHover: () => {},
      onCamera: onCamera,
      onTiles: (queued) => UI.setTilesBusy(queued),
      onCredits: (parts) => UI.setAttribution([
        ...parts,
        'Site data: <a href="https://github.com/SideQuestStudiosDev/Ancient-Aliens-GIS" target="_blank" rel="noopener">Ancient Aliens GIS</a> © <a href="https://github.com/SideQuestStudiosDev/Ancient-Aliens-GIS/blob/main/NOTICE" target="_blank" rel="noopener">Side Quest Studios</a>, CC BY 4.0 · summaries from Wikipedia (CC BY-SA 4.0)',
      ]),
    });
  } catch (err) {
    // The catalogue, search and dossiers all still work without a globe, so
    // degrade rather than fail.
    console.error(err);
    UI.hideBoot();
    UI.toast('3D globe unavailable — the catalogue and dossiers still work.',
             { kind: 'err', ms: 9000 });
    document.getElementById('globe')?.insertAdjacentHTML('afterbegin',
      `<div style="position:absolute;inset:0;display:grid;place-content:center;
                   padding:2rem;text-align:center;color:var(--ink-muted);
                   font-size:var(--fs-sm)">
         <p>WebGL is unavailable in this browser, so the 3D globe cannot
         start.<br>Every site dossier is still available from the panel.</p>
       </div>`);
    UI.showTab('sites');
    if (window.innerWidth < 900) UI.snapSheet('full');
    return;
  }

  boot.globeReady = true;
  G.addSites(store.state.sites);
  G.showOnly(store.state.visible.map((s) => s.id));
  UI.renderLayers();
  G.flyHome();

  UI.bootMessage('Ready');
  UI.hideBoot();
  UI.dom.readout?.removeAttribute('aria-hidden');

  if (boot.pendingSelect) {
    store.select(boot.pendingSelect, { origin: 'url' });
    boot.pendingSelect = null;
  } else if (window.innerWidth >= 900) {
    UI.toast(`${store.state.count} sites loaded. Pick one, or press ? for help.`,
             { kind: 'ok', ms: 5200 });
  }

  registerServiceWorker();
}

function fatal(message, err) {
  console.error(err);
  UI.bootMessage(message);
  const boot = $('#boot');
  if (boot) {
    boot.querySelector('.boot__bar')?.remove();
    boot.insertAdjacentHTML('beforeend',
      `<p style="max-width:40ch;color:var(--ink-muted);font-size:var(--fs-sm)">
         ${message} The catalogue is also published as plain GeoJSON at
         <code>data/collections/sites/items.json</code>.
       </p>
       <button class="btn" onclick="location.reload()">Retry</button>`);
  }
}

/* -------------------------------------------------------------- store wiring */

function wireStore() {
  store.on('filtered', (list) => {
    UI.renderList();
    if (boot.globeReady) G.showOnly(list.map((s) => s.id));
    if (store.state.selectedId) UI.ensureRowVisible(store.state.selectedId);
  });

  store.on('categories', () => UI.renderFilters());
  store.on('reset', () => { UI.dom.searchInput.value = ''; });

  store.on('selected', async ({ site, origin, fly }) => {
    if (!site) {
      UI.renderDetailPlaceholder();
      if (boot.globeReady) G.highlight(null);
      return;
    }
    if (boot.globeReady) {
      G.highlight(site.id);
      if (fly && origin !== 'globe') {
        G.globe.pendingFlight = site.id;
        G.flyToSite(site).catch((err) => console.warn('fly failed', err));
      }
    }
    UI.ensureRowVisible(site.id);
    UI.showTab('detail');
    UI.renderDetailLoading(site);
    try {
      const feature = await store.feature(site.id);
      // Guard against a slower response arriving after another selection.
      if (store.state.selectedId === site.id) UI.renderDetail(site, feature);
    } catch (err) {
      console.error(err);
      UI.renderDetail(site, {
        properties: {
          name: site.n, subtitle: site.s, country: site.y, region: site.r,
          category: site.c, latitude: site.lat, longitude: site.lon,
          location_precision: site.p, tags: site.t,
          claim: 'The full dossier could not be loaded.',
          context: 'Check the network connection and reload.',
        },
        links: [],
      });
      UI.toast('That dossier could not be loaded.', { kind: 'warn' });
    }
  });
}

/* ------------------------------------------------------------- globe events */

function onGlobePick(siteId, { cluster } = {}) {
  if (!siteId) return;
  const site = store.state.byId.get(siteId);
  if (!site) return;
  if (cluster) {
    // Zoom toward the cluster so it breaks apart, without committing to a pin.
    G.flyToCoords(site.lat, site.lon, 900_000);
    return;
  }
  store.select(siteId, { origin: 'globe', fly: false });
  if (window.innerWidth < 900) UI.snapSheet('half');
}

let cameraTimer = 0;

function onCamera(patch) {
  UI.updateReadout(patch);
  if (patch.cameraLat != null) {
    clearTimeout(cameraTimer);
    cameraTimer = setTimeout(
      () => store.setCameraCenter(patch.cameraLat, patch.cameraLon), 220);
  }
}

/* ------------------------------------------------------------ chrome wiring */

function wireChrome() {
  for (const btn of document.querySelectorAll('[data-scene]')) {
    btn.addEventListener('click', () => {
      const mode = btn.dataset.scene;
      G.setSceneMode(mode);
      for (const b of document.querySelectorAll('[data-scene]')) {
        b.setAttribute('aria-checked', String(b === btn));
      }
      UI.updateReadout({ sceneMode: mode });
    });
  }

  UI.dom.btnHome.addEventListener('click', () => {
    store.select(null);
    G.flyHome();
  });

  UI.dom.btnPanel.addEventListener('click', UI.togglePanel);

  UI.dom.btnFx.addEventListener('click', () => {
    const on = UI.dom.btnFx.getAttribute('aria-pressed') !== 'true';
    UI.dom.btnFx.setAttribute('aria-pressed', String(on));
    UI.dom.app.dataset.fx = on ? 'on' : 'off';
    G.setFx(on);
  });

  UI.dom.btnGeolocate.addEventListener('click', geolocate);

  window.addEventListener('resize', () => G.resize(), { passive: true });
  window.addEventListener('orientationchange', () => setTimeout(G.resize, 220));
}

function geolocate() {
  if (!navigator.geolocation) {
    UI.toast('This browser does not expose a location API.', { kind: 'warn' });
    return;
  }
  UI.toast('Requesting your location…', { ms: 2400 });
  navigator.geolocation.getCurrentPosition(
    ({ coords }) => {
      G.flyToCoords(coords.latitude, coords.longitude, 120_000);
      store.setCameraCenter(coords.latitude, coords.longitude);
      store.setSort('distance');
      UI.dom.sortBy.value = 'distance';
      const nearest = store.state.visible[0];
      UI.toast(nearest
        ? `Nearest site: ${nearest.n}`
        : 'Location found.', { kind: 'ok' });
    },
    (err) => UI.toast(
      err.code === err.PERMISSION_DENIED
        ? 'Location permission denied.'
        : 'Your location could not be determined.', { kind: 'warn' }),
    { enableHighAccuracy: false, timeout: 12000, maximumAge: 300000 },
  );
}

/* ---------------------------------------------------------------- keyboard */

function wireKeyboard() {
  document.addEventListener('keydown', (e) => {
    const typing = /^(input|textarea|select)$/i.test(e.target.tagName)
      || e.target.isContentEditable;

    if (e.key === 'Escape') {
      if (UI.helpOpen()) { UI.closeHelp(); return; }
      if (!typing && store.state.selectedId) {
        store.select(null);
        UI.showTab('sites');
      }
      return;
    }

    if (typing) return;
    if (e.metaKey || e.ctrlKey || e.altKey) return;

    switch (e.key) {
      case '/':
        e.preventDefault(); UI.focusSearch(); break;
      case '?':
        e.preventDefault(); UI.openHelp(); break;
      case '1':
        document.querySelector('[data-scene="3D"]')?.click(); break;
      case '2':
        document.querySelector('[data-scene="COLUMBUS"]')?.click(); break;
      case '3':
        document.querySelector('[data-scene="2D"]')?.click(); break;
      case 'h': case 'H':
        UI.dom.btnHome.click(); break;
      case 'l': case 'L':
        UI.dom.btnGeolocate.click(); break;
      case 'f': case 'F':
        UI.dom.btnFx.click(); break;
      default:
        break;
    }
  });
}

/* ---------------------------------------------------------- service worker */

function registerServiceWorker() {
  if (!('serviceWorker' in navigator)) return;
  if (location.protocol === 'file:') return;
  navigator.serviceWorker.register(new URL('../../sw.js', import.meta.url))
    .catch((err) => console.warn('service worker not registered', err));
}

/* --------------------------------------------------------------------- go */

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', start, { once: true });
} else {
  start();
}
