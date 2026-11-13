# THEARCHITECT_MAX — Projects-Displays

**Static publication library for 123 independently identified software and research IP assets.** View the official [project exhibition](https://thearchitect-max.github.io/MyProjects/displays/) or the [canonical public portfolio source](https://github.com/TheArchitect-max/MyProjects).

## Current public register and scope

The portfolio register covers **TA-IP-001 through TA-IP-123**, with a distinct reference alias, canonical title and private project source identity for every listed asset. The additional three GitHub repositories are publication or acquisition infrastructure, not offered product assets. TA-IP-122 and TA-IP-123 retain **provisional portfolio aliases** rather than confirmed source-side aliases. Historical compatibility URLs are redirects, not additional IP assets.

The published total of **EUR 25,153,000** is the sum of 123 individual **seller asking references**, dated **10 November 2026**. It is not a negotiated bundle price, independent market appraisal or revenue projection. The displayed EUR/USD information uses the published 10 November 2026 rate. Subsequent repository activity does not automatically expand the published edition, software maturity or seller price.

## One canonical publication, one verified mirror

**MyProjects owns the canonical public publication; Projects-Displays mirrors its approved content.** Approved hub SHA:

32af5dbb4bb7c9c261bd1d7e022341aaaa7bc916

The mirror contains **430 SHA-256-matching public files**, comprising all static publication data, 123 complete buyer presentations with PDF factsheets and briefs, and historical redirects. See [initial snapshot audit](PUBLICATION_AUDIT_2026-11-13.md).

With a checkout of MyProjects at that exact SHA, run these read-only checks:

~~~sh
python3 -m pip install pypdf==5.9.0
python3 tools/sync_snapshot.py /path/to/MyProjects
python3 tools/build_showroom.py /path/to/MyProjects
python3 tools/build_factsheets.py /path/to/MyProjects
python3 tools/sync_to_hub.py /path/to/MyProjects
node tools/build_calculation_check.cjs
python3 tools/validate.py /path/to/MyProjects
~~~

All commands are **read-only by default**. To intentionally mirror a newly reviewed and pinned public hub commit on a controlled candidate branch, update the source pin and expectations with evidence, then execute:

~~~sh
python3 tools/sync_snapshot.py /path/to/MyProjects --write
~~~

The compatibility names build_showroom.py and build_factsheets.py mirror the **whole approved snapshot** with an explicit --write. They no longer regenerate stale 119-asset HTML or obsolete three-page PDFs. The sync_to_hub.py compatibility command does **not** write to the canonical MyProjects repository.

## CI and maintenance

The [publication maintenance contract](MAINTENANCE_CONTRACT.md) specifies review boundaries and acceptance steps. The reusable GitHub Actions workflow performs **CI validation only**. It checks every identity, eight per-asset financial fields, four-page PDF contents, product descriptions and briefs, links, aliases, source hashes and a clean working tree. It does not operate a product server, user accounts, sessions, database, commerce platform or payment processor.

## Buyer scope, qualification and rights

Public viewing provides no software runtime, IP access, licence, rights transfer or sales contract. An acquisition requires a separate written agreement on specific first-party rights, edition, component obligations, third-party materials, delivery and buyer acceptance.

Static publication PASS does not prove independently appraised market value, source-code title, external scientific results, medical qualification, production security, commercial traction or deployment readiness. The 123-asset catalogue is a **dated commercial publication**, not a live release register for every separate proprietary software project.

© 2026 THEARCHITECT_MAX. First-party rights reserved.
