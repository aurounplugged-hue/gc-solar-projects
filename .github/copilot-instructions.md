# Instructions for AI coding tools

These repository instructions apply to GitHub Copilot and other AI coding assistants. Read `AGENTS.md` before making changes and follow it as mandatory repository policy.

- Never push directly to `master`. Use a `feature/...` or `fix/...` branch, open a pull request to `master`, test its Cloudflare Pages preview, then merge only through the approved PR workflow.
- Follow the binary/image integrity rules in `AGENTS.md`: images go under `images/projects/`; verify correct paths, valid format, non-zero size, and exact byte counts before and after adding or replacing assets.
- Follow the HTML and portfolio rules in `AGENTS.md`: valid UTF-8, no NUL bytes, one complete `<!doctype html>` through `</html>` document; preserve `<div class="wall-tile">` tile structure in `projects.html`.
- Whenever a new project/site is added, update the total installed kW capacity counter in `index.html` and any other capacity mentions; recalculate from verified project capacity data and keep displayed totals consistent. Recalculate after removal or capacity correction, too.
- In `projects.html`, put projects below 10 kW in `#distributed` (“Distributed Solar & Field Infrastructure”) and projects of 10 kW or more in `#commercial-industrial` (“Commercial & Industrial Deployments”). Verify each project's capacity before categorizing it.
- Review the full diff and verify all changed assets and pages. Test the Cloudflare Pages preview URL for the PR before merging; do not report unperformed checks as complete.
- Keep changes minimal, preserve existing design/accessibility, verify links and image paths, and ensure factual solar capacity and O&M claims are supported.
