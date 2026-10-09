"""
Ancient Aliens GIS — authored site catalogue (source of truth).

Each entry records:
  id         stable slug, used in URLs and OGC feature ids
  name       display name
  subtitle   human-readable place string
  country    sovereign state / territory, or "" for open ocean
  region     one of REGIONS
  category   one of CATEGORIES (drives pin colour + filter chip)
  tags       free-form keywords, also searched
  wikipedia  English Wikipedia article title (verified + geocoded at build time)
  lat/lon    authored fallback coordinates in EPSG:4326 (decimal degrees)
  precision  exact | approximate | area | uncertain
  height     camera height in metres for the fly-to
  claim      what the series asserts (reported, not endorsed)
  context    the mainstream archaeological / scientific position
  links      extra references beyond the auto-generated Wikipedia link
  aliases    additional search terms
  geometry   "point" (default) or "multipoint" with `points=[(lat,lon), ...]`

`precision` semantics, surfaced in the UI so the map never implies
accuracy it does not have:
  exact        a surveyed monument or structure; coordinates to ~100 m
  approximate  the right valley/hill/town, but the specific feature is
               not published to better than a few kilometres
  area         deliberately a region centroid; the entry describes an area,
               not a point (deserts, seas, countries, triangles)
  uncertain    the series' reference could not be tied to a published
               place name with confidence; treat the position as a label
"""

REGIONS = [
    "Africa", "Middle East", "Europe", "South Asia", "East Asia",
    "Southeast Asia & Oceania", "North America",
    "Central America & Caribbean", "South America",
    "Antarctica & Southern Ocean", "Oceans & Marine", "Beyond Earth",
]

CATEGORIES = {
    "megalithic":  ("Megalithic",        "--cat-megalithic"),
    "pyramid":     ("Pyramid / Temple",  "--cat-pyramid"),
    "geoglyph":    ("Geoglyph",          "--cat-geoglyph"),
    "underground": ("Subterranean",      "--cat-underground"),
    "underwater":  ("Submerged",         "--cat-underwater"),
    "ufo":         ("UFO Incident",      "--cat-ufo"),
    "military":    ("Military / Secure", "--cat-military"),
    "research":    ("Research Centre",   "--cat-research"),
    "sacred":      ("Sacred Site",       "--cat-sacred"),
    "anomaly":     ("Anomaly Zone",      "--cat-anomaly"),
    "landform":    ("Landform",          "--cat-landform"),
    "city":        ("Ancient City",      "--cat-city"),
    "artifact":    ("Artefact Locus",    "--cat-artifact"),
    "region":      ("Broad Region",      "--cat-region"),
    "offworld":    ("Beyond Earth",      "--cat-offworld"),
}

SITES = []


def S(sid, name, **kw):
    """Register one site. Defaults keep the per-entry literals short."""
    rec = {
        "id": sid,
        "name": name,
        "subtitle": kw.get("subtitle", ""),
        "country": kw.get("country", ""),
        "region": kw["region"],
        "category": kw["category"],
        "tags": kw.get("tags", []),
        "aliases": kw.get("aliases", []),
        "wikipedia": kw.get("wikipedia", ""),
        "lat": kw["lat"],
        "lon": kw["lon"],
        "precision": kw.get("precision", "exact"),
        "height": kw.get("height", 2500),
        "pitch": kw.get("pitch", -40.0),
        "geometry": kw.get("geometry", "point"),
        "points": kw.get("points", []),
        "radius_km": kw.get("radius_km", 0),
        "claim": kw["claim"],
        "context": kw["context"],
        "links": kw.get("links", []),
        "offworld": kw.get("offworld", False),
    }
    SITES.append(rec)
    return rec


# ===========================================================================
# AFRICA — Egypt & the Nile
# ===========================================================================

S("abydos", "Abydos — Osiris Hall",
  subtitle="Sohag Governorate, Egypt", country="Egypt", region="Africa",
  category="pyramid", tags=["temple", "new-kingdom", "hieroglyphs", "osireion"],
  aliases=["Osireion", "Seti I Temple", "helicopter hieroglyphs"],
  wikipedia="Abydos, Egypt", lat=26.1847, lon=31.9194, height=800,
  claim="The series highlights the so-called 'helicopter hieroglyphs' in the "
        "Temple of Seti I, reading the overlapping glyphs as depictions of a "
        "helicopter, submarine and jet aircraft, and treats the dry-stone "
        "Osireion as too precisely cut for Bronze Age tools.",
  context="Egyptologists identify the panel as a palimpsest: Seti I's titulary "
          "was plastered over and recarved for Ramesses II, and the two texts "
          "now show through one another. The 'aircraft' shapes are the "
          "accidental union of two legible royal titles. The Osireion is a "
          "19th-Dynasty cenotaph whose granite was quarried at Aswan and "
          "dressed with copper, stone and abrasive sand — techniques "
          "documented in unfinished quarry faces at the source."),

S("amarna", "Amarna (Akhetaten)",
  subtitle="Minya Governorate, Egypt", country="Egypt", region="Africa",
  category="city", tags=["akhenaten", "new-kingdom", "planned-city"],
  aliases=["Tell el-Amarna", "Akhetaten", "Akhenaten"],
  wikipedia="Amarna", lat=27.6619, lon=30.8958, height=4000,
  claim="Akhenaten's abrupt imposition of a single sun-disc god, his elongated "
        "portraiture, and the city raised from nothing in a few years are "
        "presented as evidence that the pharaoh was a hybrid or an "
        "extraterrestrial emissary of the Aten.",
  context="Amarna art is a deliberate royal style, applied to the whole court "
          "and abandoned after Akhenaten's death; skeletal remains from the "
          "Amarna cemeteries show ordinary human morphology. The Aten cult "
          "has traceable antecedents in earlier solar theology at Heliopolis, "
          "and the city's speed of construction is explained by mud-brick "
          "cores with stone facing and a conscripted workforce."),

S("cairo-giza", "Giza Plateau & Cairo",
  subtitle="Giza Governorate, Egypt", country="Egypt", region="Africa",
  category="pyramid", tags=["unesco", "old-kingdom", "great-pyramid", "sphinx"],
  aliases=["Great Pyramid", "Khufu", "Sphinx", "Cheops"],
  wikipedia="Giza pyramid complex", lat=29.9792, lon=31.1342, height=1600,
  pitch=-28,
  claim="The flagship claim of the series: the Great Pyramid's precision, its "
        "near-perfect cardinal alignment, the estimated 2.3 million blocks, "
        "and the granite relieving chambers are said to exceed Bronze Age "
        "capability, implying machine tooling, levitation, or a function as a "
        "power plant or navigational beacon.",
  context="Fourth-Dynasty construction is among the best-documented building "
          "programmes in antiquity. The Wadi al-Jarf papyri (c. 2560 BC) "
          "record Inspector Merer's crews ferrying Tura limestone to Giza; "
          "quarry faces, abandoned blocks, copper tools, dolerite pounders, "
          "ramp remnants at Hatnub and the workers' town excavated at Heit "
          "el-Ghurab all survive. Cardinal alignment is reproducible by "
          "stellar or solar methods available at the time.",
  links=[{"label": "Ancient Egypt Research Associates — Giza field reports",
          "url": "https://www.aeraweb.org/", "kind": "reference"}]),

S("dendera", "Dendera — Temple of Hathor",
  subtitle="Qena Governorate, Egypt", country="Egypt", region="Africa",
  category="pyramid", tags=["temple", "ptolemaic", "zodiac", "crypt"],
  aliases=["Dendera light", "Hathor", "Dendera zodiac"],
  wikipedia="Dendera", lat=26.1419, lon=32.6700, height=700,
  claim="Reliefs in the southern crypt — the 'Dendera light' — are read as "
        "Crookes tubes or arc lamps wired to a Djed-pillar insulator, "
        "explaining how artists worked in unventilated chambers without soot.",
  context="The reliefs are a standard cosmogony: a lotus flower opening to "
          "release the serpent Harsomtus, enclosed in a protective bubble, "
          "supported by a Djed pillar — a scene paralleled in text on the same "
          "walls. Soot deposits do occur elsewhere in Egyptian tombs, and "
          "polished copper mirrors relaying daylight are attested. No "
          "conductors, sockets or power source have been recovered."),

S("edfu", "Temple of Edfu",
  subtitle="Aswan Governorate, Egypt", country="Egypt", region="Africa",
  category="pyramid", tags=["temple", "ptolemaic", "horus", "edfu-texts"],
  wikipedia="Temple of Edfu", lat=24.9777, lon=32.8733, height=600,
  claim="The Edfu building texts describe the temple rising on a primeval mound "
        "according to a plan handed down by the gods; the series treats this as "
        "a surviving record of extraterrestrial architects and of a 'first "
        "time' when non-humans ruled Egypt.",
  context="The Edfu texts are Ptolemaic theological literature (c. 237–57 BC) "
          "describing a mythic charter for the temple, a genre found across "
          "Egyptian sacred architecture. They are cosmology, not construction "
          "records, and the temple itself is a well-dated Ptolemaic build with "
          "named architects and dedication inscriptions."),

S("karnak-luxor", "Karnak Temple & Luxor",
  subtitle="Luxor Governorate, Egypt", country="Egypt", region="Africa",
  category="pyramid", tags=["temple", "unesco", "obelisk", "hypostyle"],
  aliases=["Thebes", "Amun-Re", "hypostyle hall"],
  wikipedia="Karnak", lat=25.7188, lon=32.6573, height=1200,
  claim="The 134 columns of the hypostyle hall, the unfinished obelisk at "
        "nearby Aswan and the 323-tonne monoliths raised at Karnak are offered "
        "as proof of lost lifting technology or anti-gravity.",
  context="Karnak was built and rebuilt across roughly two millennia by "
          "successive dynasties, and the sequence is visible in the masonry. "
          "Mud-brick construction ramps survive against the first pylon; "
          "quarry marks, wooden sledges, lubricated trackways and the "
          "Djehutihotep relief showing 172 men hauling a colossus document the "
          "method directly."),

S("naqada", "Naqada",
  subtitle="Qena Governorate, Egypt", country="Egypt", region="Africa",
  category="city", tags=["predynastic", "cemetery", "nagada"],
  wikipedia="Naqada", lat=25.8980, lon=32.7260, height=4000,
  precision="approximate",
  claim="Elongated skulls and unusually tall skeletons from predynastic burials "
        "here are cited as a non-human or hybrid ruling lineage predating the "
        "pharaohs.",
  context="Naqada defines the Naqada I–III predynastic sequence (c. 4000–3000 "
          "BC) and is central to mainstream accounts of Egyptian state "
          "formation. The skeletal series falls within modern human variation; "
          "Petrie's 19th-century 'dynastic race' reading of the material was "
          "abandoned by the mid-20th century and is not supported by later "
          "craniometric or genetic work."),

S("saqqara", "Saqqara — Step Pyramid of Djoser",
  subtitle="Giza Governorate, Egypt", country="Egypt", region="Africa",
  category="pyramid", tags=["unesco", "old-kingdom", "step-pyramid", "serapeum"],
  aliases=["Djoser", "Imhotep", "Serapeum", "Pa-di-Imen", "Saqqara bird"],
  wikipedia="Saqqara", lat=29.8711, lon=31.2165, height=1800,
  claim="Two threads converge here: the wooden 'Saqqara bird' from the tomb of "
        "Pa-di-Imen is presented as a scale model of a glider, and the 70-tonne "
        "granite sarcophagi in the Serapeum are said to be machined beyond "
        "hand-tool tolerance.",
  context="The Saqqara bird has no tailplane and no evident control surfaces; "
          "wind-tunnel and replica tests have not produced stable flight, and "
          "the object sits comfortably within a large class of Egyptian bird "
          "votives and weathervanes. The Serapeum boxes are Late Period Apis "
          "bull burials; several are unfinished, showing the chisel and "
          "abrasive stages mid-process."),

S("nabta-playa", "Nabta Playa",
  subtitle="Nubian Desert, southern Egypt", country="Egypt", region="Africa",
  category="megalithic", tags=["archaeoastronomy", "neolithic", "calendar-circle",
                               "sahara"],
  aliases=["Nubian Desert", "calendar circle", "Sahara"],
  wikipedia="Nabta Playa", lat=22.5069, lon=30.7278, height=1500,
  claim="A Neolithic stone circle in the Sahara aligned on Sirius and Orion is "
        "read as a star map left for, or by, visitors — and as evidence that "
        "the knowledge behind Giza arrived from the desert long before Egypt "
        "was unified.",
  context="Nabta Playa is a genuinely significant archaeoastronomical site, "
          "roughly a millennium older than Stonehenge, built by cattle "
          "pastoralists around a seasonal lake. The alignments plausibly track "
          "the summer solstice and the heliacal rising of Sirius, which "
          "signalled the rains. The debate among specialists is over which "
          "stars and how precisely — not over human authorship."),

S("egypt-nile", "Egypt & the Nile Corridor",
  subtitle="Nile Valley and Delta (regional)", country="Egypt", region="Africa",
  category="region", tags=["river", "regional", "nile"], precision="area",
  radius_km=600,
  wikipedia="Nile", lat=26.8206, lon=30.8025, height=1600000, pitch=-70,
  claim="Egypt as a whole is the series' central case: a civilisation that "
        "appears to arrive fully formed, with writing, monumental stone and "
        "astronomy emerging together, is said to require outside instruction.",
  context="The predynastic record — Badarian, Naqada I–III, Maadi, Hierakonpolis "
          "— supplies a continuous four-millennium run-up to the First Dynasty, "
          "with incremental development in ceramics, metallurgy, boat building, "
          "writing and monumental mud-brick. The 'sudden appearance' framing "
          "reflects the visibility of stone monuments, not the absence of "
          "antecedents."),

# ===========================================================================
# AFRICA — beyond Egypt
# ===========================================================================

S("jebel-barkal", "Jebel Barkal",
  subtitle="Northern State, Sudan", country="Sudan", region="Africa",
  category="pyramid", tags=["unesco", "kush", "napata", "nubian-pyramids"],
  aliases=["Napata", "Nubia", "Kush"],
  wikipedia="Jebel Barkal", lat=18.5356, lon=31.8286, height=2500,
  claim="The sandstone pinnacle — read by the Egyptians as a rearing cobra and "
        "the dwelling of Amun — plus the dense field of steep Nubian pyramids, "
        "is presented as a second, older centre of the same off-world "
        "architectural programme.",
  context="Jebel Barkal is the religious capital of Napata and later of the "
          "Kingdom of Kush, a UNESCO World Heritage site with a continuous "
          "excavated sequence from the New Kingdom Egyptian occupation through "
          "the Napatan and Meroitic periods. Nubian pyramid geometry is a "
          "local development, steeper and smaller than Egyptian models and "
          "built centuries later."),

S("hoggar", "Hoggar Mountains",
  subtitle="Ahaggar, southern Algeria", country="Algeria", region="Africa",
  category="landform", tags=["rock-art", "tassili", "sahara", "volcanic"],
  aliases=["Ahaggar", "Tassili n'Ajjer", "Sahara rock art"],
  wikipedia="Hoggar Mountains", lat=23.2917, lon=5.5333, height=120000,
  precision="area", radius_km=150,
  claim="Saharan rock art of the Hoggar and neighbouring Tassili — notably the "
        "large round-headed figures Henri Lhote nicknamed the 'Great Martian "
        "God' — is cited as a contemporary record of visitors in helmets and "
        "suits.",
  context="The Round Head style (c. 10,000–6,000 BP) belongs to a long, "
          "stratified Saharan sequence spanning hunter, pastoral, horse and "
          "camel periods, documenting a green Sahara. Lhote coined the "
          "'Martian' label himself as a flourish and later regretted it; the "
          "figures are generally read as masked or painted ritual "
          "participants, a convention still practised in the region."),

S("mali-dogon", "Dogon Country — Bandiagara Escarpment",
  subtitle="Mopti Region, Mali", country="Mali", region="Africa",
  category="sacred", tags=["unesco", "ethnoastronomy", "sirius", "dogon"],
  aliases=["Dogon", "Sirius B", "Nommo", "Bandiagara"],
  wikipedia="Bandiagara Escarpment", lat=14.3500, lon=-3.6000, height=20000,
  precision="area", radius_km=60,
  claim="The Dogon are said to have known that Sirius has a dense, invisible "
        "companion with a fifty-year orbit, taught to them by amphibious beings "
        "called the Nommo who came from that system.",
  context="The claim rests on Marcel Griaule and Germaine Dieterlen's 1950 "
          "paper. Anthropologist Walter van Beek's later fieldwork among the "
          "same communities found no independent Sirius-B tradition and "
          "concluded Griaule's informants had reflected back material "
          "introduced during interviews — Sirius B's orbit was published in "
          "1844 and widely reported before Griaule's visits. The Bandiagara "
          "Escarpment remains a World Heritage site of major importance."),

S("sierra-leone-nomoli", "Nomoli Figurine Country",
  subtitle="Kono / Kenema districts, Sierra Leone", country="Sierra Leone",
  region="Africa", category="artifact",
  tags=["figurines", "soapstone", "sapi", "diamond-fields"],
  aliases=["Nomoli", "Pomdo", "Sapi"],
  wikipedia="Nomoli figurine", lat=7.8670, lon=-11.1830, height=60000,
  precision="area", radius_km=70,
  claim="Soapstone figures turned up by diamond diggers, sometimes said to be "
        "found in gravels dated far older than any local culture, are presented "
        "as portraits of non-human visitors.",
  context="Nomoli are attributed to the Sapi culture of roughly the 15th–17th "
          "centuries and are related to the Sherbro pomdo tradition; "
          "comparable Sapi ivories were exported to Portugal and are securely "
          "dated. The 'found in ancient gravel' reports come from "
          "uncontrolled artisanal mining with no stratigraphic record, so they "
          "cannot date the objects."),

S("rhino-cave", "Rhino Cave, Tsodilo Hills",
  subtitle="Ngamiland, Botswana", country="Botswana", region="Africa",
  category="underground", tags=["unesco", "rock-art", "middle-stone-age",
                                "python"],
  aliases=["Tsodilo", "Python Cave", "Female Hill"],
  wikipedia="Tsodilo", lat=18.7500, lon=21.7333, height=6000,
  precision="approximate",
  claim="A python-shaped rock panel with hundreds of worked cupules, and "
        "deliberately burned spearpoints of non-local stone, are offered as a "
        "70,000-year-old ritual to serpent beings from the sky.",
  context="Sheila Coulson's excavations did report ritual destruction of "
          "finely made points in the cave, which — if the Middle Stone Age "
          "dating holds — would place symbolic behaviour here remarkably "
          "early. That is an argument about the antiquity of human ritual, not "
          "its authorship. The Tsodilo Hills hold over 4,500 paintings and "
          "remain sacred to Ju/'hoansi and Hambukushu communities today."),

S("south-africa", "Southern Africa — Blaauboschkraal Ruins",
  subtitle="Mpumalanga, South Africa", country="South Africa", region="Africa",
  category="megalithic", tags=["stone-ruins", "adams-calendar", "bokoni"],
  aliases=["Adam's Calendar", "Blaauboschkraal", "Mpumalanga stone ruins"],
  wikipedia="Blaauboschkraal stone ruins", lat=-25.5947, lon=30.2889,
  height=4000, precision="approximate",
  claim="Promoted as 'Adam's Calendar', a 75,000-year-old solstice-aligned "
        "monument, tied to Zecharia Sitchin's Anunnaki gold-mining narrative "
        "and the region's ancient workings.",
  context="Archaeologists identify the site as part of the Bokoni stone-walled "
          "agricultural complexes of roughly AD 1500–1820 — terraces, "
          "cattle byres and homestead walls documented across Mpumalanga. No "
          "peer-reviewed dating supports a Pleistocene age; the 75,000-year "
          "figure originates in self-published work. Southern Africa does hold "
          "genuinely ancient mining, including Lion Cavern ochre workings in "
          "Eswatini at c. 41,000 BP."),

S("african-congo", "Congo Basin",
  subtitle="Democratic Republic of the Congo (regional)",
  country="Democratic Republic of the Congo", region="Africa",
  category="region", tags=["rainforest", "mokele-mbembe", "cryptid"],
  aliases=["Congo", "Mokele-mbembe"],
  wikipedia="Congo Basin", lat=-1.0000, lon=23.0000, height=1500000,
  precision="area", radius_km=800, pitch=-70,
  claim="Episodes invoke the Congo for reports of Mokele-mbembe, for Ndoki "
        "forest legends of beings descending from the sky, and for uranium "
        "from Shinkolobwe feeding the first atomic weapons — framed as "
        "knowledge directed from outside.",
  context="No specimen, bone or verified photograph of Mokele-mbembe exists "
          "after more than a century of expeditions. Shinkolobwe's uranium "
          "supply to the Manhattan Project is thoroughly documented colonial "
          "economic history. The basin's actual scientific significance lies "
          "in its biodiversity and in the Oklo natural fission reactors in "
          "neighbouring Gabon — a geological, not engineered, phenomenon."),

S("somalia-coast", "Somali Coast",
  subtitle="Horn of Africa littoral", country="Somalia", region="Africa",
  category="region", tags=["punt", "maritime", "rock-art", "laas-geel"],
  aliases=["Land of Punt", "Laas Geel"],
  wikipedia="Laas Geel", lat=9.8000, lon=48.5000, height=900000,
  precision="area", radius_km=500, pitch=-70,
  claim="Referenced as a candidate for the Egyptian Land of Punt and for the "
        "Laas Geel rock art, whose haloed cattle and robed figures are read as "
        "depictions of visitors.",
  context="Punt's location is genuinely unresolved and debated between the "
          "Somali coast, Eritrea and Sudan — an open question in Egyptology "
          "settled by neither side. Laas Geel's polychrome panels "
          "(c. 3000–2500 BC) show cattle in ceremonial collars beside herders, "
          "consistent with a pastoral cult and with comparable Saharan and "
          "Nubian imagery."),

S("canary-islands", "Canary Islands",
  subtitle="Atlantic Ocean, Spain", country="Spain", region="Africa",
  category="megalithic", tags=["guanche", "pyramids", "atlantis", "step-pyramid"],
  aliases=["Guanche", "Güímar", "Tenerife", "Atlantis"],
  wikipedia="Pyramids of Güímar", lat=28.3192, lon=-16.4139, height=40000,
  precision="approximate",
  claim="The step-pyramids of Güímar and the aboriginal Guanche — tall, "
        "sometimes fair-haired, and mummifying their dead — are presented as "
        "survivors of Atlantis or as a transplanted population.",
  context="Thor Heyerdahl promoted the Güímar terraces as pyramids; Canarian "
          "archaeologists identify them as 19th-century agricultural "
          "clearance terraces built from field stone. Guanche ancestry is "
          "genetically Berber, matching North African populations, and their "
          "mummification is an independent local practice with its own "
          "stratified sequence."),


# ===========================================================================
# MIDDLE EAST
# ===========================================================================

S("baalbek", "Baalbek — Temple of Jupiter",
  subtitle="Beqaa Valley, Lebanon", country="Lebanon", region="Middle East",
  category="pyramid", tags=["unesco", "roman", "trilithon", "megalithic"],
  aliases=["Heliopolis", "Trilithon", "Stone of the Pregnant Woman"],
  wikipedia="Baalbek", lat=34.0069, lon=36.2039, height=900,
  claim="The three Trilithon blocks in the podium, each around 800 tonnes, and "
        "the ~1,650-tonne Stone of the Pregnant Woman still in the quarry, are "
        "the series' strongest 'impossible masonry' exhibit — attributed to "
        "pre-flood giants or anti-gravity.",
  context="The blocks are Roman, cut from a quarry 800 m away and slightly "
          "uphill, and the unfinished stones remain there with their "
          "extraction trenches, wedge slots and tool marks visible. Roman "
          "engineering handled comparable masses: the Vatican obelisk "
          "(~330 t) was re-erected in 1586 with 900 men, 75 horses and 40 "
          "capstans, a method documented in contemporary engravings. German "
          "excavations since 1898 have traced the podium's construction "
          "sequence directly."),

S("gobekli-tepe", "Göbekli Tepe",
  subtitle="Şanlıurfa Province, Turkey", country="Turkey", region="Middle East",
  category="megalithic", tags=["unesco", "neolithic", "t-pillars",
                               "pre-pottery", "archaeoastronomy"],
  aliases=["Sanliurfa", "Urfa", "Potbelly Hill", "Karahan Tepe"],
  wikipedia="Göbekli Tepe", lat=37.2236, lon=38.9217, height=700,
  claim="A monumental enclosure complex 7,000 years older than Stonehenge, "
        "built before agriculture and then deliberately buried, is presented "
        "as proof of an advanced instructor civilisation — with the Pillar 43 "
        "'Vulture Stone' read as a dated record of a comet impact or a star map.",
  context="Göbekli Tepe genuinely overturned assumptions about Neolithic "
          "social complexity and is one of the most important excavations of "
          "the last half-century. It is also demonstrably local: the limestone "
          "is from the same ridge, unfinished pillars lie in situ in the "
          "bedrock quarry, and flint tools, animal bone and grinding "
          "equipment show a hunter-forager community capable of organised "
          "labour. Recent work has revised the 'deliberate backfill' model "
          "toward gradual slope accumulation. The 'comet' reading of Pillar 43 "
          "has been contested in the literature on both statistical and "
          "iconographic grounds.",
  links=[{"label": "German Archaeological Institute — Göbekli Tepe project",
          "url": "https://www.dainst.org/projekt/-/project-display/25953",
          "kind": "reference"}]),

S("derinkuyu", "Derinkuyu Underground City",
  subtitle="Nevşehir Province, Turkey", country="Turkey", region="Middle East",
  category="underground", tags=["unesco", "cappadocia", "tuff", "byzantine"],
  aliases=["Elengubu", "Nevsehir"],
  wikipedia="Derinkuyu underground city", lat=38.3747, lon=34.7350,
  height=1200,
  claim="An eighteen-storey city cut 85 m into rock, with ventilation shafts, "
        "wells, stables and multi-tonne rolling stone doors operable only from "
        "inside, is presented as a shelter against an aerial threat — or as "
        "excavated with beam technology.",
  context="Cappadocian tuff is soft volcanic ash-rock that cuts with hand "
          "tools and hardens on exposure; the region holds more than 200 such "
          "complexes. Derinkuyu's phases run from Phrygian beginnings through "
          "heavy Byzantine expansion, when the doors — barring from inside, "
          "exactly as a refuge should — sheltered populations from Arab and "
          "later Mongol raids. Chapels, wine presses and Greek inscriptions "
          "date the occupation directly."),

S("cappadocia", "Cappadocia",
  subtitle="Central Anatolia, Turkey", country="Turkey", region="Middle East",
  category="underground", tags=["unesco", "fairy-chimneys", "rock-cut",
                                "volcanic"],
  aliases=["Göreme", "fairy chimneys", "Kaymaklı"],
  wikipedia="Cappadocia", lat=38.6431, lon=34.8286, height=40000,
  precision="area", radius_km=50,
  claim="The whole landscape — hundreds of underground cities, rock-cut "
        "churches and 'fairy chimney' towers — is framed as the surface of an "
        "engineered refuge system rather than a geological formation.",
  context="The fairy chimneys are differential erosion: soft ignimbrite from "
          "Erciyes, Hasandağ and Göllüdağ capped by harder basalt. The "
          "rock-cut settlement is real, extensive and dated, running from the "
          "Hittite period through a Byzantine monastic florescence that left "
          "frescoes with donor inscriptions."),

S("hierapolis", "Hierapolis — Pluto's Gate",
  subtitle="Pamukkale, Denizli Province, Turkey", country="Turkey",
  region="Middle East", category="sacred",
  tags=["unesco", "ploutonion", "travertine", "greco-roman"],
  aliases=["Pamukkale", "Ploutonion", "Plutonium", "Gate to Hell"],
  wikipedia="Hierapolis", lat=37.9247, lon=29.1253, height=1200,
  claim="A sanctuary where birds and sacrificial animals died at the threshold "
        "while robed priests walked in unharmed is presented as a literal "
        "portal, and the white travertine terraces as artificial.",
  context="The Ploutonion sits on the Babadag fault and vents concentrated "
          "CO₂. Measurements at the site record lethal concentrations pooling "
          "at ground level at night and dispersing by day, which accounts "
          "precisely for dead birds at the entrance and for tall priests "
          "breathing above the layer. Strabo described the effect in the 1st "
          "century BC. The terraces are calcite precipitating from "
          "hot springs."),

S("nemrut-dagi", "Nemrut Dağı — Kingdom of Commagene",
  subtitle="Adıyaman Province, Turkey", country="Turkey", region="Middle East",
  category="megalithic", tags=["unesco", "hellenistic", "tumulus",
                               "archaeoastronomy"],
  aliases=["Mount Nemrut", "Antiochus I", "Commagene"],
  wikipedia="Mount Nemrut", lat=37.9808, lon=38.7414, height=1800,
  claim="Colossal severed heads on a 2,134 m summit, beside a lion relief read "
        "as the oldest horoscope, are presented as a landing marker and as a "
        "king's claim to non-human descent.",
  context="The hierothesion of Antiochus I of Commagene (r. 70–38 BC) is "
          "dated by its own Greek dedicatory inscriptions, which set out the "
          "cult calendar and name the syncretic Greco-Persian deities "
          "portrayed. The Lion Horoscope is a genuine and much-studied "
          "astronomical relief — it encodes a specific planetary conjunction, "
          "which is how the monument is dated. The heads fell from their "
          "bodies through earthquake and frost damage."),

S("taurus-mountains", "Taurus Mountains",
  subtitle="Southern Anatolia, Turkey", country="Turkey", region="Middle East",
  category="landform", tags=["karst", "obsidian", "regional"],
  wikipedia="Taurus Mountains", lat=37.3000, lon=34.5000, height=300000,
  precision="area", radius_km=250, pitch=-65,
  claim="Cited as the barrier range crossed by the first farmers, and as the "
        "source of ores and obsidian whose early, wide distribution is "
        "presented as directed trade.",
  context="The Taurus is the northern arc of the Fertile Crescent and the "
          "heartland of early plant and animal domestication. Obsidian "
          "sourcing by trace-element analysis has mapped Anatolian exchange "
          "networks in detail — showing exactly the gradual, distance-decayed "
          "pattern expected of ordinary trade."),

S("troy", "Troy (Truva)",
  subtitle="Çanakkale Province, Turkey", country="Turkey", region="Middle East",
  category="city", tags=["unesco", "bronze-age", "homer", "hisarlik"],
  aliases=["Hisarlik", "Ilios", "Trojan War", "Truva"],
  wikipedia="Troy", lat=39.9576, lon=26.2387, height=1200,
  claim="The Iliad's gods intervening in battle, and the Trojan Horse itself, "
        "are read as a garbled memory of aerial craft and of a machine "
        "mistaken for an animal.",
  context="Hisarlık holds nine superimposed settlement phases from c. 3000 BC, "
          "and Troy VI/VIIa show destruction consistent with the traditional "
          "war horizon. Divine intervention is a structural convention of "
          "Greek epic, not reportage; the horse appears in the Odyssey and "
          "later sources rather than in the Iliad's narrative, and is "
          "generally read as a siege engine or as literary invention."),

S("turkey-anatolia", "Anatolia",
  subtitle="Türkiye (regional)", country="Turkey", region="Middle East",
  category="region", tags=["regional", "neolithic", "crossroads"],
  wikipedia="Anatolia", lat=39.0000, lon=35.0000, height=1400000,
  precision="area", radius_km=600, pitch=-70,
  claim="Anatolia as a whole is treated as the hinge of the series' timeline — "
        "where Göbekli Tepe, Çatalhöyük, Derinkuyu and the Hittites supposedly "
        "record successive waves of contact.",
  context="Anatolia is one of the best-studied archaeological regions on "
          "Earth, with a continuous sequence from Palaeolithic through "
          "Neolithic Çatalhöyük and Aşıklı Höyük to Hittite, Phrygian, Greek, "
          "Roman, Byzantine, Seljuk and Ottoman phases. The density of firsts "
          "here reflects early sedentism in a resource-rich corridor."),

S("black-sea-turkey", "Black Sea (Turkish Coast)",
  subtitle="Southern Black Sea shelf", country="Turkey", region="Middle East",
  category="underwater", tags=["flood-hypothesis", "marine", "submerged"],
  aliases=["Black Sea deluge", "Ryan-Pitman"],
  wikipedia="Black Sea deluge hypothesis", lat=41.7000, lon=35.0000,
  height=600000, precision="area", radius_km=350, pitch=-70,
  claim="Drowned shorelines and freshwater molluscs on the shelf are presented "
        "as the literal Flood described to Noah — and as the event survivors "
        "were warned about from above.",
  context="Ryan and Pitman's 1997 catastrophic-inflow hypothesis is a real and "
          "actively debated piece of marine geology. Later coring and "
          "sea-level work support a Holocene reconnection with the "
          "Mediterranean but mostly argue for a slower, less violent rise than "
          "the original model, and some workers reverse the flow direction. "
          "Either way it is a datable geological event with no inferable "
          "agency."),

