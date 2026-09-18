#!/usr/bin/env python3
"""Per-category copy builders for model detail pages.

Every builder returns dict(title, seo_title, meta_desc, overview, benefits[3],
spec_rows[(label, value)], qc, oem). Wording is honest: certification and
document claims stay conditional ("confirm before order"), MOQ/lead time stay
non-numeric, matching the published MX802 template voice.
"""

SOURCE_LABEL = {
    "cbs-helmets": "CBS helmet catalogue 2026", "kuuvi-moto": "KUUVI motorcycle helmet catalogue 2025",
    "moon-sports": "MOON bicycle helmet catalogue 2026", "moon-ski": "MOON sports & ski catalogue 2025",
    "meicheng": "Meicheng helmet brochure 2025", "yongbao": "Yongbao helmet product list",
    "hongxin-visors": "Taotao visor catalogue 2026", "door-closers": "Chuanjin door closer catalogue",
    "vt-hinges": "VOTA window hardware album 2024", "doors-windows": "Aluminum doors & windows catalogue",
    "steel": "Steel structure brochure", "prefab-yk": "ESO YK prefab catalogue 2026",
    "sanitary": "HEEK / HP sanitary-ware export catalogue", "heatpumps": "Luckingstar / Ruixing heat-pump catalogues",
    "heating": "Meiri electric-heating handbook 2024", "led": "LED poster display catalogue",
    "pv": "PV mounting structure album", "storage": "Eraergy mobile storage introduction",
    "decking": "Geometry Cube decking album & quotation sheets", "track": "LP Tartan sports surface album",
    "lubricants": "Jingchuang metal-processing fluids album", "bags": "Lady handbag reference books",
    "belts": "Belt reference books", "slg": "Small leather goods reference books",
    "apparel": "Dingsheng style sheet", "eyelashes": "Lash supplier workbooks",
}

HELMET_SOURCES = ("cbs-helmets", "kuuvi-moto", "moon-sports", "moon-ski", "meicheng", "yongbao")


def _clean(v):
    import re
    v = str(v or "").strip()
    return re.sub(r"\s+", " ", v)


