# Source archive

This directory preserves the primary materials used for the ODMK reconstruction. The canonical HINTS files are the members extracted from `HINTS5_Cycle2_STATA_20240507.zip`; the separately downloaded methodology report and English instrument are retained only to make the official direct URLs auditable. Text files produced with `pdftotext -layout` are search aids, not independent sources.

The canonical public file is a 2024 remediation release, not necessarily the exact release available to the authors. NCI's methodology report documents demographic hot-deck fields used in weighting production, while the current Stata file does not expose those `_I` variables. The project therefore records release drift as unresolved and does not assume either that the authors used those fields or that NCI performed their analytic missing-data treatment.

The ODMK publisher copy is not openly downloadable. The COS sourcing sheet supplied an OSF-hosted `ODMK.pdf`, preserved here as `ODMK_COS_source.pdf` with its API-reported SHA-256. The DOI, PubMed metadata, and earlier author-uploaded ResearchGate link are also retained. No PDF was copied from an access-controlled publisher platform.

No author analysis code, supplementary analysis file, or paper-specific public repository was located after searches by exact title, DOI, and author/title combinations on the publisher page, PubMed, Google Scholar-indexed results, GitHub, OSF, and Figshare (last checked 2026-10-13). This is a search result, not proof that no private or unindexed code exists.

The original COS invitation links are now preserved as the available-papers CSV, general workflow text, and robustness-guidance text. The sourcing sheet identifies the ODMK focal result as the Table 2 Asian-versus-non-Hispanic-White PPPCQ mean comparison. The analyst guidance is the controlling protocol; the archived SCORE robustness supplement remains contextual material.

The source ledger records the 2001 EORTC QLQ-C30 scoring manual as a general pre-ODMK example of scoring a multi-item scale when at least half the items are answered. It is not treated as validation of PPPCQ or its missing-item behavior. Moser et al. (2022) is later same-instrument evidence, not proof of the original scoring rule.

DAAF 3.0.2 at commit `4c5fc85138451a30a174b714fea18457b0d3f7a0` was used as an internal plan, audit-trail, and complex-survey review lens. It did not replace COS guidance or serve as the analysis runtime. Adopted improvements are recorded in `../DAAF_review.md`.

See `source_manifest.csv` for URLs, checksums, and access notes.
