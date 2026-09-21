# Changelog

All notable changes to GC Solar Projects are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/).

## Project Overview

GC Solar Projects is a B2B Solar EPC subcontractor serving Coastal Andhra Pradesh. The project website presents the company's execution capabilities, services, project proof, and inquiry channels for commercial, industrial, and residential solar work.

## [Unreleased]

### Planned

- Add a contact form backend using Cloudflare Workers.
- Expand the project gallery with additional completed installations and case studies.

## [1.2.0] - 2026-09-21

### Changed

- **Projects Case Study Hierarchy (`projects.html` - PR #6):**
  - Restructured the 70 kW Tenali commercial installation into a rigorous 3-stage visual engineering case study: 01 Structure Erection, 02 Array Integration, 03 Grid Sync & Commissioning.
  - Replaced generic execution placeholders with technical operational copy reflecting coastal wind-load considerations, elevated GI framing, and utility synchronization (APCPDCL).
  - Standardized B2B copy standards to emphasize on-site engineering oversight and operational leadership.
- **Homepage Projects Hierarchy & Credibility Fix (`index.html` - PR #7):**
  - Removed redundant "Coastal array execution" card from the featured projects grid to eliminate ambiguity and reinforce 100% verified site proof.
  - Promoted Tenali (70 kW C&I · Guntur District · APCPDCL Grid Sync) to the primary featured showcase block with enhanced technical parameters.
  - Restructured Kovvur (3 kW) and Tadepalligudem (3 kW) into a dedicated two-column "Standardized Turnkey Deployments" secondary strip.
  - Repurposed coastal structure erection photography directly into the Civil & Structural Engineering section as visual proof for coastal mounting capabilities.

## [1.1.0] - 2026-09-21

### Added

- Custom domain configuration for gcsolarprojects.com, with Porkbun ALIAS/CNAME records pointing to Cloudflare Pages.

### Changed

- Infrastructure migration from Netlify to Cloudflare Pages due to deploy credit exhaustion.
- Fixed the WhatsApp lead-generation CTA across the header, contact section, and footer, replacing the placeholder with Chidvilas Dadi (+91 9492995950) and a pre-filled inquiry message.
- Automated the Git build and instant deployment pipeline on the `master` branch.

## [1.0.1] - 2026-09-20

### Fixed

- Restored the corrupted `index.html` from Git history (commit `969832a`).

### Preserved

- Preserved the project data structure in `data/projects.json`.

## [1.0.0] - 2026-09-18

### Added

- Initial production launch of the B2B Solar EPC marketing site.

[Unreleased]: https://github.com/aurounplugged-hue/gc-solar-projects/compare/v1.1.0...HEAD
[1.2.0]: https://github.com/aurounplugged-hue/gc-solar-projects/releases/tag/v1.2.0
[1.1.0]: https://github.com/aurounplugged-hue/gc-solar-projects/releases/tag/v1.1.0
[1.0.1]: https://github.com/aurounplugged-hue/gc-solar-projects/releases/tag/v1.0.1
[1.0.0]: https://github.com/aurounplugged-hue/gc-solar-projects/releases/tag/v1.0.0
