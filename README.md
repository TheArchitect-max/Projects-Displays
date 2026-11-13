# THEARCHITECT_MAX — Project Displays

**Public static software-IP asset display library.** The canonical published experience is [MyProjects / Project Displays](https://thearchitect-max.github.io/MyProjects/displays/).

## Portfolio baseline

As of **13 November 2026**, the current canonical public hub documents **123 independently scoped software/research assets** (TA-IP-001–TA-IP-123). Each has an individually assigned title, alias, factsheet, buyer brief, project page and seller asking reference. The 126 known repository identities include 123 private project repositories and three separate publication/acquisition support repositories. TA-IP-122 and TA-IP-123 still carry provisional portfolio aliases; do not state that those aliases are confirmed by source-side records.

The **individual seller asking references total EUR 25,153,000**, according to the dated 10 November 2026 pricing review. This is a sum of reference prices, **not** an agreed bundle price, market appraisal, revenue forecast or transaction agreement. Differences in subsequent development commits must not silently revise financial assumptions or advertised production readiness.

## Publication source and controlled refresh

The canonical publication source is [MyProjects](https://github.com/TheArchitect-max/MyProjects) at pinned commit `28f29a547d0a753825e09c1e80ba75ac81014515`. The publication files under its `displays/` directory are mirrored byte-for-byte into this repository by `python3 tools/sync_snapshot.py /path/to/pinned/MyProjects`. The script fails closed on a different source commit and checks all 123 identities, asking-price total, product pages, PDF headers and mirrored file SHA-256 hashes. See [publication verification](PUBLICATION_AUDIT_2026-11-13.md) once the mirror has been fully validated.

The one-shot workflow in `.github/workflows/sync-static-publication.yml` is restricted to the candidate branch and performs **static CI/build synchronisation only**. It is not a hosted product, application backend, scheduled worker or payments runtime. The older `tools/build_showroom.py`, factsheet builders and `tools/validate.py` reflect an earlier 119-asset generation scheme and must not be used to overwrite the 123-asset canonical publication until the generators and validators are separately migrated and verified.

## Buyer and rights boundary

The publication offers information for prospective buyer due diligence; it does **not** run any of the underlying products. It has no user database, user sessions, authentication, payments or SaaS server. A transfer requires a separate agreement identifying first-party rights, exact software edition, delivery manifest, component and third-party obligations, acceptance and price. Third-party materials remain subject to their own rights; viewing a presentation conveys no licence.

Publication checks do not certify clinical, scientific or engineering performance, production deployment, independent review, legal title or independent market valuation. The seller retains full control over first-party IP and maintains repository isolation.

© 2026 THEARCHITECT_MAX. First-party rights reserved.