S("khorsabad", "Khorsabad (Dur-Sharrukin)",
  subtitle="Nineveh Governorate, Iraq", country="Iraq", region="Middle East",
  category="city", tags=["assyrian", "lamassu", "sargon-ii"],
  aliases=["Dur-Sharrukin", "Sargon II", "Lamassu"],
  wikipedia="Dur-Sharrukin", lat=36.5094, lon=43.2286, height=2500,
  claim="The winged, human-headed lamassu bulls guarding Sargon II's gates are "
        "presented as portraits of non-human guardians, and the city — raised "
        "complete and abandoned at the king's death — as built to order.",
  context="Dur-Sharrukin is a documented royal foundation of Sargon II "
          "(r. 721–705 BC) whose building inscriptions record the commission, "
          "the labour levies and the timber imports. Lamassu are apotropaic "
          "composite guardians, a standard Mesopotamian iconographic class "
          "with a traceable stylistic development. The site was looted and "
          "partly bulldozed in 2015, making its surviving documentation "
          "especially valuable."),

S("nineveh", "Nineveh",
  subtitle="Mosul, Nineveh Governorate, Iraq", country="Iraq",
  region="Middle East", category="city",
  tags=["assyrian", "library", "ashurbanipal", "gilgamesh"],
  aliases=["Mosul", "Ashurbanipal", "Library of Nineveh"],
  wikipedia="Nineveh", lat=36.3598, lon=43.1529, height=4000,
  claim="The Library of Ashurbanipal's tablets — the Epic of Gilgamesh, the "
        "Enuma Elish, lists of kings reigning for tens of thousands of years — "
        "are read as literal history of sky-born rulers.",
  context="The library is the single richest source for Mesopotamian "
          "literature and is read continuously by Assyriologists. The "
          "implausible reign lengths appear in the Sumerian King List, a "
          "genre of legitimising royal propaganda using sexagesimal numbers; "
          "the same documents become historically accurate once they reach "
          "verifiable dynasties. Gilgamesh is epic poetry with a probable "
          "historical kernel in a king of Uruk."),

S("ur-ziggurat", "Ziggurat of Ur",
  subtitle="Dhi Qar Governorate, Iraq", country="Iraq", region="Middle East",
  category="pyramid", tags=["sumer", "ziggurat", "nanna", "ur-nammu"],
  aliases=["Temple of Ur", "Ur-Nammu", "Nanna", "Tell el-Muqayyar"],
  wikipedia="Ziggurat of Ur", lat=30.9626, lon=46.1031, height=900,
  claim="The stepped platform is presented as a landing stage, and Nanna's "
        "'house' atop it — entered only by priests — as a residence for a "
        "physical being, in line with Sitchin's reading of the Anunnaki.",
  context="Built c. 2100 BC by Ur-Nammu, rebuilt by Nabonidus, and excavated "
          "by Leonard Woolley from 1922. Foundation cylinders name the "
          "builders and the god. Ziggurats are mud-brick solid cores with no "
          "internal chambers; their form elevates a shrine, a pattern "
          "repeated across Mesopotamia and continuous with earlier "
          "platform temples at Eridu."),

S("iraq-mesopotamia", "Mesopotamia (Sumer & Akkad)",
  subtitle="Tigris–Euphrates alluvium, Iraq", country="Iraq",
  region="Middle East", category="region",
  tags=["sumer", "cuneiform", "anunnaki", "regional"],
  aliases=["Sumer", "Anunnaki", "Babylonia"],
  wikipedia="Mesopotamia", lat=32.5000, lon=44.5000, height=900000,
  precision="area", radius_km=450, pitch=-70,
  claim="The core of Zecharia Sitchin's thesis: that Sumerian texts describe "
        "the Anunnaki arriving from a planet 'Nibiru' to mine gold and to "
        "engineer humanity, and that cuneiform records this as fact.",
  context="Sitchin's translations are rejected across Assyriology. 'Anunnaki' "
          "means roughly 'offspring of Anu' and denotes a class of deities; "
          "'Nibiru' in astronomical texts refers to a crossing-point and is "
          "usually identified with Jupiter or Mercury, not an extra planet. "
          "Sumerian lexical lists, grammars and bilingual tablets allow the "
          "language to be checked independently, and they do not support the "
          "readings."),

S("baghdad-museum", "National Museum of Iraq",
  subtitle="Baghdad, Iraq", country="Iraq", region="Middle East",
  category="artifact", tags=["museum", "baghdad-battery", "looting"],
  aliases=["Baghdad Battery", "Baghdad"],
  wikipedia="National Museum of Iraq", lat=33.3272, lon=44.3867, height=1500,
  claim="The 'Baghdad Battery' — a ceramic jar with a copper cylinder and iron "
        "rod — is presented as a Parthian galvanic cell, implying "
        "electroplating and electric light in antiquity.",
  context="Replicas do produce a fraction of a volt with an acidic "
          "electrolyte, but no wires, conductors or connected sets have ever "
          "been excavated, and no object from the period shows "
          "electroplating. The accepted reading is a storage vessel for "
          "sacred scrolls, matching similar jars from Seleucia whose "
          "organic contents survived. The museum's catastrophic 2003 looting "
          "is separately documented."),

S("tigris-euphrates", "Tigris & Euphrates Confluence",
  subtitle="Al-Qurnah, Basra Governorate, Iraq", country="Iraq",
  region="Middle East", category="landform",
  tags=["river", "shatt-al-arab", "eden"],
  aliases=["Shatt al-Arab", "Garden of Eden", "Al-Qurnah"],
  wikipedia="Shatt al-Arab", lat=31.0089, lon=47.4350, height=120000,
  precision="area", radius_km=150, pitch=-65,
  claim="The four-river description of Eden in Genesis is matched to this "
        "confluence, and the garden read as an off-world genetics facility.",
  context="Genesis names Tigris, Euphrates, Pishon and Gihon; the latter two "
          "are unidentified, and proposals range from the Karun and Wadi "
          "al-Batin to the Nile. The alluvium here has shifted substantially "
          "since antiquity, and the Shatt al-Arab itself is a late "
          "formation — which is why no fixed location can be derived from "
          "the text."),

S("temple-mount", "Temple Mount & Dome of the Rock",
  subtitle="Old City, Jerusalem", country="Israel / Palestine",
  region="Middle East", category="sacred",
  tags=["unesco", "herodian", "foundation-stone", "ark"],
  aliases=["Haram al-Sharif", "Al-Aqsa", "Jerusalem", "Ark of the Covenant",
           "Western Wall"],
  wikipedia="Temple Mount", lat=31.7780, lon=35.2354, height=700,
  claim="The Herodian platform's largest ashlars — the Western Stone is "
        "estimated at several hundred tonnes — plus the Ark of the Covenant "
        "described as lethal to touch, are presented as off-world engineering "
        "and a powered device.",
  context="The retaining walls are Herodian (late 1st century BC) with "
          "quarries identified within Jerusalem; drafted-margin ashlar is a "
          "diagnostic Herodian style found across his projects at Hebron and "
          "Caesarea. The Ark's described effects are theological narrative; "
          "the object has not been recovered and no engineering inference is "
          "available from the texts."),

S("mount-of-olives", "Mount of Olives",
  subtitle="East Jerusalem", country="Israel / Palestine", region="Middle East",
  category="sacred", tags=["ascension", "necropolis", "christianity"],
  aliases=["Ascension", "Gethsemane"],
  wikipedia="Mount of Olives", lat=31.7784, lon=35.2461, height=1500,
  claim="The Ascension — Jesus taken up in a cloud from this ridge — is read "
        "as a vertical departure in a craft witnessed by the disciples.",
  context="Acts 1 is a theological narrative composed decades after the events "
          "and structured to parallel Elijah's ascent in 2 Kings. The ridge "
          "itself holds the oldest continuously used Jewish cemetery in the "
          "world and multiple well-dated Byzantine and Crusader churches."),

S("bethlehem", "Bethlehem",
  subtitle="West Bank", country="Israel / Palestine", region="Middle East",
  category="sacred", tags=["nativity", "star-of-bethlehem", "unesco"],
  aliases=["Star of Bethlehem", "Nativity"],
  wikipedia="Bethlehem", lat=31.7054, lon=35.2024, height=3000,
  claim="The Star of Bethlehem — moving ahead of the magi, then stopping over "
        "one building — is read as a craft under intelligent control, since no "
        "astronomical body behaves that way.",
  context="Astronomical candidates include the 7 BC triple conjunction of "
          "Jupiter and Saturn in Pisces and a 5 BC Chinese-recorded nova. The "
          "'stopping' is also readable as retrograde motion, or as Matthew's "
          "literary device: the account is shaped to fulfil Numbers 24:17 and "
          "appears in only one gospel."),

S("jericho", "Jericho (Tell es-Sultan)",
  subtitle="West Bank", country="Israel / Palestine", region="Middle East",
  category="city", tags=["unesco", "neolithic", "oldest-city", "walls"],
  aliases=["Tell es-Sultan", "Walls of Jericho"],
  wikipedia="Jericho", lat=31.8700, lon=35.4440, height=2500,
  claim="Walls felled by trumpets and a shout are presented as an acoustic or "
        "directed-energy weapon supplied from above, and the Neolithic tower "
        "as the oldest defensive architecture built against an aerial threat.",
  context="Tell es-Sultan holds an 11,000-year sequence including the "
          "Pre-Pottery Neolithic tower and wall — among the earliest known "
          "monumental architecture, probably flood-defence and communal ritual "
          "rather than military. Kathleen Kenyon's excavations found the Late "
          "Bronze walls already ruined and the site largely unoccupied around "
          "the traditional date of Joshua's conquest, which is the core "
          "archaeological problem with the biblical account."),

S("qumran", "Qumran",
  subtitle="West Bank, Dead Sea shore", country="Israel / Palestine",
  region="Middle East", category="artifact",
  tags=["dead-sea-scrolls", "essenes", "book-of-enoch"],
  aliases=["Dead Sea Scrolls", "Essenes", "Book of Enoch"],
  wikipedia="Qumran", lat=31.7408, lon=35.4592, height=1500,
  claim="The scrolls' Enochic literature — Watchers descending, teaching "
        "metallurgy and astronomy, and fathering the Nephilim — is treated as "
        "a suppressed eyewitness account of contact.",
  context="1 Enoch is a real and important Second Temple text, preserved at "
          "Qumran in Aramaic and canonical in the Ethiopian Orthodox "
          "tradition. It belongs to the apocalyptic genre: pseudepigraphic, "
          "visionary and composed c. 300–100 BC, many centuries after the "
          "antediluvian era it narrates. Its exclusion from the Jewish and "
          "most Christian canons is a documented process of canon formation, "
          "not a suppression."),

S("mount-sodom", "Mount Sodom & the Dead Sea",
  subtitle="Southern Dead Sea, Israel", country="Israel", region="Middle East",
  category="landform", tags=["salt-diapir", "sodom", "dead-sea"],
  aliases=["Sodom and Gomorrah", "Lot's Wife", "Har Sedom"],
  wikipedia="Mount Sodom", lat=31.1000, lon=35.3900, height=8000,
  claim="Sodom and Gomorrah's destruction — fire from the sky, a survivor "
        "warned not to look back, a woman turned to salt — is read as a "
        "nuclear or directed strike, with Mount Sodom's salt pillars as the "
        "residue.",
  context="Mount Sodom is a halite diapir: a salt body extruded upward by "
          "pressure, continuously eroded into pillars. No radiological "
          "anomaly has been found in the basin. Candidate destruction layers "
          "at Bab edh-Dhra and Numeira show Early Bronze conflagration, and a "
          "contested airburst hypothesis for Tall el-Hammam was published in "
          "2021 and challenged on its methods in 2022 — a live scientific "
          "dispute about a natural event."),

S("mount-hermon", "Mount Hermon",
  subtitle="Anti-Lebanon range, Syria / Lebanon border",
  country="Syria / Lebanon", region="Middle East", category="sacred",
  tags=["watchers", "book-of-enoch", "transfiguration"],
  aliases=["Jebel el-Sheikh", "Watchers", "Nephilim"],
  wikipedia="Mount Hermon", lat=33.4165, lon=35.8572, height=12000,
  claim="1 Enoch names Hermon as the summit where two hundred Watchers "
        "descended and swore their oath; the series treats this as a precise "
        "landing coordinate preserved in scripture.",
  context="The Hermon tradition is attested in 1 Enoch 6 and the mountain "
          "carries a dense cluster of ancient sanctuaries along its slopes, "
          "reflecting its long-standing status as sacred high ground in "
          "Canaanite, Israelite, Greek and Roman cult. The descent narrative "
          "is apocalyptic literature; what the archaeology records is a "
          "sanctuary landscape."),

S("mount-sinai", "Mount Sinai (Jebel Musa)",
  subtitle="South Sinai Governorate, Egypt", country="Egypt",
  region="Middle East", category="sacred",
  tags=["exodus", "saint-catherines", "theophany"],
  aliases=["Jebel Musa", "Horeb", "Ten Commandments"],
  wikipedia="Mount Sinai", lat=28.5392, lon=33.9750, height=8000,
  claim="The Sinai theophany — smoke, fire, trumpet blast, violent quaking, a "
        "boundary nobody may cross on pain of death — is read as a landing "
        "with an exclusion zone, and the tablets as a delivered artefact.",
  context="Jebel Musa's identification as the biblical mountain is a Byzantine "
          "tradition from the 4th century AD, not a continuous one; Jebel "
          "Serbal, Hashem el-Tarif and locations in Arabia are all argued. "
          "The theophany's imagery is standard ancient Near Eastern "
          "storm-god language, paralleled in Ugaritic and Mesopotamian texts. "
          "Volcanic readings founder on Sinai's lack of Holocene volcanism."),

S("israel-west-bank", "Israel & the West Bank",
  subtitle="Southern Levant (regional)", country="Israel / Palestine",
  region="Middle East", category="region",
  tags=["regional", "levant", "biblical-archaeology"],
  wikipedia="Southern Levant", lat=31.6000, lon=35.1000, height=400000,
  precision="area", radius_km=120, pitch=-65,
  claim="Used as a regional frame for the series' biblical material: Ezekiel's "
        "wheel, Elijah's chariot, the Nephilim, and Joshua's sun standing "
        "still are presented as a dense local cluster of contact reports.",
  context="The southern Levant is among the most intensively excavated regions "
          "on Earth. The visions concerned belong to identifiable literary "
          "genres — merkabah vision, prophetic call narrative, holy-war "
          "poetry — whose conventions are reconstructable from comparative "
          "Near Eastern texts."),

S("mecca-kaaba", "Kaaba & Masjid al-Haram",
  subtitle="Mecca, Makkah Province, Saudi Arabia", country="Saudi Arabia",
  region="Middle East", category="sacred",
  tags=["islam", "black-stone", "meteorite", "hajj"],
  aliases=["Black Stone", "Hajar al-Aswad", "Grand Mosque", "Makkah"],
  wikipedia="Kaaba", lat=21.4225, lon=39.8262, height=900,
  claim="The Black Stone set in the Kaaba's eastern corner is proposed as a "
        "meteorite — a fragment delivered from the sky and venerated for "
        "millennia, as at other ancient sites.",
  context="The stone has never been scientifically sampled, so its nature is "
          "genuinely unestablished; meteoritic, impactite and agate origins "
          "have all been proposed in the literature. Veneration of "
          "sky-fallen stones is a real and widespread ancient practice — the "
          "Artemision of Ephesus and the cult of Elagabal at Emesa are "
          "documented cases — and it requires no visitors, only a visible "
          "fall."),


# ===========================================================================
# EUROPE — British Isles
# ===========================================================================

S("stonehenge", "Stonehenge",
  subtitle="Salisbury Plain, Wiltshire, England", country="United Kingdom",
  region="Europe", category="megalithic",
  tags=["unesco", "neolithic", "archaeoastronomy", "bluestone", "trilithon"],
  aliases=["Salisbury Plain", "Wiltshire", "bluestones"],
  wikipedia="Stonehenge", lat=51.1789, lon=-1.8262, height=600, pitch=-32,
  claim="Bluestones hauled 250 km from Wales, sarsens weighing up to 30 tonnes, "
        "mortise-and-tenon joints in stone and a solstice alignment are "
        "presented as a surveyed instrument built to an external "
        "specification — sometimes as an energy device or beacon.",
  context="Stonehenge is the most intensively studied prehistoric monument in "
          "Europe, built in stages over 1,500 years. The bluestone sources at "
          "Craig Rhos-y-felin and Carn Goedog have been excavated and matched "
          "petrologically; the sarsens were traced in 2020 to West Woods, 25 "
          "km north. Antler picks, rope, timber sledges and the Durrington "
          "Walls settlement that housed the builders are all recovered. The "
          "solstice alignment is real and intentional, and achievable by "
          "observation.",
  links=[{"label": "English Heritage — Stonehenge research",
          "url": "https://www.english-heritage.org.uk/visit/places/stonehenge/history-and-stories/",
          "kind": "reference"}]),

S("avebury", "Avebury",
  subtitle="Wiltshire, England", country="United Kingdom", region="Europe",
  category="megalithic", tags=["unesco", "neolithic", "henge", "silbury-hill"],
  aliases=["Silbury Hill", "West Kennet", "The Sanctuary"],
  wikipedia="Avebury", lat=51.4286, lon=-1.8544, height=2500,
  claim="The largest stone circle in Europe, with its avenues and the "
        "artificial mound of Silbury Hill, is read as a landscape-scale "
        "diagram — and the area's crop-circle concentration as a continuing "
        "signal.",
  context="The Avebury complex (c. 2850–2200 BC) is a World Heritage "
          "landscape with excavated ditch sections, buried stones recovered "
          "and re-erected by Alexander Keiller, and Silbury Hill's internal "
          "construction phases exposed by tunnelling. Crop formations in the "
          "area have been repeatedly claimed and demonstrated by their human "
          "makers since Doug Bower and Dave Chorley came forward in 1991."),

S("anglesey", "Anglesey (Ynys Môn)",
  subtitle="Wales, United Kingdom", country="United Kingdom", region="Europe",
  category="megalithic", tags=["druids", "bryn-celli-ddu", "neolithic", "copper"],
  aliases=["Ynys Mon", "Bryn Celli Ddu", "Druids", "Mona"],
  wikipedia="Anglesey", lat=53.2800, lon=-4.4000, height=60000,
  precision="area", radius_km=30,
  claim="Tacitus's account of the Roman assault on the Druid stronghold, plus "
        "the solstice-aligned passage tomb at Bryn Celli Ddu, is used to "
        "cast the Druids as custodians of transmitted off-world knowledge.",
  context="Anglesey holds a dense, well-excavated Neolithic and Bronze Age "
          "monument group and the Parys Mountain copper workings, mined from "
          "the Bronze Age. Druidic practice is known almost entirely through "
          "hostile Roman sources; Bryn Celli Ddu's midsummer alignment is "
          "securely demonstrated and locally achievable."),

S("callanish", "Callanish Stones",
  subtitle="Isle of Lewis, Outer Hebrides, Scotland",
  country="United Kingdom", region="Europe", category="megalithic",
  tags=["neolithic", "archaeoastronomy", "lunar-standstill", "hebrides"],
  aliases=["Calanais", "Outer Hebrides", "Isle of Lewis"],
  wikipedia="Callanish Stones", lat=58.1975, lon=-6.7450, height=700,
  claim="A cruciform setting of Lewisian gneiss, reported to frame the major "
        "lunar standstill against the 'Sleeping Beauty' ridge every 18.6 "
        "years, is presented as a predictive instrument beyond its builders.",
  context="Callanish (c. 3000 BC) is a genuine candidate for deliberate lunar "
          "alignment, and the 18.6-year standstill cycle is observable by a "
          "community that watches the horizon across generations — exactly "
          "what a permanent monument records. Peat growth later buried the "
          "stones to 1.5 m, which is how the original ground surface and "
          "central chambered cairn were preserved."),

S("stenness", "Stones of Stenness & Brodgar",
  subtitle="Orkney Islands, Scotland", country="United Kingdom",
  region="Europe", category="megalithic",
  tags=["unesco", "neolithic", "ness-of-brodgar", "orkney"],
  aliases=["Ring of Brodgar", "Ness of Brodgar", "Orkney", "Maeshowe"],
  wikipedia="Stones of Stenness", lat=58.9942, lon=-3.2078, height=1200,
  claim="The Orkney complex — henges, the Maeshowe chambered cairn and the "
        "Ness of Brodgar's painted walls — is cast as a northern command "
        "centre whose influence spread south to Stonehenge.",
  context="The Heart of Neolithic Orkney is a World Heritage site, and Orkney "
          "genuinely does appear to be a Neolithic innovation centre: "
          "grooved-ware pottery and henge architecture plausibly originate "
          "here and spread south. That is a mainstream and well-evidenced "
          "conclusion drawn from excavated sequences at Barnhouse, Skara Brae "
          "and the Ness of Brodgar."),

S("edinburgh-castle", "Edinburgh Castle & the Stone of Destiny",
  subtitle="Edinburgh, Scotland", country="United Kingdom", region="Europe",
  category="artifact", tags=["stone-of-scone", "coronation", "jacob's-pillow"],
  aliases=["Stone of Scone", "Stone of Destiny", "Jacob's Pillow"],
  wikipedia="Stone of Scone", lat=55.9486, lon=-3.1999, height=900,
  claim="The coronation stone is identified with Jacob's pillow from Genesis "
        "28 — the rock he slept on when he saw a ladder with beings ascending "
        "and descending — making it a relic of a contact event.",
  context="Geologists have matched the Stone of Scone to Old Red Sandstone "
          "from the Scone area in Perthshire, which rules out a Levantine "
          "origin. The Jacob's-pillow identification is a medieval origin "
          "legend serving dynastic legitimacy, of a kind common across "
          "European regalia."),

S("tintagel", "Tintagel Castle & Island",
  subtitle="Cornwall, England", country="United Kingdom", region="Europe",
  category="city", tags=["arthurian", "post-roman", "trade", "merlin"],
  aliases=["Cornwall", "King Arthur", "Merlin"],
  wikipedia="Tintagel Castle", lat=50.6680, lon=-4.7620, height=800,
  claim="Arthur's conception by Merlin's shape-shifting magic, and the sword "
        "drawn from stone, are read as engineered birth and as advanced "
        "metallurgy — with Tintagel as the point of intervention.",
  context="Excavation has revealed a substantial 5th–7th-century high-status "
          "settlement with imported Mediterranean amphorae and Phocaean red "
          "slip ware, plus a 7th-century inscribed slate — genuinely "
          "important evidence for post-Roman Atlantic trade. The Arthurian "
          "association derives from Geoffrey of Monmouth writing c. 1136, and "
          "the castle itself is 13th-century, built partly to trade on that "
          "legend."),

S("ilkley-moor", "Ilkley Moor — Twelve Apostles",
  subtitle="West Yorkshire, England", country="United Kingdom",
  region="Europe", category="megalithic",
  tags=["rock-art", "cup-and-ring", "swastika-stone", "ufo"],
  aliases=["Twelve Apostles", "Yorkshire", "Swastika Stone", "Cow and Calf"],
  wikipedia="Twelve Apostles, West Yorkshire", lat=53.9033, lon=-1.8217,
  height=1500, precision="approximate",
  claim="Bronze Age cup-and-ring carvings here are read as star charts, and "
        "the moor's reputation — including PC Alan Godfrey-era Yorkshire "
        "sighting reports and the 1987 'Ilkley Moor alien' photograph — as "
        "continuing activity.",
  context="Cup-and-ring marking is an Atlantic-wide rock-art tradition from "
          "Iberia to Scotland, with hundreds of panels on Rombalds Moor "
          "alone; its meaning is unresolved but its distribution is "
          "thoroughly mapped. The 1987 photograph has never been "
          "independently authenticated and the figure's proportions are "
          "consistent with a small model."),

S("rudloe-manor", "Rudloe Manor & Corsham Tunnels",
  subtitle="Wiltshire, England", country="United Kingdom", region="Europe",
  category="military", tags=["raf", "ufo-desk", "bunker", "corsham"],
  aliases=["Corsham", "Corsham Computer Centre", "Burlington", "RAF Rudloe Manor"],
  wikipedia="RAF Rudloe Manor", lat=51.4167, lon=-2.1983, height=3000,
  claim="Dubbed 'Britain's Area 51': the RAF site is said to have run a "
        "covert UFO desk, with recovered material held in the Bath-stone "
        "quarry complex beneath Corsham.",
  context="The MoD acknowledged that the Provost and Security Services at "
          "Rudloe Manor handled UFO report correspondence into the 1990s — a "
          "clerical function, later moved to Whitehall and then wound up in "
          "2009 when the MoD closed its UFO desk. The underground site is the "
          "declassified Burlington Central Government War Headquarters, now "
          "public record."),

S("rendlesham", "Rendlesham Forest — RAF Bentwaters & Woodbridge",
  subtitle="Suffolk, England", country="United Kingdom", region="Europe",
  category="ufo", tags=["1980", "usaf", "halt-memo", "cold-war"],
  aliases=["RAF Bentwaters", "RAF Woodbridge", "Suffolk", "Halt memo",
           "Britain's Roswell"],
  wikipedia="Rendlesham Forest incident", lat=52.0869, lon=1.4406, height=2500,
  claim="Over several nights in December 1980, USAF personnel from the twin "
        "bases reported lights descending into the forest, a landed craft "
        "with glyph-like markings and radiation traces — Britain's "
        "best-documented military encounter.",
  context="Deputy base commander Charles Halt's memo is genuine and "
          "declassified, which is why the case matters. Proposed "
          "explanations include the Orfordness lighthouse 8 km east "
          "(matching the pulsing light's bearing and interval), a bright "
          "fireball recorded that night, and the Shipwash light vessel; the "
          "radiation readings were within regional background. Witnesses "
          "continue to dispute these accounts, and the case remains "
          "unresolved rather than explained.",
  links=[{"label": "UK National Archives — released UFO files",
          "url": "https://www.nationalarchives.gov.uk/ufos/", "kind": "official"}]),

S("bonnybridge", "Bonnybridge — Falkirk Triangle",
  subtitle="Falkirk, Scotland", country="United Kingdom", region="Europe",
  category="anomaly", tags=["ufo-hotspot", "falkirk", "sighting-cluster"],
  aliases=["Falkirk Triangle", "Falkirk"],
  wikipedia="Bonnybridge", lat=56.0000, lon=-3.8900, height=12000,
  precision="area", radius_km=12,
  claim="Several hundred sighting reports a year since 1992 make this small "
        "Scottish town, with the surrounding 'Falkirk Triangle', one of the "
        "densest reported UFO clusters on Earth.",
  context="The report volume is real and traceable to local campaigning that "
          "began in 1992 and actively solicited accounts — a reporting "
          "artefact well documented in the sighting literature. The area sits "
          "beneath Edinburgh and Glasgow approach corridors and near "
          "Grangemouth's flare stacks. No physical trace evidence has been "
          "produced."),

S("newgrange", "Newgrange (Brú na Bóinne)",
  subtitle="County Meath, Ireland", country="Ireland", region="Europe",
  category="megalithic", tags=["unesco", "neolithic", "passage-tomb",
                               "solstice", "archaeoastronomy"],
  aliases=["Bru na Boinne", "Boyne Valley", "Knowth", "Dowth"],
  wikipedia="Newgrange", lat=53.6947, lon=-6.4753, height=700,
  claim="A 5,200-year-old passage tomb whose roof-box admits the winter "
        "solstice sunrise to the exact end of a 19 m passage is presented as "
        "an engineered instrument requiring surveying the builders could not "
        "have had.",
  context="Newgrange predates Giza and Stonehenge, and the roof-box alignment "
          "is real, deliberate and among the finest in prehistory. It is also "
          "achievable by staking a sightline over successive solstices before "
          "building — a multi-generation observation programme, which the "
          "Boyne complex's three great mounds and dozens of satellites show "
          "was well within this society's organisational reach. Quartz from "
          "Wicklow and granite from the Mournes were brought by sea and "
          "river."),

S("uisneach", "Hill of Uisneach",
  subtitle="County Westmeath, Ireland", country="Ireland", region="Europe",
  category="sacred", tags=["ail-na-mireann", "bealtaine", "royal-site"],
  aliases=["Ail na Mireann", "Catstone", "Navel of Ireland"],
  wikipedia="Uisneach", lat=53.4897, lon=-7.3714, height=2500,
  claim="The ceremonial 'navel of Ireland', with its great erratic boulder "
        "marking the meeting of the provinces, is presented as a surveyed "
        "centre point fixed from above.",
  context="Uisneach is a genuine royal and assembly site with excavated "
          "enclosures, a burnt mound and a long Bealtaine fire tradition "
          "described in early Irish literature. The Ail na Mireann is a "
          "glacial erratic — a naturally transported boulder that the "
          "tradition invested with meaning. Geodetically it is near, but not "
          "at, the island's centroid."),

S("cambridge-university", "University of Cambridge",
  subtitle="Cambridge, England", country="United Kingdom", region="Europe",
  category="research", tags=["academia", "seti", "physics"],
  wikipedia="University of Cambridge", lat=52.2043, lon=0.1149, height=2000,
  claim="Appears as an interview location: Cambridge researchers are cited on "
        "exoplanet statistics, panspermia and the Drake equation, with their "
        "remarks used to support the plausibility of contact.",
  context="The institutional work referenced is real — Cambridge contributes "
          "substantially to exoplanet detection and astrobiology. The "
          "inferential leap is in the editing: statements about the "
          "likelihood of life elsewhere are not statements about visits to "
          "Earth, and researchers have repeatedly objected to that splice."),

S("open-university", "The Open University",
  subtitle="Milton Keynes, England", country="United Kingdom", region="Europe",
  category="research", tags=["academia", "planetary-science", "meteoritics"],
  aliases=["Milton Keynes"],
  wikipedia="Open University", lat=52.0245, lon=-0.7093, height=2000,
  claim="Cited for its planetary and meteoritic research, invoked to support "
        "the proposition that organic precursors — and so life — arrived on "
        "Earth from space.",
  context="The OU's planetary science group does lead genuine work on "
          "meteoritic organics and sample return. Amino acids and nucleobases "
          "in carbonaceous chondrites are an established finding. That "
          "supports exogenous delivery of chemistry, which is a mainstream "
          "hypothesis — and says nothing about intelligent agents."),

# ===========================================================================
# EUROPE — France, Iberia, Italy
# ===========================================================================

S("carnac", "Carnac Stones",
  subtitle="Brittany, France", country="France", region="Europe",
  category="megalithic", tags=["neolithic", "alignments", "menhir", "brittany"],
  aliases=["Brittany", "Menec", "Ménec", "Le Grand Menhir Brisé",
           "Kermario", "Locmariaquer"],
  wikipedia="Carnac stones", lat=47.5944, lon=-3.0794, height=3000,
  claim="More than 3,000 menhirs in multi-kilometre rows, plus Le Grand "
        "Menhir Brisé at an estimated 280 tonnes and 20 m, are presented as a "
        "surveyed grid — a runway, a lunar observatory, or an energy array "
        "exploiting the local granite's piezoelectric quartz.",
  context="The alignments were raised over roughly 2,000 years from c. 4500 BC "
          "and are a stratified, excavated landscape with contemporary "
          "settlements, tombs and quarry sources nearby. Le Grand Menhir lies "
          "in four pieces at Locmariaquer and was probably broken during "
          "erection or by earthquake; Alexander Thom's proposal that it "
          "served as a universal lunar foresight was tested and is no longer "
          "accepted. Granite's piezoelectric response is negligible at "
          "ambient stresses."),

S("chateau-chinon", "Château-Chinon",
  subtitle="Nièvre, Burgundy, France", country="France", region="Europe",
  category="ufo", tags=["sighting", "morvan", "burgundy"],
  aliases=["Chateau-Chinon", "Morvan", "Nièvre"],
  wikipedia="Château-Chinon", lat=47.0667, lon=3.9333, height=6000,
  precision="approximate",
  claim="Cited among the French sighting record — the kind of rural case that "
        "fed GEPAN/GEIPAN, France's official state investigation of "
        "unidentified aerospace phenomena.",
  context="France is genuinely unusual in running a public, state-funded "
          "investigation: GEIPAN, within CNES, has published its case files "
          "online since 2007. Its own statistics classify roughly a quarter "
          "of cases as unexplained for want of data (class D) — a statement "
          "about insufficient information, not about origin.",
  links=[{"label": "GEIPAN (CNES) — official case database",
          "url": "https://www.cnes-geipan.fr/", "kind": "official"}]),

