# Instructions for AI coding tools

These repository instructions apply to GitHub Copilot and other AI coding assistants. Read `AGENTS.md` before making changes and follow it as mandatory repository policy.

- Never push directly to `master`. Work on a `feature/...` or `fix/...` branch and open a pull request targeting `master`.
- Follow the binary/image integrity rules in `AGENTS.md`: images go under `images/projects/`; verify correct paths, valid format, non-zero size, and exact byte counts before and after adding or replacing assets.
- Follow the HTML and portfolio rules in `AGENTS.md`: valid UTF-8, no NUL bytes, one complete `<!doctype html>` through `</html>` document; preserve `<div class="wall-tile">` tile structure in `projects.html`.
- Whenever a new site is added, automatically increase the total installed kW capacity count in `index.html` and update any other capacity mentions throughout the site. Recalculate from verified project capacity data and keep all displayed totals consistent. Recalculate after removing a site or correcting its capacity, too.
- Review the full diff and verify all changed assets and pages. Test the Cloudflare Pages preview URL for the PR before merging; do not report unperformed checks as complete.
- Keep changes minimal, preserve existing design/accessibility, verify links and image paths, and ensure factual solar capacity and O&M claims are supported.
