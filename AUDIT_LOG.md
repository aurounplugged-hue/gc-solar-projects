# Audit Log: Recent Visual Overhaul and Fixes

Repository: `aurounplugged-hue/gc-solar-projects`
Branch: `master`
Scope: Changes from the project-data correction through the visual overhaul and follow-up asset fixes.

All timestamps are UTC on Sunday, September 20, 2026.

## Commit history

### d2ec0f71ac5e7e536af571cf5daa9239459e0987 — 06:09:29 UTC
Message: `remove temporary test file`

Removed a temporary repository test artifact so the project tree remained clean before the production content updates.

### b25deaade8f717dcb516634092b95393e625378a — 06:23:44 UTC
Message: `feat: add complete Tenali 70kW project entry`

Added the Tenali 70 kW Commercial & Industrial Rooftop Array project metadata, including location, capacity, completion status, DISCOM coordination, structural specification, image path, and metrics.

Rationale: Establish the requested Tenali project record in the projects data file.

### d09d7b5735e15ac9ff64473398190d9ac94eb00b — 06:33:36 UTC
Message: `fix: preserve all three solar projects`

Replaced the incomplete single-project data state with a complete projects.json containing Tenali 70 kW, Kovvur 3 kW, and Tadepalligudem 3 kW, with full metadata.

Rationale: Preserve all executed projects rather than allowing the Tenali update to remove the existing Kovvur and Tadepalligudem records.

### 3fc66351781cf90509eed465c9172da272bf4207 — 06:33:37 UTC
Message: `feat: add B2B case studies and proof metrics`

Added the initial B2B visual treatment: charcoal/slate palette, off-white background, solar amber accents, proof metric strip, Civil & Structural Engineering section, and static case-study layout.

Rationale: Make the project proof visible and align the page with an industrial B2B engineering identity.

### 0f193345d67fad6a5d88791bba44bfd71e32f571 — 06:33:42 UTC
Message: `feat: add project image`

Added the Tenali project image at `images/projects/tenali-70kw-commercial.jpeg`.

Rationale: Provide a dedicated asset for the Tenali case study.

### baf3276e6f2490650d4aca7cbdc3600fa156d50b — 06:33:47 UTC
Message: `feat: add coastal project image`

Added the coastal rooftop image at `images/projects/coastal-array-flat-roof.jpeg`.

Rationale: Provide a coastal rooftop asset for the project presentation.

### abb57d29e92fbfcba9b3a7972dd501e991ba91da — 06:33:52 UTC
Message: `feat: add structural execution image`

Added the structural execution asset at `images/projects/structure-erection-coastal.jpeg`.

Rationale: Support the Civil & Structural Engineering section with a dedicated field image.

### dbaab8596baf5884348b22fd4d1fed46247d88ad — 11:06:25 UTC
Message: `feat: restore full site with B2B engineering design language`

Rebuilt index.html as a complete site while retaining the newer visual language. Restored branded navigation, hero, proof strip, Why GC Solar, Services, Civil & Structural Engineering, three project case studies, O&M/Operations, Contact/Inquiry, footer, SEO description, JSON-LD, responsive layout, and the charcoal/slate/amber design system.

Rationale: The previous minimal template had unintentionally removed the original site’s essential sections and structure.

### 6d3a752305971de731189bb1602bbeffe72d6900 — 11:10:45 UTC
Message: `fix: restore distinct Kovvur and Tadepalligudem project images`

Updated the project cards to use the distinct original repository assets:
- `images/projects/kovvur-3kw-rooftop.jpeg`
- `images/projects/tadepalligudem-3kw-rooftop.jpeg`

Also restored the original header GC Solar logo mark using `/images/logo-mark-96.png`.

Rationale: The two cards had incorrectly reused the same coastal image, and the improvised header mark did not match the approved original brand asset.

### 1e025b1e814427d7896d46041b5efa43c1eaa9ae — 11:13:12 UTC
Message: `fix(footer): restore original GC Solar logo mark in footer`

Replaced the footer’s improvised CSS triangle mark with the original `/images/logo-mark-96.png` asset and matched the “GC Solar Projects” brand treatment used in the header.

Rationale: Keep the logo treatment consistent across the full page and remove the incorrect footer icon.

## Current verified state

The site contains three project records and distinct project image paths for Tenali, Kovvur, and Tadepalligudem. The header and footer use the original GC Solar logo mark. The full original site structure has been restored and styled with the current charcoal/slate, off-white, and solar amber B2B engineering design language.