S("orleans", "Orléans",
  subtitle="Centre-Val de Loire, France", country="France", region="Europe",
  category="sacred", tags=["joan-of-arc", "siege", "visions"],
  aliases=["Joan of Arc", "Jeanne d'Arc", "Siege of Orleans"],
  wikipedia="Orléans", lat=47.9029, lon=1.9093, height=5000,
  claim="Joan of Arc's voices and visions, her unexplained military "
        "competence and her knowledge of a hidden sword are presented as "
        "guidance from a non-human source.",
  context="Joan's trial and rehabilitation transcripts are exceptionally full "
          "primary records, and they document her own description of the "
          "voices as saints. The military record shows a figure of immense "
          "morale value operating alongside experienced commanders such as "
          "Dunois and La Hire. Medieval visionary experience is a "
          "well-studied religious and historical phenomenon."),

S("florence-vinci", "Florence & Vinci",
  subtitle="Tuscany, Italy", country="Italy", region="Europe",
  category="artifact", geometry="multipoint",
  points=[(43.7629, 11.2650), (43.7838, 10.9256)],
  tags=["leonardo", "renaissance", "flight", "codex"],
  aliases=["Leonardo da Vinci", "Piazzale Michelangelo", "Tuscany"],
  wikipedia="Leonardo da Vinci", lat=43.7696, lon=11.2558, height=30000,
  claim="Leonardo's ornithopter, parachute, aerial screw and armoured vehicle "
        "designs are presented as too far ahead of 1500 to be original, "
        "implying access to recovered or transmitted knowledge.",
  context="Leonardo's notebooks document his process — anatomical bird "
          "studies, failed trials, iterative correction and clear "
          "intellectual debts to Vitruvius, Archimedes and contemporaries "
          "such as Taccola and Francesco di Giorgio. Several designs do not "
          "work as drawn: the ornithopter cannot generate the required power "
          "and the aerial screw lacks torque compensation. That is the "
          "signature of invention, not transcription."),

S("montevecchia", "Montevecchia",
  subtitle="Brianza, Lombardy, Italy", country="Italy", region="Europe",
  category="megalithic", tags=["terraces", "claimed-pyramids", "lombardy"],
  aliases=["Milan", "Brianza", "Italian pyramids"],
  wikipedia="Montevecchia", lat=45.7050, lon=9.3917, height=5000,
  claim="Three terraced hills near Milan, reported to mirror Orion's belt and "
        "to share the Giza pyramids' slope angle, are promoted as Europe's "
        "lost pyramid complex.",
  context="The hills are natural moraine and bedrock features, agriculturally "
          "terraced over centuries for vines — a standard Brianza landscape "
          "practice. No excavation has produced built structure, and no "
          "Italian archaeological authority recognises them as monuments. "
          "Orion correlations are easy to generate from any three raised "
          "points."),

S("rome", "Rome",
  subtitle="Lazio, Italy", country="Italy", region="Europe",
  category="city", tags=["unesco", "obelisks", "pantheon", "concrete"],
  aliases=["Roman Empire", "Pantheon", "Colosseum"],
  wikipedia="Rome", lat=41.9028, lon=12.4964, height=12000,
  claim="Rome's thirteen re-erected Egyptian obelisks, the Pantheon's "
        "unreinforced 43 m concrete dome and the empire's engineering reach "
        "are cited as inherited technology.",
  context="Roman hydraulic concrete is a well-characterised material: "
          "volcanic pozzolana with lime, whose aluminous tobermorite and "
          "self-healing lime clasts were identified by modern materials "
          "science between 2017 and 2023. The Pantheon's dome tapers and uses "
          "progressively lighter aggregate toward the oculus. Obelisk "
          "transport and re-erection are documented in Pliny, in the "
          "purpose-built Obelisk Ship, and in Renaissance engravings of the "
          "1586 Vatican move."),

S("vatican-city", "Vatican City",
  subtitle="Vatican City State", country="Vatican City", region="Europe",
  category="sacred", tags=["unesco", "vatican-observatory", "archives",
                           "specola"],
  aliases=["Holy See", "Vatican Observatory", "Specola Vaticana",
           "Vatican Secret Archives"],
  wikipedia="Vatican City", lat=41.9029, lon=12.4534, height=1200,
  claim="The Vatican Observatory's work, its LUCIFER-instrumented telescope "
        "on Mount Graham, and senior clerics' public remarks about baptising "
        "extraterrestrials are presented as evidence the Church knows more "
        "than it says, with proof held in the Apostolic Archive.",
  context="The Vatican Observatory is a working research institution "
          "publishing in refereed journals, and its Mount Graham "
          "collaboration is a real partnership with the University of "
          "Arizona. LUCIFER is an acronym for a German-built near-infrared "
          "spectrograph, since renamed LUCI. The Apostolic Archive has been "
          "open to credentialed researchers since 1881; its catalogue is "
          "published.",
  links=[{"label": "Vatican Observatory", "url": "https://www.vaticanobservatory.va/",
          "kind": "official"}]),

S("sicily-shipwreck", "Sicily — Gela Shipwrecks",
  subtitle="Gela, Sicily, Italy", country="Italy", region="Europe",
  category="underwater", tags=["shipwreck", "orichalcum", "atlantis", "ingots"],
  aliases=["Gela", "orichalcum", "Atlantis ingots"],
  wikipedia="Gela", lat=37.0667, lon=14.2500, height=20000,
  precision="approximate",
  claim="Metal ingots recovered off Gela were reported in 2015 as orichalcum, "
        "the alloy Plato says clad the walls of Atlantis — cited as physical "
        "confirmation of the lost city.",
  context="Analysis identified the ingots as a brass alloy of roughly 75–80% "
          "copper with zinc, lead and iron — a composition consistent with "
          "6th-century-BC Mediterranean metallurgy and cargo from a "
          "shipwreck. 'Orichalcum' is a term of uncertain reference used by "
          "several ancient authors for brass-like alloys; the identification "
          "is a label, not a provenance, and Plato's Atlantis appears in the "
          "Timaeus and Critias as a didactic fiction."),

S("fatima", "Fátima",
  subtitle="Santarém District, Portugal", country="Portugal", region="Europe",
  category="sacred", tags=["marian-apparition", "miracle-of-the-sun", "1917"],
  aliases=["Miracle of the Sun", "Our Lady of Fatima", "Cova da Iria"],
  wikipedia="Our Lady of Fátima", lat=39.6317, lon=-8.6727, height=3000,
  claim="The 13 October 1917 'Miracle of the Sun' — a crowd of tens of "
        "thousands reporting the sun spinning, changing colour and plunging "
        "toward the earth, preceded by a luminous object and a figure visible "
        "to three children — is read as a mass contact event rather than a "
        "Marian apparition.",
  context="The event is unusually well attested for its size, and accounts "
          "vary widely: many present reported nothing. Proposed natural "
          "explanations include sun-gazing-induced retinal afterimages and "
          "phosphene effects, atmospheric optics from ice crystals, and "
          "collective expectation in a crowd primed by three months of "
          "publicity. No instrument recorded solar motion, and observatories "
          "worldwide recorded nothing."),

S("spain-explorers", "Spain",
  subtitle="Iberian Peninsula (regional)", country="Spain", region="Europe",
  category="region", tags=["regional", "conquest", "chronicles"],
  aliases=["Iberia", "conquistadors"],
  wikipedia="Spain", lat=40.4168, lon=-3.7038, height=900000,
  precision="area", radius_km=400, pitch=-70,
  claim="Spain enters the series through the chroniclers — Sahagún, Las Casas, "
        "Cieza de León — whose records of Aztec and Inca testimony about "
        "sky-born teachers are treated as transcribed eyewitness accounts.",
  context="The chronicles are indispensable primary sources and also deeply "
          "mediated: written by missionaries and soldiers, through "
          "interpreters, to justify conquest and conversion, and routinely "
          "assimilating indigenous deities to European demonological "
          "categories. Modern Mesoamerican and Andean scholarship reads them "
          "against archaeology and indigenous-language sources precisely "
          "because of that filtering."),

S("gibraltar", "Strait of Gibraltar — Pillars of Hercules",
  subtitle="Gibraltar / Spain / Morocco", country="Gibraltar / Spain / Morocco",
  region="Europe", category="landform",
  tags=["atlantis", "strait", "gorhams-cave", "neanderthal"],
  aliases=["Pillars of Hercules", "Gorham's Cave", "Jebel Musa"],
  wikipedia="Pillars of Hercules", lat=36.1408, lon=-5.3536, height=60000,
  claim="Plato places Atlantis beyond the Pillars; the series treats the "
        "strait as the gateway to a drowned civilisation, with Gorham's Cave "
        "rock engravings cited as surviving evidence of advanced "
        "pre-human culture.",
  context="The Gorham's Cave complex is a World Heritage site and genuinely "
          "important: it preserves Neanderthal occupation to c. 32,000 BP "
          "and an abstract engraved 'hashtag' panel — real evidence of "
          "Neanderthal symbolic behaviour, which is a significant scientific "
          "finding about hominins, not visitors. The Atlantis passages are "
          "Plato's own framed allegory, introduced as a story told at "
          "several removes."),

# ===========================================================================
# EUROPE — Greece & the Aegean
# ===========================================================================

S("acropolis-athens", "Acropolis of Athens & the Parthenon",
  subtitle="Athens, Attica, Greece", country="Greece", region="Europe",
  category="pyramid", tags=["unesco", "classical", "entasis", "pentelic"],
  aliases=["Parthenon", "Athens", "Athena", "Erechtheion"],
  wikipedia="Acropolis of Athens", lat=37.9715, lon=23.7267, height=700,
  claim="The Parthenon's optical refinements — entasis, upward-curving "
        "stylobate, inward-leaning columns, no two blocks identical — are "
        "presented as tolerances requiring instruments the Greeks lacked.",
  context="The refinements are real and are among the best-understood "
          "achievements in architectural history, reconstructed from the "
          "building's own cut marks, from Pentelic quarry faces, and from "
          "the Athenian accounts inscribed on stone that list materials, "
          "wages and contractors. Iktinos and Kallikrates are named as "
          "architects; Manolis Korres's drawings trace the geometry "
          "block by block from surviving tool evidence."),

S("delphi", "Delphi — Temple of Apollo",
  subtitle="Phocis, Greece", country="Greece", region="Europe",
  category="sacred", tags=["unesco", "oracle", "pythia", "ethylene"],
  aliases=["Temple of Apollo", "Oracle of Delphi", "Pythia", "Omphalos"],
  wikipedia="Delphi", lat=38.4824, lon=22.5010, height=900,
  claim="The Pythia's trance prophecies, delivered over a chasm, are "
        "presented as a channel to a non-human intelligence, with the "
        "omphalos stone marking a surveyed world centre.",
  context="Geologists de Boer and Hale mapped intersecting faults beneath the "
          "adyton and measured ethylene and methane in the spring waters — "
          "ethylene produces euphoric trance at low concentration, matching "
          "ancient descriptions of sweet-smelling pneuma. The finding has "
          "been debated on concentration grounds, but it gives a testable "
          "natural mechanism. The oracle's political function in Greek "
          "decision-making is extensively documented."),

S("mount-olympus", "Mount Olympus",
  subtitle="Thessaly / Macedonia, Greece", country="Greece", region="Europe",
  category="landform", tags=["mythology", "national-park", "mytikas"],
  aliases=["Olympos", "Mytikas", "Zeus"],
  wikipedia="Mount Olympus", lat=40.0853, lon=22.3586, height=14000,
  claim="A mountain whose summit is wreathed in cloud, named as the literal "
        "residence of beings who descended to intervene in human affairs, is "
        "read as a base — and the Olympians as its crew.",
  context="Olympus is Greece's highest massif at 2,917 m, and its cloud cap "
          "is orographic. No structural remains have been found at the "
          "summit; the ancient cult sites sit at the foot, at Dion. Homeric "
          "and Hesiodic Olympus is a mythological topography whose "
          "development can be traced across texts, and it shifts between a "
          "physical mountain and a celestial realm."),

S("mycenae", "Mycenae — Treasury of Atreus",
  subtitle="Argolis, Peloponnese, Greece", country="Greece", region="Europe",
  category="megalithic", tags=["unesco", "bronze-age", "tholos", "cyclopean",
                               "lion-gate"],
  aliases=["Treasury of Atreus", "Lion Gate", "Agamemnon", "cyclopean masonry"],
  wikipedia="Treasury of Atreus", lat=37.7276, lon=22.7556, height=800,
  claim="The 120-tonne lintel over the Treasury of Atreus and the "
        "'cyclopean' walls — which later Greeks themselves attributed to "
        "giants — are offered as masonry beyond Bronze Age capability.",
  context="The tholos (c. 1250 BC) held the largest unsupported dome in the "
          "world for over a millennium, and its construction is legible: the "
          "corbelled vault was built into a cut hillside, so the earth "
          "itself served as the ramp and the centring. Conglomerate came from "
          "local outcrops. The 'cyclopean' attribution is an ancient Greek "
          "folk etymology for masonry already old in their own time."),

S("crete-knossos", "Crete — Knossos",
  subtitle="Heraklion, Crete, Greece", country="Greece", region="Europe",
  category="city", tags=["minoan", "labyrinth", "bronze-age", "linear-a"],
  aliases=["Knossos", "Minoan", "Labyrinth", "Minotaur", "Linear A"],
  wikipedia="Knossos", lat=35.2980, lon=25.1631, height=1200,
  claim="The Minotaur is read as a genetic hybrid produced in a laboratory "
        "under the palace, with the labyrinth as its containment and "
        "undeciphered Linear A as the suppressed record.",
  context="Knossos is a multi-storey Bronze Age palace complex whose "
          "storerooms, light-wells, drainage and workshops explain the "
          "'labyrinth' impression directly; Arthur Evans named the culture "
          "after the legend, not the reverse. Linear B was deciphered as "
          "Greek by Ventris in 1952 and records inventories and rations; "
          "Linear A remains unread chiefly because the corpus is small and "
          "the underlying language unknown. Bull-leaping frescoes document "
          "the cult that the myth most likely refracts."),

S("samos", "Samos — Heraion & the Eupalinian Aqueduct",
  subtitle="North Aegean, Greece", country="Greece", region="Europe",
  category="megalithic", tags=["unesco", "pythagoras", "tunnel", "engineering"],
  aliases=["Pythagoras", "Pythagoreion", "Eupalinos", "Heraion"],
  wikipedia="Tunnel of Eupalinos", lat=37.6900, lon=26.9333, height=1500,
  claim="A 6th-century-BC tunnel driven 1,036 m from both ends and meeting "
        "with only metres of error, on an island that also produced "
        "Pythagoras, is presented as surveying from a transmitted source.",
  context="The Tunnel of Eupalinos is a landmark in the history of "
          "engineering and the method is reconstructible: Hero of Alexandria "
          "later described the geometric technique, and the tunnel's own "
          "surviving correction kinks and measurement marks show the crews "
          "detecting and fixing drift as they went. Herodotus names "
          "Eupalinos of Megara as the engineer."),

S("rhodes", "Rhodes — Colossus & Lindos",
  subtitle="Dodecanese, Greece", country="Greece", region="Europe",
  category="city", tags=["unesco", "colossus", "hellenistic", "wonder"],
  aliases=["Colossus of Rhodes", "Lindos", "Dodecanese"],
  wikipedia="Colossus of Rhodes", lat=36.4512, lon=28.2225, height=6000,
  precision="approximate",
  claim="A 33 m bronze figure raised in the 3rd century BC, then lost, is "
        "cited as evidence of large-scale metallurgy and casting "
        "capabilities beyond the period.",
  context="Philo of Byzantium describes the method: an iron armature, stone "
          "ballast, and bronze plates cast in sections and assembled in "
          "situ with earth ramps raised around the figure — the same "
          "sectional technique used for smaller Hellenistic bronzes that "
          "survive, such as the Artemision Bronze. An earthquake felled it "
          "c. 226 BC and Strabo saw the pieces."),

S("patmos", "Patmos",
  subtitle="Dodecanese, Greece", country="Greece", region="Europe",
  category="sacred", tags=["unesco", "revelation", "apocalypse", "cave"],
  aliases=["Book of Revelation", "Cave of the Apocalypse", "John of Patmos"],
  wikipedia="Patmos", lat=37.3089, lon=26.5475, height=12000,
  claim="Revelation's imagery — a sea of glass, a crystalline city descending, "
        "locust-machines with iron breastplates, a woman clothed with the "
        "sun — is presented as a literal description of craft and of an "
        "orbital structure.",
  context="Revelation is apocalyptic literature with a dense and decodable "
          "symbolic vocabulary drawn from Daniel, Ezekiel and Isaiah, and "
          "with a specific first-century political target: Rome under "
          "Domitian, named through the Babylon cipher. Its numerology and "
          "beast imagery are conventions of the genre, legible to its "
          "original audience."),

S("lemnos", "Lemnos — Hephaistia",
  subtitle="North Aegean, Greece", country="Greece", region="Europe",
  category="city", tags=["hephaestus", "metallurgy", "volcanic", "automata"],
  aliases=["Hephaistia", "Hephaestus", "Limnos", "Talos"],
  wikipedia="Lemnos", lat=39.9000, lon=25.2500, height=25000,
  precision="approximate",
  claim="The island of Hephaestus — the smith god cast down from Olympus, who "
        "forged self-moving tripods, golden handmaidens and the bronze "
        "automaton Talos — is presented as a workshop staffed by a crashed "
        "and crippled engineer.",
  context="Lemnos's Hephaestus cult is tied to its volcanic geology and early "
          "metallurgy, and the sanctuary at Hephaistia has been excavated. "
          "The automata appear in Iliad 18 and later in Apollonius; "
          "classicists read them as a mythology of craft, and historians of "
          "technology note that Hellenistic engineers — Ctesibius, Philo, "
          "Hero — later built real pneumatic and hydraulic automata, "
          "plausibly inspired by those stories."),

S("euboea-dragon-houses", "Mount Ochi — Dragon Houses",
  subtitle="Euboea, Greece", country="Greece", region="Europe",
  category="megalithic", tags=["drakospita", "corbelled", "quarry", "karystos"],
  aliases=["Drakospita", "Dragon Houses", "Evia", "Karystos", "Mount Ochi"],
  wikipedia="Dragon houses", lat=38.0500, lon=24.4667, height=3000,
  precision="approximate",
  claim="Corbel-roofed stone structures on a remote 1,400 m summit, built "
        "from multi-tonne slabs with no mortar and no agreed date or "
        "purpose, are offered as pre-Greek construction by non-human "
        "builders — hence the local 'dragon' name.",
  context="The drakospita sit beside the Karystos cipollino marble quarries "
          "that supplied Rome, and the leading reading is quarry-workers' "
          "shelters or a sanctuary of the Roman and late Classical periods, "
          "using slabs split from the outcrops on site. Dating is genuinely "
          "unresolved for want of stratified deposits; corbelling itself is "
          "a widespread Mediterranean dry-stone technique, as in Apulian "
          "trulli and Sardinian nuraghi."),

S("antikythera", "Antikythera & the Antikythera Wreck",
  subtitle="Aegean Sea, Greece", country="Greece", region="Europe",
  category="artifact", tags=["antikythera-mechanism", "shipwreck", "gearing",
                             "astronomy"],
  aliases=["Antikythera Mechanism", "Kythira", "orrery"],
  wikipedia="Antikythera mechanism", lat=35.8614, lon=23.3053, height=20000,
  claim="A bronze geared computer recovered from a 1st-century-BC wreck — "
        "with at least 30 gears modelling lunar anomaly, eclipse cycles and "
        "planetary motion — is presented as technology out of time, with no "
        "comparable device for 1,400 years.",
  context="The Antikythera Mechanism is entirely real and is one of the most "
          "important artefacts ever recovered — which is why it is also "
          "well explained. CT imaging and the 2006–2021 Antikythera "
          "Mechanism Research Project read its inscriptions and reconstructed "
          "the gearing; it implements Babylonian arithmetic astronomy and "
          "Greek geometric models described in surviving texts. Cicero "
          "describes comparable spheres by Archimedes and Posidonius, so it "
          "is a surviving example of a known Hellenistic tradition, not an "
          "isolate.",
  links=[{"label": "Antikythera Mechanism Research Project",
          "url": "https://www.antikythera-mechanism.gr/", "kind": "reference"}]),

# ===========================================================================
# EUROPE — Central, Northern & Eastern
# ===========================================================================

S("nuremberg", "Nuremberg",
  subtitle="Bavaria, Germany", country="Germany", region="Europe",
  category="ufo", tags=["1561", "broadsheet", "celestial-phenomenon"],
  aliases=["Nürnberg", "1561 celestial phenomenon", "Hans Glaser"],
  wikipedia="1561 celestial phenomenon over Nuremberg",
  lat=49.4521, lon=11.0767, height=6000,
  claim="Hans Glaser's 1561 broadsheet, showing cylinders, spheres, crosses "
        "and a great black spear-shaped object fighting above the city at "
        "dawn, is presented as a printed eyewitness record of an aerial "
        "battle.",
  context="The broadsheet is a genuine 1561 artefact in the Zurich "
          "Wickiana collection. Its own text reads the display as a divine "
          "warning calling the city to repentance — the standard function of "
          "the 16th-century prodigy broadsheet, a commercial news-and-portent "
          "genre. The described forms match a complex sun-dog display: "
          "parhelia, sun pillars and arcs, which produce exactly these "
          "spheres, rods and crosses in cold dawn air."),

S("oberjoch", "Oberjoch",
  subtitle="Bad Hindelang, Bavaria, Germany", country="Germany",
  region="Europe", category="ufo", tags=["sighting", "alps", "allgau"],
  aliases=["Bad Hindelang", "Allgäu"],
  wikipedia="Oberjoch", lat=47.5167, lon=10.4167, height=8000,
  precision="approximate",
  claim="Cited among Alpine sighting and claimed-landing reports, in the "
        "cluster of German cases the series uses to argue for continuous "
        "post-war activity over central Europe.",
  context="Oberjoch is a high Alpine pass and ski area at 1,136 m. Mountain "
          "settings generate a well-known catalogue of misperceived "
          "phenomena: lenticular cloud, Brocken spectre, alpenglow, "
          "high-altitude balloons and glider traffic. No case from the "
          "locality has produced instrumented data."),

S("freiburg-black-forest", "Freiburg & the Black Forest",
  subtitle="Baden-Württemberg, Germany", country="Germany", region="Europe",
  category="region", tags=["black-forest", "folklore", "mining"],
  aliases=["Schwarzwald", "Black Forest"],
  wikipedia="Black Forest", lat=47.9990, lon=7.8421, height=90000,
  precision="area", radius_km=60,
  claim="The forest's dwarf and kobold folklore, its deep medieval silver "
        "mines and local sighting reports are woven into a claim of a "
        "long-standing subterranean presence.",
  context="Black Forest mining folklore maps closely onto its real "
          "occupational history: silver and lead workings around Schauinsland "
          "and the Münstertal from the 11th century, with kobold traditions "
          "functioning as hazard lore for firedamp and rockfall. The word "
          "'cobalt' descends from that usage — ore that poisoned smelters "
          "was blamed on the spirit."),

S("peenemunde", "Peenemünde Army Research Centre",
  subtitle="Usedom, Mecklenburg-Vorpommern, Germany", country="Germany",
  region="Europe", category="military",
  tags=["v2", "rocketry", "operation-paperclip", "wwii"],
  aliases=["V-2", "A4 rocket", "von Braun", "Usedom", "Heeresversuchsanstalt"],
  wikipedia="Peenemünde Army Research Center", lat=54.1383, lon=13.7947,
  height=6000,
  claim="The leap from artillery to a liquid-fuelled guided ballistic missile "
        "inside a decade, and the Nazi 'foo fighter' and Die Glocke stories, "
        "are presented as German reverse-engineering of recovered craft — "
        "with the knowledge later carried to the US by Operation Paperclip.",
  context="The A4/V-2 programme is documented to an unusual depth: design "
          "drawings, test telemetry, failure reports, procurement records and "
          "the forced-labour history of Mittelwerk, where roughly 20,000 "
          "prisoners died. Its intellectual lineage runs through Oberth, "
          "Goddard and the VfR. Paperclip is also fully documented, and what "
          "it transferred was engineers and A4 hardware. Die Glocke appears "
          "first in Igor Witkowski's 2000 book, sourced to an unnamed "
          "informant and unverifiable documents."),

S("wewelsburg", "Wewelsburg Castle",
  subtitle="Büren, North Rhine-Westphalia, Germany", country="Germany",
  region="Europe", category="military", tags=["ss", "himmler", "occult",
                                              "black-sun"],
  aliases=["Himmler", "Black Sun", "Schwarze Sonne", "SS"],
  wikipedia="Wewelsburg", lat=51.6072, lon=8.6514, height=1200,
  claim="Himmler's renovated castle, with its dark-green sun wheel inlaid in "
        "the north-tower floor, is presented as the ritual centre of an SS "
        "programme to contact non-human intelligences and recover "
        "Hyperborean technology.",
  context="The SS occupation of Wewelsburg (1934–45) is well documented, and "
          "the castle now houses a permanent museum on SS ideology. The "
          "'Black Sun' name and its later esoteric meanings are post-war "
          "inventions; the ornament is an SS design of uncertain intent. The "
          "Ahnenerbe's pseudo-scholarship — Tibet and Antarctic expeditions "
          "included — was real, politically driven and produced no "
          "technology.",
  links=[{"label": "Kreismuseum Wewelsburg — SS history exhibition",
          "url": "https://www.wewelsburg.de/", "kind": "official"}]),

S("humboldt-berlin", "Humboldt University of Berlin",
  subtitle="Berlin, Germany", country="Germany", region="Europe",
  category="research", tags=["academia", "assyriology", "physics"],
  aliases=["Berlin"],
  wikipedia="Humboldt University of Berlin", lat=52.5181, lon=13.3936,
  height=1500,
  claim="Appears as an interview setting for cuneiform and ancient-text "
        "specialists, whose comments on Mesopotamian astronomy are used to "
        "support the Anunnaki reading.",
  context="Berlin is a historic centre of Assyriology, and the Vorderasiatisches "
          "Museum holds the Ishtar Gate and a major tablet collection. The "
          "discipline's published grammars, sign lists and bilingual texts "
          "are precisely what makes Sitchin's translations checkable — and "
          "German Assyriologists have been among their most direct critics."),

S("the-hague", "The Hague — World Forum",
  subtitle="South Holland, Netherlands", country="Netherlands",
  region="Europe", category="research", tags=["diplomacy", "conference",
                                              "disclosure"],
  aliases=["Den Haag", "World Forum", "ICC"],
  wikipedia="The Hague", lat=52.0862, lon=4.2846, height=4000,
  claim="Cited as a venue for disclosure conferences and as the seat of "
        "international justice that would handle first contact — framing a "
        "legal and diplomatic architecture already quietly in place.",
  context="The Hague hosts the ICJ, ICC and OPCW, and the World Forum is a "
          "commercial conference centre used by a wide range of organisers. "
          "There is no treaty body with a mandate over extraterrestrial "
          "contact; the nearest instruments are the 1967 Outer Space Treaty "
          "and COSPAR's planetary-protection protocols, which address "
          "contamination, not diplomacy."),

S("southwestern-poland", "Lower Silesia — Project Riese",
  subtitle="Owl Mountains, Lower Silesia, Poland", country="Poland",
  region="Europe", category="underground",
  tags=["project-riese", "wwii", "tunnels", "owl-mountains"],
  aliases=["Riese", "Owl Mountains", "Góry Sowie", "Walim", "Książ"],
  wikipedia="Project Riese", lat=50.6800, lon=16.3300, height=25000,
  precision="area", radius_km=25,
  claim="Seven vast unfinished tunnel complexes under the Owl Mountains, "
        "built at enormous cost by forced labour and never explained in "
        "surviving records, are presented as housing for the Nazi "
        "anti-gravity programme — the 'Wunderwaffe' and Die Glocke.",
  context="Project Riese is real, incomplete, and consumed more concrete in "
          "1944 than Germany's entire civil air-raid shelter programme. "
          "Surviving documentation is thin because the project was "
          "compartmented and records were destroyed, but Albert Speer's "
          "testimony and Todt Organisation records point to a dispersed "
          "armaments plant and a Führer headquarters. Nothing anomalous has "
          "been recovered in eighty years of exploration; thousands of "
          "Gross-Rosen prisoners died building it."),

S("moscow", "Moscow",
  subtitle="Russia", country="Russia", region="Europe", category="research",
  tags=["space-program", "archives", "cold-war"],
  aliases=["Kremlin", "Soviet Union", "USSR"],
  wikipedia="Moscow", lat=55.7558, lon=37.6173, height=20000,
  claim="Soviet archives are said to hold recovered craft and encounter "
        "reports from across the USSR — including the 1908 Tunguska event "
        "read as a crash — with the state space programme built on the "
        "findings.",
  context="Post-1991 archival opening released an enormous volume of Soviet "
          "military and space material, including candid failure reports; no "
          "recovered-craft documentation has surfaced. Tunguska is well "
          "characterised as a 3–5 km airburst of a stony body, supported by "
          "the butterfly-shaped treefall pattern, seismic and barographic "
          "records from 1908, and later microparticle work."),

S("dubna", "Dubna — Joint Institute for Nuclear Research",
  subtitle="Moscow Oblast, Russia", country="Russia", region="Europe",
  category="research", tags=["jinr", "synchrophasotron", "superheavy-elements"],
  aliases=["JINR", "Oganesson", "Dubnium"],
  wikipedia="Joint Institute for Nuclear Research", lat=56.7461, lon=37.1897,
  height=3000,
  claim="JINR's synthesis of superheavy elements is invoked for the 'island "
        "of stability' and for element 115 — the material Bob Lazar claimed "
        "fuelled a craft at S4, named moscovium when it was actually made.",
  context="Moscovium (Z=115) was first synthesised at Dubna in 2003 by "
          "bombarding americium-243 with calcium-48, and its isotopes have "
          "half-lives measured in tens to hundreds of milliseconds. It "
          "cannot be stockpiled, machined or used as fuel. Lazar's account "
          "predates the synthesis and predicted a stable, macroscopic "
          "quantity — the opposite of the measured result.",
  links=[{"label": "JINR — official site", "url": "https://www.jinr.ru/main-en/",
          "kind": "official"}]),

S("siberia", "Siberia — Permafrost Megafauna Sites",
  subtitle="Russian Federation (regional)", country="Russia", region="Europe",
  category="region", tags=["mammoth", "permafrost", "tunguska", "quaternary"],
  aliases=["woolly mammoth", "Yakutia", "Tunguska", "Yamal"],
  wikipedia="Woolly mammoth", lat=66.0000, lon=110.0000, height=3000000,
  precision="area", radius_km=1500, pitch=-75,
  claim="Mammoths frozen with undigested vegetation, found in jumbled bone "
        "beds, are presented as evidence of an instantaneous global "
        "catastrophe — a weapon, an orbital shift, or a planetary "
        "intervention.",
  context="The deposits are taphonomically well studied: most carcasses are "
          "partial, weathered and scavenged, concentrated in river-bank and "
          "thermokarst traps that accumulate remains across millennia. "
          "Radiocarbon dates span tens of thousands of years, not one event, "
          "and Wrangel Island populations survived to about 4,000 years ago. "
          "Preserved stomach contents indicate a short time to freezing for "
          "an individual animal, not a synchronous global event."),

S("oslo", "University of Oslo",
  subtitle="Oslo, Norway", country="Norway", region="Europe",
  category="research", tags=["academia", "runology", "viking-studies"],
  aliases=["Norway", "Oslo"],
  wikipedia="University of Oslo", lat=59.9399, lon=10.7215, height=2500,
  claim="Appears as an interview setting for Norse material: the Æsir "
        "descending the Bifröst, Thor's hammer and Odin's ravens read as "
        "technology, with Scandinavian rock art cited as its record.",
  context="The Museum of Cultural History holds the Oseberg and Gokstad ships "
          "and Norway's runic corpus. Norse mythology survives chiefly via "
          "the 13th-century Eddas, written in Christian Iceland two "
          "centuries after conversion; Bronze Age Scandinavian rock art — "
          "sun discs, ships, chariots — is read in mainstream scholarship as "
          "solar and maritime cult imagery with a continuous "
          "iconographic development."),

