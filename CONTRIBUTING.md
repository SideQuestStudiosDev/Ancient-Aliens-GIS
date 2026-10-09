# Contributing

Corrections are the most valuable contribution here. A catalogue of 246
sites assembled largely from one person's reading will contain errors, and
the ones that matter are factual: a coordinate in the wrong valley, a
mis-dated excavation, a context note that overstates how settled a question
is.

## Reporting a problem

Open an issue with the site id (the slug in `?site=…`) and what is wrong.
For a factual correction, a citation — a published excavation report, a
museum record, a national heritage register — settles it fastest.

## Correcting or adding a site

Everything lives in one file: [`data-source/catalog.py`](data-source/catalog.py).
One `S(...)` call per site. The schema is documented at the top.

```python
S("site-slug", "Display Name",
  subtitle="Province, Country",
  country="Country", region="Europe", category="megalithic",
  tags=["neolithic", "archaeoastronomy"],
  aliases=["another name people search for"],
  wikipedia="Exact English Wikipedia article title",
  lat=51.1789, lon=-1.8262, precision="exact", height=600,
  claim="What the series asserts, reported neutrally.",
  context="What the archaeological or scientific record shows.",
  links=[{"label": "Excavation report", "url": "https://…", "kind": "reference"}]),
```

Then:

```bash
python3 scripts/build_data.py        # enrich from Wikipedia, regenerate data/
python3 scripts/validate_data.py     # assert the published tree is coherent
```

Commit both `data-source/` and `data/`. CI rebuilds offline and fails if the
committed tree does not match.

### House rules for the text

These are what make the project worth having rather than another list.

**`claim`** — report what the series says, accurately and without sneering.
Readers come having seen the episode; a strawman is useless to them and
makes everything else look unreliable. Name the specific assertion.

**`context`** — report what the evidence shows, and say how strong it is.
Three distinct cases, and they should read differently:

- *The claim is wrong and we know why.* Say so and give the mechanism. The
  Palenque sarcophagus lid is legible Maya iconography; the Dendera relief
  is a documented cosmogony; the Nazca lines were reproduced experimentally
  in a day.
- *The claim is unfounded but the site is remarkable.* Say both. Göbekli
  Tepe genuinely overturned assumptions about Neolithic social complexity.
  The Antikythera mechanism is genuinely extraordinary. Diminishing a real
  achievement to rebut a bad explanation is its own kind of inaccuracy.
- *The question is open.* Say that. Yonaguni, the Wow! signal, the location
  of Punt, the severity of the Toba bottleneck, Rendlesham. "Unresolved" is
  an honest answer and the catalogue should contain some.

**Never** invent a detail to fill a gap. If the series' reference cannot be
tied to a published place, set `precision="uncertain"` and say so in the
context — three entries already do. An honest "this does not resolve to a
mapped location" is worth more than a plausible-looking coordinate.

**`precision`** — be strict. `exact` means the monument. If you are placing
a pin on a town because the actual site is not published, that is
`approximate`. If the entry is a desert or a sea, it is `area` with a
`radius_km`.

### Style

- British spelling, consistent with the existing text.
- Two to four sentences per field. The dossier is read on a phone.
- No exclamation marks, no scare quotes, no rhetorical questions.
- Link to primary sources — excavation reports, museum catalogues,
  institutional pages — over secondary summaries. All links must be HTTPS;
  the validator enforces it.

## Code

```bash
python3 -m http.server 8000     # run it
node scripts/smoke.mjs          # browser smoke test (needs Playwright)
python3 scripts/check_services.py   # are the map services still alive?
```

No build step, no framework, no bundler, and the intention is to keep it
that way. Plain ES modules and CSS custom properties.

- Colour, spacing, type and motion come from `assets/css/tokens.css`. Do not
  hard-code a hex value in a component.
- New map layers go in `assets/js/config.js` **and** in the table in
  `scripts/check_services.py`. A layer that is not checked will eventually
  break silently — see the CARTO note in `docs/OGC-COMPLIANCE.md`.
- Anything that changes the scene must call `render()`: the viewer runs in
  `requestRenderMode` and will not repaint on its own.
- Test at 390 px wide before opening a PR. Mobile is the priority, and the
  mobile-specific bugs in this codebase's history were all layering and
  sizing problems that only appear at that width.
