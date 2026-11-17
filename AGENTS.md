# Repository Agent Guidelines

## GC Solar Direct API Protocol
Strict rule: NEVER invoke or route to Devin for `aurounplugged-hue/gc-solar-projects` or any GC Solar tasks. Always use direct GitHub REST API with personal access token (PAT) / Node.js / js-exec scripts, adhering strictly to the Binary Integrity Protocol v2 and repo workflow protocol.

## Protocol Requirements
1. Never push directly to master. All changes must use a dedicated feature or fix branch and a Pull Request.
2. Verify exact byte counts (`wc -c`), valid UTF-8, zero NUL bytes, valid single HTML structure, and Cloudflare Pages preview.
3. Factual credibility: absolute factual accuracy on solar capacities and O&M.

## Required workflow for all contributors and AI tools
- Treat these instructions as mandatory, including Codex, Copilot, and other AI coding agents. Read this file before changing the repository; also follow `.github/copilot-instructions.md` where applicable.
- Never commit or push directly to `master`. Create a dedicated `feature/...` or `fix/...` branch, open a pull request targeting `master`, validate the Cloudflare Pages preview, and merge only through the approved PR workflow.
- After Codex finishes pushing a branch and creating a PR, Codex MUST print the Cloudflare Pages preview URL directly in its chat/terminal output alongside the PR link. Use `https://<sanitized-branch-name>.gcsolarprojects.pages.dev` as the proposed URL pattern only when verified; otherwise print the exact Cloudflare deployment URL. Never invent, imply, or claim a preview URL has been validated unless confirmed; the user needs a directly clickable URL without opening GitHub or checking email.
- Keep changes narrowly scoped. Do not modify unrelated files or overwrite existing assets without verifying their source and integrity.
- Before merging, deploy/use the Cloudflare Pages preview for the pull request and inspect the changed pages/assets. Do not claim preview validation unless it was actually performed.

## Binary and image integrity
- Project images belong under `images/projects/` and references must use the correct existing path/case.
- Before adding or replacing an image/binary, verify its provenance, format, non-zero byte size, and exact byte count (`wc -c`). Confirm the resulting repository asset's byte count after transfer; never trust a reported upload size alone.
- Do not rename, recompress, convert, or otherwise alter existing binary assets unless explicitly required. Never introduce zero-byte, truncated, placeholder, or text-corrupted binary files.

## HTML integrity and project-page conventions
- HTML files must be valid UTF-8, contain no NUL bytes, and have one complete document from `<!doctype html>` through the closing `</html>`.
- In `projects.html`, each portfolio tile must retain the established `<div class="wall-tile">` structure and its expected nesting, links, and image references. Inspect neighboring tiles before adding or changing one.
- Whenever a new site/project is added, update the total installed kW capacity counter in `index.html` and update any other capacity mentions throughout the site. Recalculate from verified project capacity data and keep all displayed totals consistent. Recalculate after removing a site or correcting its capacity.
- Project categorization on `projects.html`: projects below 10 kW belong in the smaller/distributed projects section `#distributed` (“Distributed Solar & Field Infrastructure”); projects of 10 kW or more belong in the bigger/commercial & industrial section `#commercial-industrial` (“Commercial & Industrial Deployments”). Verify capacity and place each project in the correct section.
- Preserve the site's existing design, responsive behavior, accessibility, and factual claims; check all affected links and image paths.

## Verification checklist
1. Review the complete diff and confirm only intended files changed.
2. Check exact byte counts for every changed/new file and every added/replaced binary; all binaries must be non-zero.
3. Verify changed HTML is UTF-8, has zero NUL bytes, and has one `<!doctype html>` ... `</html>` document.
4. For project tiles, verify the required `wall-tile` structure; for every added project verify the correct section by the 10 kW threshold, and update the `index.html` capacity counter and every other capacity mention using verified project data.
5. Test the deployed Cloudflare Pages PR preview before merging and record the preview URL and checks performed in the PR.
6. Merge only through the approved pull-request workflow; never bypass repository protections.