S("iceland", "Iceland",
  subtitle="North Atlantic", country="Iceland", region="Europe",
  category="landform", tags=["volcanic", "mid-atlantic-ridge", "sagas",
                             "huldufolk"],
  aliases=["Reykjavik", "huldufólk", "hidden people", "Thingvellir"],
  wikipedia="Iceland", lat=64.9631, lon=-19.0208, height=600000,
  precision="area", radius_km=300, pitch=-70,
  claim="Iceland's position astride the Mid-Atlantic Ridge is tied to "
        "Atlantis, and the enduring huldufólk ('hidden people') traditions — "
        "which still occasionally reroute road projects — to a resident "
        "non-human population.",
  context="Iceland is the exposed crest of the Mid-Atlantic Ridge above the "
          "Iceland hotspot, formed about 16–18 million years ago by seafloor "
          "spreading — continuously growing, not a sunken remnant. Huldufólk "
          "belief is a well-documented living folklore tradition studied by "
          "Icelandic ethnologists, and the road diversions are heritage and "
          "public-consultation outcomes."),

S("scandinavia", "Scandinavia",
  subtitle="Norway, Sweden, Denmark & Iceland (regional)",
  country="Nordic countries", region="Europe", category="region",
  tags=["regional", "rock-art", "norse", "bronze-age"],
  aliases=["Nordic", "Sweden", "Denmark", "Tanum"],
  wikipedia="Scandinavia", lat=62.0000, lon=15.0000, height=2500000,
  precision="area", radius_km=1000, pitch=-72,
  claim="Taken together, Norse cosmology, the Tanum petroglyphs and the "
        "Trundholm sun chariot are presented as a northern record of "
        "sky-borne visitors and of the vehicles they arrived in.",
  context="The Tanum rock-art area is a World Heritage site with some 10,000 "
          "Bronze Age figures, and the Trundholm sun chariot (c. 1400 BC) is "
          "a securely dated cult object expressing a solar theology found "
          "across Bronze Age Europe. The imagery's continuity with "
          "contemporary Danish and Swedish burial and hoard material is what "
          "allows it to be interpreted at all."),


# ===========================================================================
# SOUTH ASIA
# ===========================================================================

S("mohenjo-daro", "Mohenjo-daro",
  subtitle="Sindh, Pakistan", country="Pakistan", region="South Asia",
  category="city", tags=["unesco", "indus-valley", "bronze-age", "urban-grid"],
  aliases=["Indus Valley", "Harappan", "Sindh"],
  wikipedia="Mohenjo-daro", lat=27.3294, lon=68.1386, height=2000,
  claim="A city with a gridded street plan, covered drains and standardised "
        "fired bricks, reportedly abandoned abruptly — combined with claimed "
        "radioactive skeletons and vitrified rubble — is presented as the "
        "site of an ancient nuclear strike described in the Mahabharata.",
  context="Mohenjo-daro's planning is real and is the basis for its World "
          "Heritage listing. The 'radioactive skeletons' claim traces to "
          "popular books of the 1960s–80s with no supporting measurements; "
          "the excavated human remains are ordinary burials and casual "
          "interments, published by Marshall, Mackay and Wheeler, and no "
          "vitrified layer exists in the stratigraphy. Decline is now "
          "attributed to Indus and Ghaggar-Hakra hydrological shifts and "
          "monsoon weakening around 1900 BC, with population moving "
          "eastward."),

S("harappa", "Harappa",
  subtitle="Punjab, Pakistan", country="Pakistan", region="South Asia",
  category="city", tags=["indus-valley", "bronze-age", "seals", "granary"],
  aliases=["Harappan civilisation", "Punjab"],
  wikipedia="Harappa", lat=30.6283, lon=72.8647, height=2000,
  claim="The type-site of a civilisation whose script remains unread and whose "
        "weights and measures were standardised across a million square "
        "kilometres is presented as centrally administered from outside.",
  context="Harappa has a continuous excavated sequence from c. 3300 BC "
          "through the Mature Harappan, including kilns, workshops, "
          "cemeteries and the development of the weight system from local "
          "chert cubes. The script is undeciphered because the inscriptions "
          "are extremely short — typically five signs — and no bilingual "
          "text exists, not because it is being withheld."),

S("kot-diji", "Kot Diji",
  subtitle="Khairpur District, Sindh, Pakistan", country="Pakistan",
  region="South Asia", category="city",
  tags=["indus-valley", "early-harappan", "fortification"],
  aliases=["Kot Dijian"],
  wikipedia="Kot Diji", lat=27.3419, lon=68.7119, height=2000,
  claim="A fortified pre-Harappan settlement with a stone-and-mud defensive "
        "wall is cited as evidence of a threat requiring defence before "
        "cities and warfare are supposed to have existed in the region.",
  context="Kot Diji defines the Early Harappan Kot Dijian phase "
          "(c. 3300–2600 BC) and is important precisely because it shows "
          "indigenous development toward urbanism — fortification, "
          "specialised ceramics and a citadel-and-town layout prefiguring "
          "Mohenjo-daro. Defensive walls in this period also served against "
          "floods and for storage control."),

S("indus-valley", "Indus Valley",
  subtitle="Indus basin, Pakistan & north-west India",
  country="Pakistan / India", region="South Asia", category="region",
  tags=["regional", "bronze-age", "undeciphered-script"],
  aliases=["Harappan civilisation", "Sarasvati"],
  wikipedia="Indus Valley Civilisation", lat=27.5000, lon=68.5000,
  height=1200000, precision="area", radius_km=600, pitch=-70,
  claim="The civilisation's sudden appearance, uniform urban template and "
        "unread script, followed by an unexplained collapse, are presented as "
        "the full life cycle of an off-world colonial project.",
  context="More than 1,500 sites are known, giving a continuous sequence from "
          "Mehrgarh (c. 7000 BC) through Early, Mature and Late Harappan "
          "phases into the Painted Grey Ware cultures. Palaeoclimate records "
          "from Indian Ocean cores and Himalayan speleothems document "
          "monsoon weakening after c. 2200 BC, matching the settlement shift "
          "eastward toward the Ganges."),

S("thar-desert", "Thar Desert",
  subtitle="India–Pakistan border region", country="India / Pakistan",
  region="South Asia", category="region", precision="uncertain",
  tags=["desert", "vitrification-claim", "mahabharata"],
  aliases=["Sian Desert", "Sindh desert", "Great Indian Desert",
           "Cholistan"],
  wikipedia="Thar Desert", lat=27.0000, lon=71.0000, height=900000,
  radius_km=450, pitch=-70,
  claim="A layer of fused, radioactive glass under the desert, reportedly "
        "covering several square kilometres near a ruined city, is offered as "
        "ground zero for the Mahabharata's Brahmastra.",
  context="No such vitrified field has been located, sampled or published; "
          "the claim circulates without a site name, coordinates or "
          "institutional report. Comparable natural glasses do exist — "
          "fulgurites from lightning, and desert glass from impact events "
          "such as Libyan Desert Glass — and are geochemically "
          "distinguishable from nuclear trinitite. The series' 'Sian Desert' "
          "does not correspond to a mapped place name; the Thar is the "
          "nearest match to the described location."),

S("charama", "Charama",
  subtitle="Kanker District, Chhattisgarh, India", country="India",
  region="South Asia", category="geoglyph",
  tags=["rock-art", "chhattisgarh", "mesolithic"],
  aliases=["Chhattisgarh", "Kanker", "Rohansar"],
  wikipedia="Kanker district", lat=20.1167, lon=81.3000, height=30000,
  precision="approximate",
  claim="Rock paintings reported from caves near Charama in 2014 — showing "
        "figures without clear faces, wearing what look like helmets and "
        "suits, beside a disc-shaped object — were described by a state "
        "archaeology officer as possibly depicting extraterrestrials, and the "
        "story was carried worldwide.",
  context="The paintings are real and belong to central India's extensive "
          "Mesolithic-to-historic rock-art tradition, best known from the "
          "World Heritage shelters at Bhimbetka. The 'extraterrestrial' "
          "reading was one official's speculation to reporters, not a "
          "published finding; the stylised, featureless human figure is a "
          "standard convention across the region's panels. Local Gond "
          "communities have their own interpretive traditions for the "
          "figures."),

S("amarnath-cave", "Amarnath Cave",
  subtitle="Jammu & Kashmir, India", country="India", region="South Asia",
  category="sacred", tags=["himalaya", "shiva", "ice-lingam", "pilgrimage"],
  aliases=["Himalayas", "Shiva", "Kashmir", "ice lingam"],
  wikipedia="Amarnath Temple", lat=34.2150, lon=75.5010, height=6000,
  claim="A naturally forming ice column at 3,888 m, waxing and waning with "
        "the moon and venerated for millennia, is cited alongside Himalayan "
        "accounts of vimanas and sky-beings as a marker of a contact site.",
  context="The lingam is a stalagmite of ice formed by water seeping through "
          "the cave roof and freezing; its height varies with precipitation "
          "and temperature, and in warm years it has melted early — "
          "documented repeatedly in recent decades. The pilgrimage is a "
          "major, well-recorded Shaiva tradition."),

S("tamil-nadu", "Tamil Nadu",
  subtitle="Southern India", country="India", region="South Asia",
  category="region", tags=["kumari-kandam", "sangam", "keeladi", "temples"],
  aliases=["Kumari Kandam", "Lemuria", "Keeladi", "Dravidian"],
  wikipedia="Tamil Nadu", lat=11.1271, lon=78.6569, height=700000,
  precision="area", radius_km=350, pitch=-70,
  claim="Kumari Kandam — a submerged southern landmass in Tamil literary "
        "tradition — is merged with the 19th-century 'Lemuria' hypothesis and "
        "presented as a drowned advanced civilisation, with Tamil Nadu's "
        "temple geometry as its inheritance.",
  context="Lemuria was proposed in 1864 by zoologist Philip Sclater to "
          "explain lemur distribution and was superseded by plate tectonics "
          "and the Gondwana model. Post-glacial sea-level rise did drown "
          "large tracts of the Indian shelf, and the Gulf of Khambhat and "
          "Poompuhar nearshore finds are genuinely studied. Keeladi's "
          "excavations have pushed Tamil urban and literate culture "
          "substantially earlier — an important mainstream result."),

S("patna-ganges", "Patna & the Ganges",
  subtitle="Bihar, India", country="India", region="South Asia",
  category="city", tags=["pataliputra", "mauryan", "ashoka", "ganges"],
  aliases=["Pataliputra", "Bihar", "Ganges", "Ashoka", "Nine Unknown Men"],
  wikipedia="Patna", lat=25.5941, lon=85.1376, height=20000,
  claim="Mauryan Pataliputra is tied to the legend of Ashoka's 'Nine Unknown "
        "Men' — a secret society entrusted with nine books of dangerous "
        "knowledge, including anti-gravity and psychological warfare — "
        "presented as a custodial order for off-world technology.",
  context="Pataliputra was one of the largest cities of its age, and Megasthenes' "
          "account of its timber palisade was confirmed by excavation. "
          "The Nine Unknown Men first appears in Talbot Mundy's 1923 novel "
          "'The Nine Unknown' and has no attestation in Mauryan sources, in "
          "Ashoka's own edicts, or in Buddhist or Jain tradition."),

S("india-general", "India",
  subtitle="Republic of India (regional)", country="India",
  region="South Asia", category="region",
  tags=["regional", "vimana", "sanskrit", "mahabharata"],
  aliases=["Vimana", "Mahabharata", "Ramayana", "Vaimanika Shastra"],
  wikipedia="India", lat=21.0000, lon=78.5000, height=2500000,
  precision="area", radius_km=1200, pitch=-72,
  claim="The Sanskrit epics are the series' richest text source: vimanas "
        "described as flying palaces, the Brahmastra's described effects "
        "likened to a nuclear detonation, and the Vaimanika Shastra read as a "
        "surviving flight manual.",
  context="The Mahabharata and Ramayana are vast poetic compilations reaching "
          "their received form over roughly a thousand years; vimana means "
          "'measured-out' and denotes palaces, temple towers and divine "
          "chariots depending on context. The Vaimanika Shastra was produced "
          "by Subbaraya Shastry via psychic channelling between 1900 and "
          "1922 — it is not ancient. A 1974 Indian Institute of Science study "
          "found its described craft aerodynamically incapable of flight."),

S("nepal-lumbini", "Lumbini",
  subtitle="Rupandehi District, Nepal", country="Nepal", region="South Asia",
  category="sacred", tags=["unesco", "buddha", "ashoka-pillar", "pilgrimage"],
  aliases=["Buddha", "Siddhartha Gautama", "Maya Devi", "Nepal"],
  wikipedia="Lumbini", lat=27.4833, lon=83.2767, height=2500,
  claim="The Buddha's birth narrative — conception by a white elephant "
        "entering his mother's side in a dream, a child who walks and speaks "
        "at once, thirty-two bodily marks — is read as a managed hybrid "
        "birth, with Shambhala as the custodians' base.",
  context="Lumbini's identification rests on the Ashokan pillar erected "
          "c. 249 BC, whose inscription names the birthplace; excavation has "
          "exposed earlier timber and brick shrine phases beneath the Maya "
          "Devi temple. The miraculous birth elements belong to Buddhist "
          "hagiography and appear in later texts, not the earliest strata of "
          "the canon."),

# ===========================================================================
# EAST ASIA
# ===========================================================================

S("mount-kailash", "Mount Kailash",
  subtitle="Ngari Prefecture, Tibet, China", country="China",
  region="East Asia", category="sacred",
  tags=["pilgrimage", "unclimbed", "four-religions", "himalaya"],
  aliases=["Kailas", "Gang Rinpoche", "Tibet", "Shambhala", "Mount Meru"],
  wikipedia="Mount Kailash", lat=31.0672, lon=81.3112, height=14000,
  claim="A near-pyramidal 6,638 m peak, sacred to four religions, never "
        "summited, identified with the cosmic Mount Meru and claimed to sit "
        "on a global grid of monuments, is presented as an artificial "
        "structure or an energy node.",
  context="Kailash is a mass of Tertiary conglomerate uplifted by the "
          "India–Asia collision; its stepped profile is bedding and "
          "glacial erosion, and comparable forms occur throughout the "
          "Transhimalaya. It is unclimbed by agreement out of respect for "
          "its sanctity, not because attempts fail. The 'global grid' "
          "alignments are constructed by selecting from thousands of "
          "candidate monuments."),

S("guge-ruins", "Guge Kingdom — Tsaparang",
  subtitle="Ngari Prefecture, Tibet, China", country="China",
  region="East Asia", category="city",
  tags=["tibet", "cliff-city", "abandoned", "buddhist-murals"],
  aliases=["Tsaparang", "Zanda", "Ngari", "Guge"],
  wikipedia="Guge", lat=31.4833, lon=79.8000, height=8000,
  precision="approximate",
  claim="A honeycombed cliff city of hundreds of chambers and tunnels, "
        "abandoned and depopulated so completely that its fate was forgotten, "
        "is presented as a site of mass abduction or a vanished "
        "non-human enclave.",
  context="Guge was a Buddhist kingdom from the 10th century, central to the "
          "second transmission of Buddhism into Tibet. Its fall is "
          "attributable to the 1630 Ladakhi invasion, recorded in Tibetan "
          "and Jesuit sources — António de Andrade's mission was there from "
          "1624. The chambers are cut into soft Zanda-formation clay, and the "
          "surviving murals are a major art-historical corpus."),

S("tibet", "Tibet",
  subtitle="Tibetan Plateau (regional)", country="China", region="East Asia",
  category="region", tags=["regional", "shambhala", "plateau", "bon"],
  aliases=["Shambhala", "Tibetan Plateau", "Shangri-La", "Bön"],
  wikipedia="Tibet", lat=31.5000, lon=88.0000, height=1800000,
  precision="area", radius_km=900, pitch=-72,
  claim="Tibet is cast as the guardian of an underground city — Shambhala or "
        "Agartha — reached through tunnels, holding records from before the "
        "Flood; the Nazi Ahnenerbe expeditions of 1938–39 are offered as "
        "evidence that states took this seriously.",
  context="Shambhala appears in the Kalachakra tantra as a pure land, a "
          "spiritual rather than geographic destination within its own "
          "tradition; Tibetan commentators treat its location as not "
          "physically accessible. Ernst Schäfer's 1938–39 expedition is "
          "documented in its own publications and collected ornithological, "
          "ethnographic and anthropometric data in service of Nazi racial "
          "theory. It found no city."),

S("shaanxi-pyramids", "Shaanxi — Imperial Tumuli",
  subtitle="Xianyang Plain, Shaanxi, China", country="China",
  region="East Asia", category="pyramid",
  tags=["han-tombs", "qin", "tumulus", "mausoleum"],
  aliases=["Chinese pyramids", "Xi'an", "Maoling", "Qin Shi Huang",
           "White Pyramid"],
  wikipedia="Chinese pyramids", lat=34.3853, lon=108.8880, height=25000,
  claim="Dozens of flat-topped 'pyramids' on the Xianyang plain — including a "
        "'Great White Pyramid' reported by a USAAF pilot in 1945 — are "
        "presented as a concealed complex that China refuses to excavate.",
  context="They are rammed-earth imperial burial mounds of the Qin, Western "
          "Han and Tang, well catalogued and freely visible on open "
          "satellite imagery; the Maoling mausoleum of Emperor Wu is the "
          "largest. Excavation is deliberately limited by Chinese heritage "
          "policy pending better conservation techniques — the same policy "
          "that leaves most of the Qin Shi Huang mausoleum unopened while "
          "the terracotta army pits beside it are excavated and published."),

S("zhongtiao-shan", "Zhongtiao Mountains",
  subtitle="Shanxi Province, China", country="China", region="East Asia",
  category="landform", tags=["copper", "ancient-mining", "shanxi"],
  aliases=["Shanxi", "Zhongtiao Shan", "Zhongtiaoshan"],
  wikipedia="Zhongtiao Mountains", lat=35.1667, lon=111.5000, height=90000,
  precision="area", radius_km=60,
  claim="Vast ancient copper workings in the range are tied to the Sitchin "
        "mining narrative and to legends of the Yellow Emperor's ascent on a "
        "dragon from this region.",
  context="The Zhongtiao copper belt is a genuine and important early mining "
          "district — its ores fed Erlitou and Shang bronze production, "
          "traced by lead-isotope analysis of excavated vessels. That makes "
          "it central to the archaeology of Chinese metallurgy. The Yellow "
          "Emperor is a legendary culture-hero of the mythic Three Sovereigns "
          "and Five Emperors sequence, not a documented ruler."),

S("fuxian-lake", "Fuxian Lake",
  subtitle="Yuxi, Yunnan Province, China", country="China", region="East Asia",
  category="underwater", tags=["submerged-ruins", "yunnan", "diving"],
  aliases=["Fuxian Hu", "Yunnan", "underwater city"],
  wikipedia="Fuxian Lake", lat=24.5500, lon=102.8833, height=25000,
  claim="Stone structures surveyed at depth in China's second-deepest lake "
        "since 2001 — reported as walls, roads and a stepped platform — are "
        "presented as a drowned city predating Chinese civilisation.",
  context="Chinese archaeologists have confirmed submerged stone structures "
          "and sonar anomalies, and the leading interpretation is the "
          "Han-era town of Yuyuan, lost to subsidence or earthquake — "
          "plausible on an active fault margin. Some surveyed features are "
          "assessed as natural karst. This is an open, publishing "
          "investigation of a historical-period site."),

S("wucheng-sichuan", "Sichuan Basin — 'Wucheng' Reference",
  subtitle="Sichuan Province, China", country="China", region="East Asia",
  category="region", precision="uncertain",
  tags=["sanxingdui", "bronze-age", "unresolved-reference"],
  aliases=["Wucheng", "Sanxingdui", "Sichuan"],
  wikipedia="Sichuan", lat=30.6500, lon=104.0667, height=900000,
  radius_km=350, pitch=-70,
  claim="A Sichuan locality is referenced in connection with bronze masks "
        "bearing enormous protruding eyes and non-human proportions, "
        "presented as portraits of visitors.",
  context="The place name as given does not resolve to a published "
          "archaeological site in Sichuan — the mapped Wucheng sites are in "
          "Jiangxi and Shandong — so this entry is positioned on the Sichuan "
          "Basin as a label rather than a location. The imagery described "
          "matches Sanxingdui (c. 1200 BC) near Guanghan, whose bronze masks "
          "and 2.6 m standing figure are stylised ritual objects from a "
          "distinct Shu culture, excavated with crucibles, moulds and "
          "casting debris on site."),

S("three-pagodas", "Three Pagodas of Chongsheng Temple",
  subtitle="Dali, Yunnan Province, China", country="China",
  region="East Asia", category="pyramid",
  tags=["tang", "dali-kingdom", "earthquake-resistant"],
  aliases=["Dali", "Chongsheng Temple", "Yunnan"],
  wikipedia="Three Pagodas", lat=25.6997, lon=100.1517, height=1200,
  claim="Three pagodas that survived repeated major earthquakes — one "
        "account says they split apart and realigned themselves — are "
        "presented as built with knowledge of seismic engineering acquired "
        "from outside.",
  context="The central pagoda dates to the 9th-century Tang period and the "
          "flanking pair to the Dali Kingdom. Their survival is explicable: "
          "tapered masonry, a low centre of mass and a wide base are "
          "recognised seismic virtues, and the structures have been repaired "
          "repeatedly, most substantially in 1978–81. The 'self-realigning' "
          "story derives from a local chronicle account of a 1515 "
          "earthquake."),

S("tsinghua", "Tsinghua University",
  subtitle="Beijing, China", country="China", region="East Asia",
  category="research", tags=["academia", "bamboo-slips", "astronomy"],
  aliases=["Beijing", "Qinghua", "Tsinghua Bamboo Slips"],
  wikipedia="Tsinghua University", lat=40.0000, lon=116.3264, height=2500,
  claim="Cited for Chinese astronomical records and for the Tsinghua Bamboo "
        "Slips, used to argue that early Chinese texts preserve dated "
        "observations of craft and of visitors.",
  context="Chinese astronomical records are genuinely the longest continuous "
          "observational series on Earth, and they are scientifically "
          "valuable — supernova and comet records from them underpin modern "
          "work on SN 1054 and on Halley's orbit. The Tsinghua Bamboo Slips "
          "are a Warring States manuscript cache acquired in 2008 and "
          "published progressively; they are historical and divinatory "
          "texts."),

S("sun-yat-sen-university", "Sun Yat-sen University",
  subtitle="Guangzhou, Guangdong, China", country="China", region="East Asia",
  category="research", tags=["academia", "anthropology", "archaeology"],
  aliases=["Guangzhou", "Zhongshan University"],
  wikipedia="Sun Yat-sen University", lat=23.0966, lon=113.2988, height=2500,
  claim="Appears as an interview location for Chinese archaeological and "
        "ethnographic material, including the Dropa stone discs and southern "
        "Chinese cave-burial traditions.",
  context="The Dropa stones story — perforated discs and small-statured "
          "beings in a Bayan Har cave — has no provenance: the cited "
          "institutions and the Professor 'Tsum Um Nui' credited with "
          "translating them cannot be documented, and the tale is traceable "
          "to 1960s Soviet and Western fringe magazines. Chinese academic "
          "archaeology in the region is extensively published."),

S("ise-grand-shrine", "Ise Grand Shrine",
  subtitle="Mie Prefecture, Japan", country="Japan", region="East Asia",
  category="sacred", tags=["shinto", "shikinen-sengu", "amaterasu", "mirror"],
  aliases=["Ise Jingu", "Amaterasu", "Yata no Kagami"],
  wikipedia="Ise Grand Shrine", lat=34.4553, lon=136.7256, height=2500,
  claim="A shrine rebuilt identically every twenty years for over 1,300 "
        "years, housing a sacred mirror that no one may view, descended from "
        "a sun goddess whose grandson came down to rule Japan, is presented "
        "as a maintained relic of a contact event.",
  context="The Shikinen Sengū rebuilding is a documented ritual practice that "
          "preserves carpentry technique by transmission rather than "
          "preserving timber, and it is a case study in intangible heritage. "
          "The Yata no Kagami is one of the three imperial regalia; its "
          "concealment is a religious prohibition, and the descent narrative "
          "comes from the 8th-century Kojiki and Nihon Shoki, compiled to "
          "legitimise the imperial line."),

S("kansai-science-city", "Kansai Science City",
  subtitle="Keihanna, Kyoto / Osaka / Nara, Japan", country="Japan",
  region="East Asia", category="research",
  tags=["robotics", "ai", "atr", "keihanna"],
  aliases=["Keihanna", "ATR", "Kyoto"],
  wikipedia="Kansai Science City", lat=34.7500, lon=135.7800, height=12000,
  claim="Japan's concentration of humanoid robotics and AI research is framed "
        "as humanity recapitulating its own creation — building synthetic "
        "servants exactly as the series says we were built.",
  context="Keihanna hosts ATR, NICT facilities and corporate laboratories "
          "doing published, peer-reviewed work in human–robot interaction and "
          "speech translation. The parallel drawn is rhetorical: that humans "
          "build tools in their own image is a long-noted feature of design "
          "psychology, not evidence about human origins."),

S("cape-muroto", "Cape Muroto & Mikurodo Cave",
  subtitle="Kōchi Prefecture, Shikoku, Japan", country="Japan",
  region="East Asia", category="underground",
  tags=["kukai", "shingon", "unesco-geopark", "shikoku"],
  aliases=["Mikurodo", "Kukai", "Kobo Daishi", "Shikoku", "Muroto"],
  wikipedia="Cape Muroto", lat=33.2444, lon=134.1792, height=4000,
  claim="The cave where the monk Kūkai is said to have attained "
        "enlightenment — a morning star entering his mouth, after which he "
        "could recite texts he had never read — is presented as a transfer of "
        "knowledge from a descending object.",
  context="Kūkai's own 'Sangō shiiki' records the experience in the standard "
          "vocabulary of Shingon ascetic practice, in which the morning star "
          "represents the bodhisattva Ākāśagarbha; the Gumonji-hō rite he "
          "performed explicitly aims at perfect retention. Cape Muroto is a "
          "UNESCO Global Geopark for its rapidly uplifting marine terraces."),

S("yonaguni", "Yonaguni Monument",
  subtitle="Yonaguni Island, Okinawa, Japan", country="Japan",
  region="East Asia", category="underwater",
  tags=["submerged", "sandstone", "ryukyu", "diving"],
  aliases=["Yonaguni-jima", "Okinawa", "Iseki Point", "Ryukyu"],
  wikipedia="Yonaguni Monument", lat=24.4367, lon=123.0108, height=2000,
  claim="A submerged formation off Yonaguni with flat terraces, right angles, "
        "straight channels and what are described as steps and a road is "
        "presented as a city drowned by post-glacial sea-level rise — making "
        "it older than any accepted civilisation.",
  context="Masaaki Kimura argues for human modification; Robert Schoch and "
          "most marine geologists who have dived it identify natural "
          "features. The rock is Miocene Yaeyama sandstone with closely "
          "spaced horizontal bedding and two near-perpendicular joint sets, "
          "which fracture into exactly these steps and channels — and the "
          "same forms continue in the adjacent cliffs above water. No "
          "artefacts, tool marks or cultural deposits have been recovered. "
          "The debate is live but asymmetric."),

# ===========================================================================
# SOUTHEAST ASIA & OCEANIA
# ===========================================================================

S("angkor-wat", "Angkor Wat",
  subtitle="Siem Reap, Cambodia", country="Cambodia",
  region="Southeast Asia & Oceania", category="pyramid",
  tags=["unesco", "khmer", "archaeoastronomy", "hydraulic-city"],
  aliases=["Khmer", "Siem Reap", "Angkor Thom", "Suryavarman II"],
  wikipedia="Angkor Wat", lat=13.4125, lon=103.8670, height=2000,
  claim="The largest religious monument on Earth, raised in about 35 years "
        "from 5–10 million sandstone blocks quarried 40 km away, with "
        "equinoctial alignments and proportions said to encode the "
        "precessional cycle, is presented as built to a supplied design.",
  context="Angkor is exceptionally well documented by its own inscriptions, "
          "by Zhou Daguan's 13th-century eyewitness account, and by LiDAR "
          "survey since 2012 that mapped the surrounding hydraulic city, "
          "quarry roads and canal network used to float blocks from Phnom "
          "Kulen. The equinox alignment is real and is one of several "
          "deliberate cosmological features; the precession claims come from "
          "Graham Hancock's unit-of-measure selections."),

S("borobudur", "Borobudur",
  subtitle="Magelang, Central Java, Indonesia", country="Indonesia",
  region="Southeast Asia & Oceania", category="pyramid",
  tags=["unesco", "buddhist", "stupa", "mandala", "java"],
  aliases=["Magelang", "Java", "Sailendra"],
  wikipedia="Borobudur", lat=-7.6079, lon=110.2038, height=1200,
  claim="A nine-tier stone mandala of some two million blocks, assembled "
        "without mortar, interlocked to survive eruptions and earthquakes, "
        "then abandoned and buried under ash for centuries, is presented as "
        "built to withstand a cataclysm foreseen from outside.",
  context="Borobudur is a 9th-century Sailendra monument whose 2,672 relief "
          "panels narrate specific Buddhist texts — the Lalitavistara, "
          "Jatakas and Gandavyuha — identifying its builders and their "
          "programme precisely. Interlocking dry masonry is standard in "
          "Javanese candi architecture. Its decline follows the shift of "
          "Javanese power east and the spread of Islam; the Merapi ash "
          "burial is well dated."),

S("candi-sukuh", "Candi Sukuh",
  subtitle="Karanganyar, Central Java, Indonesia", country="Indonesia",
  region="Southeast Asia & Oceania", category="pyramid",
  tags=["majapahit", "step-pyramid", "lingam", "java"],
  aliases=["Sukuh", "Java", "Javanese pyramid"],
  wikipedia="Candi Sukuh", lat=-7.6269, lon=110.9294, height=1200,
  claim="A truncated step-pyramid on Mount Lawu, unlike any other Javanese "
        "temple and stylistically compared to Mesoamerican platforms, is "
        "offered as evidence of transoceanic contact or a shared off-world "
        "template.",
  context="Candi Sukuh is a 15th-century late-Majapahit temple with a dated "
          "chronogram, built as Javanese Hindu-Buddhism absorbed indigenous "
          "mountain and ancestor cult — which is exactly why it looks "
          "unlike court temples. Its reliefs are legible Javanese "
          "iconography, including a Sudamala narrative and metalworking "
          "scenes. Terraced sanctuaries are a recognised Javanese class, as "
          "at nearby Candi Cetho."),

S("lake-toba", "Lake Toba",
  subtitle="North Sumatra, Indonesia", country="Indonesia",
  region="Southeast Asia & Oceania", category="landform",
  tags=["supervolcano", "caldera", "genetic-bottleneck", "sumatra"],
  aliases=["Toba catastrophe", "Sumatra", "Mount Toba"],
  wikipedia="Lake Toba", lat=2.6845, lon=98.8756, height=90000,
  claim="The Toba supereruption of about 74,000 years ago, said to have cut "
        "humanity to a few thousand breeding individuals, is presented as the "
        "bottleneck that prompted an off-world rescue or a genetic "
        "intervention in the survivors.",
  context="The eruption is real, one of the largest of the Quaternary, with "
          "its ash layer traced across South Asia and into Antarctic and "
          "Greenland ice. The severity of its human impact is now "
          "substantially downgraded: excavations at Pinnacle Point and in "
          "the Middle Awash show populations persisting through the ash "
          "horizon, and the genetic bottleneck signal is explicable by "
          "ordinary founder effects during dispersal."),

S("mount-tambora", "Mount Tambora",
  subtitle="Sumbawa, West Nusa Tenggara, Indonesia", country="Indonesia",
  region="Southeast Asia & Oceania", category="landform",
  tags=["1815-eruption", "year-without-summer", "caldera"],
  aliases=["Sumbawa", "Year Without a Summer", "1815"],
  wikipedia="Mount Tambora", lat=-8.2500, lon=118.0000, height=30000,
  claim="The 1815 eruption — the largest in recorded history, which caused "
        "the 'year without a summer' and global crop failure — is used to "
        "argue that such events have been monitored, and sometimes "
        "triggered, from orbit.",
  context="Tambora 1815 is the best-documented large eruption in the "
          "instrumental and historical record: ship logs, ice-core sulphate "
          "spikes, tree-ring suppression and 1816 harvest data converge. "
          "The buried settlement of Tambora was excavated in 2004. Its "
          "cultural consequences, including the writing of 'Frankenstein' "
          "during a sunless Swiss summer, are traceable social history."),

