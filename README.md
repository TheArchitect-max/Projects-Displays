# THEARCHITECT_MAX — Projects Displays

## Complete source and financial-reference review - 16 October 2026

All 105 displays, briefs and two-page factsheets now disclose their individual cost-evidence status and retained financial reference. The collection links to each project once. Method and source pages explain the WIPO, Knab and limited Upwork context, missing cost budgets and correlated internal scenarios. Asking amounts are unchanged. See the [complete review](https://github.com/TheArchitect-max/MyProjects/blob/main/docs/MULTISOURCE_VALUATION_REVIEW_2026-10-16.md).

The records below describe preceding publication states.

## Complete directory update - 16 October 2026

All 107 repositories and 105 project profiles were checked. Three repository renames, the AEGIS Vision product brand, five canonical route migrations, current main versions and separate development candidates are synchronized with all 105 displays, briefs and factsheets. Existing individual prices, qualifications and stable TA-IP references retain their dated scope. Read [the current update](docs/PORTFOLIO_UPDATE_2026-10-16.md).

The dated records below describe earlier publication states.

## Universal Video Intelligence Platform - 14 October 2026

TA-IP-101 / Ophelia now distinguishes the current v0.9.8 main from the unmerged v0.9.9 candidate. R28 records a source-pinned, user-operated live YouTube PASS for five scenarios in each official Chrome and Edge browser; accessibility, privacy, security, performance and durability gates remain open. The profile, display, factsheet and source register are refreshed. Existing price references and assurance grades are retained. Read [the dated status update](docs/UVIP_STATUS_UPDATE_2026-10-14.md).

One maintained exhibition for **105 individually scoped software IP assets**. Each project has its own product display, two-page PDF factsheet and editable product brief. Canonical TA-IP references and titles match the existing MyProjects hub.

**[Open the exhibition](https://thearchitect-max.github.io/MyProjects/displays/)** · **[Return to the main hub](https://thearchitect-max.github.io/MyProjects/)**

## Navigation and publication

The hub links every project profile, collection row and relevant connection member to its own display. Every display has a **Return to hub** button leading to the main page and a **View project profile** link leading to the corresponding full assessment.

This repository is the maintained display source. Its static exhibition is published under the existing MyProjects website at `/MyProjects/displays/`. A second hosting configuration is not required. All 105 displays share this repository; presentation repositories are excluded from the count of IP assets.

## Content

- `products/<display-slug>/index.html`: individual buyer-facing display.
- `products/<display-slug>/factsheet.pdf`: retained PDF factsheet.
- `products/<display-slug>/product-brief.md`: editable product brief.
- `project-map.json`: exact correspondence between project references, hub profiles and displays.
- `catalogue.csv` and `source-register.csv`: exhibition and non-technical source registers.
- `acquisition.html`, `methodology.html` and `sources.html`: acquisition, pricing and disclosure context.

The exhibition uses the supplied 13 October 2026 package. Existing asking references, recreation estimates, dated seller assessments and product boundaries are retained. Publication does not establish a new valuation or new qualification of the underlying products. Product source code, architecture, algorithms, dependency inventories and private development materials are excluded.

## Update the existing hub

After editing the relevant display, synchronize into a local MyProjects checkout:

```bash
python tools/sync_to_hub.py /absolute/path/to/MyProjects
python tools/validate.py /absolute/path/to/MyProjects
```

The synchronizer checks canonical identities, copies the static exhibition, updates the hub display directory and refreshes its attestation digest. Review and commit both checkouts through the normal Git workflow. No custom Actions workflow or application server is required.

Search, category filters, sorting, local enquiry preparation, printing and downloads run on the visitor's device. The exhibition provides no checkout, payment processing, accounts, user/session database or SaaS runtime. Acquisition closes separately under definitive written terms.

See [the integration record](docs/INTEGRATION_2026-10-13.md) and [the validation record](docs/VALIDATION_2026-10-13.json).

© 2026 THEARCHITECT_MAX. First-party rights reserved. Receipt of this display does not transfer product ownership or licences.