def build(source, entry):
    model = _clean(entry.get("model") or entry.get("id"))
    etype = _clean(entry.get("type"))
    display_name = _clean(entry.get("name"))
    spec = _clean(entry.get("spec"))
    if not etype and spec:
        etype = spec  # grid/table catalogs store the type phrase in spec
    label = SOURCE_LABEL.get(source, "supplier catalogue")
    shell = _clean(entry.get("shell"))
    sizes = _clean(entry.get("sizes"))
    cert = _clean(entry.get("cert"))
    refr = _clean(entry.get("refrigerant"))
    cap = _clean(entry.get("capacity"))
    material = _clean(entry.get("material"))
    page = entry.get("page")

    title = f"{model} {etype}" if etype and model.lower() not in etype.lower() else (etype or model)
    title = title[:70]
    if display_name and display_name.lower() != model.lower():
        title = display_name

    if source in HELMET_SOURCES:
        overview = (
            f"{model} is a {etype.lower()} recorded in the {label}. "
            + (f"The shell is {shell}. " if shell and "not" not in shell.lower() else "")
            + (f"Sizes: {sizes}. " if sizes else "")
            + (f"The catalogue page carries {cert}. " if cert and "per panel" not in cert and "none" not in cert.lower() else "Certification markings follow the model-specific catalogue panel. ")
            + "Colourways, graphics and packaging are confirmed against the order specification before production."
        ).strip()
        benefits = [
            ("Catalogued configuration", f"Positioning is clear from the catalogue: {etype.lower()}."),
            (f"Size range {sizes}" if sizes else "Size range on file", "Adult and junior size runs are confirmed per model before sampling."),
            ("Documents before commitment", "Model-specific test reports or certificates for your target market are requested from the supplier and shared before order confirmation."),
        ]
        qc = "Order checks cover specification confirmation against the approved sample, shell and finish inspection, weight and size-run verification, and carton and packing checks. Photo or video evidence is shared before shipment."
        oem = "Custom colours, graphics and logo placement are available subject to model-specific minimum order quantities. Send your artwork, target quantity and destination market, and we confirm feasibility and cost with the factory."
    elif source == "hongxin-visors":
        overview = (
            f"Aftermarket replacement visor matched to the {model} helmet family, recorded in the {label}. "
            "Standard finishes cover clear, smoke and mirrored options; current colour availability is confirmed per order. "
            "Fitment is checked against the helmet revision before dispatch — send the exact helmet model when you inquire."
        ).strip()
        benefits = [
            ("Model-matched fitment", f"Produced against the {model} mounting pattern and checked per helmet revision."),
            ("Finish options", "Clear, smoke and mirrored finishes; the running colour list is confirmed when you order."),
            ("Aftermarket clarity", "These are aftermarket replacement parts, not original-brand items — positioning stays honest towards your customers."),
        ]
        qc = "Each batch is checked for optical clarity, coating adhesion and mounting-hole alignment against the reference helmet before packing."
        oem = "Private-label packaging and carton printing are available subject to quantity. Send your target quantity and market, and we confirm options with the factory."
    elif source == "door-closers":
        overview = (
            f"{model} is a door closer recorded in the {label}. Configuration: {spec}. "
            "Body finishes, hold-open options and arm types are confirmed against the order specification."
        ).strip()
        benefits = [
            ("Door-weight matched", "Select the body size by door weight and leaf width; we cross-check your door schedule before quoting."),
            ("Cycle-rated mechanism", "The catalogue states cycle ratings for each series; request the current test evidence with your quotation."),
            ("Installation options", "Surface, concealed and slide-rail versions cover standard fire-door and retrofit projects."),
        ]
        qc = "Checks cover closing-speed adjustment, leak inspection, arm operation through the full opening cycle, and finish and carton checks before shipment."
        oem = "Logo printing and custom finishes are available subject to quantity. Send your project door schedule and target quantity for confirmation."
    elif source == "vt-hinges":
        overview = (
            f"{model} is a window-hardware series recorded in the VOTA album. Configuration: {spec}. "
            "Groove system (13.5 mm / 23 mm / Euro), left/right handing and sash weight are confirmed per project window schedule."
        ).strip()
        benefits = [
            ("Stainless construction", "SUS304 material is the album baseline across the friction-stay and concealed ranges."),
            ("Load and cycle data", "Catalogue load ratings and cycle counts are matched to your sash dimensions before quoting."),
            ("Suite compatibility", "Pairs with VOTA lock cases, handles and four-piece sets for a complete window hardware package."),
        ]
        qc = "Checks cover sash-weight simulation, operation smoothness through the catalogue opening angle, screw-hole alignment and plating inspection."
        oem = "Custom lengths, packing and logo requirements are confirmed with the factory subject to quantity."
    elif source == "doors-windows":
        overview = (
            f"{model} is an aluminum {etype.lower()} recorded in the {label}. Configuration: {spec}. "
            "Glass specification, frame finishes and hardware brands are confirmed per project specification."
        ).strip()
        benefits = [
            ("Thermal and glazing options", "IGU build-ups and strip systems are confirmed against your climate and energy targets."),
            ("Project-scale production", "Fabricated to opening schedule with hardware and screen options confirmed per order."),
            ("Export packing", "Systems are packed for container shipment with corner protection and per-opening labelling."),
        ]
        qc = "Checks cover profile and glazing bead assembly, hardware operation, water and air-seal details against the approved sample, and packing lists per opening."
        oem = "Custom colours (powder coating / anodizing), glass and hardware packages are confirmed per project quantity."
    elif source == "sanitary":
        overview = (
            f"{model} is a {etype.lower()} recorded in the {label}. " +
            (f"Configuration: {spec}. " if spec and spec.lower() != etype.lower() else "")
            + "Finishes, rough-in dimensions and packing details are confirmed against the order specification."
        ).strip()
        benefits = [
            ("Export-oriented range", "The series is built for container programmes with mixed-model loading."),
            ("Finish and size options", "Colour and dimension variants in the catalogue are reconfirmed at order stage."),
            ("Fitting documentation", "Installation drawings and rough-in sizes are shared before order confirmation."),
        ]
        qc = "Checks cover glaze surface inspection, flushing or function testing where applicable, fitting accessories completeness, and carton drop-test standard."
        oem = "Logo printing, carton design and mixed-container loading are available subject to quantity."
    elif source == "heatpumps":
        overview = (
            f"{model} is a {etype.lower()} recorded in the {label}. "
            + (f"Capacity: {cap}. " if cap else "")
            + (f"Refrigerant: {refr}. " if refr and refr != "-" else "")
            + "Voltage, ErP documentation and destination-market certification scope are confirmed per order."
        ).strip()
        benefits = [
            ("Capacity programme", (f"Covers the {cap} class for " + ("residential" if "domestic" in etype.lower() or "residential" in etype.lower() else "project") + " applications.") if cap else "Series covers a wide capacity ladder for residential and light-commercial projects."),
            ("Refrigerant documentation", "Refrigerant and safety documentation for your destination market are confirmed before shipment."),
            ("Cold-climate variants", "EVI and low-ambient versions exist across the range; match the variant to your winter design temperature."),
        ]
        qc = "Checks cover run-testing against rated parameters, pressure and leak inspection, controller function, and export crating with foam and board protection."
        oem = "Logo placement, controller language and packaging are available subject to quantity and destination market."
    elif source == "heating":
        overview = (
            f"{model} is a {etype.lower()} recorded in the {label}. " +
            (f"Configuration: {spec}. " if spec and spec.lower() != etype.lower() else "")
            + "Tube material, flange dimensions and terminal options are confirmed per order specification."
        ).strip()
        benefits = [
            ("Element engineering", "Tube alloys (316L / 310S / 840 class) and enamelling options are matched to the water quality of your market."),
            ("Power and voltage builds", "Wattage and voltage are built to order — send your target specification with the inquiry."),
            ("Appliance fitment", "Flange and pipe dimensions follow the original appliance interfaces for straightforward replacement programmes."),
        ]
        qc = "Checks cover resistance and dielectric testing, weld integrity, enamel or surface finish inspection, and packing for appliance-assembly lines."
        oem = "Custom dimensions, terminals and packaging are available subject to quantity — drawings speed up confirmation."
    elif source == "led":
        overview = (
            f"{model} is a {etype.lower()} recorded in the {label}. " +
            (f"Configuration: {spec}. " if spec and spec.lower() != etype.lower() else "")
            + "Pixel pitch, cabinet size and control options are confirmed against the order specification."
        ).strip()
        benefits = [
            ("Indoor / outdoor variants", "Brightness class and waterproofing are matched to the deployment environment."),
            ("Transport-friendly build", "Foldable and movable formats are designed for retail and event logistics."),
            ("Control options", "Synchronous, asynchronous and APP control paths are confirmed per project."),
        ]
        qc = "Checks cover dead-pixel and colour-uniformity screening, cabinet alignment, power and receiving-card function, and flight-case or carton packing."
        oem = "Logo printing on cabinets and custom packing are available subject to quantity."
    elif source == "pv":
        overview = (
            f"{model} is a {etype.lower()} recorded in the {label}. " +
            (f"Configuration: {spec}. " if spec and spec.lower() != etype.lower() else "")
            + "Project loads, wind/snow cases and material grades are confirmed per engineering drawing."
        ).strip()
        benefits = [
            ("Drawing-based production", "Structures are quoted and fabricated against your module layout and site loads."),
            ("Material options", "Hot-dip galvanized and zinc-aluminum-magnesium lines cover different corrosion budgets."),
            ("Container-ready kits", "Bolts, clamps and rails are kitted per project for site efficiency."),
        ]
        qc = "Checks cover coating thickness, dimensional accuracy against drawings, fastener kits completeness, and bundle marking per array."
        oem = "Private-label bundling and project documentation packages are available subject to quantity."
    elif source == "storage":
        overview = (
            f"{model} is a {etype.lower()} recorded in the {label}. " +
            (f"Configuration: {spec}. " if spec and spec.lower() != etype.lower() else "")
            + "Battery certification scope, destination-market compliance and delivery terms are confirmed per order."
        ).strip()
        benefits = [
            ("Fleet-ready platform", "Tank, Station and Flow units are designed to work as one dispatchable system."),
            ("Certification path", "Cell- and pack-level certificates for your market are confirmed before order placement."),
            ("Quiet alternative to diesel", "The catalogue positions the platform against generator sets on noise and running cost."),
        ]
        qc = "Checks cover capacity and charge/discharge verification, BMS communication tests, enclosure and caster inspection, and export crating."
        oem = "Branding, livery and software-language options are confirmed with the factory subject to quantity."
    elif source == "decking":
        overview = (
            f"{model} is a {etype.lower()} recorded in the {label}. " +
            (f"Configuration: {spec}. " if spec and spec.lower() != etype.lower() else "")
            + "Standard colours (walnut, teak, sub-teak, stone grey, ancient shipwood, black gold) and lengths are confirmed per order."
        ).strip()
        benefits = [
            ("Texture and colour programme", "Six standard colourways with wood-grain, striped and grooved textures; custom colours by quantity."),
            ("Installation system", "Matching joists, clips and adjustable pedestals are quoted with the boards."),
            ("Sample-first decisions", "Colour and texture samples are arranged before container confirmation."),
        ]
        qc = "Checks cover profile dimension and colour-lot consistency, grid pattern alignment, moisture and packing checks per bundle."
        oem = "Private-label bundles and project-mixed containers are available subject to quantity."
    elif source == "track":
        overview = (
            f"{model} is a {etype.lower()} recorded in the {label}. " +
            (f"Configuration: {spec}. " if spec and spec.lower() != etype.lower() else "")
            + "Thickness, colour and line marking layout are confirmed against your site drawings."
        ).strip()
        benefits = [
            ("Standard-compliant builds", "Systems reference IAAF-style structures and GB 36246 for school surfaces where noted."),
            ("Site-oriented delivery", "Material, primer and line-marking paint are quoted as one package."),
            ("Reference projects", "School and stadium references exist for each system; ask for the closest climate match."),
        ]
        qc = "Checks cover batch mixing records, thickness sampling during installation, curing timeline, and line-marking accuracy against the layout."
        oem = "Colour matching and thickness upgrades are confirmed per project quantity."
    elif source == "lubricants":
        overview = (
            f"{model} is a {etype.lower()} recorded in the {label}. " +
            (f"Configuration: {spec}. " if spec and spec.lower() != etype.lower() else "")
            + "Packaging sizes and concentration guidance follow the catalogue's recommended-use tables."
        ).strip()
        benefits = [
            ("Application-matched chemistry", "Formulas are organised by metal, process and bath type rather than a generic product list."),
            ("Usage documentation", "Recommended concentrations and make-up guidance come with the quotation."),
            ("Trial support", "Bench or line trials can be arranged with the factory before volume orders."),
        ]
        qc = "Checks cover batch COA documentation, concentration verification, packaging integrity, and label compliance for your destination market."
        oem = "Bulk, drum and private-label packing are available subject to quantity."
    elif source in ("bags", "belts", "slg"):
        words = {
            "bags": "handbag style", "belts": "belt style", "slg": "small-leather-goods style",
        }[source]
        mat = material if material and material not in ("leather",) else "leather"
        overview = (
            f"Reference {words} from the supplier's {label} (reference {model}). "
            + (f"Shown in {mat}. " if material else "")
            + "Material, hardware, lining and dimensions are developed to your specification; colours are customized. "
            "Third-party branded designs shown in the reference books are excluded — development stays brand-free."
        ).strip()
        benefits = [
            ("Brand-free development", "Styles are developed from the supplier's own reference patterns, with branded designs excluded."),
            ("Material and hardware options", "Full-grain, split, suede and PU builds with your hardware finish are confirmed by sample."),
            ("Low-risk sampling", "Counter-samples are reviewed and approved before bulk production."),
        ]
        qc = "Checks cover material inspection against the approved sample, stitching and hardware pull tests, lining and fitting checks, and carton packing counts."
        oem = "Your logo, hardware finish, lining print and packaging are developed against your target quantity."
    elif source == "apparel":
        overview = (
            f"Style reference {model} from the {label}. Fabric, size grading and trims are developed to your tech pack; "
            "the reference image defines the silhouette only. Branded designs shown in the source sheet are excluded."
        ).strip()
        benefits = [
            ("Tech-pack driven", "Silhouette from the style sheet; fabric, grading and trims follow your specification."),
            ("Sample-first workflow", "Proto and size-set samples are approved before bulk."),
            ("Flexible order building", "Styles can be mixed within one programme subject to fabric minimums."),
        ]
        qc = "Checks cover fabric inspection, measurement against the approved size set, stitching quality and packing counts."
        oem = "Private-label trims, labels and packaging are available subject to quantity."
    else:
        overview = f"{model} — {etype or 'catalogue reference'} from the {label}. Specifications are confirmed against the supplier catalogue per order."
        benefits = [("Catalogue-backed configuration", "Positioning and options follow the reviewed supplier catalogue."),
                    ("Documents before commitment", "Model-specific documents for your market are requested before order confirmation."),
                    ("Sourcing support", "Factory checks and sample reviews can be arranged on request.")]
        qc = "Specification confirmation against the approved sample plus packing checks before shipment."
        oem = "Customization options are confirmed with the factory subject to quantity."

    spec_rows = [("Model / series", model), ("Catalogue source", label)]
    if etype: spec_rows.append(("Type", etype))
    if shell and shell.lower() != "not stated": spec_rows.append(("Shell", shell))
    if sizes: spec_rows.append(("Sizes", sizes))
    if cert and cert.lower() != "per panel" and cert.lower() != "none printed": spec_rows.append(("Markings noted in catalogue", cert))
    if refr and refr != "-": spec_rows.append(("Refrigerant", refr))
    if cap: spec_rows.append(("Capacity", cap))
    if material and source in ("bags", "belts", "slg"): spec_rows.append(("Reference material", material))
    if spec and spec.lower() not in (etype.lower(), ""): spec_rows.append(("Configuration", spec))
    if page: spec_rows.append(("Catalogue page", f"p.{page}"))

    seo_title = f"{model} {etype} Sourcing | Taotao Sourcing" if etype else f"{model} Sourcing | Taotao Sourcing"
    seo_title = seo_title[:70]
    meta_desc = (f"Source the {model} ({etype or 'catalogue reference'}) from reviewed supplier catalogues. "
                 f"Taotao Sourcing confirms specifications, documents and samples before you commit.")[:158]
    return {"title": title, "seo_title": seo_title, "meta_desc": meta_desc,
            "overview": overview, "benefits": benefits, "spec_rows": spec_rows,
            "qc": qc, "oem": oem}