S("nan-madol", "Nan Madol",
  subtitle="Temwen Island, Pohnpei, Federated States of Micronesia",
  country="Federated States of Micronesia", region="Southeast Asia & Oceania",
  category="megalithic", tags=["unesco", "basalt", "artificial-islets",
                               "saudeleur"],
  aliases=["Pohnpei", "Temwen Island", "Madol", "Saudeleur", "Venice of the Pacific"],
  wikipedia="Nan Madol", lat=6.8419, lon=158.3322, height=1500,
  claim="Ninety-nine artificial islets built from an estimated 750,000 tonnes "
        "of columnar basalt — some pieces over 50 tonnes — on a remote "
        "Pacific reef, with local tradition saying the stones were flown into "
        "place by sorcery, is presented as the clearest case of levitation "
        "technology.",
  context="The columnar basalt comes from identified quarries on Pohnpei; "
          "bamboo rafts and log rollers at high tide are the method "
          "indicated by ethnographic accounts and by the reef-flat "
          "setting. Construction ran from roughly AD 1180 to 1600 under the "
          "Saudeleur dynasty, with radiocarbon dates from islet fill. The "
          "oral traditions describing sorcery are recorded Pohnpeian "
          "history, and they also name the dynasty, its rulers and its fall."),

S("tuyen-quang", "Tuyên Quang Province",
  subtitle="Northern Vietnam", country="Vietnam",
  region="Southeast Asia & Oceania", category="ufo",
  tags=["sighting", "karst", "vietnam"],
  aliases=["Vietnam", "Tuyen Quang"],
  wikipedia="Tuyên Quang province", lat=21.8233, lon=105.2142, height=60000,
  precision="area", radius_km=40,
  claim="Cited for reported sightings and claimed physical traces in northern "
        "Vietnam's limestone country, offered as part of a dense South-East "
        "Asian activity corridor.",
  context="Tuyên Quang is a mountainous karst province in the Northeast "
          "region. No instrumented or institutionally investigated case from "
          "the province appears in the published record; Vietnam has no "
          "state UAP investigation comparable to France's GEIPAN or the US "
          "AARO."),

S("kimberley", "Kimberley — Wandjina Rock Art",
  subtitle="Western Australia", country="Australia",
  region="Southeast Asia & Oceania", category="geoglyph",
  tags=["rock-art", "wandjina", "gwion", "first-nations"],
  aliases=["Wandjina", "Wondjina", "Gwion Gwion", "Bradshaw figures",
           "Western Australia"],
  wikipedia="Wandjina", lat=-16.5000, lon=126.0000, height=250000,
  precision="area", radius_km=250, pitch=-65,
  claim="Wandjina figures — large pale faces with huge dark eyes, no mouths "
        "and radiating halo-like headdresses — are among the series' most "
        "frequently shown images, presented as portraits of visitors.",
  context="Wandjina are ancestral rain and creation beings of the Worrorra, "
          "Ngarinyin and Wunambal peoples, who hold continuing custodial "
          "authority over the images and repaint them as a maintenance "
          "obligation. The iconography is explained within that living "
          "tradition: the halo is storm cloud and lightning, the absent "
          "mouth signifies the power of rain held in check. Traditional "
          "owners have objected publicly and repeatedly to the "
          "extraterrestrial reading."),

S("melanesia-png", "Melanesia & Papua New Guinea",
  subtitle="South-west Pacific (regional)",
  country="Papua New Guinea / Melanesia", region="Southeast Asia & Oceania",
  category="region", tags=["cargo-cult", "john-frum", "ethnography"],
  aliases=["cargo cult", "John Frum", "Vanuatu", "Tanna"],
  wikipedia="Cargo cult", lat=-6.0000, lon=147.0000, height=1800000,
  precision="area", radius_km=900, pitch=-72,
  claim="The series inverts the cargo cults as its central analogy: if "
        "islanders built runways and effigy aircraft to summon back the "
        "Americans who once descended with goods, then ancient temples and "
        "ziggurats are the same impulse aimed at earlier visitors.",
  context="The analogy is the series' strongest rhetorical move and its "
          "clearest logical gap. Cargo cults are documented twentieth-century "
          "responses to a contact that demonstrably occurred, with living "
          "witnesses, dated wartime airstrips and surviving materiel. "
          "Anthropologists also now read them less as misunderstanding than "
          "as political movements asserting a claim on wealth. The analogy "
          "predicts that ancient contact would leave comparable residue — "
          "which is precisely what has not been found."),

S("hawaiian-islands", "Hawaiian Islands",
  subtitle="Hawaii, United States", country="United States",
  region="Southeast Asia & Oceania", category="landform",
  tags=["hotspot", "heiau", "navigation", "menehune"],
  aliases=["Hawaii", "Menehune", "Mauna Kea", "heiau"],
  wikipedia="Hawaiian Islands", lat=20.7984, lon=-156.3319, height=800000,
  precision="area", radius_km=350, pitch=-65,
  claim="Polynesian open-ocean navigation across thousands of kilometres "
        "without instruments, plus the Menehune traditions of small beings "
        "who built stone works overnight, are presented as transmitted "
        "knowledge and as a resident non-human population.",
  context="Polynesian wayfinding is a reconstructed and demonstrated human "
          "skill: Hōkūle'a's voyages since 1976, navigated by Mau Piailug "
          "and successors using star paths, swell patterns and bird "
          "behaviour, have crossed the Pacific repeatedly without "
          "instruments. The Menehune Ditch and Alekoko fishpond are "
          "Hawaiian-built structures; the Menehune tradition is now generally "
          "read as referring to an earlier social class or settlement wave."),

S("haleakala", "Haleakalā Observatory",
  subtitle="Maui, Hawaii, United States", country="United States",
  region="Southeast Asia & Oceania", category="research",
  tags=["observatory", "pan-starrs", "space-surveillance", "maui"],
  aliases=["Maui", "Science City", "Pan-STARRS", "AMOS"],
  wikipedia="Haleakalā Observatory", lat=20.7083, lon=-156.2572, height=8000,
  claim="A military and civilian optical complex at 3,055 m — tracking "
        "satellites, hosting Pan-STARRS and sitting atop a volcano Hawaiian "
        "tradition calls the house of the sun — is presented as a monitoring "
        "post for inbound traffic, with its findings withheld.",
  context="Haleakalā hosts the Air Force Maui Optical and Supercomputing site "
          "and Pan-STARRS, whose near-Earth-object survey is published "
          "continuously through the Minor Planet Center and which discovered "
          "1I/ʻOumuamua in 2017. Space-surveillance tracking data on "
          "catalogued objects is public via space-track.org. Native Hawaiian "
          "concerns about summit development are real, well-articulated and "
          "unrelated to the claim.",
  links=[{"label": "Pan-STARRS survey", "url": "https://panstarrs.stsci.edu/",
          "kind": "reference"}]),

S("mauritius", "Mauritius",
  subtitle="Indian Ocean", country="Mauritius", region="Africa",
  category="landform", tags=["mauritia", "zircon", "lost-continent", "dodo"],
  aliases=["Mauritia", "lost continent", "Indian Ocean"],
  wikipedia="Mauritius", lat=-20.3484, lon=57.5522, height=120000,
  claim="Three-billion-year-old zircon crystals recovered on a nine-million-"
        "year-old volcanic island, reported in 2013 and 2017 as evidence of a "
        "drowned continent called Mauritia, are presented as the physical "
        "remains of Lemuria.",
  context="The zircons are real and the finding is mainstream geology: they "
          "indicate a fragment of Archean continental crust stranded beneath "
          "Mauritius when Madagascar and India separated, and 'Mauritia' is "
          "the geological name for it. It is sunken continental crust tens "
          "of kilometres down, not a habitable landmass, and it foundered "
          "roughly 84 million years before any hominin existed."),


# ===========================================================================
# NORTH AMERICA — pre-Columbian & archaeological
# ===========================================================================

S("serpent-mound", "Great Serpent Mound",
  subtitle="Adams County, Ohio, United States", country="United States",
  region="North America", category="geoglyph",
  tags=["effigy-mound", "fort-ancient", "archaeoastronomy", "cryptoexplosion"],
  aliases=["Adams County", "Ohio", "Serpent Mound"],
  wikipedia="Serpent Mound", lat=39.0255, lon=-83.4300, height=1200,
  claim="A 411 m serpent effigy built on the rim of a cryptoexplosion "
        "structure — a site of either meteorite impact or deep gas "
        "collapse — with solstice alignments in its coils, is presented as a "
        "marker placed on a crash site.",
  context="The Serpent Mound Disturbance is a genuine and unusual geological "
          "feature, and shocked quartz supports an impact origin some 300 "
          "million years ago. The mound itself is attributed to the Fort "
          "Ancient culture around AD 1070 on the basis of radiocarbon dates "
          "from the embankment, with possible earlier Adena involvement. "
          "Serpent imagery is widespread in Mississippian and Fort Ancient "
          "iconography."),

S("big-horn-medicine-wheel", "Bighorn Medicine Wheel",
  subtitle="Bighorn National Forest, Wyoming, United States",
  country="United States", region="North America", category="megalithic",
  tags=["archaeoastronomy", "medicine-wheel", "plains", "national-landmark"],
  aliases=["Medicine Mountain", "Wyoming", "Big Horn"],
  wikipedia="Bighorn Medicine Wheel", lat=44.8264, lon=-107.9222, height=1200,
  claim="A 24 m stone wheel with 28 spokes at 2,940 m, reported to align on "
        "the solstice sunrise and on the risings of Aldebaran, Rigel and "
        "Sirius, is presented as a precision instrument beyond its builders.",
  context="The wheel is roughly 300–800 years old and is one of about 150 "
          "medicine wheels on the northern Plains. Jack Eddy's 1974 survey "
          "did find plausible stellar alignments, and the heliacal risings "
          "concerned are directly observable from the ridge across "
          "generations. The site remains in active ceremonial use by Crow, "
          "Cheyenne, Arapaho, Shoshone and Lakota people, and is co-managed "
          "with those nations."),

S("chaco-canyon", "Chaco Canyon",
  subtitle="San Juan County, New Mexico, United States",
  country="United States", region="North America", category="city",
  tags=["unesco", "ancestral-puebloan", "archaeoastronomy", "great-houses",
        "lunar-standstill"],
  aliases=["Chaco Culture", "Pueblo Bonito", "New Mexico", "Sun Dagger"],
  wikipedia="Chaco Culture National Historical Park", lat=36.0603,
  lon=-107.9559, height=4000, precision="area", radius_km=14,
  claim="Great houses of up to 650 rooms, 400 km of engineered roads running "
        "dead straight over mesas, buildings aligned to the 18.6-year lunar "
        "standstill, and the Fajada Butte 'Sun Dagger' are presented as a "
        "surveyed complex built to an off-world plan in a desert that could "
        "not feed its builders.",
  context="Chaco is one of the most thoroughly investigated archaeological "
          "landscapes in North America, with tree-ring dating to the "
          "individual year of construction for many rooms — the Chaco "
          "sequence runs c. AD 850–1150. Timber was carried from the Chuska "
          "and Zuni mountains, traced by strontium isotopes; cacao and "
          "macaws document trade with Mesoamerica. The alignments are real "
          "and are mainstream archaeoastronomy. Descendant Pueblo, Hopi and "
          "Navajo nations maintain continuous cultural connection to the "
          "site."),

S("zuni-pueblo", "Zuni Pueblo",
  subtitle="McKinley County, New Mexico, United States",
  country="United States", region="North America", category="sacred",
  tags=["pueblo", "oral-tradition", "kachina", "emergence"],
  aliases=["A:shiwi", "Zuni", "New Mexico"],
  wikipedia="Zuni Pueblo, New Mexico", lat=35.0692, lon=-108.8492, height=3000,
  claim="Zuni emergence narratives and kachina traditions are cited — "
        "sometimes alongside a claimed Zuni–Japanese linguistic link — as a "
        "record of ancestors who came from the sky or from another world.",
  context="Zuni is a continuously occupied community with its own living "
          "religious institutions, and its oral traditions are the property "
          "and responsibility of that community. Zuni is a language isolate; "
          "Nancy Yaw Davis's proposed Japanese connection has not been "
          "accepted by linguists, who find the correspondences too few and "
          "too loose. Emergence narratives are a widespread Pueblo "
          "theological form."),

S("black-mesa", "Black Mesa",
  subtitle="Navajo & Hopi lands, north-eastern Arizona, United States",
  country="United States", region="North America", category="landform",
  tags=["hopi", "navajo", "coal", "mesa"],
  aliases=["Arizona", "Hopi", "Navajo", "Dzil Yijiin"],
  wikipedia="Black Mesa (Arizona)", lat=36.5000, lon=-110.3000, height=90000,
  precision="area", radius_km=60,
  claim="Hopi prophecy — the emergence from previous worlds, the Blue Star "
        "Kachina, and the Ant People who sheltered the Hopi underground "
        "between worlds — is presented as a preserved account of off-world "
        "guardians, with Black Mesa as its centre.",
  context="Hopi religious knowledge is held by initiated members of specific "
          "clans and societies, and Hopi authorities have repeatedly stated "
          "that popularised versions of 'Hopi prophecy' — including most "
          "published Blue Star material, which traces to non-Hopi authors "
          "from the 1950s onward — misrepresent it. The mesa's documented "
          "modern history is dominated by the Peabody coal lease, aquifer "
          "drawdown and the Navajo–Hopi land dispute."),

S("grand-canyon", "Grand Canyon",
  subtitle="Coconino County, Arizona, United States", country="United States",
  region="North America", category="landform",
  tags=["unesco", "colorado-river", "1909-hoax", "geology"],
  aliases=["Colorado River", "Arizona", "Kincaid cave", "Egyptian cave"],
  wikipedia="Grand Canyon", lat=36.0544, lon=-112.1401, height=25000,
  pitch=-30, precision="area", radius_km=70,
  claim="A 1909 Arizona Gazette story described a Smithsonian expedition "
        "finding a vast cavern of Egyptian and Oriental artefacts, mummies "
        "and hieroglyphs in the canyon wall — presented as a discovery "
        "subsequently buried by the institution.",
  context="The Gazette piece names 'S. A. Jordan' and 'G. E. Kinkaid', "
          "neither of whom appears in Smithsonian personnel records, and the "
          "Smithsonian states it has no record of the expedition. The story "
          "ran once, with no follow-up, in a period when the paper carried "
          "frequent sensational filler. The canyon's Egyptian-sounding place "
          "names — Isis Temple, Tower of Ra — were assigned by surveyor "
          "Clarence Dutton in 1882 as a deliberate naming scheme."),

S("flagstaff-san-francisco-peaks", "San Francisco Peaks & Flagstaff",
  subtitle="Coconino County, Arizona, United States", country="United States",
  region="North America", category="research",
  tags=["lowell-observatory", "sacred-mountain", "volcanic", "pluto"],
  aliases=["Flagstaff", "Lowell Observatory", "Humphreys Peak", "Nuva'tukya'ovi",
           "Dook'o'oosłííd"],
  wikipedia="San Francisco Peaks", lat=35.3464, lon=-111.6780, height=20000,
  claim="A sacred mountain to thirteen tribes, which Hopi tradition names as "
        "the home of the kachinas, sitting beside the observatory where Pluto "
        "was found and where Percival Lowell mapped Martian 'canals', is "
        "presented as a monitored contact point.",
  context="The Peaks are an eroded stratovolcano, and their sacred status to "
          "Hopi, Navajo, Havasupai, Zuni and others is legally recognised "
          "and the subject of sustained litigation over development. Lowell "
          "Observatory is a working institution: Clyde Tombaugh found Pluto "
          "there in 1930, and Lowell's canals were resolved as an optical "
          "artefact of small-aperture visual observing, confirmed by Mariner "
          "imaging in 1965."),

S("mount-shasta", "Mount Shasta",
  subtitle="Siskiyou County, California, United States",
  country="United States", region="North America", category="landform",
  tags=["volcano", "lemuria", "telos", "new-age"],
  aliases=["Shasta", "Telos", "Lemurians", "California", "Guy Ballard"],
  wikipedia="Mount Shasta", lat=41.4092, lon=-122.1949, height=20000,
  claim="A 4,322 m stratovolcano said to house Telos, a Lemurian city inside "
        "the mountain, and to produce lenticular clouds read as cloaked "
        "craft — one of North America's densest clusters of contact claims.",
  context="Shasta is an active Cascade stratovolcano with four overlapping "
          "cones; its lenticular caps are standard orographic clouds formed "
          "in the lee of an isolated peak. The Telos tradition begins with "
          "Frederick Spencer Oliver's 1894 novel 'A Dweller on Two Planets' "
          "and was developed by Guy Ballard's 'I AM' movement from 1930. "
          "Geological and geophysical surveys show no cavity system; the "
          "mountain is sacred to Winnemem Wintu, Shasta, Modoc and Achumawi "
          "peoples."),

S("lake-michigan-stones", "Grand Traverse Bay Stone Alignment",
  subtitle="Traverse City, Michigan, United States", country="United States",
  region="North America", category="underwater",
  tags=["submerged", "boulders", "glacial", "great-lakes"],
  aliases=["Traverse City", "Lake Michigan", "Michigan Stonehenge",
           "Grand Traverse Bay"],
  wikipedia="Grand Traverse Bay", lat=44.9500, lon=-85.5500, height=20000,
  precision="approximate",
  claim="A line of boulders found in 2007 at about 12 m depth in Grand "
        "Traverse Bay, one reportedly carved with a mastodon, is presented as "
        "a drowned megalithic alignment from before the lake filled.",
  context="Mark Holley, who located the boulders, has consistently described "
          "them as probably natural glacial deposits and has cautioned "
          "against the 'Stonehenge' framing applied by media. Boulder trains "
          "and moraine lines are exactly what retreating ice leaves on the "
          "Great Lakes floor. The claimed mastodon carving has not been "
          "authenticated; mastodons did inhabit the region and the bay floor "
          "was dry land during the low-water Chippewa phase."),

S("miami-circle", "Miami Circle",
  subtitle="Miami, Florida, United States", country="United States",
  region="North America", category="megalithic",
  tags=["tequesta", "national-landmark", "post-holes", "florida"],
  aliases=["Miami", "Tequesta", "Brickell Point", "Florida"],
  wikipedia="Miami Circle", lat=25.7714, lon=-80.1874, height=800,
  claim="A 12 m ring of basins cut into bedrock at the mouth of the Miami "
        "River, discovered in 1998, is presented as an astronomical "
        "instrument or a landing marker of unknown authorship.",
  context="The circle is a National Historic Landmark attributed to the "
          "Tequesta and dated to roughly 2,000 years ago. The 24 basins are "
          "read as footings for a substantial circular structure, matching "
          "post-hole patterns from other Tequesta sites; associated "
          "artefacts include shell tools, pottery and faunal remains. A "
          "second partial circle was later found across the river."),

S("fort-george-island", "Fort George Island",
  subtitle="Jacksonville, Florida, United States", country="United States",
  region="North America", category="city",
  tags=["timucua", "mount-cornelia", "shell-mound", "fort-caroline"],
  aliases=["Jacksonville", "Timucua", "Fort Caroline", "Florida"],
  wikipedia="Fort George Island", lat=30.4300, lon=-81.4300, height=6000,
  claim="Mount Cornelia, one of the highest points on the US Atlantic coast "
        "south of New Jersey, and the surrounding shell mounds are presented "
        "as artificial earthworks of unknown and possibly non-human origin.",
  context="Mount Cornelia is a relict dune with shell-midden capping, and the "
          "island holds a long archaeological sequence of Timucua occupation "
          "plus the Kingsley Plantation. Shell middens on this coast are "
          "accumulated refuse and deliberate mounding by known cultures, "
          "excavated and dated across the south-east."),

S("green-river-utah", "Green River",
  subtitle="Emery County, Utah, United States", country="United States",
  region="North America", category="military",
  tags=["missile-range", "athena", "white-sands", "rock-art"],
  aliases=["Utah", "Green River Launch Complex", "Athena missile"],
  wikipedia="Green River, Utah", lat=38.9955, lon=-110.1588, height=8000,
  claim="The town's decommissioned launch complex, which fired Athena "
        "missiles toward White Sands, and the surrounding canyon rock art — "
        "including large figures with antennae-like headdresses — are "
        "presented as an old and a new use of the same corridor.",
  context="The Green River Launch Complex operated from 1964 to 1979 as an "
          "Army range extension, and its history is fully declassified. The "
          "rock art belongs to the Barrier Canyon style, attributed to "
          "Archaic hunter-gatherers and dated broadly to 2000 BC–AD 500; "
          "its tall, tapering anthropomorphs are a well-defined regional "
          "convention."),

S("utah-monolith", "Utah Monolith Site",
  subtitle="Red Rock Country, San Juan County, Utah, United States",
  country="United States", region="North America", category="artifact",
  tags=["2020", "art-installation", "hoax", "canyon"],
  aliases=["Utah monolith", "metal monolith", "Lockhart Basin"],
  wikipedia="Utah monolith", lat=38.3435, lon=-109.6661, height=3000,
  claim="A three-metre steel prism found in a remote slot canyon by a "
        "wildlife helicopter crew in November 2020, with no road access and "
        "no explanation, was widely presented as an artefact of non-human "
        "placement — then vanished nine days later.",
  context="Satellite imagery dates the installation to between July and "
          "October 2016, and it is generally attributed to the artist John "
          "McCracken or to someone working in his idiom; McCracken's gallery "
          "initially suggested his authorship. A group of men filmed "
          "removing it came forward, citing damage from visitor traffic to "
          "the canyon. Copycat monoliths subsequently appeared worldwide."),

# ===========================================================================
# NORTH AMERICA — military, secure & research
# ===========================================================================

S("area-51", "Groom Lake, Papoose Mountain & S4",
  subtitle="Nevada Test and Training Range, Nevada, United States",
  country="United States", region="North America", category="military",
  tags=["area-51", "nts", "u2", "oxcart", "lazar"],
  aliases=["Area 51", "Groom Lake", "Dreamland", "S4", "Papoose Lake",
           "Homey Airport", "Bob Lazar"],
  wikipedia="Area 51", lat=37.2350, lon=-115.8111, height=20000,
  precision="area", radius_km=26,
  claim="The series' signature military site: Bob Lazar's 1989 account of "
        "nine recovered craft in hangars at S4 near Papoose Lake, a "
        "gravity-wave propulsion system fuelled by element 115, and a "
        "reverse-engineering programme hidden inside a classified airfield.",
  context="Area 51's existence was officially acknowledged in 2013 with the "
          "CIA's declassified OXCART history, which documents its actual "
          "purpose: flight testing the U-2, A-12, SR-71, F-117 and later "
          "programmes — aircraft whose unfamiliar profiles generated "
          "genuine sighting reports. Lazar's claimed credentials from MIT "
          "and Caltech have not been substantiated by either institution, "
          "and his element-115 predictions were contradicted when the "
          "element was actually synthesised at Dubna in 2003.",
  links=[{"label": "CIA — declassified OXCART history",
          "url": "https://www.cia.gov/readingroom/", "kind": "official"}]),

S("archuleta-mesa", "Archuleta Mesa & Dulce",
  subtitle="Jicarilla Apache Nation, New Mexico, United States",
  country="United States", region="North America", category="military",
  tags=["dulce-base", "cattle-mutilation", "jicarilla"],
  aliases=["Dulce", "Dulce Base", "Jicarilla Apache", "New Mexico"],
  wikipedia="Dulce Base", lat=36.9500, lon=-106.9900, height=12000,
  precision="approximate",
  claim="A seven-level joint human–alien laboratory is said to lie inside the "
        "mesa above Dulce, with genetic experimentation on its lower floors, "
        "tied to the regional cattle-mutilation reports of the 1970s.",
  context="The account originates with Paul Bennewitz in the early 1980s. "
          "Declassified Air Force Office of Special Investigations records "
          "and the testimony of Richard Doty describe a deliberate "
          "disinformation effort directed at Bennewitz, who was "
          "independently monitoring Kirtland AFB transmissions. The 1979–80 "
          "Rommel report, a federally funded investigation by a former FBI "
          "agent, attributed New Mexico's mutilations to ordinary "
          "scavenging — soft tissue removed by birds and small predators. No "
          "excavation, geophysical survey or construction record supports a "
          "facility."),

S("white-sands", "White Sands Proving Ground",
  subtitle="Doña Ana County, New Mexico, United States",
  country="United States", region="North America", category="military",
  tags=["trinity", "v2", "missile-range", "1947"],
  aliases=["White Sands Missile Range", "Trinity site", "New Mexico"],
  wikipedia="White Sands Missile Range", lat=32.7805, lon=-106.3250,
  height=120000, precision="area", radius_km=80,
  claim="The range that hosted the Trinity test and the first American V-2 "
        "launches is cast as the trigger: the detonation that drew attention, "
        "and the site where captured and recovered craft were first flown.",
  context="White Sands is extensively documented, including the July 1945 "
          "Trinity test and the 1946–52 Hermes V-2 programme, whose "
          "telemetry, films and failure reports are archived. Clyde "
          "Tombaugh — the discoverer of Pluto — ran the range's optical "
          "tracking and did report an anomalous 1949 sighting; he also "
          "maintained it was probably an atmospheric phenomenon."),

S("alamogordo", "Alamogordo",
  subtitle="Otero County, New Mexico, United States", country="United States",
  region="North America", category="military",
  tags=["holloman", "1964-film", "atomic-age"],
  aliases=["Holloman Air Force Base", "New Mexico"],
  wikipedia="Alamogordo, New Mexico", lat=32.8995, lon=-105.9603, height=12000,
  claim="A 1964 landing at nearby Holloman AFB, said to be captured on film "
        "and to show a craft met by Air Force officers, is presented as "
        "documented official contact.",
  context="The Holloman landing footage traces to the 1974 pseudo-documentary "
          "'UFOs: Past, Present and Future' and to Robert Emenegger, who has "
          "stated the sequence was a planned reconstruction he was offered "
          "and which never materialised as real footage. Holloman's actual "
          "aerospace record — high-altitude balloon programmes, rocket sleds "
          "and early biomedical flights — generated many genuine reports."),

S("roswell", "Roswell",
  subtitle="Chaves County, New Mexico, United States", country="United States",
  region="North America", category="ufo",
  tags=["1947", "mogul", "crash-retrieval", "foster-ranch"],
  aliases=["New Mexico", "Project Mogul", "Foster Ranch", "RAAF"],
  wikipedia="Roswell incident", lat=33.3943, lon=-104.5230, height=60000,
  geometry="multipoint", points=[(33.3943, -104.5230), (33.9472, -105.4583)],
  claim="The founding case: debris recovered from a ranch north-west of "
        "Roswell in July 1947, announced by the Roswell Army Air Field as a "
        "'flying disc', then retracted as a weather balloon the next day — "
        "with later witnesses describing memory metal, beams with glyphs and "
        "bodies.",
  context="The Air Force's 1994 and 1997 reports identify the debris as "
          "Project Mogul Flight 4, a classified constant-altitude balloon "
          "array of neoprene, foil-laminate radar targets and balsa "
          "battens — materials that match the first-hand descriptions of "
          "foil that would not stay creased and lightweight beams with "
          "pinkish-purple floral tape. The secrecy was real and was about "
          "nuclear-test acoustic detection. The body accounts entered the "
          "record from the late 1970s onward, over thirty years after the "
          "event. Two points are mapped here: the town, where the press "
          "release was issued, and the Foster Ranch debris field near "
          "Corona some 95 km north-west, where the material was found.",
  links=[{"label": "GAO — Roswell records audit (1995)",
          "url": "https://www.gao.gov/products/nsiad-95-187", "kind": "official"}]),

S("offutt-afb", "Offutt Air Force Base",
  subtitle="Omaha, Nebraska, United States", country="United States",
  region="North America", category="military",
  tags=["stratcom", "looking-glass", "command"],
  aliases=["Omaha", "Nebraska", "STRATCOM", "SAC"],
  wikipedia="Offutt Air Force Base", lat=41.1183, lon=-95.9125, height=8000,
  claim="The seat of Strategic Air Command and now USSTRATCOM, with its "
        "deep underground command centre, is presented as the node that would "
        "coordinate a response to contact — and as a site of Cold War "
        "sighting reports over nuclear assets.",
  context="Offutt's command role is public, and reports of unidentified "
          "objects over US nuclear installations are documented in Project "
          "Blue Book files and in the 1967 Malmstrom missile-shutdown "
          "accounts, which remain contested between witness testimony and "
          "the Air Force's electromagnetic-fault explanation. The current "
          "US effort is AARO, established in 2022, which publishes annual "
          "reports to Congress.",
  links=[{"label": "AARO — All-domain Anomaly Resolution Office",
          "url": "https://www.aaro.mil/", "kind": "official"}]),

S("andrews-afb", "Joint Base Andrews & Washington National",
  subtitle="Washington, D.C. area, United States", country="United States",
  region="North America", category="ufo", geometry="multipoint",
  points=[(38.8108, -76.8670), (38.8512, -77.0402)],
  tags=["1952", "radar-visual", "project-blue-book", "washington-flap"],
  aliases=["Andrews Air Force Base", "Washington National Airport",
           "Washington flap", "1952 Washington"],
  wikipedia="1952 Washington, D.C. UFO incident", lat=38.8310, lon=-76.9536,
  height=30000,
  claim="Over two July weekends in 1952, objects were tracked simultaneously "
        "on radar at Washington National, Andrews and Bolling, seen visually "
        "by airline and military pilots, and intercepted by F-94s — the "
        "best-corroborated radar-visual case in US history, prompting the "
        "largest Air Force press conference since the war.",
  context="The case is genuine, extensively documented and remains partly "
          "unresolved. The Air Force attributed the returns to temperature "
          "inversions producing anomalous propagation, which Washington's "
          "July conditions support and which was a known radar artefact; "
          "Edward Ruppelt, who ran Project Blue Book, considered the "
          "explanation incomplete. Capt. Harry Barnes's and the pilots' "
          "accounts are on the record and have never been retracted."),

S("nasa-ames", "NASA Ames Research Center & Moffett Field",
  subtitle="Mountain View, California, United States", country="United States",
  region="North America", category="research",
  tags=["nasa", "astrobiology", "kepler", "seti", "wind-tunnel"],
  aliases=["Moffett Field", "Mountain View", "Ames", "Kepler", "SETI"],
  wikipedia="Ames Research Center", lat=37.4089, lon=-122.0644, height=6000,
  claim="Ames is presented as the public face of a quiet search: it managed "
        "the Kepler exoplanet mission, hosts astrobiology work, and sits "
        "beside the SETI Institute — with the implication that confirmation "
        "has already been reached internally.",
  context="Kepler's science is wholly public: its catalogue of several "
          "thousand confirmed exoplanets is published and the raw light "
          "curves are archived at MAST for anyone to reanalyse. The SETI "
          "Institute is a separate non-profit with an open data policy and "
          "a published post-detection protocol. Ames also ran NASA's "
          "1970s Project Orion-era and later astrobiology programmes under "
          "normal peer review.",
  links=[{"label": "NASA Exoplanet Archive",
          "url": "https://exoplanetarchive.ipac.caltech.edu/", "kind": "reference"}]),

S("huntsville", "Huntsville — Marshall Space Flight Center",
  subtitle="Madison County, Alabama, United States", country="United States",
  region="North America", category="research",
  tags=["nasa", "saturn-v", "von-braun", "paperclip"],
  aliases=["Marshall Space Flight Center", "Alabama", "Redstone Arsenal",
           "von Braun"],
  wikipedia="Marshall Space Flight Center", lat=34.6490, lon=-86.6744,
  height=8000,
  claim="Wernher von Braun's team, brought from Peenemünde under Operation "
        "Paperclip, built the Saturn V here — presented as German "
        "reverse-engineering of recovered technology transplanted into the "
        "Apollo programme.",
  context="The Saturn V's development is documented to the level of "
          "individual component test reports, failure reviews and "
          "contractor records across Marshall, Rocketdyne, Boeing and North "
          "American. It is a scaled, iterated descendant of the A4 and "
          "Redstone, built with 1960s American industrial metallurgy and "
          "computing. Paperclip is fully documented, including the "
          "deliberate laundering of several scientists' Nazi records — a "
          "real scandal, and a different one."),

S("princeton-ias", "Institute for Advanced Study",
  subtitle="Princeton, New Jersey, United States", country="United States",
  region="North America", category="research",
  tags=["physics", "einstein", "wormholes", "oppenheimer"],
  aliases=["Princeton", "IAS", "Einstein", "New Jersey"],
  wikipedia="Institute for Advanced Study", lat=40.3317, lon=-74.6761,
  height=2500,
  claim="Cited for the theoretical physics that would make interstellar "
        "travel possible — Einstein–Rosen bridges, warp metrics and the "
        "Oppenheimer-era work — implying that the mechanism is known and the "
        "application classified.",
  context="The Einstein–Rosen paper of 1935 is real and foundational, and "
          "traversable-wormhole and Alcubierre-metric solutions do exist "
          "within general relativity. Every known version requires exotic "
          "matter with negative energy density in quantities with no "
          "demonstrated source, and quantum energy conditions constrain it "
          "severely. The literature is open and actively published — which "
          "is how its difficulties are known."),

