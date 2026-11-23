Research on: Global AI Data Center Power Capacity & Energy Footprint Reconciliation

Hackathon: Grid Infrastructure & Sustainable Compute Data Challenge

Objectives:
Your challenge is to build a verified, normalized dataset and statistical reconciliation report that helps grid operators estimate the true electricity demand of frontier AI data centers through 2028. You must gather data from utility interconnection filings, hyperscaler sustainability reports, local permitting documents, and independent energy studies across at least 8 major hyperscale AI campus projects globally. Any verifiable facility metric can be used, as long as it helps quantify electrical load and energy consumption—such as peak IT power capacity in megawatts (MW), Power Usage Effectiveness (PUE) ratios, and annualized electricity consumption in terawatt-hours (TWh).

You can use public utility commission dockets, environmental impact assessments, and engineering benchmarks (such as rack power density guidelines for liquid-cooled GPU clusters) to reconcile conflicting energy estimates. Which hyperscale campuses have confirmed grid interconnection agreements versus speculative multi-phase announcements? Why do reported MW capacity figures frequently diverge from actual TWh energy consumption? How do cooling architectures (such as direct-to-chip liquid cooling versus traditional air cooling) alter facility PUE and total grid draw? When do two credible sources disagree on a facility's power footprint due to Phase 1 versus full-buildout reporting? What standardized load-factor formulas should be applied to normalize disparate industry estimates? These are questions worth considering as you develop your solution.   
tech plus trends

Mathematical rigor and schema standardization play an important role in presenting reliable energy forecasts. You may consider taking advantage of clean CSV data tables, explicit conversion formulas, and variance annotations to present the information. For example, your submission could pair a machine-readable facility dataset with an outlier analysis explaining every discrepancy across data sources.

Potential Considerations:
You may (but are not required to) consider the following:

Your dataset could separate grid-supplied electricity from behind-the-meter generation (such as on-site natural gas turbines, nuclear power purchase agreements, or solar microgrids).

Your analysis could model sensitivity ranges showing how shifting utilization rates (e.g., 70% vs. 90% continuous inference load) impact total 2028 TWh demand.

Your output could include the following features:

A standardized CSV export with unified units (MW for capacity, TWh/year for energy, dimensionless ratios for PUE)

Explicit mathematical equations documenting every unit conversion and load-factor assumption

Variance flags that preserve conflicting source figures side-by-side rather than silently averaging them

Do not assume that policy readers understand electrical engineering units. Your report should clearly explain the physical difference between instantaneous power capacity (MW) and cumulative energy consumption (TWh).