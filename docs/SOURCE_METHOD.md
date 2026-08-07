# Source Acquisition Method

Sources are ranked in this order:

1. reusable raw data with explicit license and monitor identity;
2. reusable peer-reviewed matched-monitor tables;
3. official vendor field and export documentation;
4. public files without clear reuse permission, cataloged as reference only;
5. secondary claims, retained only when they identify a candidate source.

Each source is recorded with an access date and limitations. Downloaded
external candidates receive a byte-level SHA-256, and GitHub-hosted candidates
also receive a pinned commit reference. URLs alone are not considered stable
provenance. When a collection environment cannot reach a publisher or vendor
domain directly, a source may be cataloged from search-index snapshots; such
rows say so in their limitations and stay `reference_only` until the page is
verified directly.

The build is intentionally network-free. Network collection and scientific
curation are separate review steps so a changed website cannot silently change
the released database.