S("penn-state", "Pennsylvania State University",
  subtitle="State College, Pennsylvania, United States",
  country="United States", region="North America", category="research",
  tags=["academia", "technosignatures", "exoplanets"],
  aliases=["State College", "Penn State", "Pennsylvania"],
  wikipedia="Pennsylvania State University", lat=40.7982, lon=-77.8599,
  height=3000,
  claim="Appears as an interview location, with its exoplanet and "
        "technosignature researchers cited to support the likelihood of "
        "detectable extraterrestrial civilisations.",
  context="Penn State's Center for Exoplanets and Habitable Worlds does lead "
          "genuine technosignature work, including Jason Wright's programme "
          "and the Breakthrough Listen analyses. That research is explicitly "
          "a search: its published results to date are non-detections and "
          "upper limits, which is the opposite of the inference drawn from "
          "its existence."),

S("uc-irvine", "University of California, Irvine",
  subtitle="Irvine, California, United States", country="United States",
  region="North America", category="research",
  tags=["academia", "neutrinos", "chemistry"],
  aliases=["UCI", "Irvine", "California"],
  wikipedia="University of California, Irvine", lat=33.6405, lon=-117.8443,
  height=3000,
  claim="Cited as an interview venue for physical-science commentary used to "
        "frame propulsion and materials questions in the series.",
  context="UC Irvine's relevant distinction is Frederick Reines's Nobel-"
          "winning neutrino detection and Sherwood Rowland's ozone work — "
          "both examples of a difficult claim being established through "
          "instrumented, replicated measurement, the standard the series' "
          "central propositions have not met."),

S("ohio-state", "Ohio State University",
  subtitle="Columbus, Ohio, United States", country="United States",
  region="North America", category="research",
  tags=["big-ear", "wow-signal", "radio-astronomy"],
  aliases=["Columbus", "Ohio", "Big Ear", "Wow! signal"],
  wikipedia="Wow! signal", lat=40.0067, lon=-83.0305, height=3000,
  claim="The 'Wow!' signal — a 72-second narrowband burst at 1420 MHz "
        "recorded by Ohio State's Big Ear telescope on 15 August 1977, never "
        "repeated — is presented as a detected transmission.",
  context="The signal is real and remains unexplained, and it is the "
          "strongest candidate SETI has produced. It is also "
          "non-reproducible: Big Ear's twin-feed design should have seen it "
          "twice and recorded it once, and no subsequent search of that sky "
          "position has recovered it. Proposed natural and terrestrial "
          "explanations include a scintillating background source, a comet's "
          "hydrogen cloud and satellite interference, none established."),

# ===========================================================================
# NORTH AMERICA — incident & regional
# ===========================================================================

S("aurora-texas", "Aurora",
  subtitle="Wise County, Texas, United States", country="United States",
  region="North America", category="ufo",
  tags=["1897", "airship-wave", "grave", "hoax"],
  aliases=["Texas", "1897 airship", "Aurora crash"],
  wikipedia="Aurora, Texas UFO incident", lat=33.0576, lon=-97.5058,
  height=6000,
  claim="An 1897 Dallas Morning News report described an airship striking a "
        "windmill in Aurora, scattering unknown metal and killing a pilot "
        "said to be buried in the town cemetery — presented as the earliest "
        "American crash retrieval.",
  context="The story belongs to the 1896–97 mystery-airship wave, a "
          "well-studied newspaper phenomenon in which hundreds of papers "
          "competed with invented sightings during a period of real, "
          "publicised dirigible experimentation. Aurora residents "
          "interviewed in the 1970s, including Etta Pegues, identified the "
          "author S. E. Haydon as a known local jokester and said the "
          "windmill never existed. The cemetery's unmarked grave has "
          "produced no remains; a 1973 metal-detector hit was later "
          "attributed to buried debris."),

S("stephenville-texas", "Stephenville",
  subtitle="Erath County, Texas, United States", country="United States",
  region="North America", category="ufo",
  tags=["2008", "radar", "mufon", "f16"],
  aliases=["Texas", "Erath County", "2008 Stephenville"],
  wikipedia="Stephenville, Texas", lat=32.2207, lon=-98.2023, height=12000,
  claim="In January 2008 dozens of witnesses around Stephenville reported a "
        "silent object around a mile wide with F-16s in pursuit; FAA radar "
        "data obtained under FOIA was said to show an uncorrelated target "
        "tracking toward President Bush's Crawford ranch.",
  context="The witness volume and the FOIA radar release are real and make "
          "this one of the better-documented recent US cases. The Air Force "
          "initially denied, then confirmed, that ten F-16s from the 457th "
          "Fighter Squadron were conducting training in the airspace that "
          "evening — a reversal that drove much of the suspicion. Analysts "
          "disagree over whether the uncorrelated returns represent a "
          "discrete object or transponder-off traffic and radar artefacts."),

S("el-paso-texas", "El Paso",
  subtitle="El Paso County, Texas, United States", country="United States",
  region="North America", category="ufo",
  tags=["border", "fort-bliss", "sighting"],
  aliases=["Texas", "Fort Bliss"],
  wikipedia="El Paso, Texas", lat=31.7619, lon=-106.4850, height=20000,
  claim="Referenced for sightings along the Fort Bliss and White Sands "
        "corridor, where the series argues post-war weapons testing and "
        "reported activity overlap most densely.",
  context="El Paso adjoins Fort Bliss and the White Sands complex, among the "
          "most intensively used military airspace on Earth. Project Blue "
          "Book's own statistics attributed the large majority of its 12,618 "
          "cases to aircraft, balloons, astronomical objects and other "
          "identified causes, with 701 left unidentified — mostly for lack "
          "of data rather than anomalous content."),

S("hill-abduction", "Betty & Barney Hill Encounter Site",
  subtitle="Franconia Notch, New Hampshire, United States",
  country="United States", region="North America", category="ufo",
  tags=["1961", "abduction", "hypnosis", "star-map"],
  aliases=["Betty Hill", "Barney Hill", "New Hampshire", "Zeta Reticuli",
           "Indian Head"],
  wikipedia="Barney and Betty Hill", lat=44.1000, lon=-71.6800, height=15000,
  precision="approximate",
  claim="The template for the abduction narrative: on 19 September 1961 the "
        "Hills reported a craft near Lincoln, two hours of missing time, and "
        "— under later hypnosis — an onboard examination, with Betty's "
        "recalled star map matched by Marjorie Fish to Zeta Reticuli.",
  context="The case's cultural importance is beyond dispute; it established "
          "most elements of the modern abduction script. The hypnotist, "
          "Benjamin Simon, concluded the recovered material was a shared "
          "fantasy rather than recall, and hypnosis is now known to generate "
          "confident false memories. The Fish map correlation was undermined "
          "by later Hipparcos parallax data, which revised several of the "
          "stars' distances and broke the pattern. Barney's initial "
          "description also closely tracked a widely broadcast television "
          "episode aired twelve days earlier."),

S("montauk-plum-island", "Montauk & Plum Island",
  subtitle="Suffolk County, New York, United States", country="United States",
  region="North America", category="military", geometry="multipoint",
  points=[(41.0359, -71.9545), (41.1833, -72.1833)],
  tags=["camp-hero", "montauk-project", "animal-disease-center", "sage-radar"],
  aliases=["Camp Hero", "Montauk Project", "Plum Island", "Philadelphia Experiment"],
  wikipedia="Montauk Project", lat=41.0800, lon=-72.0500, height=20000,
  claim="The Montauk Project: time travel, mind control and contact "
        "experiments said to have continued at Camp Hero beneath a "
        "decommissioned radar station, with the Plum Island animal-disease "
        "laboratory nearby cast as its biological arm.",
  context="Camp Hero is a real former Air Force station whose SAGE AN/FPS-35 "
          "radar tower still stands and is now a state park. The Montauk "
          "narrative originates with Preston Nichols's 1992 book, built on "
          "recovered-memory claims and continuous with the Philadelphia "
          "Experiment legend, itself traceable to Carl Allen's letters to "
          "Morris Jessup. Plum Island is a USDA foreign-animal-disease "
          "facility whose mission, inspections and biosafety record are "
          "public and regularly audited."),

S("new-york-city", "New York City",
  subtitle="New York, United States", country="United States",
  region="North America", category="artifact",
  tags=["rockefeller-center", "christies", "auction", "collections"],
  aliases=["Rockefeller Center", "Christie's", "Manhattan", "NYC"],
  wikipedia="New York City", lat=40.7128, lon=-74.0060, height=12000,
  claim="Appears for the antiquities trade: Rockefeller Center and the "
        "Christie's salerooms as the point where artefacts the series "
        "considers anomalous — Egyptian, Mesopotamian and Mesoamerican — "
        "pass into private hands and out of study.",
  context="The concern about objects leaving the scholarly record is "
          "legitimate and widely shared by archaeologists, though for "
          "ordinary reasons: unprovenanced sales destroy context, launder "
          "looted material and have funded armed groups. Both major houses "
          "now publish provenance research, and repatriations from US "
          "collections to Egypt, Iraq and Italy are frequent and documented. "
          "Nothing in the trade record involves anomalous material."),

S("boston", "Boston",
  subtitle="Suffolk County, Massachusetts, United States",
  country="United States", region="North America", category="research",
  tags=["academia", "harvard", "mit", "interviews"],
  aliases=["Massachusetts", "Harvard", "MIT"],
  wikipedia="Boston", lat=42.3601, lon=-71.0589, height=12000,
  claim="Used as a hub for academic interviews, and tied to the Harvard "
        "psychiatrist John Mack, whose clinical work with people reporting "
        "abduction experiences is presented as institutional validation.",
  context="John Mack's work was real, and Harvard's 1994–95 inquiry into it "
          "concluded with his academic freedom affirmed and no finding of "
          "misconduct — while explicitly not endorsing his conclusions. Mack "
          "himself consistently framed his interest as the experiencers' "
          "psychological reality rather than a physical claim. Sleep "
          "paralysis with hypnopompic hallucination is the "
          "best-characterised mechanism for the core experience."),

S("roxbury-massachusetts", "Roxbury",
  subtitle="Boston, Massachusetts, United States", country="United States",
  region="North America", category="ufo", tags=["sighting", "urban"],
  aliases=["Massachusetts", "Boston"],
  wikipedia="Roxbury, Boston", lat=42.3152, lon=-71.0914, height=6000,
  claim="Cited among urban sighting reports in the Boston area, used to argue "
        "that activity is not confined to remote sites.",
  context="The specific case the series references is not identifiable in the "
          "published sighting catalogues, so this entry marks the locality "
          "rather than a documented event. Dense urban reporting is "
          "expected: more observers, more aircraft on approach to Logan, and "
          "far more camera phones than in rural areas."),

S("bridgewater-triangle", "Bridgewater Triangle & Hockomock Swamp",
  subtitle="South-eastern Massachusetts, United States",
  country="United States", region="North America", category="anomaly",
  tags=["hockomock", "folklore", "wampanoag", "cryptid"],
  aliases=["Hockomock Swamp", "Bridgewater", "Massachusetts", "Place of Fear",
           "Pukwudgie"],
  wikipedia="Bridgewater Triangle", lat=41.9800, lon=-71.0500, height=40000,
  precision="area", radius_km=30,
  claim="A roughly 500 km² area of south-eastern Massachusetts said to "
        "concentrate UFO sightings, thunderbirds, Bigfoot reports, "
        "poltergeists and ritual sites — a terrestrial Bermuda Triangle "
        "named by cryptozoologist Loren Coleman in 1970.",
  context="The 'triangle' is a modern framing drawn around a pre-existing "
          "folkloric landscape; Hockomock itself is a Wampanoag name often "
          "rendered 'place where spirits dwell'. The core is a large, "
          "genuinely difficult wetland that was a refuge during King "
          "Philip's War, which seeded centuries of local legend. No category "
          "of report here exceeds the regional baseline once population and "
          "reporting activity are accounted for."),

S("canton-new-york", "Canton",
  subtitle="St. Lawrence County, New York, United States",
  country="United States", region="North America", category="ufo",
  tags=["sighting", "north-country", "rural"],
  aliases=["New York", "St. Lawrence County"],
  wikipedia="Canton (town), New York", lat=44.5953, lon=-75.1685, height=8000,
  claim="Referenced among North Country encounter reports along the "
        "St. Lawrence corridor near the Canadian border.",
  context="As with several small-town references in the series, no "
          "institutionally investigated case from this locality appears in "
          "the public record, so the entry marks the place rather than an "
          "event. The corridor carries heavy cross-border air traffic and "
          "sits under the aurora's southern reach, both routine sources of "
          "misidentification."),

S("danville-illinois", "Danville",
  subtitle="Vermilion County, Illinois, United States",
  country="United States", region="North America", category="ufo",
  tags=["sighting", "midwest", "illinois"],
  aliases=["Illinois", "Vermilion County"],
  wikipedia="Danville, Illinois", lat=40.1245, lon=-87.6300, height=8000,
  claim="Cited among midwestern sighting reports, in the broader context of "
        "the 2000 Illinois triangle wave over the Mississippi valley.",
  context="The well-documented Illinois case is the 5 January 2000 Highland "
          "and Lebanon event, in which police officers in five towns "
          "independently reported a large triangular object and the "
          "dispatch tapes survive — a different part of the state. No "
          "comparably documented Danville case is in the record."),

S("barron-wisconsin", "Barron",
  subtitle="Barron County, Wisconsin, United States", country="United States",
  region="North America", category="ufo",
  tags=["sighting", "upper-midwest", "wisconsin"],
  aliases=["Wisconsin", "Barron County"],
  wikipedia="Barron, Wisconsin", lat=45.4025, lon=-91.8496, height=8000,
  claim="Referenced among upper-midwestern encounter reports in the farm "
        "country of north-western Wisconsin.",
  context="No investigated case from this locality appears in the published "
          "catalogues, so this entry marks the place. Wisconsin's "
          "best-documented episode is the 1961 Eagle River 'pancake' "
          "contactee account of Joe Simonton, which Project Blue Book "
          "examined and attributed to a hoax or a sincere misperception."),

S("laingsburg-michigan", "Laingsburg",
  subtitle="Shiawassee County, Michigan, United States",
  country="United States", region="North America", category="ufo",
  tags=["sighting", "1966-michigan-wave", "swamp-gas"],
  aliases=["Michigan", "Shiawassee County", "swamp gas"],
  wikipedia="Laingsburg, Michigan", lat=42.8914, lon=-84.3539, height=8000,
  claim="Cited within Michigan's sighting record, the state whose 1966 wave "
        "prompted the Air Force consultant J. Allen Hynek to offer the "
        "'swamp gas' explanation that discredited official investigation and "
        "turned him into its sharpest critic.",
  context="The March 1966 Dexter–Hillsdale sightings and Hynek's press "
          "conference are well documented, as is the backlash: the episode "
          "contributed directly to Congressional hearings and to the "
          "commissioning of the Condon Report. Hynek later founded CUFOS and "
          "argued publicly that Blue Book had been inadequately resourced. "
          "No specific Laingsburg case is in the record."),

S("west-virginia", "West Virginia — Point Pleasant",
  subtitle="Mason County, West Virginia, United States",
  country="United States", region="North America", category="anomaly",
  tags=["mothman", "1967", "silver-bridge", "folklore"],
  aliases=["Mothman", "Point Pleasant", "Silver Bridge", "TNT area"],
  wikipedia="Mothman", lat=38.8454, lon=-82.1371, height=12000,
  claim="Thirteen months of Mothman reports around Point Pleasant in 1966–67 "
        "— a winged figure with red eyes, seen near the abandoned TNT area — "
        "culminating in the Silver Bridge collapse that killed 46 people, are "
        "presented as a warning from a non-human observer.",
  context="The sightings are genuinely documented in contemporary newspapers, "
          "and the bridge collapse of 15 December 1967 is separately and "
          "fully explained: the NTSB traced it to a single cleavage fracture "
          "in an eyebar from stress-corrosion cracking, in a design with no "
          "redundancy. The sandhill crane — tall, red-faced, well outside its "
          "usual range — has been proposed for the figure. The Mothman "
          "narrative as popularly known derives largely from John Keel's "
          "1975 book."),

S("mount-washington", "Mount Washington",
  subtitle="Coös County, New Hampshire, United States",
  country="United States", region="North America", category="landform",
  tags=["extreme-weather", "observatory", "presidential-range"],
  aliases=["New Hampshire", "Presidential Range", "Agiocochook"],
  wikipedia="Mount Washington (New Hampshire)", lat=44.2706, lon=-71.3033,
  height=14000,
  claim="The Northeast's highest summit — holder for decades of the "
        "fastest surface wind ever directly measured, and visible from the "
        "Hill encounter route — is tied to the region's sighting cluster and "
        "to claims of a monitoring presence.",
  context="The 231 mph gust of 12 April 1934 is a real instrumented record, "
          "and the mountain's notorious weather comes from the collision of "
          "three storm tracks over an isolated high summit. The observatory "
          "has operated continuously since 1932 and publishes its data. The "
          "Presidential Range is sacred to Abenaki tradition."),

S("mount-rainier", "Mount Rainier",
  subtitle="Pierce County, Washington, United States", country="United States",
  region="North America", category="ufo",
  tags=["1947", "kenneth-arnold", "flying-saucer", "cascades"],
  aliases=["Kenneth Arnold", "flying saucer", "Washington", "Tahoma"],
  wikipedia="Kenneth Arnold UFO sighting", lat=46.8523, lon=-121.7603,
  height=25000,
  claim="On 24 June 1947 the pilot Kenneth Arnold reported nine crescent "
        "objects weaving between Rainier and Mount Adams at an estimated "
        "1,700 mph — the sighting that gave the world the phrase 'flying "
        "saucer' and opened the modern era.",
  context="Arnold's report is the origin point of the entire phenomenon as a "
          "public category, and the term itself came from a reporter's "
          "compression of his description of how the objects moved, not "
          "their shape. Proposed explanations include a formation of "
          "pelicans, lenticular cloud and mirage effects over the Cascades; "
          "Arnold rejected all of them and never recanted. Rainier is an "
          "active, heavily glaciated stratovolcano and the most dangerous "
          "volcano in the contiguous US by lahar risk."),

S("denali", "Denali",
  subtitle="Denali National Park, Alaska, United States",
  country="United States", region="North America", category="landform",
  tags=["highest-peak", "alaska", "1986-jal-case"],
  aliases=["Mount McKinley", "Alaska", "Mt. Denali"],
  wikipedia="Denali", lat=63.0695, lon=-151.0074, height=30000,
  claim="North America's highest summit anchors the Alaskan material, "
        "including the November 1986 Japan Air Lines Flight 1628 case in "
        "which a crew reported two small craft and then a vast object "
        "tracking them, with the captain's account corroborated by ground "
        "radar.",
  context="JAL 1628 is a genuinely strong case: Captain Kenju Terauchi's "
          "report, the FAA's investigation and division chief John Callahan's "
          "later testimony about the radar data are all on record. The FAA "
          "concluded the radar returns were a split image of the aircraft "
          "itself, and the visual elements have been attributed to Jupiter "
          "and Mars, unusually bright and low on the horizon at that "
          "latitude and date. Terauchi maintained his account and was "
          "reassigned to a desk."),

S("pacific-northwest", "Pacific Northwest",
  subtitle="US–Canada border region", country="United States / Canada",
  region="North America", category="region",
  tags=["cascades", "sasquatch", "maury-island", "regional"],
  aliases=["Cascadia", "Sasquatch", "Bigfoot", "Maury Island"],
  wikipedia="Pacific Northwest", lat=47.5000, lon=-122.0000, height=900000,
  precision="area", radius_km=450, pitch=-68,
  claim="Treated as a persistent hotspot: the Arnold sighting, the Maury "
        "Island affair, the 1967 Patterson–Gimlin film and the region's "
        "Sasquatch traditions are presented as a single long-running "
        "phenomenon.",
  context="The region's First Nations do have long-standing wild-man "
          "traditions, which anthropologists study as cultural history. The "
          "Maury Island case was investigated in 1947 and concluded to be a "
          "hoax by Harold Dahl and Fred Crisman, with the slag identified as "
          "smelter waste; two Air Force investigators died in a crash "
          "returning from it, which fuelled the story. The Patterson–Gimlin "
          "film remains disputed, with a suit-maker's confession on one side "
          "and gait analyses on the other, and no specimen or skeletal "
          "material has ever been produced."),

S("mojave-desert", "Mojave Desert",
  subtitle="California / Nevada / Arizona, United States",
  country="United States", region="North America", category="region",
  tags=["integratron", "giant-rock", "contactee", "edwards-afb"],
  aliases=["Giant Rock", "Integratron", "George Van Tassel", "Landers"],
  wikipedia="Mojave Desert", lat=35.0000, lon=-116.5000, height=700000,
  precision="area", radius_km=300, pitch=-68,
  claim="The cradle of the 1950s contactee movement: George Van Tassel's "
        "Giant Rock conventions drew thousands, and he built the Integratron "
        "at Landers to plans he said were dictated by Venusians — all within "
        "sight of the Edwards and China Lake test ranges.",
  context="Giant Rock and the Integratron are both still standing, and the "
          "conventions are well documented in photographs and periodicals. "
          "The Integratron does not function as described and no "
          "rejuvenation effect has been demonstrated. The proximity to "
          "Edwards AFB matters: the Mojave was where the X-planes flew, and "
          "the region's sighting record tracks the flight-test calendar "
          "closely."),

S("las-vegas", "Las Vegas",
  subtitle="Clark County, Nevada, United States", country="United States",
  region="North America", category="city",
  tags=["janet-flights", "mcarran", "tourism"],
  aliases=["Nevada", "Janet", "Harry Reid Airport", "Extraterrestrial Highway"],
  wikipedia="Las Vegas", lat=36.1699, lon=-115.1398, height=20000,
  claim="Presented as the public-facing edge of the Nevada complex: the "
        "unmarked 'Janet' fleet that commutes contractors to Groom Lake flies "
        "from a dedicated terminal here, and the city is where Bob Lazar went "
        "public in 1989.",
  context="The Janet fleet is real, operates from a gated terminal on the "
          "west side of Harry Reid International, and is openly trackable; "
          "its existence confirms a classified workforce at a classified "
          "airfield, which the government acknowledged in 2013. Nevada "
          "renamed State Route 375 the Extraterrestrial Highway in 1996 as a "
          "tourism measure."),

S("los-angeles", "Los Angeles",
  subtitle="California, United States", country="United States",
  region="North America", category="ufo",
  tags=["1942", "battle-of-los-angeles", "wwii", "media"],
  aliases=["California", "Battle of Los Angeles", "Hollywood"],
  wikipedia="Battle of Los Angeles", lat=34.0522, lon=-118.2437, height=25000,
  claim="On the night of 24–25 February 1942, anti-aircraft batteries fired "
        "more than 1,400 rounds at an object over Los Angeles that "
        "searchlights held and that shells appeared not to damage — "
        "photographed by the Los Angeles Times and presented as a craft "
        "surviving a sustained barrage.",
  context="The event is fully documented and occurred eleven weeks after "
          "Pearl Harbor, amid genuine invasion fear and the previous day's "
          "Japanese submarine shelling of Ellwood. The Army initially "
          "blamed a false alarm, then jittery nerves; later analysis points "
          "to a weather balloon launched that night, with searchlight beams "
          "converging in smoke and haze. The famous photograph was "
          "substantially retouched before publication, a routine practice "
          "of the period. Five civilian deaths resulted from the barrage."),

S("pacific-palisades", "Pacific Palisades",
  subtitle="Los Angeles, California, United States", country="United States",
  region="North America", category="sacred",
  tags=["self-realization", "esoteric", "contactee"],
  aliases=["California", "Lake Shrine"],
  wikipedia="Pacific Palisades, Los Angeles", lat=34.0481, lon=-118.5261,
  height=6000,
  claim="Referenced for Southern California's dense concentration of esoteric "
        "organisations and contactee groups in the mid-20th century, "
        "presented as a network seeded by genuine contact.",
  context="The concentration is a real and well-studied feature of "
          "California religious history — Theosophy, Vedanta, the I AM "
          "movement and dozens of successors took root here from the 1890s. "
          "Historians attribute it to migration patterns, inexpensive land "
          "and the absence of established religious authority, not to an "
          "external cause."),

S("malibu-point-dume", "Malibu & Point Dume",
  subtitle="Los Angeles County, California, United States",
  country="United States", region="North America", category="underwater",
  tags=["sonar-anomaly", "malibu-plateau", "seafloor"],
  aliases=["Point Dume", "Malibu", "California", "underwater base"],
  wikipedia="Point Dume", lat=34.0017, lon=-118.8056, height=12000,
  claim="A Google Earth bathymetric feature off Point Dume, circulated from "
        "2012 as a vast flat-topped structure with columns 3 km down, was "
        "presented as an underwater base.",
  context="The feature is a well-understood artefact of bathymetric data "
          "processing: ship-track sonar swaths of differing resolution "
          "stitched together produce rectilinear terraces and ridges aligned "
          "to the survey lines. NOAA has explained the same artefact for "
          "comparable 'discoveries' worldwide, including the 'Atlantis grid' "
          "off West Africa in 2009. Higher-resolution surveys show ordinary "
          "continental slope."),

S("palm-springs", "Palm Springs",
  subtitle="Riverside County, California, United States",
  country="United States", region="North America", category="ufo",
  tags=["coachella", "desert", "sighting"],
  aliases=["California", "Coachella Valley"],
  wikipedia="Palm Springs, California", lat=33.8303, lon=-116.5453,
  height=12000,
  claim="Cited among Coachella Valley sighting reports and in connection with "
        "the desert's mid-century contactee circuit, a short drive from "
        "Giant Rock.",
  context="The Coachella Valley sits between the Chocolate Mountain Aerial "
          "Gunnery Range, Twentynine Palms and the Banning Pass air "
          "corridor, and the clear desert sky and low humidity make distant "
          "aircraft lights, flares and balloons unusually visible — the "
          "standard explanatory set for desert sighting clusters."),

S("riverside-quarry", "Riverside — Stone Valley Quarry",
  subtitle="Riverside County, California, United States",
  country="United States", region="North America", category="artifact",
  precision="uncertain", tags=["quarry", "aggregate", "unresolved-reference"],
  aliases=["Stone Valley Materials", "Riverside", "California"],
  wikipedia="Riverside County, California", lat=33.9533, lon=-117.3962,
  height=30000,
  claim="A Southern California aggregate quarry is referenced in connection "
        "with anomalous stone or artefacts reportedly recovered during "
        "extraction.",
  context="The specific operation named does not resolve to a published site, "
          "so this entry is positioned on Riverside County as a label. "
          "Quarry 'anomalies' generally resolve into geodes, concretions, "
          "fulgurites or modern debris; the one category of genuine "
          "palaeontological importance in the region is the Pleistocene "
          "vertebrate material recovered from Inland Empire aggregate pits "
          "under standard mitigation monitoring."),

S("scottsdale", "Scottsdale",
  subtitle="Maricopa County, Arizona, United States", country="United States",
  region="North America", category="ufo",
  tags=["phoenix-lights", "1997", "arizona"],
  aliases=["Arizona", "Phoenix Lights", "Phoenix"],
  wikipedia="Phoenix Lights", lat=33.4942, lon=-111.9261, height=25000,
  claim="The Phoenix Lights of 13 March 1997 — a V-formation of lights "
        "crossing Arizona, witnessed by thousands from Henderson to Tucson "
        "and filmed repeatedly — are among the most widely observed events "
        "in the record, with the Scottsdale and Phoenix footage its core.",
  context="The evening comprised two separate events. The later 10 p.m. "
          "lights over the Estrella range were identified as LUU-2B/B "
          "illumination flares dropped by A-10s on the Barry Goldwater "
          "Range, confirmed by the Maryland Air National Guard in 2000 and "
          "consistent with the footage's descent and burnout. The earlier "
          "8:30 p.m. formation is less settled; amateur astronomers tracked "
          "it as five distinct aircraft in loose V-formation, and the "
          "'single craft' impression is attributed to the dark sky between "
          "the lights."),

S("winnemucca-lake", "Winnemucca Lake",
  subtitle="Pershing County, Nevada, United States", country="United States",
  region="North America", category="geoglyph",
  tags=["petroglyphs", "oldest-rock-art", "pyramid-lake", "paiute"],
  aliases=["Nevada", "Northern Paiute", "oldest petroglyphs"],
  wikipedia="Winnemucca Lake", lat=40.1667, lon=-119.2500, height=20000,
  claim="Petroglyphs on a dry lake bed, dated by carbonate crust to between "
        "14,800 and 10,500 years ago — the oldest securely dated rock art in "
        "North America — are presented as a record left at first contact, "
        "their abstract forms read as star maps or craft.",
  context="The dating, published in 2013 by Larry Benson and colleagues "
          "using the tufa coating's radiocarbon and lake-level history, is "
          "genuine and important: it establishes symbolic expression in the "
          "Great Basin at or before the earliest accepted human presence. "
          "The motifs are deeply incised geometric and dendritic forms, a "
          "recognised Great Basin Carved Abstract style. The site is on "
          "Pyramid Lake Paiute land and access is restricted."),

S("badlands-guardian", "Badlands Guardian",
  subtitle="Near Medicine Hat, Alberta, Canada", country="Canada",
  region="North America", category="geoglyph",
  tags=["erosion", "pareidolia", "coulee", "alberta"],
  aliases=["Alberta", "Medicine Hat", "Gravelbourg", "Saskatchewan",
           "Indian Head"],
  wikipedia="Badlands Guardian", lat=50.0106, lon=-110.1133, height=6000,
  claim="A 255 m formation resembling a human head in a feathered "
        "headdress — complete with what looks like an earbud and a road "
        "running to it — found on satellite imagery in 2006, is presented as "
        "a deliberate geoglyph or a message visible only from above.",
  context="The feature is a drainage network eroded into soft clay-rich "
          "badlands, and the apparent profile depends entirely on viewing "
          "angle and sun azimuth; it inverts into a valley at other "
          "lighting. The 'earbud' is an access road and a wellhead installed "
          "in the 1990s. It is a textbook case of pareidolia in "
          "remote-sensing imagery, alongside the Face on Mars."),

S("united-states", "United States",
  subtitle="Continental United States (regional)", country="United States",
  region="North America", category="region",
  tags=["regional", "blue-book", "aaro", "disclosure"],
  aliases=["USA", "Project Blue Book", "Condon Report", "AARO", "AATIP"],
  wikipedia="Unidentified flying object", lat=39.8283, lon=-98.5795,
  height=4500000, precision="area", radius_km=2000, pitch=-78,
  claim="The United States is the series' institutional frame: successive "
        "official programmes — Sign, Grudge, Blue Book, AATIP, UAPTF, "
        "AARO — are presented as a seventy-year managed concealment, with "
        "Congressional hearings as its slow unravelling.",
  context="The programme history is real and documentable. Blue Book closed "
          "in 1969 after the Condon Report found no national-security or "
          "scientific value, and its 12,618 case files are public at the "
          "National Archives. AATIP's existence was reported in 2017, and "
          "AARO was created by statute in 2022; its 2024 historical review "
          "found no evidence of recovered extraterrestrial technology, while "
          "documenting how classified aerospace programmes and inaccurate "
          "internal briefings generated and sustained the belief that there "
          "was. Both findings are on the record.",
  links=[{"label": "National Archives — Project Blue Book files",
          "url": "https://www.archives.gov/research/military/air-force/ufos",
          "kind": "official"},
         {"label": "AARO — reports to Congress", "url": "https://www.aaro.mil/",
          "kind": "official"}]),


# ===========================================================================
# CENTRAL AMERICA & CARIBBEAN
# ===========================================================================

S("teotihuacan", "Teotihuacan",
  subtitle="State of Mexico, Mexico", country="Mexico",
  region="Central America & Caribbean", category="pyramid",
  tags=["unesco", "pyramid-of-the-sun", "mica", "mercury", "avenue-of-the-dead"],
  aliases=["Pyramid of the Sun", "Avenue of the Dead", "Mexico City", "mica"],
  wikipedia="Teotihuacan", lat=19.6925, lon=-98.8438, height=2000,
  claim="A city of 125,000 whose builders left no name, no king-lists and no "
        "readable script; sheets of mica from Brazil set into floors where "
        "they cannot be seen; and liquid mercury and thousands of metallic "
        "spheres found in a tunnel under the Temple of the Feathered "
        "Serpent — presented as industrial materials in a reactor or "
        "insulation.",
  context="Teotihuacan is intensively excavated and its chronology is secure "
          "(c. 100 BC–AD 550). Mica occurs in Mexican deposits in Oaxaca "
          "and Hidalgo; long-distance exchange in exotic materials is "
          "normal Mesoamerican practice, documented for jade, obsidian, "
          "cacao and quetzal feathers. Mercury appears in several "
          "Mesoamerican ritual deposits — at Copán and Kaminaljuyú too — and "
          "is read as a mirror-symbol for an underworld lake; the spheres "
          "are clay coated in pyrite, a reflective ritual material."),

