# Research Report: Global AI Data Center Power Capacity & Energy Footprint Reconciliation

## TL;DR
- **MW and TWh are physically different quantities and the single largest source of reconciliation error.** MW is an instantaneous rate (a snapshot of demand); TWh is cumulative energy (rate × time). Converting requires a **load factor** (average-to-peak utilization) and, if the quoted MW is IT load, a **PUE multiplier**. The industry uses wildly different load factors — LBNL models **50%** capacity utilization, while Barclays converts MW→TWh at **85%** utilization — which alone can swing a facility's annualized figure by ~70%.
- **The top hyperscale operators (Google, Microsoft, Meta, Amazon) reported electricity growth above 25% for a second straight year in 2024**, with Google at ~32 TWh and Microsoft at ~30 TWh ([Barclays/Investing.com](https://ca.investing.com/news/stock-market-news/google-microsoft-electricity-demand-jumps-over-25-for-second-year-in-a-row-4088172)). Facility-level campus figures (Stargate, Meta Louisiana, AWS Indiana, xAI Memphis) can be reconciled against utility interconnection filings, which are the most reliable "confirmed" signal.
- **Cooling architecture is the dominant lever on facility PUE.** AI racks now hit 120–200 kW (GB200 NVL72 ~120–130 kW), beyond air cooling's ~20 kW ceiling; direct-to-chip liquid cooling pushes PUE from the legacy air-cooled **1.5–1.8** down to **1.1–1.3**, whereas hyperscale fleets already report **1.09 (Google) to 1.16 (Microsoft)** vs. the global industry average of **1.54–1.56** ([Uptime Institute](https://datacenter.uptimeinstitute.com/rs/711-RIA-145/images/2025.Annual.Survey.Report.pdf)).
- **"Behind-the-meter" generation must be separated from grid draw, and financial PPAs are not the same as physical generation.** xAI's Colossus runs largely off-grid gas turbines (~247 MW permitted on-site), Entergy is building 2,260 MW of dedicated gas for Meta, but Microsoft's 835 MW Three Mile Island deal is a *financial VPPA* — it does **not** physically reduce grid draw. Conflating these systematically over- or under-states true grid load.
- **Confirmed vs. speculative divergence is severe.** Abilene's announced "up to 4.5 GW" Stargate network and even a "600 MW expansion" have been walked back; only ~1.2 GW of campus power delivery is engineered and approved. Your dataset must carry **phase status** and **variance flags** rather than averaging announced and energized capacity.

---

## Detailed Findings

### 1. Unit Primer for Policy Readers: Power (MW) vs. Energy (TWh) vs. Efficiency (PUE)

These three units answer three different questions and are frequently conflated in press coverage:

| Quantity | Unit | Physical meaning | Plain-language analogy |
|---|---|---|---|
| **Power capacity** | MW (or GW, kW) | The *rate* at which a facility can draw/consume electricity at an instant | Speedometer reading (how fast, right now) |
| **Energy consumption** | MWh / GWh / TWh | Power delivered *accumulated over time* | Odometer reading (total distance driven) |
| **PUE** | dimensionless ratio (≥1.0) | Total facility energy ÷ energy reaching IT equipment | Overhead factor on every unit of compute |

The conversion is the crux of the entire challenge:

```
1 MW held constant for 1 year = 1 MW × 8,760 hours = 8,760 MWh = 0.00876 TWh
```

A facility drawing an average load of 1 MW continuously consumes 24 MWh/day or 8,760 MWh/year ([SPS Sales](https://www.sps-sales.com/blog/data-center-energy-consumption)). Critically, **a "100 MW data center" is ambiguous** — the noun attached to MW matters: connection capacity, facility demand, IT load, installed equipment, peak draw, average draw, backup power, or ultimate buildout are all different numbers ([Policloud](https://www.policloud.com/post/data-center-power-consumption)). Their worked example is the canonical illustration of why single-source MW→TWh conversions fail:

| Interpretation of "100 MW" | Annual energy | Assumptions |
|---|---|---|
| Nameplate max (100 MW × 8,760 h) | **876 GWh** | 100% load factor |
| Average 70 MW across year | **613 GWh** | 70% load factor |
| Early Phase-1 (avg 35 MW) | **307 GWh** | 35% load factor |

**Product implication:** Your schema must store the *load-factor basis* and the *capacity definition* as first-class columns, or downstream users will silently compare a peak-interconnection number to a phase-1 average-draw number.

---

### 2. The Standardized Normalization Framework (Conversion Formulas)

To reconcile disparate MW and TWh figures, apply this master equation. This should be encoded as explicit, testable functions in your submission:

```
E_TWh = ( C_MW × PUE_factor × 8,760 × LF ) / 1,000,000

Where:
  C_MW      = quoted power capacity (MW)
  PUE_factor = PUE multiplier  → include ONLY if C_MW is IT/critical load
               (omit, i.e. = 1.0, if C_MW is already facility/grid total demand)
  8,760     = hours per year
  LF        = load factor (average draw ÷ peak draw), dimensionless 0–1
  ÷1,000,000 = MWh → TWh conversion
```

Two load-factor conventions dominate the literature and must be flagged, not blended:

| Convention source | Load/utilization assumption | Use case |
|---|---|---|
| **LBNL 2024 U.S. report** | **50%** average capacity utilization → 74–132 GW for 325–580 TWh | Conservative, all-data-center fleet modeling ([LBNL](https://eta-publications.lbl.gov/sites/default/files/2024-12/lbnl-2024-united-states-data-center-energy-usage-report_1.pdf)) |
| **Barclays (analyst)** | **85%** utilization → 17 TWh ≈ 2.3 GW | Hyperscaler incremental capacity ([Barclays](https://ca.investing.com/news/stock-market-news/google-microsoft-electricity-demand-jumps-over-25-for-second-year-in-a-row-4088172)) |
| **Guidi et al. (Baxtel, 2,000+ DCs)** | **75%** uniform utilization | Academic estimate (193 TWh 2023); likely *overestimates* per IEA-4E review ([IEA-4E](https://www.iea-4e.org/wp-content/uploads/2025/05/Data-Centre-Energy-Use-Critical-Review-of-Models-and-Results.pdf)) |
| **AI server operational time (LBNL)** | **75–85%** of the year for AI servers specifically | Operation-energy sub-model (240–380 TWh) |

**PUE factorization worked example** ([Policloud](https://www.policloud.com/post/data-center-power-consumption)):
- Facility supporting **80 MW IT load at PUE 1.25 → ~100 MW total** facility demand.
- If a project instead claims **100 MW of IT capacity at PUE 1.25 → ~125 MW total** grid requirement.

This is a recurring Phase-1-vs-full-buildout and IT-vs-facility discrepancy source — the difference between quoting IT load and total facility load is exactly one PUE factor (~9–56% depending on cooling).

---

### 3. Facility-Level Reconciliation Dataset (8+ Global Campuses)

The table below separates **confirmed/energized** capacity from **announced/full-buildout**, records the load definition, and flags behind-the-meter (BTM) generation. This is the core evidence base for your CSV.

| # | Facility (Owner / Partner) | Utility / Interconnection | Capacity (confirmed → announced) | Load basis | Status / Phase | BTM / Dedicated generation | Key sources |
|---|---|---|---|---|---|---|---|
| 1 | **Stargate Abilene** (OpenAI / Oracle / Crusoe; Lancium Clean Campus, TX) | AEP / ERCOT; 200 MW substation (Lancium, expandable 5×); 1,200 MW full power delivery approved | 1.2 GW campus engineered; "up to 4.5 GW" network announced; 600 MW expansion **cancelled** | Facility total | 1 building operational, 2nd near-complete (Sep 2025); "past 1 GW" ultimate potential | 360.5 MW on-site gas (Crusoe "Project Ludicrous"), 24/7 | [CNBC](https://www.cnbc.com/2025/09/23/openai-first-data-center-in-500-billion-stargate-project-up-in-texas.html), [ESIG/Lancium](https://www.esig.energy/wp-content/uploads/2025/05/ESIG_LLTF_PresentationLancium.pdf), [Enverus](https://www.enverus.com/blog/stargate-scales-back-openai-and-oracle-abandon-data-center-expansion), [Business Insider](https://www.businessinsider.com/stargate-data-center-powered-by-natural-gas-2025-1) |
| 2 | **Meta Richland Parish / Franklin Farm** (Meta, LA) | Entergy Louisiana; 2,260 MW combined-cycle (3 CTs); ~100 mi 500 kV + 8 × 230 kV lines | **2 GW "compute" IT (initial phase)**; total campus reported up to ~5 GW | **IT load** (explicitly excludes cooling) | Generators online 2028–2029; largest Meta DC (>4M sq ft) | Dedicated Entergy gas (2,260 MW), grid-connected, ~$2B gen cost | [Entergy](https://www.entergy.com/news/entergy-louisiana-power-meta-s-data-center-in-richland-parish), [Yahoo/Entergy](https://finance.yahoo.com/news/entergy-expects-data-centers-drive-083705752.html) |
| 3 | **xAI Colossus 1** (xAI, South Memphis, TN) | MLGW / TVA; initial **8 MW** grid → **150 MW** (Nov 2024); second site request up to **1.1 GW** | 150 MW utility feed; **>300 MW IT compute** | Mixed (grid + BTM) | Live July 2024; grid tie conditioned on **aggressive demand response** | ~247 MW permitted on-site gas (15 × Solar SMT-130); ~35 turbines observed; Colossus 2 adds ~495 MW in MS | [GEM](https://www.gem.wiki/Colossus_1_power_station), [DCD](https://www.datacenterdynamics.com/en/news/xai-removes-some-of-controversial-gas-turbines-from-memphis-data-center), [Measured AI](https://measuredai.substack.com/p/xai-colossus-data-center-cluster), [SELC](https://www.selc.org/news/xai-built-an-illegal-power-plant-to-power-its-data-center) |
| 4 | **AWS Project Rainier** (Amazon / Anthropic, New Carlisle, IN) | Indiana Michigan Power (AEP); largest customer in I&M history | **2.25 GW utility draw / ~1.96 GW IT** across 3 phases; ~30 buildings | Facility (utility) + IT | First ~500 MW online June 2025; 7 buildings now, 30 planned | Primarily **air-cooled** (chiller-free; only 2% of year needs water); thin PUE margin | [Measured AI](https://measuredai.substack.com/p/aws-new-carlisle-data-center-campus), [CNBC](https://www.cnbc.com/2025/10/29/amazon-opens-11-billion-ai-data-center-project-rainier-in-indiana.html), [Yahoo/I&M](https://finance.yahoo.com/news/indiana-michigan-power-amazon-google-082940475.html) |
| 5 | **Microsoft Fairwater Wisconsin** (Microsoft, Mount Pleasant, WI) | Wisconsin Electric Power Co. | ~**450–500 MW** campus ($3.3B initial); ramp 50→100→200→400→500 MW | Facility total | Going live early–mid 2026; 1.2M sq ft, 315 acres | Grid-supplied | [datacenter.fyi](https://www.datacenter.fyi/facility/microsoft-fairwater-wisconsin-wi-a2ef4c99), [UBS/Yahoo](https://finance.yahoo.com/news/microsofts-azure-poised-for-fairwater-boost-151956045.html), [Glenn Klockwood](https://www.glennklockwood.com/garden/systems/fairwater) |
| 6 | **Microsoft / Constellation Crane (Three Mile Island Unit 1)** | PJM (generation supply, not a campus) | **835 MW** nuclear, 100% contracted | Generation | 20-yr PPA (Sep 2024); restart targeted 2027; $1.6B restart | **Financial VPPA** — does NOT physically cut grid draw; reshapes market accounting | [Constellation/Construction Review](https://constructionreviewonline.com/us1-billion-loan-for-crane-clean-energy-center-as-constellation-revives-the-835-mw-three-mile-island-nuclear-reactor), [Yahoo/Meta-Constellation VPPA](https://finance.yahoo.com/news/meta-constellation-virtual-ppa-could-105848961.html) |
| 7 | **Google (global fleet)** | Multiple | ~32 TWh/yr total (2024, +27% YoY) | Energy (reported) | Ongoing | Mixed PPA / CFE procurement | [DCD/Google](https://www.datacenterdynamics.com/en/news/google-data-center-power-use-up-27-emissions-down-17-report), [Google Env Report](https://www.smartenergydecisions.com/wp-content/uploads/2025/07/google-2025-environmental-report-1.pdf) |
| 8 | **Microsoft (global fleet)** | Multiple | ~30 TWh/yr (FY24, +27% YoY) | Energy (reported) | Ongoing | Crane + other | [Barclays/Investing.com](https://ca.investing.com/news/stock-market-news/google-microsoft-electricity-demand-jumps-over-25-for-second-year-in-a-row-4088172) |

> **Confirmed-interconnection vs. speculative takeaway:** The facilities with **executed utility agreements and energized load** are xAI Colossus 1 (150 MW MLGW/TVA), AWS New Carlisle (I&M, ramping), Microsoft Fairwater (WEPC), and Meta Richland Parish (Entergy, under construction with a CPCN-style generation commitment). Stargate Abilene's 1.2 GW campus is engineered/approved, but the broader "4.5 GW network" and the cancelled 600 MW expansion are **announcements, not interconnections**. This mirrors the structural finding that **interconnection queues are inflated** by speculative large-load requests ([Enverus](https://www.enverus.com/blog/stargate-scales-back-openai-and-oracle-abandon-data-center-expansion)).

---

### 4. Cooling Architecture and Its Effect on PUE and Grid Draw

Rack power density has outgrown air cooling, forcing a cooling transition that directly changes the PUE factor in the normalization equation.

**Rack density and cooling threshold bands** ([Network World](https://www.networkworld.com/article/4149069/why-ai-rack-densities-make-liquid-cooling-nonnegotiable.html), [Accelsius](https://accelsius.com/data-center-liquid-cooling), [Ariat-tech](https://www.ariat-tech.com/blog/AI-Data-Center-Power-Requirements-Rack-Density%2CCooling%2CPUE%2Cand-Grid-Capacity.html)):

| Cooling method | Practical density ceiling |
|---|---|
| Air cooling | up to ~20 kW/rack |
| Rear-door heat exchangers (RDHx) | up to ~100 kW |
| Direct-to-chip liquid cooling (DLC) | ~100–175 kW |
| Immersion | >175 kW |

**Chip/rack trajectory** ([Network World](https://www.networkworld.com/article/4149069/why-ai-rack-densities-make-liquid-cooling-nonnegotiable.html), [Canovate](https://www.youtube.com/watch?v=TRMZjxU_czE)):

| Generation | Per-chip power / rack power |
|---|---|
| NVIDIA A100 (2020) | 400 W/chip |
| NVIDIA H100 | 700 W/chip |
| NVIDIA B200 | 1,000 W/chip |
| GB200 NVL72 rack | ~120–130 kW/rack total |
| Next-gen DLC design | up to 200 kW/rack |

**PUE by cooling approach** ([ToneCooling](https://tonecooling.com/data-center-pue-optimization-liquid-cooling)):

| Cooling approach | Typical PUE |
|---|---|
| Traditional air-cooled (legacy) | **1.5–1.8** |
| Rear-door heat exchanger (RDHx) | **1.2–1.3** |
| Full direct-to-chip liquid cooling | **<1.10** |

The reason DLC lowers PUE: it eliminates energy-intensive CRAC/CRAH air handlers and enables higher coolant temperatures (35–45 °C) suitable for free cooling or heat reuse ([ToneCooling](https://tonecooling.com/data-center-pue-optimization-liquid-cooling)). Liquid removes heat ~1,000× more effectively than air by volume ([Accelsius](https://accelsius.com/data-center-liquid-cooling)).

**Grid-draw implication:** A ~1.96 GW IT AI campus (like AWS Rainier) at air-cooled PUE (~1.15–1.25, thin margin because chiller-free) draws ~2.25 GW from the grid; the same IT load on full DLC at PUE ~1.1 would draw ~2.16 GW. The ~4–9% swing is material at gigawatt scale (≈90–150 MW of avoided grid capacity).

---

### 5. Grid-Supplied Electricity vs. Behind-the-Meter (BTM) Generation

For grid operators, the **location of generation** relative to the meter is the decisive distinction. Three archetypes appear in the evidence:

| Archetype | Example | Physical effect on grid draw | Accounting caveat |
|---|---|---|---|
| **On-site BTM gas** | xAI Colossus (~247 MW permitted turbines; ~495 MW at Colossus 2, MS) | Reduces grid import; grid tie only 150 MW with mandatory demand response | Emissions shift to facility air permits (NOx cap 87.14 tons/yr); frequently unpermitted at first ([SELC](https://www.selc.org/news/xai-built-an-illegal-power-plant-to-power-its-data-center), [GEM](https://www.gem.wiki/Colossus_1_power_station)) |
| **Utility-built dedicated generation** | Entergy's 2,260 MW CCGT for Meta | Grid-connected; adds firm supply *and* load to the same balancing area | Ratepayer cost allocation debated; still counts as grid electricity ([Yahoo/Entergy](https://finance.yahoo.com/news/entergy-breaks-ground-power-facility-224359619.html)) |
| **Financial (virtual) PPA** | Microsoft–Constellation 835 MW Crane | **No physical reduction in grid draw**; reshapes market/renewable accounting | Must NOT be subtracted from location-based grid load — a top reconciliation trap ([Yahoo/Meta-Constellation VPPA](https://finance.yahoo.com/news/meta-constellation-virtual-ppa-could-105848961.html)) |

**Data-model implication:** Your schema should carry a `generation_type` enum (grid / BTM-thermal / dedicated-utility / financial-PPA) and a `location_based_vs_market_based` flag. IEA separately models **consumption** (415 TWh in 2024) and **generation supply** (460 TWh in 2024, higher due to T&D losses and self-generation) — a gap your dataset should reproduce rather than collapse ([IEA Energy Supply](https://www.iea.org/reports/energy-and-ai/energy-supply-for-ai)).

---

### 6. Macro Reconciliation: Why Aggregate Estimates Diverge So Much

Independent studies agree on direction but disagree widely on magnitude — the spread *is* the story.

| Source | Year(s) | Metric | Figure | Notes |
|---|---|---|---|---|
| **IEA** | 2024 | Global DC consumption | ~415 TWh | Consumption basis |
| **IEA (Base Case)** | 2030 | Global DC consumption | **~945 TWh** | ~15%/yr; <3% of global elec. |
| **IEA (Headwind)** | 2030 | Global | ~670 TWh | Trade-war downside scenario |
| **IEA (Base / Lift-Off)** | 2035 | Global generation | ~1,200 TWh / ~2,000 TWh | Supply basis |
| **LBNL (US)** | 2023 | U.S. DC | **176 TWh** (4.4% of U.S.) | Up from 58 TWh in 2014 |
| **LBNL (US)** | 2028 | U.S. DC | **325–580 TWh** (6.7–12%); **74–132 GW** | Range driven by 50% util. + cooling scenarios |
| **Nature Sustainability** | 2024→2030 | Top-6 hyperscalers | ~118 → 239–295 TWh | CAGR 13–17% |
| **Barclays** | 2024 | GOOG+MSFT+META add | +17 TWh ≈ 2.3 GW @85% | Incremental only |

Sources: [IEA Executive Summary](https://www.iea.org/reports/energy-and-ai/executive-summary), [IEA Energy Demand](https://www.iea.org/reports/energy-and-ai/energy-demand-from-ai), [IEA Headwind/Yahoo](https://ca.finance.yahoo.com/news/global-trade-war-may-produce-040819748.html), [LBNL Report](https://eta-publications.lbl.gov/sites/default/files/2024-12/lbnl-2024-united-states-data-center-energy-usage-report_1.pdf), [DOE](https://www.energy.gov/articles/doe-releases-new-report-evaluating-increase-electricity-demand-data-centers), [Nature](https://www.nature.com/articles/s44458-026-00152-5).

**Root causes of divergence** (documented by the IEA-4E critical review):
1. **Utilization-rate assumptions** — uniform 75% (Guidi) vs. 50% (LBNL) vs. 85% (Barclays) drive most of the spread.
2. **Peak-power vs. TDP** — assuming racks run at nameplate TDP 100% of the time inflates estimates; realistic peak < TDP and load < 100% ([IEA-4E](https://www.iea-4e.org/wp-content/uploads/2025/05/Data-Centre-Energy-Use-Critical-Review-of-Models-and-Results.pdf)).
3. **AI share uncertainty** — AI-specific TWh estimates range from ~85 TWh (2024) toward ~430 TWh (2030) across sources ([Presenc AI](https://presenc.ai/research/ai-data-center-energy-consumption-2026)).
4. **U.S. concentration** — U.S. + China account for **~80%** of global data-center demand growth to 2030; U.S. alone +240 TWh (+130%), China +175 TWh (+170%), Europe +45 TWh (+70%), Japan +15 TWh (+80%) ([IEA Energy Demand](https://www.iea.org/reports/energy-and-ai/energy-demand-from-ai)).

**Operator fleet PUE benchmarks** (for the PUE-factor column defaults):

| Operator / class | PUE | Source |
|---|---|---|
| Google fleet (2024) | **1.09** (TTM 1.10–1.11) | [Google](https://datacenters.google/efficiency) |
| Microsoft global (FY24/FY25) | **1.16 / 1.17** | [Microsoft](https://datacenters.microsoft.com/sustainability/efficiency) |
| AWS global (2024) | **1.15** (best EU site 1.04) | [Holdfast](https://www.holdfastprojects.com/us-datacentre-pue.md-2) |
| Industry average (Uptime 2024 / 2025) | **1.56 / 1.54** | [Uptime](https://datacenter.uptimeinstitute.com/rs/711-RIA-145/images/2025.Annual.Survey.Report.pdf) |
| Recent builds (~2020+) | **1.48** | Uptime 2025 |
| Large DCs (≥20 MW) | **1.44** | Uptime 2025 |

Note the tension: hyperscalers report ~1.1 PUE, but the *survey-weighted* industry average sits near 1.54 because it is dominated by legacy facilities. **Which PUE you plug into the normalization equation is itself a reconciliation decision that must be flagged.**

---

### 7. Recommended CSV Schema & Variance-Flagging Design

To satisfy the challenge's rigor requirements, emit a machine-readable facility dataset with these columns (unit-normalized) plus explicit variance annotations:

```csv
facility_id,facility_name,owner,region,utility_ipo,country,
capacity_mw_confirmed,capacity_mw_announced,load_basis,pue,
grid_supply_mw,btm_generation_mw,generation_type,
phase_status,energized_date,load_factor_low,load_factor_high,
twh_year_low,twh_year_high,source_primary,source_secondary,
variance_flag,notes
```

**Formula columns (document in a companion equations file):**
- `twh_year = capacity_mw × (pue_if_IT else 1) × 8760 × load_factor / 1,000,000`
- Emit `twh_year_low` at LF=0.50 (LBNL convention) and `twh_year_high` at LF=0.90 (high-inference convention) to bracket uncertainty.

**Variance-flag taxonomy (never silently average conflicting sources):**
- `PHASE_MISMATCH` — one source reports Phase-1 (e.g., AWS 500 MW) vs. another full-buildout (2.25 GW).
- `IT_VS_FACILITY` — Meta's "2 GW compute" (IT) vs. Entergy's 2,260 MW (facility total).
- `CONFIRMED_VS_ANNOUNCED` — Abilene 1.2 GW engineered vs. 4.5 GW network announced vs. 600 MW expansion cancelled.
- `GRID_VS_BTM` — xAI 150 MW grid vs. ~400 MW total including on-site gas.
- `FINANCIAL_PPA_NOT_PHYSICAL` — Microsoft–Crane 835 MW is a VPPA, excluded from location-based grid load.
- `LF_ASSUMPTION` — flags which utilization rate produced a given TWh.

---

### 8. 2028 Sensitivity Modeling (70% vs. 90% Inference Load)

Applying the master formula to the confirmed capacities demonstrates the sensitivity the challenge asks for. Example: **AWS New Carlisle at full 2.25 GW** and **Meta Richland at 2 GW IT × PUE 1.2**:

| Facility / basis | LF = 0.50 | LF = 0.70 | LF = 0.85 | LF = 0.90 |
|---|---|---|---|---|
| AWS New Carlisle (2,250 MW grid) | 9.86 TWh | 13.80 TWh | 16.75 TWh | 17.74 TWh |
| Meta Richland (2,000 MW IT × PUE 1.2 = 2,400 MW) | 10.51 TWh | 14.72 TWh | 17.87 TWh | 18.92 TWh |
| Stargate Abilene (1,200 MW campus) | 5.26 TWh | 7.36 TWh | 8.93 TWh | 9.46 TWh |

*(Computed via E_TWh = MW × PUE × 8,760 × LF ÷ 1,000,000.)*

**Reading for grid operators:** shifting a single gigawatt-scale campus from 70% to 90% utilization adds **~1.9–2.0 TWh/yr** — roughly the annual consumption of ~170,000–180,000 U.S. homes at ERCOT's rough conversion (1 MW ≈ 250 peak residential customers) ([Business Insider/ERCOT](https://www.businessinsider.com/stargate-data-center-powered-by-natural-gas-2025-1)). The aggregate LBNL 2028 band of **325–580 TWh** is essentially this LF/PUE sensitivity scaled to the entire U.S. fleet.

---

## Key Sources
- [LBNL — 2024 United States Data Center Energy Usage Report (PDF)](https://eta-publications.lbl.gov/sites/default/files/2024-12/lbnl-2024-united-states-data-center-energy-usage-report_1.pdf) — primary U.S. benchmark: 176 TWh (2023) → 325–580 TWh / 74–132 GW (2028).
- [DOE — 2024 Report on U.S. Data Center Energy Use](https://www.energy.gov/articles/doe-releases-new-report-evaluating-increase-electricity-demand-data-centers) — official confirmation of LBNL figures.
- [IEA — Energy and AI, Executive Summary](https://www.iea.org/reports/energy-and-ai/executive-summary) & [Energy Demand from AI](https://www.iea.org/reports/energy-and-ai/energy-demand-from-ai) — 415 TWh (2024) → 945 TWh (2030) base case; regional breakdown.
- [IEA-4E — Critical Review of Data Centre Energy Models (PDF)](https://www.iea-4e.org/wp-content/uploads/2025/05/Data-Centre-Energy-Use-Critical-Review-of-Models-and-Results.pdf) — documents utilization-rate assumptions (50/75/85%) driving divergence.
- [Nature — Communications Sustainability, AI data centers ~1% of global demand](https://www.nature.com/articles/s44458-026-00152-5) — top-6 hyperscaler 118 → 239–295 TWh by 2030.
- [Entergy Louisiana — Meta Richland Parish announcement](https://www.entergy.com/news/entergy-louisiana-power-meta-s-data-center-in-richland-parish) — 2,260 MW dedicated CCGT; 2 GW IT "compute" basis.
- [Measured AI — AWS New Carlisle / Project Rainier](https://measuredai.substack.com/p/aws-new-carlisle-data-center-campus) — 2.25 GW grid / 1.96 GW IT, I&M largest-ever load.
- [Global Energy Monitor — Colossus 1 power station](https://www.gem.wiki/Colossus_1_power_station) & [DCD — xAI gas turbines](https://www.datacenterdynamics.com/en/news/xai-removes-some-of-controversial-gas-turbines-from-memphis-data-center) — 8→150 MW grid tie, ~247 MW BTM gas.
- [ESIG/Lancium — Abilene Clean Campus (PDF)](https://www.esig.energy/wp-content/uploads/2025/05/ESIG_LLTF_PresentationLancium.pdf) & [CNBC — Stargate Abilene](https://www.cnbc.com/2025/09/23/openai-first-data-center-in-500-billion-stargate-project-up-in-texas.html) & [Enverus — scaled-back expansion](https://www.enverus.com/blog/stargate-scales-back-openai-and-oracle-abandon-data-center-expansion) — 1.2 GW engineered vs. announced network; 600 MW expansion cancelled.
- [Google — Data Center PUE efficiency page](https://datacenters.google/efficiency) & [Google 2025 Environmental Report](https://www.smartenergydecisions.com/wp-content/uploads/2025/07/google-2025-environmental-report-1.pdf) — fleet PUE 1.09; ~32 TWh (+27%).
- [Microsoft — Datacenter efficiency (PUE/WUE)](https://datacenters.microsoft.com/sustainability/efficiency) — global PUE 1.16 (FY24).
- [Uptime Institute — 2024](https://datacenter.uptimeinstitute.com/rs/711-RIA-145/images/2024.GlobalDataCenterSurvey.Report.pdf) & [2025 Global Data Center Survey (PDF)](https://datacenter.uptimeinstitute.com/rs/711-RIA-145/images/2025.Annual.Survey.Report.pdf) — industry-average PUE 1.56 / 1.54; ≥20 MW DCs at 1.44.
- [Network World — AI rack densities & liquid cooling](https://www.networkworld.com/article/4149069/why-ai-rack-densities-make-liquid-cooling-nonnegotiable.html) & [ToneCooling — PUE by cooling type](https://tonecooling.com/data-center-pue-optimization-liquid-cooling) — cooling bands and PUE (air 1.5–1.8 → DLC <1.10).
- [Policloud — Power vs. energy & PUE factorization](https://www.policloud.com/post/data-center-power-consumption) — canonical MW→TWh worked examples and load-factor logic.
- [Yahoo/Investing — Barclays hyperscaler electricity note](https://ca.investing.com/news/stock-market-news/google-microsoft-electricity-demand-jumps-over-25-for-second-year-in-a-row-4088172) — 85% utilization conversion; +17 TWh ≈ 2.3 GW.
- [Constellation/Construction Review — Crane Clean Energy Center (835 MW)](https://constructionreviewonline.com/us1-billion-loan-for-crane-clean-energy-center-as-constellation-revives-the-835-mw-three-mile-island-nuclear-reactor) & [Meta–Constellation VPPA analysis](https://finance.yahoo.com/news/meta-constellation-virtual-ppa-could-105848961.html) — financial VPPA vs. physical generation distinction.