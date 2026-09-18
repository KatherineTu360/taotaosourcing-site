#!/usr/bin/env python3
"""Hierarchy configuration: category -> groups -> leaf groups -> model assignment.

Model sources are intel JSON files in data/intel/. Every intel entry must land in
exactly one leaf group; build_hierarchy.py asserts full coverage so no catalog
model is dropped.
"""

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def g(slug, title, intro=None, subs=None, models=None, image=None):
    return {"slug": slug, "title": title, "intro": intro or "", "subs": subs or [],
            "models": models or [], "image": image}

def m(source, keys=None, match=None, name_prefix=None, exclude=None):
    """Model assignment rule: from intel `source`, take entries whose model/id is
    in `keys`, or where `match(model)` is truthy."""
    return {"source": source, "keys": keys or [], "match": match,
            "name_prefix": name_prefix, "exclude": exclude or []}

# ---------------------------------------------------------------------------
# per-category groups
# ---------------------------------------------------------------------------

def contains(*frags):
    def f(model, entry=None):
        return any(x in model for x in frags)
    return f

GROUPS = {
    "helmets": [
        g("motorcycle", "Motorcycle Helmets",
          "Full-face, flip-up, off-road, vintage and open-face motorcycle helmet platforms from the CBS and KUUVI lines, plus the Meicheng city range. Certification printed on each model varies (ECE 22.06, DOT, CCC); request the model-specific certificate before committing.", subs=[
            g("full-face-touring", "Full-Face Touring & Carbon", "Road-focused full-face platforms in ABS and FRP/carbon shell options, single- and double-visor.", models=[
                m("cbs-helmets", keys=["F605","F606","F607","F609","F611"]),
                m("catalog", keys=["f607-full-face-motorcycle-helmet","f609-double-visor-full-face-helmet"]),
            ]),
            g("full-face-sport-racing", "Full-Face Sport & Racing", "Sport and track full-face models, including 12K carbon racing shells.", models=[
                m("cbs-helmets", keys=["F616","F617","F618","M906"]),
                m("catalog", keys=["f616-double-visor-full-face-helmet","fk108-double-visor-full-face-helmet"]),
                m("kuuvi-moto", keys=["FK108","KU936","FK218","FK117","KU07","KU07-T","FF07"]),
            ]),
            g("flip-up-modular", "Flip-Up Modular", "Chin-bar modular helmets for touring and urban riders.", models=[
                m("cbs-helmets", keys=["M902"]),
                m("kuuvi-moto", keys=["FK112","KU965A","IRONMAN"]),
            ]),
            g("off-road", "Off-Road & Motocross", "Peak-equipped off-road platforms from ABS entry shells to 12K carbon professional models, with removable-chin trial options.", models=[
                m("cbs-helmets", keys=["MX801"]),
                m("kuuvi-moto", keys=["KU129","KS08","KU901","KS001","KS05","KS03M"]),
                m("catalog", keys=["mx802-carbon-adventure-helmet"]),  # existing detail page
            ]),
            g("vintage-cruiser", "Vintage & Cruiser", "Fiberglass and 3K carbon retro full-face and Harley-style 3/4 open-face helmets with bubble shields.", models=[
                m("kuuvi-moto", keys=["KU08","KU600","KU701","FK01","FK02"]),
            ]),
            g("open-face-half", "Open-Face & Half Shell", "3/4 open-face, jet and shorty half shells for city riding, including carbon jet versions.", models=[
                m("cbs-helmets", keys=["P103","P118","P122","P126","P152"]),
                m("catalog", keys=["p103-open-face-motorcycle-helmet"]),
                m("kuuvi-moto", keys=["FK203","FK110","BH03","BH02","FG-01","KU500","FK113","FK102","FK99","FK107"]),
            ]),
            g("smart-bluetooth", "Smart Bluetooth", "Full-face and open-face helmets with intercom, AI voice control and LED taillights.", models=[
                m("kuuvi-moto", keys=["KU636","FK07","FT08"]),
            ]),
            g("kids-junior", "Kids & Junior", "Children's full-face, open-face and half motorcycle helmets in cartoon graphics.", models=[
                m("cbs-helmets", keys=["P121","P128"]),
                m("kuuvi-moto", keys=["KU128","M3","FK106"]),
            ]),
            g("novelty-gift", "Novelty & Gift", "Licensed-style flip-up and character helmets plus mini gift helmets.", models=[
                m("kuuvi-moto", keys=["HIPHOP","SKULL","BATMAN","LP01"]),
            ]),
            g("meicheng-city", "Meicheng City & Cruiser", "DOT + ECE 22.06 certified full-face and half helmets from the Meicheng line.", models=[
                m("meicheng", keys=["M609","M901","MC-DVH","MC-VSV","MC-DVQ"]),
            ]),
        ]),
        g("cycling-sports", "Cycling & Sports Helmets",
          "Road, MTB, city, e-bike, smart and kids cycling helmets from the MOON line (CE + CPSC across the range) and the Yongbao factory list. NTA 8776 applies to marked e-bike models.", subs=[
            g("road", "Road Cycling", "In-mould road helmets from 170 g ultra-light to aero and Mips-equipped versions, with taillight and magnetic visor options.", models=[
                m("moon-sports", keys=["AR01","AR3","AR37","HB102","FT19","HB101","HB92","HB3-1","HB90","YM03","MV100","MV96","MV99","HY97","HB98","MV53","MV29","KS29SP","MV37","MV49","HB3-8","MV32"]),
                m("yongbao", keys=["HO-06","HO-210","YB-17","HO-186","HO-108","HO-109","YB-69","HO-99","HO-196","HO-022","HO-03","HO-028","HO-888","YZ-A001","YZ-A002","YZ-A002G","YZ-A003"]),
                m("catalog", keys=["ho210-road-bicycle-helmet"]),
            ]),
            g("mtb", "Mountain Bike (MTB)", "Open-face and large-peak MTB helmets, in-mould and out-mould.", models=[
                m("moon-sports", keys=["SKS-3","SKS113","SKS31","SKS32","KS33","KS39","HB3-7","KS32SP","KS30","KS31","HB3-9","HB3-5","HB3-6","HB3-3"]),
                m("yongbao", keys=["YB-05","YB-28","YB-90","YB-07","YZ-B-091-L1"]),
            ]),
            g("downhill-fullface", "Downhill & Full-Face", "Full-face downhill and kids full-face helmets with removable chin options.", models=[
                m("moon-sports", keys=["FT89","KS05B","SKS217","KS03B","KS11"]),
                m("yongbao", keys=["YZ-B-056-L1"]),
            ]),
            g("city-commuter", "City & Commuter", "Urban commuting helmets, folding commuter models and goggle-equipped city helmets with rechargeable lights.", models=[
                m("moon-sports", keys=["KS35","HS60","FK111B","HB15","KS83","HS66","HB103","FA05","KS60","HB25","KS22"]),
                m("yongbao", keys=["YB-006","HO-89","YB-11","YB-13","YB-16","YB-96","YB-19","HO-86","HO-86L","HO-85","YZ-F002","YB-15","YD-82","YB-31"]),
                m("catalog", keys=["ks83-city-bicycle-helmet"]),
            ]),
            g("e-bike", "E-Bike (NTA 8776)", "E-bike helmets certified/tested against NTA 8776 where marked, with lens and smart variants.", models=[
                m("moon-sports", keys=["FT09","FT11","FT09C"]),
                m("yongbao", keys=["HO-209","YZ-X001"]),
            ]),
            g("smart-camera", "Smart & Camera", "Bluetooth, camera, LED-music and turn-signal smart helmets.", models=[
                m("moon-sports", keys=["W3","HB3-1S","FT03","FT04","MTV23","FT01","FT06C","FT02","ASP013","ASP020","ASP015","ASP011"]),
                m("yongbao", keys=["YB-10","H2"]),
            ]),
            g("visor-led", "Visor & Taillight Series", "Helmet families with integrated lenses or LED taillights.", models=[
                m("moon-sports", keys=["TY04","KS09","KS28","MV88","HB3-2","FT10","BH39","PANKING"]),
            ]),
            g("aero-triathlon", "Aero & Triathlon", "Time-trial and triathlon aero helmets.", models=[
                m("moon-sports", keys=["KS13","KS01","KS02A"]),
            ]),
            g("freestyle-skate", "Freestyle & Skate", "Skatepark and freestyle helmets in in-mould and out-mould builds.", models=[
                m("moon-sports", keys=["MTV12","MTV28","MTV26B","MTV01","MTV18S","MTV26"]),
            ]),
            g("kids", "Kids & Junior Cycling", "Children's cycling, balance-bike and animal-print helmets, 180-300 g class.", models=[
                m("moon-sports", keys=["HB3-4","MV11","MB11","KS87","HB5-5","HS66K","KS16","MA2","KS61","HB6-2","HB6-5","HB5-2","MV12K","KS15","HB3-5K","HB8","MV6-2","MV6-3","HB5-3","MV7","HB10","MV5-2","HB6-3","MV4","MB10","MV7A","MTV12A","KLM","BHC1"]),
                m("yongbao", keys=["HO-11P","HO-11M","HO-191","HO-09L","HO-09S","HO-09G","HO-11PC","YB-88","HO-102","YB-62","YB-65","YB-68","HO-169","HO-168","HO-165","YD-39","HO-055","YZ-C-010","YZ-C001"]),
            ]),
        ]),
        g("snow-sports", "Ski & Snow Sports",
          "Ski and snowboard helmets with removable visors, vent control and race variants, plus EN 174 goggles. Certifications printed on the MOON ski line: CE, CPSC, ASTM; smart models add Bluetooth audio.", subs=[
            g("ski-adult", "Adult Ski & Snowboard", "In-mould and hard-shell adult ski helmets, visor-ready models with Shield-X lenses.", models=[
                m("moon-ski", keys=["MS108","MS106","MS105","MS99","MS97","MTV17SK","MS100","MS95","MS96","MS102","MS103","MS91","MTV20","MTV12SK","MS90","MS101","MS86","MS85","MS88"]),
                m("yongbao", keys=["HO-111","YB-98","HO-269","YB-18","YB-289"]),
                m("catalog", keys=["ms108-ski-helmet"]),
            ]),
            g("ski-kids", "Kids & Youth Ski", "Kids ski helmets with visor, mohawk prints and LED taillight options.", models=[
                m("moon-ski", keys=["MS95B","MTV18SK","MS98","SW1"]),
                m("yongbao", keys=["YB-29","YZ-X001S"]),
            ]),
            g("race-snow", "Race & Smart Ski", "Race helmets with extended ear protection and Bluetooth smart ski models.", models=[
                m("moon-ski", keys=["JY05B","MS82","ASP016","ASP018"]),
            ]),
            g("goggles", "Ski & Snow Goggles", "Adult and kids double-layer spherical goggles, magnetic-lens and anti-fog coated (EN 174 marked).", models=[
                m("moon-ski", keys=["SK88","SK694","SK687","GK79","GK80","GK57","GK61"]),
            ]),
        ]),
        g("specialty-sports", "Equestrian, Climbing & Water",
          "Specialty sport helmets beyond cycling: equestrian (VG1 / EN 1384 / ASTM F1163), climbing, water sports, speed skating, hockey and snow body protection.", subs=[
            g("equestrian", "Equestrian", "Riding helmets with removable visors, VG1 and EN 1384 / ASTM F1163 marked models, adults and kids.", models=[
                m("moon-ski", keys=["MK01","MSU05","MSU03","MSU04","MS01","MS02","MS06","MS07","MS08","MS09"]),
                m("yongbao", keys=["YB-02","YB-03","YZ-D001"]),
            ]),
            g("climbing", "Climbing", "Lightweight EPP/PC climbing helmets.", models=[
                m("moon-ski", keys=["PY02","PY01","HB16","HB12"]),
                m("yongbao", keys=["YZ-E001"]),
            ]),
            g("water-sports", "Water Sports", "Whitewater and rescue helmets with EVA liners and ear protection.", models=[
                m("moon-ski", keys=["JY04","JY05","MTV16","MTV12B"]),
                m("moon-sports", keys=["JY04W","JY05W"]),
            ]),
            g("ice-hockey", "Speed Skating & Hockey", "Speed skating helmets and caged hockey helmets.", models=[
                m("moon-ski", keys=["MM03","MM08","MM04","HB08"]),
            ]),
            g("protection", "Body Protection", "SP2 back protectors, jackets and kids protector sets.", models=[
                m("moon-ski", keys=["PC03","PJ01","PJA03","PJK03"]),
            ]),
        ]),
    ],

    "helmet-visors": [
        g("brand-visors", "Model-Compatible Replacement Visors",
          "Aftermarket replacement visors matched to specific helmet families. Fitment is confirmed per helmet revision before ordering; products are aftermarket parts, not original-brand items.", subs=[
            g("agv", "AGV-Compatible", models=[
                m("hongxin-visors", keys=["AGV K1/K1S/K3SV/K5/K5S","AGV K5 PLUS","AGV K6/K6S","AGV PISTA","AGV NEW STYLE K3/K4","AGV PISTA GP RR spoiler"]),
                m("catalog", keys=["agv-compatible-helmet-visors"]),
            ]),
            g("hjc", "HJC-Compatible", models=[
                m("hongxin-visors", keys=["HJC C70 (HJ20M)","HJC I10/I70 (HJ31)","HJC HJ26 (RPHA11)","HJC HJ42 (RPHA12)","HJC i90/i91 (HJ33)","HJC HJ34P (C10)","HJC HJ17 (C91)","HJC HJ38 (i71)","HJC RPHA11 HJ-26 spoiler"]),
                m("catalog", keys=["hjc-compatible-helmet-visors"]),
            ]),
            g("shoei", "SHOEI-Compatible", models=[
                m("hongxin-visors", keys=["SHOEI Z7","SHOEI X14","SHOEI Z8/X15","SHOEI GT-Air I/II (CNS-1)","SHOEI Neotec 2 (CNS-3 side-open)","SHOEI Neotec 3 (CNS-3C center-open)","SHOEI Hornet ADV (A6)","SHOEI Glamster (CPB-1V)","SHOEI JC","SHOEI Z8 spoiler"]),
                m("catalog", keys=["shoei-compatible-helmet-visors"]),
            ]),
            g("arai", "Arai-Compatible", models=[
                m("hongxin-visors", keys=["Arai RX-7X","Arai Tour Cross 5","Arai Tour-Cross 3 (TX3/XD4)","Arai VZ-RAM","Arai spoiler (RX-7V/Signet-X)"]),
                m("catalog", keys=["arai-compatible-helmet-visors"]),
            ]),
            g("ls2", "LS2-Compatible", models=[
                m("hongxin-visors", keys=["LS2 FF801/FF397/FF813","LS2 FF808","LS2 FF811","LS2 353/320/328/800","LS2 352/802/358 (center-open)","LS2 OF626","LS2 OF618","LS2 OF603","LS2 OF608","LS2 FF906","LS2 FF908","LS2 FF910","LS2 MX701"]),
                m("catalog", keys=["ls2-compatible-helmet-visors"]),
            ]),
            g("mt", "MT-Compatible", models=[
                m("hongxin-visors", keys=["MT V-12/Targo","MT V-14 (Revenge 2/Rapide Pro/Targo)","MT V-14B (Revenge 2S)","MT V-28B (Thunder 4SV)","MT Rimiy 935/SH4000/V-25B","MT V-18B","MT V-18C","MT V-29/KRE+ carbon","MT V-32 (JARAMA)","MT V31","MT V31B"]),
                m("catalog", keys=["mt-compatible-helmet-visors"]),
            ]),
            g("kyt", "KYT-Compatible", models=[
                m("hongxin-visors", keys=["KYT R2R","KYT TT-REVO"]),
                m("catalog", keys=["kyt-compatible-helmet-visors"]),
            ]),
            g("shark", "SHARK-Compatible", models=[
                m("hongxin-visors", keys=["SHARK Spartan GT/GT PRO/RS","SHARK SKWAL","SHARK GP","SHARK i3/D-Skwal 3/Ridill 2"]),
                m("catalog", keys=["shark-compatible-helmet-visors"]),
            ]),
            g("scorpion-exo", "Scorpion EXO-Compatible", models=[
                m("hongxin-visors", keys=["Scorpion EXO R1 520/1400","Scorpion EXO R420"]),
                m("catalog", keys=["scorpion-exo-compatible-helmet-visors"]),
            ]),
            g("icon-nolan", "Icon & Nolan-Compatible", models=[
                m("hongxin-visors", keys=["ICON IC-06 (wing)","NOLAN X-803"]),
                m("catalog", keys=["icon-compatible-helmet-visors","nolan-x803-compatible-visor"]),
            ]),
            g("bell", "Bell-Compatible", models=[
                m("hongxin-visors", keys=["Bell RS-1","Bell bubble flat visor"]),
                m("catalog", keys=["bell-rs1-compatible-visor"]),
            ]),
            g("other-brands", "Alpinestars, Motorax, Ruroc & More", models=[
                m("hongxin-visors", keys=["Alpinestars Supertech R10","Motorax R50S","RUROC Atlas 3.0/4.0"]),
                m("catalog", keys=["alpinestars-r10-compatible-visor","motorax-r50s-compatible-visor","ruroc-atlas-compatible-visor","helmet-rear-spoiler-range"]),
            ]),
            g("bubble-open-face", "Bubble & Open-Face Visors", "3-snap bubble visors and open-face wind shields for vintage and city helmets.", models=[
                m("hongxin-visors", keys=["Bubble visor REGULAR (3-snap)","BOBO wind visor"]),
                m("catalog", keys=["bubble-visor-open-face","bobo-wind-visor"]),
            ]),
            g("public-mold", "Public-Mold Visor Program", "Liangyu public-mold visor families for volume programs; confirm tooling and brand fitment per project.", models=[
                m("hongxin-visors", keys=["__public_molds__"]),
            ]),
        ]),
    ],

    "doors-windows": [
        g("windows", "System Windows", subs=[
            g("thermal-sliding", "Thermal-Break Sliding Windows", models=[m("doors-windows", keys=["TC76","TC115","DW-128"]),m("catalog", keys=["m76-thermal-break","xingyan-88-two-track"])]),
            g("standard-sliding", "Standard (Non-Thermal-Break) Sliding", models=[m("doors-windows", keys=["DW-100"])]),
            g("casement-tilt-turn", "Casement & Tilt-Turn System Windows", models=[m("doors-windows", keys=["TZ110C","PC110","PC120","WP92PS","WP118PS"]),m("catalog", keys=["m78-triple-glazed"])]),
        ]),
        g("doors", "Patio & Interior Doors", subs=[
            g("sliding-doors", "Sliding & Side-Pressure Doors", models=[m("doors-windows", keys=["DW-116SP","DW-4068","DW-5070"]),m("catalog", keys=["t130-heavy-duty"])]),
            g("lift-slide", "Lift-Slide & Heavy Thermal-Break Doors", models=[m("doors-windows", keys=["DW-4075","DW-5090","DW-7096"])]),
            g("swing-doors", "Swing (Casement) Doors", models=[m("doors-windows", keys=["DW-4048","DW-4068C"])]),
            g("sunrooms", "Sunroom Systems", models=[m("catalog", keys=["t120-sunroom"])]),
            g("interior-minimalist", "Interior Minimalist Doors", models=[m("doors-windows", keys=["DW-PS","DW-16S","DW-16W"])]),
        ]),
    ],

    "door-closers": [
        g("surface-standard", "Standard Surface-Mounted Closers",
          "150,000-cycle economy fire-door line with square and round bodies, 25-85 kg doors.", models=[
            m("door-closers", keys=["CJ051","CJ061-S","CJ061-R","CJ071"]),
            m("catalog", keys=["cj051-compact-surface","cj061-medium-surface","cj5022-high-cycle"]),
        ]),
        g("surface-high-cycle", "High-Cycle Heavy-Duty Closers",
          "300,000-cycle high-grade line with upgraded internals, German seal rings and AW/AD options.", models=[
            m("door-closers", keys=["CJ5011-S","CJ5011-R","CJ5022-S","CJ5022-R","CJ5033-S","CJ5033-R"]),
            m("catalog", keys=["cj5022-high-cycle"]),
        ]),
        g("concealed", "Concealed Closers", "Hidden-installation closers for 1000-1200 mm doors.", models=[
            m("door-closers", keys=["CJ2022","CJ2122"]),
            m("catalog", keys=["cj2022-concealed"]),
        ]),
        g("special-shape", "Special-Shaped & Slide-Rail", "Triangular and quadrilateral full-auto bodies, including slide-rail arm version.", models=[
            m("door-closers", keys=["CJ3023","CJ8133","CJ8133-S"]),
        ]),
    ],

    "hinges": [
        g("friction-stays", "Heavy-Duty Friction Stays", "SUS304 casement hinges from 50 kg to 150 kg rated loads, 88-degree opening.", models=[
            m("vt-hinges", keys=["VT-358","VT-353C","VT-331C","VT-331B","VT-335B","VT-332","VT-353A","VT-355","VT-336"]),
            m("catalog", keys=["vt331b","vt353a"]),
        ]),
        g("concealed-hinges", "Concealed & Stealth Hinges", "165-180 degree concealed hinges, including screen-door and quick-install versions.", models=[
            m("vt-hinges", keys=["VT-351F","VT-351D","VT-180A","VT-180B","VT-351A","VT-351C","VT-351D2","VT-KZ"]),
            m("catalog", keys=["vt351a"]),
        ]),
        g("top-hung-stays", "Top-Hung Stays & Limit Arms", "Damped and zero-damping top-hung window stays, 38-70 degree opening.", models=[
            m("vt-hinges", keys=["VT-330A","VT-330B","VT-333A","VT-333B","VT-337"]),
            m("catalog", keys=["vt330a"]),
        ]),
        g("lock-cases", "Transmission Lock Cases", "Stainless espagnolette lock cases in 11 centre heights (7.5-35 cm).", models=[
            m("vt-hinges", keys=["VT-315B","VT-315","VT-315C"]),
        ]),
        g("handles", "Window & Door Handles", "Aluminium and CNC-machined handles with fluorocarbon finishes.", models=[
            m("vt-hinges", keys=["VT-2368","VT-2369","VT-2386","VT-2396","VT-2397"]),
        ]),
        g("espag-sets", "Four-Piece Sets & Strikes", "Anti-pry espagnolette sets and strike plates for Euro and 23 mm grooves.", models=[
            m("vt-hinges", keys=["VT-2056B","VT-2056C","VT-2051A","VT-2046","VT-2045","VT-517","VT-518","VT-520","VT-521"]),
        ]),
        g("hardware-suites", "Honor-Series Hardware Suites", "Matched full-window hardware suites (friction stay + concealed hinge + lock case + handles + espag set).", models=[
            m("vt-hinges", keys=["VT-SZB","VT-ZXS","VT-ZSS"]),
        ]),
    ],

    "decking": [
        g("co-extruded", "2nd-Generation Co-Extruded Decking", models=[
            m("decking", keys=["LFM14025K6","LFM15023K7","LFM13823K6A","LFM14521K7","LFM13823K6B","LFM14023SX"]),
            m("catalog", keys=["lfm14025k6"]),
        ]),
        g("core-decking", "Aluminum & Steel Core Decking", models=[
            m("decking", keys=["LXD-14525","LXD-14522","GXD-14525","GXD-15025","LXD-15025"]),
            m("catalog", keys=["lxd14525"]),
        ]),
        g("asa-decking", "ASA Co-Extruded Decking & Panels", models=[
            m("decking", keys=["ASA-14021","ASA-11316","ASA-17717","ASA-18020"]),
            m("catalog", keys=["asa14021"]),
        ]),
        g("wall-fence", "Wall, Fence & Great-Wall Panels", models=[
            m("decking", keys=["LFM18024","LFM9024","LFM21826","LFM16921","LXF-17717"]),
        ]),
        g("trims-handrails", "Trims & Handrails", models=[
            m("decking", keys=["LXF-5050","LXF-10010","LXF-8045-F"]),
        ]),
        g("installation-system", "Joists, Clips & Pedestals", models=[
            m("decking", keys=["DBPJ-170","DBPJ-171","DBPJ-171-1","DBPJ-171-2","DBPJ-171-3","DBPJ-171-4","DBPJ-171-6","DBPJ-172","DBPJ-174"]),
        ]),
    ],

    "steel": [
        g("purlins", "C & Z Purlins", models=[
            m("steel", keys=["C-purlin","Z-purlin"]),
            m("catalog", keys=["c-section","z-section"]),
        ]),
        g("truss-deck", "Reinforced Truss Decking", models=[
            m("steel", keys=["TD-A","TD-B"]),
            m("catalog", keys=["tda-tdb"]),
        ]),
        g("closed-deck", "Closed Floor Decks", models=[
            m("steel", keys=["YX42-180-745","YX65-226-675","YX40-185-555","YXB65-220-660","YXB50-200-600","YXB40-185-740","YZX65-170-510","YXB90-340"]),
        ]),
        g("open-deck", "Open Profile Decks", models=[
            m("steel", keys=["YX76-295-880","YX76-305-915","YX76-305-600","YX76-305-490","YX51-325-970"]),
            m("catalog", keys=["profiled-steel-floor-deck"]),
        ]),
        g("roof-panels", "Roof Cladding Profiles", models=[
            m("steel", keys=["YX25-207-830","YX15-478","YX15-410-820","YX51-390-783","YX61-500","YX38-152-914","YX5-380-760","YX25-210-840C"]),
            m("catalog", keys=["profiled-roof-wall-sandwich"]),
        ]),
        g("wall-panels", "Wall Cladding Profiles", models=[
            m("steel", keys=["S-373","YX25-210-840","YX35-125-750","YX9-100-900","YXZ25-249-992","YX-2Y-18-63.5-825","YX-LH-38-333-999","YX50-290-870","YX-ZH-35-270-810","YX31.5-135-810","YX12-225-900"]),
        ]),
        g("sandwich-panels", "Sandwich Panels", models=[
            m("steel", keys=["SP-950","SP-850","SP-830PU","SP-1050","SP-1150"]),
        ]),
        g("daylighting", "Daylighting Panels", models=[
            m("steel", keys=["FRP830","FRP380","PC-830"]),
        ]),
        g("accessories", "Fasteners, Trims & Insulation", models=[
            m("steel", keys=["ACC-KIT"]),
        ]),
        g("fabrication", "Fabricated Steel Members", "Project-based welded members: box columns, trusses, wind-tower sections and metro station steel.", models=[
            m("steel", keys=["FAB-MEMBER"]),
        ]),
    ],

    "prefab": [
        g("studios", "Studio & Compact Units", models=[
            m("prefab-yk", keys=["YK-1","YK-3"]),
            m("catalog", keys=["yk1-prefab","yk3-prefab"]),
        ]),
        g("tea-pavilion", "Tea House Pavilion", models=[
            m("prefab-yk", keys=["YK-2"]),
        ]),
        g("one-bedroom", "One-Bedroom Units", models=[
            m("prefab-yk", keys=["YK-4","YK-6"]),
            m("catalog", keys=["yk4-prefab","yk6-prefab"]),
        ]),
        g("bar-lounge", "Bar & Lounge Units", models=[
            m("prefab-yk", keys=["YK-5"]),
        ]),
    ],

    "sanitary": [
        g("smart-toilets", "Smart Toilets & Bidet Seats", subs=[
            g("smart-toilet", "Smart Toilets", models=[
                m("sanitary", keys=[], match=contains("2213","2208","2209","2230","2014","2217","2212","2206","2205","2201","2218","W02B","2236","2235","2103","2203","2021","2216","2215","2232","2106","2057","2242","2240","2044","2214","2046","2033")),
                m("sanitary", keys=["HP-2001C","HP-2002C"],),
                m("catalog", keys=["hp20001c"]),
            ]),
            g("bidet-seats", "Bidet Seats", models=[
                m("sanitary", match=contains("1002","1201","1033","1034","SH237","SH08","1024","1025"),),
            ]),
        ]),
        g("toilets", "Toilets", subs=[
            g("one-piece", "One-Piece Toilets", models=[
                m("sanitary", keys=["HP-2301","HP-2302","HP-2303","HP-2304","HP-2305","HP-2306","HP-2313","HP-2312","HP-2311"],),
                m("catalog", keys=["hp2301"]),
            ]),
            g("two-piece", "Two-Piece Toilets", models=[
                m("sanitary", match=lambda model, e: model.startswith("HP-8") or model.startswith("HP-6") and model not in ("HP-630","HP-631","HP-632","HP-633","HP-609") or model in ("HP-2620","HP-2621","HP-2622","HP-2622P","HP-2308","HP-588","HP-2062S","HP-2062SF","HP-2401T","HP-2802","HP-2808","HP-2808F","HP-2809","HP-8501","HP-8502","HP-8503","HP-T302","HP-T660","HP-T670","HP-T970")),
            ]),
            g("wall-hung", "Wall-Hung Toilets", models=[
                m("sanitary", keys=["HP-505","HP-505YB","HP-506","HP-T027","HP-T035","HP-T036","HP-T045","HP-630","HP-631","HP-632","HP-633"],),
                m("catalog", keys=["hp630"]),
            ]),
        ]),
        g("basins", "Basins", subs=[
            g("pedestal", "Pedestal Basins", models=[
                m("sanitary", match=lambda model, e: model in ("HP-7301","HP-7308","HP-7309","HP-7328","HP-437","HP-451","HP-452","HP-453") or (model.startswith("HP-440") or model.startswith("HP-441") or model.startswith("HP-442") or model in ("HP-229","HP-260","HP-211","HP-220","HP-221","HP-222","HP-223","HP-228","HP-282","HP-283","HP-285") or (model.startswith("HP-504") or model.startswith("HP-507") or model.startswith("HP-508")))),
            ]),
            g("wall-counter", "Wall-Hung & Countertop Basins", models=[
                m("sanitary", keys=["HP-403","HP-405","HP-406","HP-407","HP-408","HP-409","HP-434","HP-435","HP-609","HP-625","HP-7220","HP-7222","HP-7007","HP-7002","HP-7011","HP-7025","HP-7025A","HP-7050","HP-7031-40","HP-7032-40","HP-7033-40","HP-7034-35","HP-7035-40","HP-7036-35","HP-7037-35","HP-7039-40","HP-7044-35","HP-7047-42","HP-7048-60","HP-7040-35","HP-531"],),
                m("catalog", keys=["hp403"]),
            ]),
            g("art-undermount", "Art & Under-Counter Basins", models=[
                m("sanitary", match=lambda model, e: model.startswith("HP-X") or model.startswith("HP-XY") or model.startswith("HP-XS") or model.startswith("HP-CS")),
                m("sanitary", match=lambda model, e: model.startswith("HP-A"),),
            ]),
        ]),
        g("squat-urinal", "Squat Pans, Urinals & Tubs", subs=[
            g("squat-pans", "Squat Pans", models=[
                m("sanitary", match=lambda model, e: model.startswith("HP-65"),),
            ]),
            g("urinals", "Urinals", models=[
                m("sanitary", match=lambda model, e: model.startswith("HP-50") and any(c in model for c in ("01","02","04","06","07","09","32","39"))),
            ]),
            g("mop-tubs", "Mop Tubs", models=[
                m("sanitary", match=lambda model, e: model.startswith("HP-74"),),
            ]),
        ]),
        g("cisterns", "Cisterns & Flush Valves", models=[
            m("sanitary", keys=["MQ120","HP-010J","HP-011","Y1","Y2","Y3","Y4"],),
        ]),
        g("showers", "Shower Systems", subs=[
            g("shower-columns", "Shower Columns", models=[
                m("sanitary", match=lambda model, e: model.startswith("HP-100") or model.startswith("HP-110")),
            ]),
            g("concealed-showers", "Concealed Shower Sets", models=[
                m("sanitary", match=lambda model, e: model.startswith("HP-500") and e.get("page", 99) == 6),
            ]),
        ]),
        g("faucets", "Faucets & Valves", subs=[
            g("basin-faucets", "Basin Faucets", models=[
                m("sanitary", match=lambda model, e: model.startswith("HP-200"),),
            ]),
            g("kitchen-faucets", "Kitchen Faucets", models=[
                m("sanitary", match=lambda model, e: model.startswith("HP-210"),),
            ]),
            g("taps-valves", "Bib Taps & Angle Valves", models=[
                m("sanitary", match=lambda model, e: model.startswith("HP-310") or model.startswith("HP-300")),
            ]),
        ]),
        g("hanging-pans", "Hanging Pans (Mop Sinks)", models=[
            m("sanitary", match=lambda model, e: model.startswith("HP-531") and e.get("page") == 16 or model in ("HP-533",)),
        ]),
        g("bathroom-accessories", "Accessory Sets & Floor Drains", models=[
            m("sanitary", match=lambda model, e: model.startswith("HP-600") or model.startswith("HP-800")),
        ]),
    ],

    "track": [
        g("running-tracks", "Running Track Systems", models=[
            m("track", keys=["LP-BREATHABLE","LP-HYBRID","LP-FULLPU","LP-SEMI"]),
            m("catalog", keys=["breathable-running","full-pu-running","hybrid-pu-running","semi-prefabricated"]),
        ]),
        g("court-surfaces", "Court Surfacing", models=[
            m("track", keys=["LP-SILIPU","LP-ACRYLIC-H","LP-ACRYLIC-F"]),
        ]),
        g("rubber-surfaces", "Prefabricated & Poured Rubber", models=[
            m("track", keys=["LP-EPR-5050","LP-EPR-6161","LP-EPDM"]),
            m("catalog", keys=["epr-prefabricated"]),
        ]),
        g("coatings-adhesives", "Coatings & Adhesives", models=[
            m("track", keys=["LP-511","LP-FLOOR-PS","LP-WALL-PS","LP-ANTI-CORR","LP-ASPHALT"]),
        ]),
    ],

    "pv": [
        g("fixed-mounting", "Fixed & Adjustable Mounting", models=[
            m("pv", keys=["HDG-MOUNT","FIXED"]),
            m("catalog", keys=["fixed-and-tracking"]),
        ]),
        g("carports", "Solar Carports", models=[
            m("pv", keys=["CARPORT-1","CARPORT-2","CARPORT-Y"]),
            m("catalog", keys=["solar-pv-carport"]),
        ]),
        g("tracking", "Tracking Systems", models=[
            m("pv", keys=["TRACK-1A","TRACK-SA","TRACK-DA","TRACK-ADJ"]),
        ]),
        g("special-systems", "BIPV, Flexible & Floating", models=[
            m("pv", keys=["BIPV","FLEX","FLOAT"]),
            m("catalog", keys=["special-pv-mounting"]),
        ]),
        g("materials", "Mounting Materials & Components", models=[
            m("pv", keys=["ZAM-TUBE","CZU-PURLIN"]),
            m("catalog", keys=["pv-support-materials"]),
        ]),
    ],

    "storage": [
        g("mobile-storage", "Mobile Storage Robots", models=[
            m("storage", keys=["Tank Mini","Energy Tank 100 Pro","Energy Tank 100 Ultra","Energy Tank 200 Pro"]),
            m("catalog", keys=["energy-tank-100-pro","energy-tank-200-pro"]),
        ]),
        g("pcs-charging", "PCS & Charging Gateways", models=[
            m("storage", keys=["Energy Station 200KW","Energy Flow 100KVA"]),
            m("catalog", keys=["energy-flow-100kva","energy-station-200kw"]),
        ]),
        g("power-packages", "Off-Grid Power Packages", models=[
            m("storage", keys=["ERAERGY-GO","PKG-DLINE","PKG-TEMP"]),
        ]),
    ],

    "heatpump": [
        g("residential-hot-water", "Residential Hot Water", models=[
            m("heatpumps", match=lambda model, e: e.get("book") == "hotwater" and ("split" in e["type"] or "monobloc" in e["type"].lower() or "All-in-one" in e["type"])),
            m("catalog", keys=["domestic-all-in-one"]),
        ]),
        g("residential-heating", "Residential Heating & Cooling Monoblocs", models=[
            m("heatpumps", match=lambda model, e: model.startswith("R290-") or model.endswith("PEN5") or "VRZY" in model or "VBL2ZY" in model or "VPFFS" in model),
            m("catalog", keys=["r290-ultimate","r32-elite"]),
        ]),
        g("evi-cold-climate", "EVI Cold-Climate Systems", models=[
            m("heatpumps", match=lambda model, e: "HVC" in model or "DC-F" in model or ("DCZ1" in model and "EVI" in e["type"]) or model.startswith("RS-400DCZ1V") or "WCBZ" in model or ("BL2NS" in model) or ("B2NS" in model) or ("R2NS" in model)),
        ]),
        g("commercial-hot-water", "Commercial Hot Water", models=[
            m("heatpumps", match=lambda model, e: "DCB" in model or ("DKC" in model or "GD" in model and e["book"] == "ruixing-c") or "UltraHeat" in e["type"] or "BU/" in model or ("DCZ1H" in model and "large" in e["type"]) or "GBCN" in model or "SWC" in model),
            m("catalog", keys=["r290-ultraheat"]),
        ]),
        g("high-temp", "High-Temperature (80C)", models=[
            m("heatpumps", match=lambda model, e: "HTC" in model or "GBCN" in model),
        ]),
        g("pool-spa", "Pool & SPA Heat Pumps", models=[
            m("heatpumps", match=lambda model, e: "CD-Na" in model or "F0" in model and "SPA" in e["type"] or "BCB" in model or "GZ1H" in model or "GCZ1H" in model or "JPCX" in model or "PDYT" in model),
            m("catalog", keys=["herring-inverter-pool"]),
        ]),
        g("commercial-heating", "Commercial Heating & Cooling", models=[
            m("heatpumps", match=lambda model, e: "RZ1" in model or "VB2Z" in model or "VREP" in model or "RELP" in model),
        ]),
        g("tanks", "Buffer & Water Tanks", models=[
            m("heatpumps", match=lambda model, e: "L-B" in model and e["book"] == "hotwater"),
        ]),
    ],

    "heating": [
        g("enamel-elements", "Enamel Heating Elements", models=[
            m("heating", match=lambda model, e: e.get("group") == "enamel"),
            m("catalog", keys=["mr-166-enamel"]),
        ]),
        g("storage-elements", "Storage Water-Heater Elements", models=[
            m("heating", match=lambda model, e: e.get("group") == "storage"),
            m("catalog", keys=["mr-120-storage"]),
        ]),
        g("mini-kitchen", "Mini Kitchen Elements", models=[
            m("heating", match=lambda model, e: e.get("group") == "minikitchen"),
            m("catalog", keys=["mr-002-mini-kitchen"]),
        ]),
        g("instant-elements", "Instant (Tankless) Elements", models=[
            m("heating", match=lambda model, e: e.get("group") == "instant"),
            m("catalog", keys=["mr-43-instant"]),
        ]),
        g("cast-aluminum", "Cast Aluminum Heating Bodies", models=[
            m("heating", match=lambda model, e: e.get("group") == "castalu"),
            m("catalog", keys=["mr-105-cast"]),
        ]),
        g("connecting-pipes", "Stainless Connecting Pipes", models=[
            m("heating", match=lambda model, e: e.get("group") == "pipes"),
        ]),
    ],

    "led": [
        g("movable-posters", "Movable LED Poster Boards", models=[
            m("led", match=lambda model, e: model.startswith("HB-SP") or model in ("P2","P2.5","P3.0")),
            m("catalog", keys=["hb-sp-indoor","outdoor-movable-led-display"]),
        ]),
        g("foldable-updown", "Up-Down Foldable Posters", models=[
            m("led", match=lambda model, e: model.startswith("HB-X") and "XZD" not in model),
            m("catalog", keys=["hb-x-foldable"]),
        ]),
        g("trifold", "Tri-Fold Double-Sided Posters", models=[
            m("led", match=lambda model, e: model.startswith("HB-XZD")),
        ]),
        g("special-displays", "Standalone, Battery & Outdoor", models=[
            m("led", match=lambda model, e: model.startswith("HB-D") or model.startswith("HB-CN") or model.endswith("-OD")),
            m("catalog", keys=["hb-cn-battery"]),
        ]),
    ],

    "robots": [
        g("applications", "Robot Application References", models=[
            m("robots", keys=["ROBOT-PALLETISING"]),
            m("catalog", keys=["robot-carton-palletising"]),
        ]),
        g("machine-tending", "Press & Machine Tending", models=[
            m("robots", keys=["ROBOT-PRESS"]),
            m("catalog", keys=["robot-press-machine"]),
        ]),
    ],

    "apparel": [
        g("sets-lounge", "Sets, Lounge & Dresses", models=[
            m("catalog", keys=["casual-tops-wide-leg","long-sleeve-lounge","tank-top-and-shorts","sleeveless-casual"]),
        ]),
        g("style-gallery", "2026 Style Gallery", "Reference styles from the Dingsheng style sheet; each style is developed to your fabric, size spec and branding requirements.", models=[
            m("apparel", match=lambda model, e: model.startswith("DS-")),
        ]),
    ],

    "jewelry": [
        g("gift-boxes", "Rigid & Wood-Look Gift Boxes", models=[
            m("catalog", keys=["rigid-jewelry-gift","wood-look-jewelry"]),
        ]),
        g("organizers-travel", "Organizers & Travel Cases", models=[
            m("catalog", keys=["book-style-jewelry","travel-jewelry"]),
        ]),
        g("display-props", "Display Trays & Props", models=[
            m("catalog", keys=["jewelry-display-trays"]),
        ]),
    ],

    "eyelashes": [
        g("cluster-trays", "Cluster Lash Trays", models=[
            m("eyelashes", keys=["CN-CL6P","CN-CL10P","CN-CL30P","CN-GLUE","EXP-LASH-A"]),
        ]),
    ],

    "leather": [
        g("handbags", "Lady Handbags", subs=[
            g("totes", "Tote Bags", models=[m("bags", match=lambda model, e: e["type"] == "tote")]),
            g("shoulder", "Shoulder Bags", models=[m("bags", match=lambda model, e: e["type"] == "shoulder")]),
            g("hobo", "Hobo Bags", models=[m("bags", match=lambda model, e: e["type"] == "hobo")]),
            g("crossbody", "Crossbody Bags", models=[m("bags", match=lambda model, e: e["type"] == "crossbody")]),
            g("top-handle", "Top-Handle & Satchel", models=[m("bags", match=lambda model, e: e["type"] == "top-handle")]),
            g("bucket", "Bucket Bags", models=[m("bags", match=lambda model, e: e["type"] == "bucket")]),
            g("clutch", "Clutch & Evening", models=[m("bags", match=lambda model, e: e["type"] == "clutch")]),
            g("backpacks", "Backpacks", models=[m("bags", match=lambda model, e: e["type"] == "backpack")]),
        ]),
        g("belts", "Belts", subs=[
            g("mens-automatic", "Men's Automatic Buckle", models=[m("belts", match=lambda mid, e: mid.startswith("MB") and "-auto" in e["type"])]),
            g("mens-pin", "Men's Pin Buckle Dress & Casual", models=[m("belts", match=lambda mid, e: mid.startswith(("MB","NB25W","B1")) and e["type"].startswith(("mens","unisex")) and "-auto" not in e["type"] and not any(k in e["type"] for k in ("golf","webbing","braided")))]),
            g("mens-sport", "Men's Golf, Webbing & Braided", models=[m("belts", match=lambda mid, e: any(k in e["type"] for k in ("golf","webbing","braided")))]),
            g("womens-skinny", "Women's Skinny Belts", models=[m("belts", match=lambda model, e: e["type"].startswith("womens") and ("skinny" in e["type"] or "micro" in e["type"]))]),
            g("womens-wide", "Women's Wide & Statement", models=[m("belts", match=lambda model, e: e["type"].startswith("womens") and any(k in e["type"] for k in ("wide","corset","asym","double","check")))]),
            g("womens-classic", "Women's Classic & Fashion Hardware", models=[m("belts", match=lambda model, e: e["type"].startswith("womens"))]),
        ]),
        g("small-leather-goods", "Small Leather Goods", subs=[
            g("card-holders", "Card Holders", models=[
                m("slg", match=lambda model, e: e["type"] == "card-holder" or e["type"] == "card-wallet"),
            ]),
            g("key-holders", "Key Holders", models=[m("slg", match=lambda model, e: e["type"] == "key-holder")]),
            g("passport-covers", "Passport Covers", models=[m("slg", match=lambda model, e: e["type"] == "passport-cover")]),
            g("wallets", "Wallets", models=[m("slg", match=lambda model, e: e["type"] in ("short-wallet","long-wallet"))]),
        ]),
    ],

    "lubricants": [
        g("casting-additives", "Casting & Foundry Additives", models=[
            m("lubricants", match=lambda model, e: e.get("group") == "casting"),
            m("catalog", keys=["casting-refining-additives"]),
        ]),
        g("cleaners-degreasers", "Surface Treatment & Degreasers", models=[
            m("lubricants", match=lambda model, e: e.get("group") == "degrease"),
            m("catalog", keys=["industrial-degreasers","rust-prevention-passivation"]),
        ]),
        g("industrial-oils", "Industrial & Metalworking Oils", models=[
            m("lubricants", match=lambda model, e: e.get("group") == "oils"),
            m("catalog", keys=["metalworking-cutting","rolling-drawing"]),
        ]),
    ],
}
