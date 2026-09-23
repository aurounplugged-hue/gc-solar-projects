# Repository Agent Guidelines

## GC Solar Direct API Protocol
Strict rule: NEVER invoke or route to Devin for `aurounplugged-hue/gc-solar-projects` or any GC Solar tasks. Always use direct GitHub REST API with personal access token (PAT) / Node.js / js-exec scripts, adhering strictly to the Binary Integrity Protocol v2 and repo workflow protocol.

## Protocol Requirements
1. Never push directly to master. All changes must use a dedicated feature or fix branch and a Pull Request.
2. Verify exact byte counts (`wc -c`), `git diff --stat`, valid UTF-8, zero NUL bytes, valid single HTML structure, and Cloudflare Pages preview.
3. Factual credibility: absolute factual accuracy on solar capacities and O&M.