S("chichen-itza", "Chichén Itzá — El Castillo",
  subtitle="Yucatán, Mexico", country="Mexico",
  region="Central America & Caribbean", category="pyramid",
  tags=["unesco", "maya", "equinox", "kukulkan", "acoustics", "cenote"],
  aliases=["El Castillo", "Kukulkan", "Yucatan", "Temple of Kukulcan"],
  wikipedia="Chichen Itza", lat=20.6829, lon=-88.5686, height=900,
  claim="A pyramid with 365 steps whose balustrade casts a descending "
        "serpent at the equinoxes, whose staircase returns a chirped echo "
        "resembling the quetzal's call, and which sits atop a cenote and "
        "nested earlier structures, is presented as an engineered instrument "
        "built to a supplied specification.",
  context="Both effects are real and both are now well studied. The "
          "equinoctial shadow serpent is widely accepted as deliberate — "
          "Kukulkan's descent is the building's stated subject. The chirped "
          "echo was analysed by Declercq and others and arises from "
          "periodic scattering off the step risers, a predictable "
          "consequence of the geometry that Maya builders could tune by ear. "
          "The subterranean cenote was confirmed by electrical resistivity "
          "survey in 2015, matching Maya placement of temples over water "
          "entrances to the underworld."),

S("palenque", "Palenque — Temple of the Inscriptions",
  subtitle="Chiapas, Mexico", country="Mexico",
  region="Central America & Caribbean", category="pyramid",
  tags=["unesco", "maya", "pakal", "sarcophagus-lid", "classic"],
  aliases=["Pakal", "K'inich Janaab' Pakal", "Chiapas", "Palace",
           "Temple of the Inscriptions"],
  wikipedia="Palenque", lat=17.4840, lon=-92.0461, height=1200,
  claim="The carved lid of K'inich Janaab' Pakal's sarcophagus is the "
        "series' most reproduced image: read as a pilot reclining in a "
        "capsule, hands on controls, a breathing apparatus at his face and "
        "exhaust streaming behind — the 'Palenque Astronaut'.",
  context="The lid is fully readable in Maya iconographic terms and its own "
          "glyphic text names and dates the occupant: Pakal, died AD 683, "
          "shown falling into the maw of the underworld along the world "
          "tree, with the Celestial Bird above and a quadripartite badge "
          "below. Every element of the composition recurs in other Maya "
          "monuments. Rotating the image 90° to produce the rocket reading "
          "breaks the register conventions the rest of the tomb follows."),

S("uxmal", "Uxmal",
  subtitle="Yucatán, Mexico", country="Mexico",
  region="Central America & Caribbean", category="pyramid",
  tags=["unesco", "maya", "puuc", "pyramid-of-the-magician", "venus"],
  aliases=["Pyramid of the Magician", "Puuc", "Yucatan", "Dwarf"],
  wikipedia="Uxmal", lat=20.3597, lon=-89.7714, height=1200,
  claim="The legend of the Pyramid of the Magician — raised in a single "
        "night by a dwarf hatched from an egg — is cited as a memory of "
        "rapid construction by non-human means, and the Governor's Palace's "
        "Venus alignment as precision astronomy.",
  context="The pyramid has five superimposed construction phases, "
          "excavated and dated, spanning several centuries — the opposite "
          "of overnight. The Governor's Palace does face the southerly "
          "extreme of Venus's rising, a genuine and deliberate alignment "
          "reflected in the Venus glyphs on its own façade and consistent "
          "with the Dresden Codex's Venus tables. The dwarf legend was "
          "recorded in the 19th century by John Lloyd Stephens from local "
          "informants."),

S("la-venta", "La Venta",
  subtitle="Tabasco, Mexico", country="Mexico",
  region="Central America & Caribbean", category="city",
  tags=["olmec", "colossal-heads", "basalt", "formative"],
  aliases=["Olmec", "Tabasco", "colossal heads"],
  wikipedia="La Venta", lat=18.1061, lon=-94.0397, height=2000,
  claim="The Olmec colossal heads — up to 40 tonnes of basalt carried about "
        "100 km from the Tuxtla mountains, with features the series "
        "describes as African or non-human and wearing what look like "
        "helmets — are presented as portraits of visitors.",
  context="Basalt sourcing to Cerro Cintepec in the Tuxtlas is established "
          "petrologically, and river-raft transport across the Coatzacoalcos "
          "drainage is the accepted mechanism. The 'helmets' are generally "
          "read as ballgame headgear or rulers' regalia, matching Olmec "
          "ballcourt iconography. The facial features fall within "
          "indigenous Mesoamerican variation; the African-origin reading "
          "advanced by Ivan van Sertima has been rejected on skeletal, "
          "dental and genetic grounds. La Venta also produced the earliest "
          "known Mesoamerican jade workshops and a magnetite mirror "
          "tradition."),

S("comalcalco", "Comalcalco",
  subtitle="Tabasco, Mexico", country="Mexico",
  region="Central America & Caribbean", category="pyramid",
  tags=["maya", "fired-brick", "chontalpa", "classic"],
  aliases=["Tabasco", "brick pyramid", "Joy Chan"],
  wikipedia="Comalcalco", lat=18.2642, lon=-93.1839, height=1200,
  claim="The only major Maya city built of fired brick rather than stone, "
        "with hundreds of bricks bearing marks and figures on their hidden "
        "faces, is presented as evidence of an outside building tradition — "
        "and the 2012 discovery of a brick with a Long Count date as a "
        "second prophecy text.",
  context="Comalcalco sits in the Chontalpa, an alluvial plain with no "
          "building stone — which is precisely why its builders fired brick "
          "from local clay. The marked faces were laid inward, so they are "
          "read as makers' marks, tallies and casual graffiti, a category "
          "well known from Roman and medieval brickwork. The 2012 brick "
          "records a calendrical date; epigraphers noted at the time that it "
          "carries no prophetic statement."),

S("tortuguero", "Tortuguero",
  subtitle="Tabasco, Mexico", country="Mexico",
  region="Central America & Caribbean", category="artifact",
  tags=["maya", "monument-6", "long-count", "2012"],
  aliases=["Monument 6", "2012 prophecy", "Tabasco", "Bolon Yokte"],
  wikipedia="Tortuguero (Maya site)", lat=17.8167, lon=-92.9333, height=4000,
  precision="approximate",
  claim="Monument 6 from this small Maya site carries the only known ancient "
        "inscription referring to the 13-baktun date of 21 December 2012 — "
        "presented as a dated warning of the end of a cycle and the return "
        "of its authors.",
  context="The monument is genuine and the reference is real, which is why "
          "epigraphers studied it closely. The passage is eroded and reads, "
          "in the standard translation, that the god Bolon Yokte' K'uh will "
          "'descend' or be 'displayed' at the period ending — a routine "
          "dedicatory formula tying a local ruler's works to a future "
          "calendar station. Maya Long Count dates run far beyond 2012 at "
          "Palenque and Coba, so the calendar does not end. The site was "
          "largely destroyed by a cement works."),

S("veracruz-voladores", "Papantla — Danza de los Voladores",
  subtitle="Veracruz, Mexico", country="Mexico",
  region="Central America & Caribbean", category="sacred",
  tags=["unesco-ich", "totonac", "el-tajin", "ritual"],
  aliases=["Voladores", "Papantla", "El Tajín", "Veracruz", "flyers"],
  wikipedia="Danza de los Voladores", lat=20.4472, lon=-97.3208, height=2000,
  claim="Five men who climb a 30 m pole, bind themselves by the ankles and "
        "spin to the ground in thirteen revolutions each — a rite recorded "
        "since before the conquest — are presented as re-enacting the "
        "descent of beings from the sky.",
  context="The dance is inscribed on UNESCO's Intangible Cultural Heritage "
          "list and its symbolism is documented by Totonac practitioners "
          "and by ethnographers: four flyers times thirteen revolutions "
          "gives the 52-year Mesoamerican calendar round, with the "
          "caporal on the platform representing the sun. It is a petition "
          "for rain and fertility, performed by named families who hold the "
          "right to it."),

S("merida-caves", "Mérida — Yucatán Cave System",
  subtitle="Yucatán, Mexico", country="Mexico",
  region="Central America & Caribbean", category="underground",
  tags=["cenote", "xibalba", "chicxulub", "karst"],
  aliases=["Xibalba", "Yucatan caves", "cenotes", "Balankanche",
           "Sac Actun"],
  wikipedia="Cenote", lat=20.9674, lon=-89.5926, height=60000,
  precision="area", radius_km=70,
  claim="A flooded cave network the Maya called Xibalba, the underworld — "
        "with cenotes arranged in a ring across the northern Yucatán — is "
        "presented as an engineered subterranean complex and an entrance to "
        "an inner world.",
  context="The Ring of Cenotes is the surface expression of the buried "
          "Chicxulub impact crater, a 66-million-year-old structure "
          "identified by gravity and magnetic anomalies and confirmed by "
          "drilling — the asteroid impact associated with the end-Cretaceous "
          "extinction. The caves themselves are karst dissolution in "
          "limestone, mapped by cave divers to over 370 km in the Sac "
          "Actun system. Maya ritual use of cenotes, including the "
          "Balankanche offerings, is extensively excavated."),

S("yucatan-peninsula", "Yucatán Peninsula",
  subtitle="Mexico, Belize & Guatemala (regional)",
  country="Mexico / Belize / Guatemala",
  region="Central America & Caribbean", category="region",
  tags=["maya", "regional", "chicxulub", "lowlands"],
  aliases=["Yucatan", "Maya lowlands"],
  wikipedia="Yucatán Peninsula", lat=19.5000, lon=-89.0000, height=900000,
  precision="area", radius_km=400, pitch=-70,
  claim="The peninsula is treated as a single dense cluster: the Maya "
        "calendar, the Long Count, the cities abandoned at their height, and "
        "the Chicxulub crater beneath them, read as one continuous story of "
        "intervention.",
  context="Maya collapse research has converged on a multi-causal model — "
          "severe multi-decadal drought documented in Yok Balum and "
          "Chaac speleothem records, soil exhaustion, escalating warfare and "
          "political fragmentation — with abandonment staggered across "
          "roughly AD 800–1000 and northern cities such as Chichén Itzá "
          "flourishing afterwards. Maya communities number several million "
          "today; the civilisation did not vanish."),

S("casas-grandes", "Casas Grandes (Paquimé)",
  subtitle="Chihuahua, Mexico", country="Mexico",
  region="Central America & Caribbean", category="city",
  tags=["unesco", "mogollon", "adobe", "macaw-pens", "water-system"],
  aliases=["Paquime", "Chihuahua", "Mogollon"],
  wikipedia="Casas Grandes", lat=30.3725, lon=-107.9533, height=1500,
  claim="A multi-storey adobe city with piped water, subterranean "
        "reservoirs, macaw breeding pens and T-shaped doorways matching "
        "Chaco Canyon's, built in the middle of a desert and abandoned, is "
        "presented as a planted settlement linking two regions.",
  context="Paquimé is a World Heritage site excavated by Charles Di Peso, "
          "and its Chaco and Mesoamerican connections are the mainstream "
          "interpretation: it was a trading centre between the Puebloan "
          "south-west and West Mexico, moving copper bells, shell and "
          "scarlet macaws north. The macaw pens and the water system are "
          "real engineering by the Casas Grandes culture, with regional "
          "antecedents."),

S("sierra-madre-occidental", "Sierra Madre Occidental",
  subtitle="North-western Mexico", country="Mexico",
  region="Central America & Caribbean", category="region",
  tags=["copper-canyon", "rarámuri", "volcanic", "regional"],
  aliases=["Copper Canyon", "Tarahumara", "Rarámuri", "Barranca del Cobre"],
  wikipedia="Sierra Madre Occidental", lat=25.0000, lon=-106.5000,
  height=900000, precision="area", radius_km=450, pitch=-68,
  claim="The range's cave-dwelling traditions, the Rarámuri's extraordinary "
        "long-distance running, and isolated cliff granaries are presented as "
        "the legacy of a sheltered population.",
  context="The Sierra Madre Occidental is the world's largest ignimbrite "
          "province, and its canyons exceed the Grand Canyon in depth. "
          "Rarámuri running is a well-studied cultural and physiological "
          "adaptation — persistence hunting and rarájipari ball races — not "
          "an anomaly. The cliff structures are Paquimé-related granaries and "
          "dwellings, surveyed and dated."),

S("zona-del-silencio", "Zona del Silencio",
  subtitle="Mapimí, Durango / Chihuahua / Coahuila, Mexico", country="Mexico",
  region="Central America & Caribbean", category="anomaly",
  tags=["mapimi", "meteorites", "athena-missile", "biosphere-reserve"],
  aliases=["Zone of Silence", "Mapimi", "Ceballos", "Bolsón de Mapimí"],
  wikipedia="Mapimí Silent Zone", lat=26.7000, lon=-103.7500, height=120000,
  precision="area", radius_km=60,
  claim="A desert tract said to swallow radio signals, deflect compasses and "
        "attract meteorites, where a US Athena missile went badly off course "
        "in 1970 — presented as a magnetic anomaly or a deliberate landing "
        "corridor.",
  context="The 1970 Athena RTV that overflew from Green River, Utah into "
          "Chihuahua is real and documented, and the recovery operation drew "
          "wide attention — which is where the legend begins. Radio "
          "propagation tests have found no attenuation anomaly, and no "
          "magnetic anomaly appears in Mexican geological surveys. The "
          "region's genuine distinction is the Mapimí Biosphere Reserve and "
          "its endemic desert tortoise. The 1969 Allende meteorite fell "
          "nearby, a well-studied carbonaceous chondrite."),

S("copan", "Copán",
  subtitle="Copán Department, Honduras", country="Honduras",
  region="Central America & Caribbean", category="pyramid",
  tags=["unesco", "maya", "hieroglyphic-stairway", "stelae", "altar-q"],
  aliases=["Honduras", "Hieroglyphic Stairway", "Altar Q", "Yax Pasaj"],
  wikipedia="Copán", lat=14.8400, lon=-89.1419, height=1200,
  claim="Copán's Hieroglyphic Stairway, its dynastic record and the "
        "astronomical content of its stelae are cited for calendrical "
        "precision said to require transmitted knowledge — and the "
        "fire-serpent imagery for arriving craft.",
  context="Copán has one of the most complete dynastic sequences in the Maya "
          "world: Altar Q names sixteen rulers over four centuries, and "
          "Stela A through J record period endings with eclipse and Venus "
          "data. Tunnelling beneath Structure 10L-16 exposed the earlier "
          "Rosalila and Margarita temples intact, giving a stratified "
          "construction history. Its calendrical accuracy comes from "
          "centuries of recorded observation, preserved in the Dresden "
          "Codex's own tables."),

S("quirigua", "Quiriguá",
  subtitle="Izabal, Guatemala", country="Guatemala",
  region="Central America & Caribbean", category="megalithic",
  tags=["unesco", "maya", "stelae", "zoomorphs", "k'ak'-tiliw"],
  aliases=["Guatemala", "Izabal", "Stela E"],
  wikipedia="Quiriguá", lat=15.2694, lon=-89.0406, height=1000,
  claim="Stela E — at over 10 m and about 60 tonnes the tallest "
        "free-standing monument in the Maya world — plus the site's "
        "boulder-carved 'zoomorphs', are presented as beyond local "
        "capability for a minor city.",
  context="Quiriguá's monuments are dated by their own inscriptions to the "
          "reign of K'ak' Tiliw Chan Yopaat (AD 724–785), and the "
          "monumental programme follows directly from his capture and "
          "sacrifice of Copán's ruler in 738 — a political statement "
          "recorded in the texts themselves. The sandstone came from the "
          "nearby Motagua valley, and the river provided transport."),

S("tikal", "Tikal",
  subtitle="Petén, Guatemala", country="Guatemala",
  region="Central America & Caribbean", category="pyramid",
  tags=["unesco", "maya", "temple-i", "lidar", "reservoirs"],
  aliases=["Guatemala", "Peten", "Yax Mutal", "Temple of the Great Jaguar"],
  wikipedia="Tikal", lat=17.2220, lon=-89.6237, height=1800,
  claim="Temples rising 70 m above the rainforest canopy, a city of perhaps "
        "60,000 supported by engineered reservoirs, abandoned and swallowed "
        "by jungle, are presented as evidence of a managed colony and its "
        "sudden recall.",
  context="Tikal is one of the most completely excavated Maya cities, with a "
          "dynastic record spanning AD 90–869 and a documented "
          "interruption following defeat by Caracol in 562. Airborne LiDAR "
          "since 2016 has mapped tens of thousands of surrounding "
          "structures, causeways and defensive works across the Petén, "
          "revolutionising population estimates — a mainstream result that "
          "makes the landscape more intensively human, not less. Its "
          "reservoirs, including filtration using quartz sand and zeolite, "
          "are a genuine water-engineering achievement."),

S("lubaantun", "Lubaantun",
  subtitle="Toledo District, Belize", country="Belize",
  region="Central America & Caribbean", category="artifact",
  tags=["maya", "crystal-skull", "dry-masonry", "mitchell-hedges"],
  aliases=["Belize", "Crystal Skull", "Mitchell-Hedges", "Toledo"],
  wikipedia="Lubaantun", lat=16.2825, lon=-88.9617, height=1200,
  claim="The Mitchell-Hedges crystal skull, said to have been found here by "
        "a teenage Anna Mitchell-Hedges in 1924, is presented as carved from "
        "a single quartz crystal against the grain by methods unavailable to "
        "the Maya — one of thirteen skulls holding stored knowledge.",
  context="Smithsonian and British Museum analyses of this and comparable "
          "skulls found rotary-tool marks — wheel-cut striations "
          "inconsistent with pre-Columbian lapidary technique and "
          "consistent with 19th-century European workshops. F. A. "
          "Mitchell-Hedges did not mention the skull in his 1931 account of "
          "the excavation, and records indicate he bought it at a Sotheby's "
          "sale in 1943. Lubaantun itself is a genuine Late Classic site, "
          "notable for mortarless masonry and the absence of stelae."),

S("haiti", "Port-au-Prince",
  subtitle="Ouest Department, Haiti", country="Haiti",
  region="Central America & Caribbean", category="city",
  tags=["vodou", "taino", "2010-earthquake", "enriquillo-fault"],
  aliases=["Haiti", "Hispaniola", "Vodou", "Taino"],
  wikipedia="Port-au-Prince", lat=18.5944, lon=-72.3074, height=15000,
  claim="Referenced for Vodou's lwa — spirits who mount and speak through "
        "practitioners — read as channelled non-human intelligences, and for "
        "Taíno traditions of beings who came from the sky.",
  context="Vodou is a syncretic religion with West African, Taíno and "
          "Catholic components, studied extensively by anthropologists; "
          "possession trance is a documented, culturally patterned "
          "phenomenon found in religious traditions worldwide. The 2010 "
          "earthquake was a magnitude 7.0 rupture on the Enriquillo–Plantain "
          "Garden fault, a known strike-slip system."),

S("cuba-underwater", "Western Cuba — Offshore Structures",
  subtitle="Guanahacabibes shelf, Pinar del Río, Cuba", country="Cuba",
  region="Central America & Caribbean", category="underwater",
  tags=["sonar", "submerged", "atlantis-claim", "deep-water"],
  aliases=["Cuba", "Cabo San Antonio", "Guanahacabibes", "underwater city"],
  wikipedia="Cuba", lat=21.9000, lon=-84.9500, height=60000,
  precision="approximate",
  claim="Side-scan sonar images collected by Advanced Digital "
        "Communications in 2001 off western Cuba, showing what were "
        "described as pyramids and streets at 600–750 m, were widely "
        "reported as a drowned city — and are presented as Atlantis.",
  context="No follow-up survey, submersible dive or sample has ever "
          "confirmed the structures, and the original imagery has not been "
          "published in a peer-reviewed venue. The depth is the central "
          "problem: no credible sea-level model places that shelf above "
          "water within the span of human occupation of the Americas, so "
          "the features would need to be tens of millions of years old. "
          "Geologists who have commented identify probable natural blocks "
          "from slope failure."),

S("bimini-road", "Bimini Road",
  subtitle="North Bimini, Bahamas", country="Bahamas",
  region="Central America & Caribbean", category="underwater",
  tags=["beachrock", "cayce", "submerged", "atlantis-claim"],
  aliases=["Bahamas", "North Bimini", "Edgar Cayce", "Bimini Wall"],
  wikipedia="Bimini Road", lat=25.7656, lon=-79.2958, height=3000,
  claim="A half-mile line of rectilinear blocks in 5 m of water off North "
        "Bimini, found in 1968 — the year Edgar Cayce had predicted Atlantis "
        "would begin to re-emerge near Bimini — is presented as a paved road "
        "or harbour wall.",
  context="Petrographic and radiocarbon work identifies the blocks as "
          "beachrock: carbonate sand cemented in the intertidal zone, which "
          "fractures into rectangular joints as it is undercut. The "
          "constituent grains and shell fragments run in continuous "
          "stratigraphic order across adjacent blocks, which excludes "
          "quarrying and placement, and the cement dates to roughly "
          "2,000–4,000 years ago. Comparable formations occur throughout the "
          "Bahamas and the Mediterranean."),

# ===========================================================================
# SOUTH AMERICA
# ===========================================================================

S("nazca", "Nazca Lines",
  subtitle="Nazca Desert, Ica Region, Peru", country="Peru",
  region="South America", category="geoglyph",
  tags=["unesco", "geoglyph", "nazca-culture", "aqueducts", "von-daniken"],
  aliases=["Nazca Desert", "Nasca", "Ica", "hummingbird", "runways"],
  wikipedia="Nazca lines", lat=-14.7390, lon=-75.1300, height=9000, pitch=-55,
  precision="area", radius_km=28,
  claim="Erich von Däniken's founding example: hundreds of kilometres of "
        "dead-straight lines and vast figures visible only from altitude, "
        "read as runways and as signals to craft overhead.",
  context="The lines were made by clearing dark oxidised stones to expose "
          "pale ground beneath, a technique replicated in a day with "
          "stakes, cord and a few people; Joe Nickell's team reproduced a "
          "large figure to Nazca accuracy in 1982. Many figures are legible "
          "from surrounding foothills, and the same motifs appear on dated "
          "Nazca pottery and textiles. The accepted readings concern water "
          "and fertility ritual — supported by the Cantalloc aqueducts and "
          "by lines converging on water sources. Hundreds more geoglyphs "
          "have been found since 2019 using AI-assisted survey."),

S("palpa", "Palpa Geoglyphs",
  subtitle="Ica Region, Peru", country="Peru", region="South America",
  category="geoglyph", tags=["geoglyph", "paracas", "hillside-figures"],
  aliases=["Ica", "Palpa lines"],
  wikipedia="Palpa Province", lat=-14.5397, lon=-75.1861, height=12000,
  precision="area", radius_km=14,
  claim="The Palpa figures — older than Nazca's, cut into hillsides and "
        "including humanoid forms with large heads — are presented as the "
        "earlier, more explicit phase of the same signalling programme.",
  context="Palpa's geoglyphs are attributed to the Paracas culture, roughly "
          "400–200 BC, predating the Nazca lines by centuries. Their "
          "hillside placement makes them visible from the ground, which is "
          "the central interpretive point: they were meant to be seen by "
          "people on nearby paths. German–Peruvian survey since the 1990s "
          "has mapped and dated them systematically."),

S("cahuachi", "Cahuachi",
  subtitle="Nazca, Ica Region, Peru", country="Peru", region="South America",
  category="pyramid", tags=["nazca-culture", "ceremonial-centre", "adobe"],
  aliases=["Nazca", "Great Pyramid of Cahuachi"],
  wikipedia="Cahuachi", lat=-14.8167, lon=-75.1167, height=4000,
  claim="A 24 km² ceremonial centre beside the Nazca lines, with mounds of "
        "adobe and little residential evidence, is presented as a staging "
        "ground for the geoglyph programme rather than a city.",
  context="Giuseppe Orefici's long-running excavations identify Cahuachi "
          "exactly as a pilgrimage centre with low permanent population — "
          "that is the mainstream finding, and it fits the Nazca lines "
          "as ritual landscape. The mounds are modified natural hills "
          "faced with adobe. Textiles, musical instruments and trophy "
          "heads recovered there tie it directly to Nazca material "
          "culture."),

S("caral", "Caral-Supe",
  subtitle="Barranca Province, Lima Region, Peru", country="Peru",
  region="South America", category="city",
  tags=["unesco", "oldest-city-americas", "quipu", "preceramic"],
  aliases=["Caral", "Supe Valley", "Norte Chico"],
  wikipedia="Caral", lat=-10.8917, lon=-77.5208, height=2000,
  claim="A city with sunken plazas and six pyramids, contemporary with the "
        "Egyptian Old Kingdom and with no evidence of warfare or defensive "
        "works, is presented as a planted settlement peacefully administered "
        "from outside.",
  context="Caral is genuinely one of the oldest urban centres in the "
          "Americas (c. 2600 BC) and its excavation by Ruth Shady "
          "transformed Andean prehistory. Its subsistence base — anchovy "
          "and sardine from the coast exchanged for cotton and squash — is "
          "documented in midden analysis, and the Norte Chico region holds "
          "around twenty contemporary sites showing regional development. "
          "The absence of fortification is a real and interesting finding "
          "about early Andean society."),

S("paracas", "Paracas",
  subtitle="Ica Region, Peru", country="Peru", region="South America",
  category="artifact", tags=["paracas-skulls", "candelabra", "textiles",
                             "cranial-modification"],
  aliases=["Paracas skulls", "Paracas Candelabra", "Ica", "elongated skulls"],
  wikipedia="Paracas culture", lat=-13.8400, lon=-76.2500, height=12000,
  claim="The elongated Paracas skulls — with reported cranial volumes up to "
        "25% greater than normal, fewer sutures and claimed anomalous DNA "
        "results — are the series' leading physical-evidence claim, alongside "
        "the 180 m Candelabra geoglyph on the bay's cliff.",
  context="Artificial cranial modification by binding infants' heads is "
          "documented worldwide — in Peru, Mesoamerica, the Caucasus, "
          "France and Melanesia — and reshapes without increasing volume. "
          "Published measurements on the Paracas series fall within human "
          "range. The 'anomalous DNA' claims come from unpublished "
          "commercial sequencing with no peer review, no chain of custody "
          "and contamination patterns typical of degraded ancient samples; "
          "the 2014 announcement's lab has never released data. Paracas "
          "textiles are, separately, among the finest in the ancient world."),

S("machu-picchu", "Machu Picchu — Temple of the Three Windows",
  subtitle="Cusco Region, Peru", country="Peru", region="South America",
  category="city", tags=["unesco", "inca", "ashlar", "intihuatana",
                         "archaeoastronomy"],
  aliases=["Peru", "Inca", "Temple of Three Windows", "Intihuatana",
           "Cusco"],
  wikipedia="Machu Picchu", lat=-13.1631, lon=-72.5450, height=1500, pitch=-25,
  claim="Mortarless ashlar fitted so tightly a blade will not enter, on a "
        "2,430 m ridge between fault lines, with solstice-aligned windows "
        "and the Intihuatana stone, is presented as impossible without "
        "stone-softening or cutting technology.",
  context="Machu Picchu is a 15th-century royal estate of Pachacuti, "
          "identified in Spanish colonial land documents. Inca masonry "
          "technique is directly observable: unfinished walls, abandoned "
          "blocks with pounding scars, hammerstones and the quarry inside "
          "the site itself all survive. Blocks were shaped by repeated "
          "percussion and fitted by trial, which is slow but needs no "
          "exotic method; the dry joints and trapezoidal openings are "
          "deliberate seismic design that has held through five centuries "
          "of earthquakes."),

S("ollantaytambo", "Ollantaytambo",
  subtitle="Sacred Valley, Cusco Region, Peru", country="Peru",
  region="South America", category="megalithic",
  tags=["inca", "sacred-valley", "monoliths", "quarry", "terraces"],
  aliases=["Sacred Valley", "Temple of the Sun", "Wall of Six Monoliths",
           "Cachicata"],
  wikipedia="Ollantaytambo", lat=-13.2583, lon=-72.2639, height=1500,
  claim="The Wall of Six Monoliths — porphyry blocks of up to 70 tonnes "
        "quarried across the valley and 900 m above, then raised onto a "
        "terrace — with thin stone shims between them, is presented as "
        "machined work.",
  context="The Cachicata quarries are visible across the Urubamba and the "
          "whole logistics chain is preserved in place: dozens of abandoned "
          "blocks lie along the hauling ramps, with slide tracks, "
          "retaining works and the river crossing still traceable. "
          "Protzen's field experiments reproduced Inca dressing and "
          "fitting with hammerstones, and the shims are a documented Inca "
          "levelling technique. The site was unfinished when the Spanish "
          "arrived, which is why the method is so legible."),

S("sacsayhuaman", "Cusco & Sacsayhuamán",
  subtitle="Cusco Region, Peru", country="Peru", region="South America",
  category="megalithic", tags=["unesco", "inca", "cyclopean", "puma-shape",
                               "zigzag-walls"],
  aliases=["Saqsaywaman", "Cuzco", "Sacsayhuaman", "Qorikancha", "Cusco"],
  wikipedia="Sacsayhuamán", lat=-13.5097, lon=-71.9819, height=1200,
  claim="Andesite blocks estimated up to 125 tonnes, cut with convex and "
        "concave faces that interlock in three dimensions with no mortar and "
        "no gaps, are the series' primary Andean exhibit for stone-softening "
        "or directed-energy cutting.",
  context="The quarries at Rumiqolqa and Waqoto are identified and the "
          "hauling roads mapped; abandoned blocks lie along them with "
          "pounding marks and attachment nubs intact. Spanish chroniclers "
          "including Cieza de León and Garcilaso described the construction "
          "from eyewitness testimony, naming the labour rotations "
          "(mit'a) involved. Protzen demonstrated that the complex "
          "polygonal fit is produced by iterative pounding and test-fitting, "
          "which leaves exactly the dimpled surfaces observed."),

S("coricancha", "Coricancha & Lake Puray",
  subtitle="Cusco Region, Peru", country="Peru", region="South America",
  category="pyramid", geometry="multipoint",
  points=[(-13.5201, -71.9751), (-13.4100, -72.0300)],
  tags=["inca", "temple-of-the-sun", "gold", "ceque-system"],
  aliases=["Qorikancha", "Temple of the Sun", "Lake Puray", "Cusco",
           "Santo Domingo"],
  wikipedia="Coricancha", lat=-13.5201, lon=-71.9751, height=1200,
  claim="The Temple of the Sun, whose walls were sheathed in gold and whose "
        "garden held life-sized gold maize and llamas, is presented as the "
        "repository of off-world metalworking — and the forty-one ceque "
        "sightlines radiating from it as a surveyed grid.",
  context="Coricancha's Inca walls survive beneath the Dominican convent "
          "built over them, and the gold's fate is documented: it was "
          "stripped for Atahualpa's ransom and melted, recorded in Spanish "
          "accounts with weights. The ceque system was reconstructed by "
          "Bernabé Cobo and analysed by Tom Zuidema and Brian Bauer — a "
          "genuine radial organisation of shrines, calendar and kin groups, "
          "and a major achievement of Andean spatial thought."),

S("x-zone-cusco", "X-Zone, Sacsayhuamán",
  subtitle="Cusco Region, Peru", country="Peru", region="South America",
  category="megalithic", precision="approximate",
  tags=["inca", "carved-bedrock", "huaca", "unresolved-reference"],
  aliases=["Zona X", "Qenqo", "Chinkana", "Cusco"],
  wikipedia="Sacsayhuamán", lat=-13.5060, lon=-71.9760, height=900,
  claim="An area of carved bedrock near Sacsayhuamán — stepped platforms, "
        "channels, seats and tunnels cut directly into living rock, with no "
        "clear function — is presented as melted or machined stone.",
  context="The carved outcrops around Cusco are huacas: sacred stones "
          "modified as ritual architecture, documented across the Inca "
          "heartland at Qenqo, Chinkana, Lacco and Kusilluchayoq, and "
          "integrated into the ceque system. The forms are chiselled and "
          "ground from andesite and limestone; tool marks are visible at "
          "close range, and unfinished examples show the stages. The "
          "'X-Zone' is a tour name rather than an archaeological "
          "designation."),

