# GC Solar Projects

GC Solar Projects is a B2B solar EPC subcontractor and ground-execution partner serving Coastal Andhra Pradesh. This repository contains the public website, project data, images, and deployment configuration.

## Deployment and hosting

- Production hosting: Cloudflare Pages.
- Cloudflare Pages project: `gc-solar-projects.pages.dev`.
- Custom-domain DNS: managed at Porkbun, with the domain pointed to Cloudflare Pages.
- Deployment source: the `master` branch; pushes trigger the production build and deployment pipeline.
- Netlify migration: the site was migrated from Netlify to Cloudflare Pages. Netlify is no longer the production hosting provider. Any historical Netlify references in the changelog or audit history describe the former setup and are retained only for project history.

## Forms and lead capture

The current site does not use a server-backed contact-form submission flow. The primary inquiry path is the WhatsApp lead-generation CTA, available from the header, contact section, and footer, with a pre-filled inquiry message.

A contact-form backend using Cloudflare Workers remains planned and is not yet represented as an active production capability. Until that work is implemented, documentation and UI should not imply that form submissions are being stored or processed by a backend.

## Repository documentation

- `PROJECTS.md` — project and technical reference material.
- `CHANGELOG.md` — release history, including the Netlify-to-Cloudflare Pages migration and Porkbun custom-domain configuration.
- `AUDIT_LOG.md` — recent implementation and visual-change history.
- `TODO.md` — outstanding product, content, deployment, and repository tasks.
- `_redirects` — route redirect configuration retained with the site assets.

## Local site structure

The site is currently a static HTML/CSS/JavaScript website with project data in `data/projects.json`, page assets under `images/`, and supporting site functionality under `functions/` and `admin/`.

## Contact

GC Solar Projects is based in Rajahmundry, Andhra Pradesh, India. See the site source and project documentation for current contact and operations details.
