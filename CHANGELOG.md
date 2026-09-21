# Changelog

All notable changes to GC Solar Projects are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/).

## Project Overview

GC Solar Projects is a B2B Solar EPC subcontractor serving Coastal Andhra Pradesh. The project website presents the company's execution capabilities, services, project proof, and inquiry channels for commercial, industrial, and residential solar work.

## [Unreleased]

### Planned

- Add a contact form backend using Cloudflare Workers.
- Expand the project gallery with additional completed installations and case studies.

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
[1.1.0]: https://github.com/aurounplugged-hue/gc-solar-projects/releases/tag/v1.1.0
[1.0.1]: https://github.com/aurounplugged-hue/gc-solar-projects/releases/tag/v1.0.1
[1.0.0]: https://github.com/aurounplugged-hue/gc-solar-projects/releases/tag/v1.0.0