S("lake-titicaca", "Lake Titicaca",
  subtitle="Peru / Bolivia border", country="Peru / Bolivia",
  region="South America", category="landform",
  tags=["viracocha", "high-altitude", "submerged-ruins", "uros"],
  aliases=["Titicaca", "Viracocha", "Isla del Sol", "Khoa Reef"],
  wikipedia="Lake Titicaca", lat=-15.7500, lon=-69.4000, height=120000,
  precision="area", radius_km=90,
  claim="Andean tradition places Viracocha's emergence here, and submerged "
        "structures on the lake floor plus marine fossils at 3,812 m are "
        "presented as evidence of a drowned civilisation and a catastrophic "
        "uplift.",
  context="Submerged remains are real and excavated: the Khoa Reef offerings "
          "near Isla del Sol were documented by underwater archaeologists in "
          "2013–19, and Tiwanaku-period structures lie in shallow water — "
          "products of lake-level fluctuation, which palaeoclimate cores "
          "track in detail. The marine fossils are Cretaceous, uplifted over "
          "tens of millions of years by Andean orogeny at a few millimetres "
          "a year — a rate measured directly by GPS geodesy."),

S("hayu-marca", "Puerta de Hayu Marca",
  subtitle="Near Puno, Peru", country="Peru", region="South America",
  category="megalithic", tags=["gate-of-the-gods", "rock-face", "aramu-muru"],
  aliases=["Gate of the Gods", "Aramu Muru", "Hayumarca", "Puno"],
  wikipedia="", lat=-15.9500, lon=-69.6500, height=2000,
  precision="approximate",
  claim="A 7 m T-shaped recess cut into a rock face near Lake Titicaca, with "
        "a smaller niche at its base, is presented as a sealed doorway — a "
        "portal through which a priest named Aramu Muru is said to have "
        "departed with a golden disc.",
  context="The feature is a partly worked natural rock face in a region of "
          "heavily jointed sandstone; the recess is shallow, with no "
          "chamber, threshold or fittings behind it, and comparable "
          "false-door niches are a recognised Andean form found at Tiwanaku "
          "and in Inca huacas. The Aramu Muru story appears in New Age "
          "literature from the 1990s and not in colonial or earlier Andean "
          "sources."),

S("puma-punku", "Pumapunku & Tiwanaku",
  subtitle="La Paz Department, Bolivia", country="Bolivia",
  region="South America", category="megalithic",
  tags=["unesco", "tiwanaku", "h-blocks", "andesite", "gateway-of-the-sun"],
  aliases=["Puma Punku", "Tiahuanaco", "Tiwanaku", "H-blocks",
           "Gate of the Sun", "La Paz"],
  wikipedia="Pumapunku", lat=-16.5617, lon=-68.6797, height=900,
  claim="The H-blocks of Pumapunku — andesite cut to interchangeable "
        "profiles with flat faces, sharp interior angles and drilled "
        "channels — plus 130-tonne sandstone slabs, are presented as "
        "machine-made to a standard template, with Arthur Posnansky's "
        "archaeoastronomical dating pushing the site to 15,000 BC.",
  context="Tiwanaku is radiocarbon-dated to roughly AD 500–1000, not 15,000 "
          "BC; Posnansky's figure came from assuming the obliquity of the "
          "ecliptic at construction and has been superseded by direct "
          "dating. Sandstone came from Kimsachata 10 km south and andesite "
          "from the Copacabana peninsula across the lake, both identified "
          "petrologically. Jean-Pierre Protzen and Stella Nair showed the "
          "interchangeable profiles were produced from templates by "
          "percussion and grinding — modular prefabrication, which is a real "
          "and impressive engineering choice. Unfinished blocks on site "
          "preserve the stages.",
  links=[{"label": "UNESCO — Tiwanaku World Heritage listing",
          "url": "https://whc.unesco.org/en/list/567/", "kind": "reference"}]),

S("paititi", "Paititi Region",
  subtitle="South-eastern Andes–Amazon, Peru", country="Peru",
  region="South America", category="region", precision="area",
  tags=["legend", "lost-city", "cloud-forest", "lidar"],
  aliases=["Paititi", "lost city", "El Dorado", "Pantiacolla"],
  wikipedia="Paititi", lat=-12.9000, lon=-71.5000, height=250000,
  radius_km=150, pitch=-60,
  claim="A lost Inca city of gold in the cloud forest east of Cusco, sought "
        "for four centuries and never found, is presented as a site "
        "deliberately concealed — or as still occupied.",
  context="Paititi is a composite legend rooted in genuine Inca retreat "
          "into the Antisuyu after 1532 and in colonial-era gold fever. The "
          "region does hold real undocumented archaeology: Espíritu Pampa "
          "(Vilcabamba) was identified as the last Inca capital, and "
          "airborne LiDAR has since revealed extensive pre-Columbian "
          "settlement under Amazonian canopy at Llanos de Mojos and "
          "Upano. The terrain's difficulty, not concealment, explains the "
          "gaps."),

S("peru-general", "Peru",
  subtitle="Republic of Peru (regional)", country="Peru",
  region="South America", category="region",
  tags=["regional", "inca", "andes", "chronology"],
  aliases=["Inca Empire", "Tawantinsuyu", "Andes"],
  wikipedia="Peru", lat=-9.1900, lon=-75.0152, height=2000000,
  precision="area", radius_km=800, pitch=-72,
  claim="Peru is the series' densest cluster after Egypt: Nazca, "
        "Sacsayhuamán, Ollantaytambo, Paracas and Machu Picchu are "
        "presented together as one engineering programme spanning "
        "millennia.",
  context="Andean archaeology provides a continuous 5,000-year sequence — "
          "Caral, Chavín, Paracas, Nazca, Moche, Wari, Tiwanaku, Chimú, "
          "Inca — in which masonry, metallurgy, textiles and hydraulics "
          "develop traceably, each culture building on the last. The Inca "
          "state itself lasted under a century at full extent, which is why "
          "so many of its sites were unfinished and their methods are "
          "legible."),

S("colombia", "Colombia",
  subtitle="Republic of Colombia (regional)", country="Colombia",
  region="South America", category="region",
  tags=["regional", "muisca", "gold", "san-agustin"],
  aliases=["Muisca", "El Dorado", "San Agustín", "Ciudad Perdida"],
  wikipedia="Colombia", lat=4.5709, lon=-74.2973, height=1500000,
  precision="area", radius_km=600, pitch=-70,
  claim="Muisca goldwork — including the tunjo figurines and the "
        "so-called 'Gold Flyer' models that some claim resemble delta-winged "
        "aircraft — is presented as scale modelling of observed craft.",
  context="The Quimbaya and Muisca figurines are catalogued votive objects, "
          "and zoologists identify the 'aircraft' forms as stylised fish, "
          "insects, bats and flying reptiles — motifs that recur across the "
          "same assemblages in unambiguous versions. Colombian goldwork "
          "used lost-wax casting and depletion gilding, techniques "
          "documented in excavated workshops. San Agustín's monumental "
          "statuary and Ciudad Perdida are the region's major "
          "archaeological complexes."),

S("lake-guatavita", "Lake Guatavita",
  subtitle="Cundinamarca, Colombia", country="Colombia",
  region="South America", category="sacred",
  tags=["muisca", "el-dorado", "offerings", "crater-lake"],
  aliases=["Guatavita", "El Dorado", "Guanavita", "Cundinamarca"],
  wikipedia="Lake Guatavita", lat=4.9767, lon=-73.7739, height=4000,
  claim="The ritual lake behind the El Dorado legend — where a gilded Muisca "
        "chief was rafted out to cast gold into the water — is presented as "
        "a deposit site for offerings to beings who arrived there.",
  context="Muisca lake offerings are archaeologically confirmed; the "
          "Muisca raft in Bogotá's Gold Museum, recovered from a cave near "
          "Pasca, depicts the ceremony directly. Spanish drainage attempts "
          "from 1562 onward, including Antonio de Sepúlveda's partial cut "
          "of the rim, recovered gold and are documented in colonial "
          "records. The lake is a volcanic or impact-related depression, "
          "now a protected site where diving is prohibited."),

S("magdalena-river", "Magdalena River",
  subtitle="Colombia", country="Colombia", region="South America",
  category="landform", tags=["river", "fossils", "navigation"],
  aliases=["Rio Magdalena", "Colombia"],
  wikipedia="Magdalena River", lat=7.0000, lon=-74.7000, height=600000,
  precision="area", radius_km=300, pitch=-65,
  claim="Referenced as the artery into Colombia's interior used by "
        "treasure-seeking expeditions, and for fossil finds along its "
        "course cited as out-of-place remains.",
  context="The Magdalena is Colombia's principal river and the main "
          "colonial route inland. Its basin is genuinely important "
          "palaeontologically — the La Venta fauna of the Honda Group is a "
          "world-class Miocene vertebrate assemblage, and Villa de Leyva's "
          "Cretaceous marine reptiles are a major Colombian heritage site. "
          "These are dated, catalogued and published, with nothing "
          "out of sequence."),

S("brazil-mica", "Minas Gerais — Mica Districts",
  subtitle="Brazil", country="Brazil", region="South America",
  category="artifact", precision="area",
  tags=["mica", "pegmatite", "trade", "teotihuacan-link"],
  aliases=["Brazil", "mica", "Minas Gerais", "pegmatite"],
  wikipedia="Minas Gerais", lat=-18.5000, lon=-44.0000, height=900000,
  radius_km=400, pitch=-68,
  claim="Mica sheets found at Teotihuacan are said to have been sourced "
        "3,000 miles away in Brazil, implying intercontinental transport "
        "beyond any known ancient capability.",
  context="The Brazil attribution traces to a 1950s-era trace-element claim "
          "that has not been replicated, and Mexico has its own substantial "
          "mica-bearing pegmatites in Oaxaca, Hidalgo and Jalisco. "
          "Mesoamerican long-distance exchange is real but regional, and "
          "well mapped by obsidian and jade sourcing. Minas Gerais is "
          "genuinely one of the world's great pegmatite provinces — which "
          "is why it was the modern industrial source and so the one that "
          "came to mind."),

S("atacama-giant", "Atacama Giant, Cerro Unitas",
  subtitle="Tarapacá Region, Chile", country="Chile", region="South America",
  category="geoglyph", tags=["geoglyph", "atacama", "archaeoastronomy",
                             "largest-anthropomorph"],
  aliases=["Gigante de Atacama", "Cerro Unitas", "Atacama Desert", "Tarapacá"],
  wikipedia="Atacama Giant", lat=-19.9475, lon=-69.6333, height=4000,
  claim="A 119 m anthropomorphic figure on a desert hillside — the largest "
        "prehistoric human figure on Earth, with a rayed headdress and "
        "rectangular body — is presented as a portrait of a visitor in a "
        "suit and helmet.",
  context="The figure is attributed to Andean cultures of roughly AD "
          "1000–1400 and sits among more than 5,000 geoglyphs along the "
          "Atacama's caravan routes, many depicting llamas, llama trains and "
          "human figures. It is read as a deity or lunar calendar marker: "
          "the headdress rays align with the moon's position at different "
          "seasons, giving caravan travellers a reference. The desert's "
          "hyperaridity is why the whole corpus survives."),

S("el-enladrillado", "El Enladrillado",
  subtitle="Altos de Lircay, Maule Region, Chile", country="Chile",
  region="South America", category="megalithic", precision="approximate",
  tags=["basalt", "plateau", "ufo-hotspot", "columnar-jointing"],
  aliases=["Altos de Vilches", "Altos de Lircay", "Maule", "Vilches"],
  wikipedia="Altos de Lircay National Reserve", lat=-35.4667, lon=-70.9500,
  height=6000,
  claim="A high Andean plateau paved with hundreds of flat basalt slabs in "
        "apparent rows, locally reputed as a landing field with a frequent "
        "sighting record, is presented as an engineered platform at 2,200 m.",
  context="The slabs are columnar basalt: lava cooling into polygonal "
          "columns that weather and spall into flat-topped pavement — the "
          "same process that makes the Giant's Causeway and Devils "
          "Postpile. The arrangement follows the flow's cooling joints. No "
          "archaeological survey has reported tool marks, quarrying or "
          "cultural deposits. The area is a Chilean national reserve."),

S("antofagasta-concepcion", "Antofagasta & Concepción",
  subtitle="Chile", country="Chile", region="South America", category="ufo",
  geometry="multipoint", points=[(-23.6509, -70.3975), (-36.8270, -73.0498)],
  tags=["sighting", "cefaa", "chile"],
  aliases=["Chile", "Antofagasta", "Concepcion", "CEFAA"],
  wikipedia="Antofagasta", lat=-30.2390, lon=-71.7236, height=900000,
  precision="area", radius_km=700,
  claim="Chilean cases from these two cities feature in the series as "
        "state-investigated encounters, including naval and air-force "
        "reports handled by CEFAA, Chile's official aerial-phenomena "
        "committee.",
  context="CEFAA is genuine — a civil aviation authority body, one of very "
          "few worldwide — and it publishes conclusions. Its most "
          "publicised case, the 2014 Chilean Navy helicopter infrared "
          "footage released in 2017, was independently analysed and "
          "identified as an airliner's contrail lit by low sun, with the "
          "flight matched by schedule and transponder data. CEFAA has "
          "since acknowledged that explanation.",
  links=[{"label": "DGAC Chile — CEFAA",
          "url": "https://www.dgac.gob.cl/", "kind": "official"}]),

S("tierra-del-fuego", "Tierra del Fuego — Selk'nam Territory",
  subtitle="Chile & Argentina", country="Chile / Argentina",
  region="South America", category="sacred",
  tags=["selknam", "hain", "body-paint", "ethnography"],
  aliases=["Selk'nam", "Ona", "Hain", "Patagonia", "Fuegians"],
  wikipedia="Selk'nam people", lat=-54.0000, lon=-68.5000, height=400000,
  precision="area", radius_km=200, pitch=-65,
  claim="Martin Gusinde's 1920s photographs of the Selk'nam Hain "
        "initiation — figures in conical masks and striped full-body paint — "
        "are among the series' most striking images, presented as depictions "
        "of visitors.",
  context="The photographs are real and are an irreplaceable ethnographic "
          "record, taken with the participation of Selk'nam elders who "
          "explained the ceremony to Gusinde. The figures are named spirits "
          "of the Hain, each with a role in a documented initiation drama; "
          "the designs are recorded in the ethnography by name and meaning. "
          "The Selk'nam were subjected to genocide during the Patagonian "
          "sheep expansion, and the photographs date from the final years "
          "of the practice. Selk'nam descendants have recently won formal "
          "recognition in Chile."),

S("galapagos-vents", "Galápagos Rift — Hydrothermal Vents",
  subtitle="Eastern Pacific, Ecuador", country="Ecuador",
  region="South America", category="underwater",
  tags=["hydrothermal", "chemosynthesis", "abiogenesis", "alvin"],
  aliases=["Galapagos", "Rose Garden", "black smokers", "Alvin"],
  wikipedia="Hydrothermal vent", lat=0.7833, lon=-86.1333, height=150000,
  precision="approximate",
  claim="The 1977 discovery of chemosynthetic ecosystems at the Galápagos "
        "Rift — life thriving in darkness at 400 °C without sunlight — is "
        "used to argue that life's origin requires explanation beyond "
        "Earth, and so arrived from elsewhere.",
  context="The discovery by Alvin's crew is one of the most significant in "
          "20th-century biology, and it cuts the other way: vents supply "
          "exactly the chemical disequilibrium, mineral catalysts and "
          "temperature gradients that leading abiogenesis models require, "
          "and alkaline hydrothermal systems are now a mainstream candidate "
          "for life's origin on this planet. They are also the primary "
          "analogue for Europa and Enceladus."),


# ===========================================================================
# ADDENDA — remaining list entries
# ===========================================================================

S("ramesseum", "Ramesseum, Thebes",
  subtitle="Luxor Governorate, Egypt", country="Egypt", region="Africa",
  category="pyramid", tags=["unesco", "new-kingdom", "colossus", "ozymandias"],
  aliases=["Thebes", "Ramesses II", "Ozymandias", "Memnon", "Luxor"],
  wikipedia="Ramesseum", lat=25.7280, lon=32.6103, height=900,
  claim="The shattered 1,000-tonne colossus of Ramesses II — a single block "
        "of Aswan granite quarried 200 km upriver and carved to a polish — "
        "is presented as beyond any plausible Bronze Age lifting or finishing "
        "capability.",
  context="The seated colossus is carved from one block, and the quarry at "
          "Aswan preserves the extraction process: the Unfinished Obelisk "
          "lies there still attached to bedrock, with trenching, wedge slots "
          "and dolerite pounding marks visible along its whole length. "
          "River transport on purpose-built barges at inundation is "
          "attested in reliefs at Deir el-Bahari and in the Hatshepsut "
          "obelisk scenes. The Ramesseum's own inscriptions and the Papyrus "
          "of the Ramesseum date and attribute the complex."),

S("cave-of-tayos", "Cueva de los Tayos",
  subtitle="Morona-Santiago, Ecuador", country="Ecuador",
  region="South America", category="underground",
  tags=["karst", "shuar", "metal-library", "1976-expedition"],
  aliases=["Cave of Tayos", "Tayos", "Metal Library", "Juan Moricz",
           "Andes", "Ecuador"],
  wikipedia="Cueva de los Tayos", lat=-3.0521, lon=-78.2054, height=4000,
  claim="Juan Moricz claimed in 1969 to have found a 'metal library' of "
        "engraved plates deep inside this Shuar-held cave system, with "
        "worked passages and gold artefacts; the 1976 British–Ecuadorian "
        "expedition that followed — with Neil Armstrong as honorary "
        "president — is cited as proof that the claim was taken seriously at "
        "the highest level.",
  context="The 1976 expedition was real, large and well publicised, and it "
          "found no library, no metal plates and no worked chambers — its "
          "genuine results were zoological and speleological, plus a "
          "burial of ordinary archaeological interest. Moricz never "
          "produced the plates or showed anyone the chamber, and the "
          "passages are limestone karst shaped by water. The cave is "
          "sacred to the Shuar, who harvest oilbird (tayos) chicks there, "
          "and access is at their discretion."),

# ===========================================================================
# ANTARCTICA & SOUTHERN OCEAN
# ===========================================================================

S("antarctica-victoria-land", "Victoria Land & the Oates Coast",
  subtitle="East Antarctica", country="Antarctica (Antarctic Treaty)",
  region="Antarctica & Southern Ocean", category="region",
  tags=["dry-valleys", "transantarctic", "piri-reis", "regional"],
  aliases=["Oates Coast", "Victoria Land", "Shackleton Range",
           "Transantarctic Mountains", "Piri Reis map"],
  wikipedia="Victoria Land", lat=-72.0000, lon=160.0000, height=2000000,
  precision="area", radius_km=800, pitch=-72,
  claim="The 1513 Piri Reis map, said to show an ice-free Antarctic "
        "coastline, plus satellite images read as pyramids in the "
        "Transantarctic ranges, are presented as evidence of a civilisation "
        "beneath the ice and of a deliberately restricted continent.",
  context="The Piri Reis map's southern landmass is a conventional "
          "cartographic Terra Australis, and the coastline does not match "
          "Antarctica's subglacial topography as mapped by BEDMAP radar; "
          "Charles Hapgood's correlation required substantial "
          "reprojection. Antarctica has been ice-covered for roughly 34 "
          "million years. The 'pyramids' are nunataks — glacially carved "
          "horns, the same form as the Matterhorn, common throughout the "
          "range. Access is restricted by the Antarctic Treaty's "
          "environmental protocols and by logistics, not secrecy."),

S("mcmurdo-station", "McMurdo Station, Ross Island",
  subtitle="Ross Dependency, Antarctica", country="Antarctica (United States)",
  region="Antarctica & Southern Ocean", category="research",
  tags=["usap", "logistics", "ross-island", "neutrino"],
  aliases=["Ross Island", "USAP", "Operation Deep Freeze"],
  wikipedia="McMurdo Station", lat=-77.8419, lon=166.6863, height=12000,
  claim="The scale of the US Antarctic Program — an airfield, a former "
        "nuclear reactor, continuous military airlift and high-profile "
        "visitors — is presented as cover for work at a site under the ice.",
  context="McMurdo is the logistics hub for US Antarctic science, and its "
          "operations are published in annual USAP reports with open "
          "science plans. The PM-3A reactor operated 1962–72 and was "
          "removed; its decommissioning is documented. The research it "
          "supports is likewise public: the IceCube neutrino observatory at "
          "the Pole, ice-core palaeoclimate programmes, and the Antarctic "
          "meteorite collection that yielded the Martian meteorite ALH84001.",
  links=[{"label": "US Antarctic Program", "url": "https://www.usap.gov/",
          "kind": "official"}]),

S("davis-station", "Davis Station",
  subtitle="Princess Elizabeth Land, East Antarctica",
  country="Antarctica (Australia)", region="Antarctica & Southern Ocean",
  category="research", tags=["aad", "vestfold-hills", "oasis"],
  aliases=["Vestfold Hills", "Australian Antarctic Division", "East Antarctica"],
  wikipedia="Davis Station", lat=-68.5764, lon=77.9689, height=15000,
  claim="Australia's station in the ice-free Vestfold Hills — an "
        "'Antarctic oasis' with saline lakes — is cited among the "
        "continent's anomalous zones and as a site of restricted activity.",
  context="The Vestfold Hills are a genuine ice-free oasis of about 400 km², "
          "exposed because local topography diverts the ice sheet, and the "
          "hypersaline Deep Lake is among the coldest liquid water on Earth "
          "at around −20 °C. It is a major astrobiological analogue site, "
          "and the halophilic archaea living in it are published. The "
          "Australian Antarctic Division's programme and station logs are "
          "public."),

S("mount-erebus", "Mount Erebus",
  subtitle="Ross Island, Antarctica", country="Antarctica (Antarctic Treaty)",
  region="Antarctica & Southern Ocean", category="landform",
  tags=["volcano", "lava-lake", "anorthoclase", "flight-901"],
  aliases=["Erebus", "Ross Island", "lava lake"],
  wikipedia="Mount Erebus", lat=-77.5297, lon=167.1533, height=20000,
  claim="The southernmost active volcano, with a persistent lava lake and a "
        "long association with the 1979 Air New Zealand Flight 901 "
        "disaster, is presented as a vent or power source for a facility "
        "beneath the ice.",
  context="Erebus has hosted a convecting phonolite lava lake since at least "
          "1972 and is continuously monitored by the Mount Erebus Volcano "
          "Observatory; it is one of very few volcanoes worldwide with a "
          "long-lived lake, which is its actual scientific importance, along "
          "with the large anorthoclase crystals it ejects. Flight 901 "
          "killed 257 people and was investigated twice: the Mahon Royal "
          "Commission attributed it to an altered flight plan and the "
          "whiteout 'sector whiteout' illusion, not pilot error."),

S("south-georgia", "South Georgia Island",
  subtitle="South Atlantic (sub-Antarctic)",
  country="South Georgia & the South Sandwich Islands",
  region="Antarctica & Southern Ocean", category="landform",
  tags=["sub-antarctic", "shackleton", "whaling", "endurance"],
  aliases=["Grytviken", "Shackleton", "South Atlantic"],
  wikipedia="South Georgia Island", lat=-54.4296, lon=-36.5879, height=120000,
  claim="Referenced in the series' Antarctic material as an outpost on the "
        "approach to the continent, tied to Shackleton's survival crossing "
        "and his reported sense of an unseen fourth presence.",
  context="South Georgia is sub-Antarctic rather than Antarctic — about "
          "1,400 km from the Antarctic Peninsula — and the distinction "
          "matters for its biology, which is dominated by seabird and seal "
          "colonies rather than polar desert. Shackleton's 1916 crossing "
          "is documented in his own account, and the 'third man factor' he "
          "described is a well-studied phenomenon of extreme exertion, "
          "isolation and hypoxia, reported by mountaineers and solo "
          "sailors."),

# ===========================================================================
# OCEANS & MARINE
# ===========================================================================

S("bermuda-triangle", "Bermuda Triangle",
  subtitle="Western North Atlantic", country="",
  region="Oceans & Marine", category="anomaly",
  tags=["flight-19", "gulf-stream", "methane-hydrate", "marine"],
  aliases=["Devil's Triangle", "Flight 19", "USS Cyclops", "Atlantic"],
  wikipedia="Bermuda Triangle", lat=25.0000, lon=-71.0000, height=1800000,
  precision="area", radius_km=800, pitch=-72,
  claim="A tract between Miami, Bermuda and Puerto Rico where ships and "
        "aircraft are said to vanish without trace — Flight 19 in 1945, the "
        "USS Cyclops in 1918 — is presented as the site of a submerged "
        "Atlantean power source or a recurring extraction point.",
  context="Lloyd's of London and the US Coast Guard have both stated the "
          "area shows no elevated loss rate, and marine insurers charge no "
          "premium for it — a straightforward actuarial test the claim "
          "fails. It is also one of the busiest stretches of ocean, crossed "
          "by the Gulf Stream, prone to rapid tropical development and to "
          "sudden squalls. Flight 19's loss is attributable to the flight "
          "leader's compass failure and disorientation over featureless "
          "water, documented in the Navy's own board of inquiry."),

S("dragons-triangle", "Dragon's Triangle",
  subtitle="Philippine Sea, south of Japan", country="",
  region="Oceans & Marine", category="anomaly",
  tags=["devils-sea", "seamounts", "submarine-volcanism", "marine"],
  aliases=["Devil's Sea", "Ma-no Umi", "Pacific", "Miyake"],
  wikipedia="Dragon's Triangle", lat=25.0000, lon=135.0000, height=1500000,
  precision="area", radius_km=700, pitch=-72,
  claim="A Pacific counterpart to the Bermuda Triangle, where Japanese "
        "vessels are said to disappear and where the government reportedly "
        "declared a danger zone after losing survey ships in the 1950s.",
  context="The single documented loss is the research vessel Kaiyō Maru No. 5 "
          "in 1952, which sank investigating the eruption of Myōjin-shō — a "
          "submarine volcano that was actively erupting, a fully "
          "sufficient cause. Japanese authorities have stated no "
          "danger-zone declaration of the kind described was made. The area "
          "is genuinely hazardous: it sits on the Izu–Bonin volcanic arc "
          "with frequent seamount eruptions and typhoon tracks."),

S("mediterranean-sea", "Mediterranean Sea",
  subtitle="Between Europe, Africa & Asia", country="",
  region="Oceans & Marine", category="region",
  tags=["messinian", "maritime", "shipwrecks", "marine"],
  aliases=["Mediterranean", "Mare Nostrum", "Zanclean flood"],
  wikipedia="Mediterranean Sea", lat=35.0000, lon=18.0000, height=2500000,
  precision="area", radius_km=1200, pitch=-74,
  claim="The sea is treated as the corridor along which transmitted "
        "knowledge moved between Egypt, the Levant, Greece and Iberia — and "
        "as the floor beneath which drowned cities, Atlantis among them, "
        "remain.",
  context="Mediterranean maritime exchange is among the best-evidenced "
          "subjects in archaeology, reconstructed from several thousand "
          "catalogued wrecks — Uluburun, Cape Gelidonya, Antikythera — whose "
          "cargoes map trade routes directly. Genuine submerged settlements "
          "exist and are excavated: Pavlopetri, Atlit-Yam and parts of "
          "Alexandria, all drowned by ordinary subsidence and sea-level "
          "change and all of known date. The basin did dry out in the "
          "Messinian, 5.9–5.3 million years ago, long before hominins."),

S("english-channel", "English Channel",
  subtitle="Between England & France", country="",
  region="Oceans & Marine", category="region",
  tags=["doggerland", "foo-fighters", "wwii", "marine"],
  aliases=["La Manche", "Doggerland", "Channel"],
  wikipedia="English Channel", lat=50.2000, lon=-0.5000, height=600000,
  precision="area", radius_km=200, pitch=-68,
  claim="Wartime 'foo fighter' reports by Allied aircrew over the Channel "
        "and north-west Europe, and the submerged prehistoric landscape "
        "beneath it, are presented as evidence of ongoing observation of "
        "human conflict and of a drowned culture.",
  context="Foo-fighter reports are genuine and numerous in squadron records, "
          "and most are attributed to St Elmo's fire, ball lightning, "
          "tracer and flak afterimages, or German experimental ordnance. "
          "The submerged landscape is real and important: Doggerland in the "
          "southern North Sea has yielded Mesolithic tools, bone harpoons "
          "and faunal remains trawled from the seabed, drowned by "
          "post-glacial sea-level rise and the Storegga tsunami around "
          "8,200 years ago — mainstream prehistory on a grand scale."),

S("bering-sea", "Bering Sea",
  subtitle="North Pacific, between Alaska & Siberia", country="",
  region="Oceans & Marine", category="region",
  tags=["beringia", "land-bridge", "migration", "marine"],
  aliases=["Beringia", "Bering Strait", "land bridge"],
  wikipedia="Bering Sea", lat=58.0000, lon=-178.0000, height=1800000,
  precision="area", radius_km=800, pitch=-72,
  claim="The peopling of the Americas across Beringia is cited as a "
        "migration too rapid and too technologically abrupt to be "
        "unassisted, and the sea as the route by which guidance arrived.",
  context="Beringia's exposure during the Last Glacial Maximum is "
          "established by sea-level and sediment records, and the peopling "
          "sequence is now reconstructed in detail from ancient DNA — the "
          "Beringian standstill, the coastal and interior routes, and the "
          "Ancient Beringian genome from Upward Sun River. Coastal "
          "watercraft capability is indicated by the Monte Verde and Huaca "
          "Prieta dates far to the south. It is one of the best-resolved "
          "migration stories in prehistory."),

S("indian-ocean", "Indian Ocean",
  subtitle="Between Africa, Asia & Australia", country="",
  region="Oceans & Marine", category="region",
  tags=["kumari-kandam", "mauritia", "monsoon", "marine"],
  aliases=["Lemuria", "Kumari Kandam", "Ninety East Ridge"],
  wikipedia="Indian Ocean", lat=-20.0000, lon=80.0000, height=3500000,
  precision="area", radius_km=1800, pitch=-76,
  claim="The ocean is presented as the grave of Lemuria and Kumari Kandam, "
        "with the Mauritia crustal fragment and submerged banks offered as "
        "its remains.",
  context="The basin's structure is mapped in detail: the Ninety East Ridge "
          "is a hotspot trace, the Mascarene Plateau is volcanic and "
          "continental-fragment crust, and Mauritia is deeply submerged "
          "Archean basement. All are products of Gondwanan breakup from "
          "about 180 million years ago. Genuine submerged human-period "
          "archaeology does exist on the shallow Indian shelf — the Gulf of "
          "Khambhat and Poompuhar — and is dated to the Holocene."),

# ===========================================================================
# BEYOND EARTH
# ===========================================================================

S("sea-of-tranquility", "Sea of Tranquility",
  subtitle="Mare Tranquillitatis, the Moon", country="", offworld=True,
  region="Beyond Earth", category="offworld",
  tags=["moon", "apollo-11", "mare", "selenography"],
  aliases=["Mare Tranquillitatis", "Moon", "Apollo 11", "Tranquility Base"],
  wikipedia="Mare Tranquillitatis", lat=8.5000, lon=31.4000, height=0,
  precision="exact",
  claim="Apollo 11's landing site is presented as a destination chosen on "
        "prior knowledge, with the mission's transmission gaps, the "
        "Armstrong 'we were warned off' legend, and anomalous features in "
        "Lunar Orbiter frames read as evidence of structures already there.",
  context="This site is not on Earth, so it has no position on the globe "
          "below; the coordinates given are selenographic. The 'warned off' "
          "quotation has no source in the mission transcripts, which are "
          "published in full with the audio, and Armstrong denied it. The "
          "Lunar Reconnaissance Orbiter has since imaged every Apollo site "
          "at sub-metre resolution, showing the descent stages, "
          "experiment packages and astronaut tracks — and no structures. "
          "Mare Tranquillitatis is a basalt flood plain, chosen in 1969 "
          "because it was flat, well-lit at the landing window and "
          "photographed in advance by Ranger 8 and Surveyor 5.",
  links=[{"label": "NASA — Apollo 11 mission transcripts",
          "url": "https://www.nasa.gov/history/alsj/a11/a11transcript_tec.html",
          "kind": "official"},
         {"label": "LROC — Apollo landing site imagery",
          "url": "https://www.lroc.asu.edu/", "kind": "reference"}]),
