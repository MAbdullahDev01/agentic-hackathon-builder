# Research Report: Health Monitoring Software for Astronauts on Space Missions

## TL;DR
- **Design for Earth-Independent Autonomy:** While ISS crews rely on real-time Flight Surgeon support, deep-space missions (Moon/Mars) face >20-minute one-way communication delays, requiring Level of Care (LoC) V autonomous Clinical Decision Support Systems (CDSS) that enable non-physician crews to detect, diagnose, and treat conditions independently ([npj Microgravity](https://www.nature.com/articles/s41526-023-00284-1), [NASA NTRS](https://ntrs.nasa.gov/citations/20205011448)).
- **Anchor Metrics to Real On-Orbit Hardware:** Your software should ingest and interpret data matching actual spacecraft instruments—specifically **2-minute blood chemistry panels** (Abbott i-STAT), **handheld single-probe ultrasound** (Butterfly iQ), **wearable ECG/SpO2 garments** (CSA Bio-Monitor/Astroskin), **Amsler Grid/ocular checks** (for SANS), and **3-minute Psychomotor Vigilance Tests** (PVT-B) ([NASA](https://www.nasa.gov/missions/station/ultrasound-scans-in-space-transform-medicine-on-earth), [Hexoskin](https://hexoskin.com/pages/astroskin), [Abbott](https://www.globalpointofcare.abbott/us/en/product-details/apoc/i-stat-system-us.html)).
- **Prioritize High-Risk Spaceflight Syndromes with Quantitative Thresholds:** Focus body-map visualizations and trend charts on bone loss (**1–1.5%/month**), Spaceflight-Associated Neuro-ocular Syndrome (**~70%** of ISS astronauts show posterior eye swelling), radiation (**600 mSv** career limit), cabin $\text{ppCO}_2$ (**≤3 mmHg** 1-hr limit), and sleep/fatigue (**<6 hrs/day** for 3+ days degrades vigilance) ([NASA](https://www.nasa.gov/reference/fundamentals-of-human-health), [NASA OCHMO](https://www.nasa.gov/wp-content/uploads/2023/12/ochmo-tb-004-carbon-dioxide.pdf), [NASA NTRS](https://ntrs.nasa.gov/api/citations/20090029851/downloads/20090029851.pdf)).
- **Follow NASA-STD-3001 UI & Alerting Rules:** Use standardized **Green / Amber-Yellow / Red** status indicators paired with **redundant non-color cues** (icons, text labels, audio alerts) as required by NASA Crew Interface standards, and pair every off-nominal alert with step-by-step guided countermeasures (e.g., ARED, fluid loading, LBNP) ([NASA STD-3001 Vol 2](https://www.nasa.gov/reference/10-0-crew-interfaces-vol-2)).

---

## Detailed Findings

### 1. Spaceflight Hazards & Physiological Risk Matrix
NASA’s Human Research Program (HRP) organizes health risks around five interacting hazards: **Space Radiation, Isolation and Confinement, Distance from Earth, Gravity Fields (microgravity to partial gravity), and Hostile/Closed Environments** ([NASA HRP Hazards](https://www.nasa.gov/hrp/hazards), [NASA HRP Risks](https://www.nasa.gov/hrp/risks)). For an interactive human-body UI, each anatomical region should map directly to these mission-specific physiological risks:

| Body System / Region | Primary Spaceflight Hazard | Key Condition & Quantitative Impact | Product / UI Implication |
| :--- | :--- | :--- | :--- |
| **Eyes & Brain (CNS)** | Microgravity fluid shift, $\text{CO}_2$, radiation | **SANS:** ~70% of ISS astronauts show some posterior eye swelling; 15–20% develop clinically concerning optic disc edema, globe flattening, or hyperopic shifts ([NASA SANS](https://www.nasa.gov/reference/risk-of-spaceflight-associated-neuro-ocular-syndrome-sans), [Ophthalmology Times](https://www.ophthalmologytimes.com/view/potential-risk-factors-for-severe-spaceflight-associated-neuro-ocular-syndrome)). | Clickable head/eye node with interactive **Amsler Grid** self-check, vision refraction logger, and optic nerve sheath ultrasound upload. |
| **Musculoskeletal** | Gravity unloading | **Osteopenia & Atrophy:** 1–1.5% bone mineral density (BMD) loss/month; spine elongates up to 3%; muscle loses up to 30% mass and 50% strength without countermeasures ([NASA](https://www.nasa.gov/reference/risk-of-spaceflight-induced-bone-changes), [Physiological Effects Review](https://www.academia.edu/35864615/The_physiological_effects_of_human_spaceflight)). | Track cumulative mission BMD risk trajectory, spinal stretch, and daily **2-hour ARED/T2/CEVIS** exercise compliance. |
| **Cardiovascular & Fluids** | Microgravity & reentry G-loads | **Deconditioning & Orthostatic Intolerance:** Cephalic fluid shift, reduced plasma volume, decreased heart rate, and post-flight syncope risk ([npj Microgravity](https://www.nature.com/articles/s41526-024-00389-1), [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9018660)). | Monitor resting HR, HRV, BP trends, and trigger **fluid-loading countdowns** before EVA or planetary landing. |
| **Renal / Urinary** | Microgravity calcium excretion | **Renal Stones & Retention:** Hypercalciuria from bone resorption plus urine supersaturation elevates kidney stone risk ([NASA](https://www.nasa.gov/reference/fundamentals-of-human-health), [ISS National Lab](https://issnationallab.org/iss360/human-health-on-the-space-station)). | Hydration tracker (mL/day), urine dipstick/chemistry log, and alerts for flank pain + hematuria. |
| **Immune & Hematologic** | Radiation, stress, closed habitat | **Immune Dysregulation & Latent Virus Reactivation:** Suppressed cell-mediated immunity + altered microbial virulence in closed loops ([NASA HRP](https://www.nasa.gov/hrp/risks), [ISS National Lab](https://issnationallab.org/iss360/human-health-on-the-space-station)). | Log skin rashes, fever, hematology counts, and environmental swab/air anomalies. |
| **Behavioral & Cognitive** | Isolation, circadian shift, workload | **Fatigue & Performance Decline:** ISS crew sleep averages ~6.38–6.42 hrs/night; cognitive speed/accuracy drops during extended wakefulness or high $\text{CO}_2$ ([KBR/NASA Study](https://www.kbr.com/en/document/16756), [NASA NTRS](https://ntrs.nasa.gov/api/citations/20090029851/downloads/20090029851.pdf)). | Built-in **3-minute PVT-B** reaction test and mood/sleep check-ins with gamified streak rewards. |

---

### 2. Measurable Health Indicators & On-Orbit Diagnostic Hardware
Rather than inventing fictional sensors, your tool should reflect what crews actually measure using the **ISS Crew Health Care System (CHeCS)** and next-generation deep-space kits ([JAXA](https://humans-in-space.jaxa.jp/en/biz-lab/med-in-space/healthcare/medops/system)):

1. **Point-of-Care Blood Chemistry (Abbott i-STAT 1):**
   - **Specs:** ~0.5 kg handheld analyzer; requires **2–3 drops of whole blood** and yields lab-grade results in **~2 minutes** ([NASA NTRS](https://ntrs.nasa.gov/api/citations/20100011008/downloads/20100011008.pdf), [Abbott](https://www.globalpointofcare.abbott/us/en/product-details/apoc/i-stat-system-us.html)).
   - **Measurable Indicators:** Blood gases ($\text{pH}$, $\text{pCO}_2$, $\text{pO}_2$), electrolytes ($\text{Na}^+$, $\text{K}^+$, $\text{Cl}^-$), glucose, lactate, renal panel (BUN, creatinine), hematocrit/hemoglobin, and cardiac **troponin** ([Henry Schein / Abbott](https://www.henryschein.com/us-en/medical/products/manufacturer-showcase/abbott-i-stat-1.aspx)).
   - *Design Note:* Because i-STAT derives hemoglobin from hematocrit via conductometry (which can be skewed in microgravity), ISS CARDIOLAB supplements it with a dedicated hemoglobinometer/centrifuge—a great "guided instruction" tip to show in your app ([NASA NTRS](https://ntrs.nasa.gov/api/citations/20100011008/downloads/20100011008.pdf)).
2. **Portable Single-Probe Ultrasound (Butterfly iQ / iQ+ / iQ3):**
   - **Specs:** Semiconductor *Ultrasound-on-Chip* replaces multiple piezoelectric probes with a single handheld probe connected to a tablet/PC across iOS, Windows, and Linux ([Butterfly Network](https://www.butterflynetwork.com), [TrialX](https://trialx.com/cross-platform-ultrasound-space-health)).
   - **Space Use (ADUM Protocol):** Non-physician astronauts perform guided scans of the **optic nerve sheath** (for SANS), **internal jugular vein** (for thrombosis/stasis), **bladder/kidneys** (for retention/stones), **lungs** (pneumothorax), and **heart** ([NASA](https://www.nasa.gov/missions/station/ultrasound-scans-in-space-transform-medicine-on-earth)).
   - *Design Note:* Support **camera/image upload** in your software with an overlay guide showing target probe placement and anatomical landmarks.
3. **Continuous Wearable Biometrics (CSA Bio-Monitor / Hexoskin Astroskin):**
   - **Specs:** Sensor-embedded smart garment + headband capturing **3-lead ECG (250 Hz, 97% accuracy)**, respiratory inductance plethysmography, forehead **$\text{SpO}_2$**, blood pressure, skin temperature, and accelerometry—recording **69,000 raw data points/minute** for up to **48 hours** ([Hexoskin Astroskin](https://hexoskin.com/pages/astroskin), [Hexoskin News](https://hexoskin.com/blogs/news/bio-monitor-astroskin-to-launch-to-the-international-space-station)).
4. **Cognitive & Fatigue Assessments (Cognition Battery / PVT-B):**
   - **Specs:** NASA’s **Reaction Self-Test** pairs a 2-minute activity questionnaire with a **3-minute Psychomotor Vigilance Test (PVT-B)** to score reaction speed, lapses (omission errors), and impulsivity (commission errors) on a 0–100% scale relative to astronaut norms without learning-effect bias ([NASA NTRS](https://ntrs.nasa.gov/api/citations/20090029851/downloads/20090029851.pdf), [UPenn Cognition](https://www.med.upenn.edu/uep/cognition.html)).

---

### 3. Quantitative Thresholds, Environmental Triggers & Escalation Rules
Astronaut health software must fuse **physiological data** with **habitat/environmental telemetry** across mission environments (Spacecraft, Station, Rover, Lunar/Mars Base) because environmental excursions directly drive symptoms:

| Parameter / Indicator | Nominal Baseline / Limit | Caution / Action Threshold | Critical / Escalation Trigger | Source |
| :--- | :--- | :--- | :--- | :--- |
| **Cabin $\text{ppCO}_2$ (1-hr avg)** | ≤ 3.0 mmHg (keeps headache risk <1.4%) | > 3.0 mmHg (spikes occur during scrubber faults) | ≥ 3.5 mmHg (linked to frontal headaches, poor sleep, blurred vision, cough) | [NASA-STD-3001 Vol 2](https://www.nasa.gov/wp-content/uploads/2025/05/nasa-std-3001-vol-2.pdf?emrc=6a069b6815c88), [OCHMO-TB-004](https://www.nasa.gov/wp-content/uploads/2023/12/ochmo-tb-004-carbon-dioxide.pdf) |
| **Total Cabin Pressure** | 34.5 kPa < P ≤ 103 kPa (5–15 psia) | Rapid delta during EVA suit transfer | Drop below 34.5 kPa or DCS symptoms (bubble formation) | [NASA OCHMO](https://www.nasa.gov/ochmo-tb-004-carbon-dioxide-2), [NASA HRP](https://www.nasa.gov/hrp/risks) |
| **Radiation Exposure** | ISS: ~0.5–0.65 mSv/day; Mars Surface: ~0.67 mSv/day | Mars Transit: ~1.8 mSv/day (~0.66 Sv round-trip) | **600 mSv** NASA career effective dose limit; Solar Particle Events (SPEs) | [NASA OCHMO](https://www.nasa.gov/wp-content/uploads/2023/03/radiation-protection-technical-brief-ochmo.pdf), [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9916691), [SwRI](https://www.swri.org/newsroom/press-releases/swri-scientists-publish-first-radiation-measurements-the-surface-of-mars) |
| **CSF Pressure (SANS)** | Normal terrestrial < 18 cm $\text{H}_2\text{O}$ | > 18 cm $\text{H}_2\text{O}$ (high normal) + Amsler Grid distortion | **> 25 cm $\text{H}_2\text{O}$** (requires treatment) or worsening optic disc edema | [NASA OCHMO-MTB-001](https://www.nasa.gov/wp-content/uploads/2024/02/ochmo-mtb-001-sans.pdf?emrc=d4c581) |
| **Sleep & Duty Fatigue** | Target ~8 hrs sleep/day (ISS actual ~6.4 hrs) | Sleep < 6 hrs/day for 3+ days, wake > 16 hrs, or duty > 12 hrs/day | PVT-B lapse spike or > 6 consecutive work days without rest | [NASA NTRS](https://ntrs.nasa.gov/api/citations/20090029851/downloads/20090029851.pdf), [KBR](https://www.kbr.com/en/document/16756) |
| **Blood Pressure (Baseline)** | Astronaut selection baseline < 140/90 mmHg (sitting) | Orthostatic drop or sustained hypertension during fluid shifts | Syncope/presyncope, chest pain, or elevated i-STAT troponin | [NASA/Business Insider](https://www.businessinsider.com/how-to-apply-to-be-nasa-astronaut-2015-11), [Abbott](https://www.globalpointofcare.abbott/us/en/product-details/apoc/i-stat-system-us.html) |

*(Note: Standard terrestrial clinical reference ranges apply to i-STAT blood glucose in mg/dL, electrolytes, and lactate when evaluating acute anomalies, as NASA-STD-3001 public briefs defer specific lab panel cutoffs to individualized pre-flight baselines and Flight Surgeon Medical Operations Requirements Documents.)*

#### Escalation Architecture: LEO vs. Deep Space
- **Low Earth Orbit (ISS / Commercial Stations):** Near-real-time Private Medical Conferences (PMCs) with ground Flight Surgeons; the Crew Medical Officer (CMO) executes tests and treatments (IV fluids, medications, AED, eye wash, basic surgical kit) under live ground direction ([JAXA](https://humans-in-space.jaxa.jp/en/biz-lab/med-in-space/healthcare/medops/system)).
- **Lunar / Mars Exploration (LoC V):** With **>20-minute one-way communication delays** and no rapid evacuation, your software should include an **Environment Toggle** (`ISS / LEO` vs. `Lunar Base / Rover` vs. `Mars Transit`). In deep-space mode, alerts shift from *"Wait for Flight Surgeon PMC"* to **Autonomous Decision Support**: immediate step-by-step triage trees, drug/dosage guidance, and asynchronous encrypted medical packet queuing for Earth review ([NASA Ames](https://www.nasa.gov/centers-and-facilities/ames/ames-science/ames-space-biosciences/a-clinical-decision-support-system-for-earth-independent-medical-operations), [npj Microgravity](https://www.nature.com/articles/s41526-023-00284-1)).

---

### 4. Evidence-Based Countermeasures & Preventative Protocols
To satisfy the prompt’s requirement to provide actionable *guidance on treatments and health improvements*, build automated routines and alert-triggered protocols around these validated NASA countermeasures:

1. **Daily Exercise Countermeasure (2 Hours/Day):**
   - **Hardware:** **ARED** (Advanced Resistive Exercise Device, piston/flywheel vacuum system up to **272 kg / 600 lbs** peak load), **T2 Treadmill** (**2.4–19.3 km/h** with harness/bungee loading), and **CEVIS** cycle ergometer (**70–100% $\dot{V}\text{O}_{2\text{peak}}$** intervals) ([NASA](https://www.nasa.gov/missions/station/iss-research/astronaut-exercise), [PMC Sprint Study](https://pmc.ncbi.nlm.nih.gov/articles/PMC7434884)).
   - *App Feature:* Schedule workouts, track load/heart-rate zones, and include spine-protective stretching/yoga blocks added after NASA spinal health studies ([CNBC/NASA Twins Study](https://www.cnbc.com/2018/03/20/space-medicine-scientists-study-effects-of-space-on-human-body.html)).
2. **Nutritional & Pharmacological Prophylaxis:**
   - **Vitamin D3:** **800 IU/day** provided to all US ISS crewmembers (increased from 400 IU/day) due to lack of UVB exposure ([NASA Nutrition Report](https://www.nasa.gov/wp-content/uploads/2024/10/human-adaptation-to-spaceflight-the-role-of-nutrition.pdf?emrc=6a1624)).
   - **Bisphosphonates (Bone Loss):** Combining **ARED + alendronate** (or pre-flight zoledronic acid) significantly attenuates or completely prevents postflight areal BMD loss ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11352369)).
   - *Caution Note:* Monitor renal stone risk closely when administering potassium citrate or calcium-altering regimens ([ISS National Lab](https://issnationallab.org/iss360/human-health-on-the-space-station)).
3. **Fluid-Shift & Reentry Countermeasures:**
   - **LBNP (Lower Body Negative Pressure / Chibis Suit):** Applies vacuum suction to the lower body to pull cephalic fluids downward, reducing intracranial/ocular congestion (SANS) and preserving orthostatic tolerance ([npj Microgravity](https://www.nature.com/articles/s41526-024-00389-1), [NASA/YouTube](https://www.youtube.com/watch?v=Wl3KxYwnW6I)).
   - **Reentry Fluid Loading Protocol:** Consume **18–20 mL/kg** body weight of water with **0.18–0.20 g/kg** dry salt (or isotonic NaCl solution) **3–4 times in the final 12–20 hours before landing** (or 0.9 g NaCl + 300 mL water prior to Chibis LBNP) ([NASA NTRS](https://ntrs.nasa.gov/api/citations/20150007319/downloads/20150007319.pdf)).

---

### 5. Existing Software Benchmarks & NASA UI/UX Design Standards

#### Benchmark: ESA/CNES EveryWear App
Developed by MEDES for CNES and flying on the ISS since 2016 (and expanding to **Artemis II / Orion**), **EveryWear** is the premier operational crew health app. Astronauts use it on tablets to log nutrition and medications, complete questionnaires, connect wirelessly to wearable sensors, and send **end-to-end encrypted data** to Flight Surgeons ([ESA Orion Blog](https://blogs.esa.int/orion/2026/04/06/everywear-from-earth-orbit-to-the-moon)).
- **Hackathon Opportunity:** EveryWear focuses heavily on *data logging and ground transmission* rather than interactive self-diagnosis, body-map visualization, gamified adherence, or autonomous LoC V deep-space guidance—your team can explicitly position your app as the **"next-generation autonomous visual companion"** bridging that gap.

#### Mandatory UI Rules from NASA-STD-3001 Vol 2 & HIDH
To impress judges with space-grade human factors, adhere to NASA’s **Crew Interfaces ([Section 10.4](https://www.nasa.gov/reference/10-0-crew-interfaces-vol-2))** and **Human Integration Design Handbook ([HIDH](https://www.nasa.gov/wp-content/uploads/2015/03/human_integration_design_handbook_revision_1.pdf))**:
- **Strict Color-Coding Semantics:**
  - **Green:** Nominal / Good physiological state.
  - **Orange-Yellow (Amber):** Caution / Tolerable but requires attention or countermeasure adjustment.
  - **Red (or Flashing Red):** Warning / Emergency / Not tolerable (immediate medical intervention or Flight Surgeon escalation).
  - Reserve **White/Blue** strictly for neutral information or auxiliary cues so alert colors retain maximum visual salience.
- **Redundant Non-Color Coding ([V2 10045]):** Never rely on color alone (lighting conditions, EVA visors, and color vision variability degrade color perception). Always pair status colors with **distinct icons, explicit text labels, units (mg/dL, mmHg, mSv), and optional audio/speech alerts** for warnings ([NASA STD-3001 Vol 2](https://www.nasa.gov/reference/10-0-crew-interfaces-vol-2)).
- **Plain-Language Guided Explanations & Gamification:** Because non-medical crewmembers perform self-checks under high stress and fatigue, pair every metric with a *"Why this exam matters"* tooltip, visual measurement instructions (e.g., how to hold a probe or place a fingerstick on an i-STAT cartridge), and a **Mission Readiness / Streak** gamification loop for daily ARED workouts, hydration, Vitamin D, and PVT-B cognitive check-ins.

---

## Key Sources
- [NASA Human Research Program — 5 Hazards of Human Spaceflight](https://www.nasa.gov/hrp/hazards)
- [NASA Human Research Program — Risks of Human Spaceflight](https://www.nasa.gov/hrp/risks)
- [NASA OCHMO-MTB-001 — Spaceflight Associated Neuro-ocular Syndrome (SANS)](https://www.nasa.gov/wp-content/uploads/2024/02/ochmo-mtb-001-sans.pdf?emrc=d4c581)
- [NASA OCHMO-TB-004 — Carbon Dioxide (CO2) Technical Brief](https://www.nasa.gov/wp-content/uploads/2023/12/ochmo-tb-004-carbon-dioxide.pdf)
- [NASA OCHMO — Radiation Protection Technical Brief](https://www.nasa.gov/wp-content/uploads/2023/03/radiation-protection-technical-brief-ochmo.pdf)
- [NASA-STD-3001 Volume 2 — Crew Interfaces (Section 10.0)](https://www.nasa.gov/reference/10-0-crew-interfaces-vol-2)
- [NASA Human Integration Design Handbook (HIDH)](https://www.nasa.gov/wp-content/uploads/2015/03/human_integration_design_handbook_revision_1.pdf)
- [NASA Ames / npj Microgravity — Clinical Decision Support System for Earth-Independent Medical Operations](https://www.nature.com/articles/s41526-023-00284-1)
- [NASA — Fundamentals of Human Health & Bone Changes](https://www.nasa.gov/reference/fundamentals-of-human-health)
- [NASA — Ultrasound Scans in Space (ADUM & Butterfly iQ)](https://www.nasa.gov/missions/station/ultrasound-scans-in-space-transform-medicine-on-earth)
- [NASA — Human Adaptation to Spaceflight: The Role of Nutrition](https://www.nasa.gov/wp-content/uploads/2024/10/human-adaptation-to-spaceflight-the-role-of-nutrition.pdf?emrc=6a1624)
- [NASA NTRS — Portable Diagnostics Technology Assessment (Abbott i-STAT)](https://ntrs.nasa.gov/api/citations/20100011008/downloads/20100011008.pdf)
- [NASA NTRS — Psychomotor Vigilance Self Test on ISS (Reaction Self-Test)](https://ntrs.nasa.gov/api/citations/20090029851/downloads/20090029851.pdf)
- [NASA NTRS — Risk of Orthostatic Intolerance & Fluid Loading Protocol](https://ntrs.nasa.gov/api/citations/20150007319/downloads/20150007319.pdf)
- [ESA Orion Blog — EveryWear: From Earth Orbit to the Moon](https://blogs.esa.int/orion/2026/04/06/everywear-from-earth-orbit-to-the-moon)
- [JAXA — Equipment Used for Medical Operations on Orbit (CHeCS)](https://humans-in-space.jaxa.jp/en/biz-lab/med-in-space/healthcare/medops/system)
- [Hexoskin — Astroskin / CSA Bio-Monitor Wearable Platform](https://hexoskin.com/pages/astroskin)
- [PMC — High Intensity Training During Spaceflight (ARED, T2, CEVIS)](https://pmc.ncbi.nlm.nih.gov/articles/PMC7434884)
- [PMC — The Case for Bisphosphonate Use in Astronauts](https://pmc.ncbi.nlm.nih.gov/articles/PMC11352369)
- [SwRI — Radiation Measurements from the Surface of Mars & Cruise](https://www.swri.org/newsroom/press-releases/swri-scientists-publish-first-radiation-measurements-the-surface-of-mars)